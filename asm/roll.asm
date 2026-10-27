; ROLL.BIN - the rolling moonscape under the title's earthrise (MOON.BAS).
; Called from GW-BASIC as  CALL RA!(PR(0))  with RA! = VARPTR(RC(0)) and DEF SEG = BASIC's segment.
;   PR(0) = 0 : asks DOS for a 64K segment, returned in PR(1) (0 if there is not enough memory)
;   PR(0) = 3 : gives segment PR(1) back (before CHAIN or SYSTEM)
;   PR(0) = 1 : one frame: the ground moves PR(11) steps toward the viewer.  PR(1) segment (ROLL.DAT
;               BLOADed at offset 0).  PR(2..5) rows y1, y2 and bytes b1, b2 (b2 not included) of a
;               box to leave alone (the menu), PR(6..9) a second box left of the first (the pad hints).
;               A box with y1 > y2 is off.  PR(10) >= 0: first draw the rising Earth with its top on
;               that row, only the rows above the horizon (row 126).
; ROLL.DAT, made by tools/mkrollmoon.py:
;   0000 rows NR, 0002 first row Y0, 0004 masked rows NM, 0006 bands NB, 0008.. variables,
;   003E address of the Earth (82 rows of 24 bytes, drawn at x 112)
;   0040 bands, 8 bytes each: phase, step, rows*256 (all 8.8 fixed point, in texture rows)
;   0100 rows, 8 bytes each: texture for even screen rows, for odd rows, band offset, depth A (8.8)
;   0400 the first NM rows are part sky: 240 bytes each, SKY mask, GROUND mask, skyline LIP pixels
;   1800 band textures: rows of 80 bytes, two copies per band (dithered for even and odd screen rows)
bits 16
cpu 8086
org 0
H_NR   equ 0
H_Y0   equ 2
H_NM   equ 4
H_NB   equ 6
V_BOX  equ 8            ; 10 words: box 1 y1 y2 b1 b2, box 2 y1 y2 b1 b2, Earth top, steps
V_EY   equ 18h
V_NS   equ 1Ah
V_R    equ 20h
V_Y    equ 22h
V_SRC  equ 24h
V_DST  equ 26h
V_LO   equ 28h
H_EAR  equ 3Eh
EHZ    equ 126
EROWS  equ 82
BANDS  equ 40h
ROWS   equ 100h
MASKS  equ 400h

entry:
        push bp
        mov bp, sp
        mov bx, [bp+6]
        mov ax, [bx]
        cmp ax, 0
        je alloc
        cmp ax, 3
        jne work
        mov ax, [bx+2]                  ; mode 3: give the segment back to DOS
        or ax, ax
        jz ret0
        push es
        mov es, ax
        mov ah, 49h
        int 21h
        pop es
        mov word [bx+2], 0
ret0:   pop bp
        retf 2
alloc:  mov ah, 48h                     ; mode 0: ask DOS for 64K
        push bx
        mov bx, 1000h
        int 21h
        pop bx
        jnc gotmem
        xor ax, ax
gotmem: mov [bx+2], ax
        pop bp
        retf 2

work:   push es
        push ds
        push si
        push di
        cld
        mov ax, [bx+2]                  ; copy the two boxes into the segment's variables
        mov es, ax
        lea si, [bx+4]
        mov di, V_BOX
        mov cx, 10
        rep movsw
        mov ds, ax
nstep:  cmp word [V_NS], 0
        jle stepped
        dec word [V_NS]
        mov cx, [H_NB]                  ; every band moves on one step
        mov si, BANDS
bstep:  mov ax, [si]
        add ax, [si+2]
        cmp ax, [si+4]
        jb bok
        sub ax, [si+4]
bok:    mov [si], ax
        add si, 8
        loop bstep
        jmp nstep
stepped:
        mov ax, 0B800h
        mov es, ax
        mov bx, [V_EY]                  ; the rising Earth, rows above the horizon only
        or bx, bx
        jl noearth
        mov si, [H_EAR]
erow:   cmp bx, EHZ
        jge noearth
        mov ax, bx
        sub ax, [V_EY]
        cmp ax, EROWS
        jge noearth
        mov ax, bx
        shr ax, 1
        mov dx, 80
        mul dx
        test bl, 1
        jz eeven
        add ax, 2000h
eeven:  add ax, 28
        mov di, ax
        mov cx, 12
        rep movsw
        inc bx
        jmp erow
noearth:
        mov word [V_R], 0

rowloop:
        mov ax, [V_R]
        cmp ax, [H_NR]
        jb rgo
        jmp finish
rgo:    mov bx, ax
        add ax, [H_Y0]
        mov [V_Y], ax                   ; screen row y
        mov cl, 3
        shl bx, cl
        add bx, ROWS                    ; bx = this row's entry
        mov si, [bx+4]                  ; band
        mov ax, [bx+6]
        add ax, [si]                    ; depth + phase
        cmp ax, [si+4]
        jb jok
        sub ax, [si+4]
jok:    mov al, ah
        xor ah, ah                      ; texture row j
        mov dx, 80
        mul dx
        test byte [V_Y], 1
        jz srce
        add ax, [bx+2]
        jmp srcd
srce:   add ax, [bx]
srcd:   mov [V_SRC], ax
        mov ax, [V_Y]                   ; screen address
        mov bx, ax
        shr ax, 1
        mov dx, 80
        mul dx
        test bl, 1
        jz deven
        add ax, 2000h
deven:  mov [V_DST], ax
        mov ax, [V_R]
        cmp ax, [H_NM]
        jae plain

        ; ---- part-sky row: keep the sky (stars, the Earth), lay the ground under it, add the lip
        mov dx, 240
        mul dx
        add ax, MASKS
        mov bx, ax
        mov si, [V_SRC]
        mov di, [V_DST]
        mov cx, 80
mloop:  mov al, [es:di]
        and al, [bx]
        mov ah, [si]
        and ah, [bx+80]
        or al, ah
        or al, [bx+160]
        stosb
        inc si
        inc bx
        loop mloop
        jmp nextrow

        ; ---- ground row: plain copy, around the boxes
plain:  mov word [V_LO], 0
        mov si, V_BOX+8                 ; box 2 (left) first
        call box
        mov si, V_BOX                   ; then box 1
        call box
        mov cx, 80
        call span
nextrow:
        inc word [V_R]
        jmp rowloop

; si = box (y1, y2, b1, b2): if this row is in it, copy up to b1 and skip to b2
box:    mov ax, [V_Y]
        cmp ax, [si]
        jl boxno
        cmp ax, [si+2]
        jg boxno
        mov cx, [si+4]
        push si
        call span
        pop si
        mov ax, [si+6]
        mov [V_LO], ax
boxno:  ret

; copy bytes V_LO .. cx-1 of this row
span:   sub cx, [V_LO]
        jle spno
        mov si, [V_SRC]
        add si, [V_LO]
        mov di, [V_DST]
        add di, [V_LO]
        shr cx, 1
        jnc spw
        movsb
spw:    rep movsw
spno:   ret

finish: pop di
        pop si
        pop ds
        pop es
        pop bp
        retf 2
