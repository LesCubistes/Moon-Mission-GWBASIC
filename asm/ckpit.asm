; CKPIT.BIN - draws the view out of the cockpit window for the Moon Landing success ending.
; Called from GW-BASIC as  CALL CA!(PR(0))  with CA! = VARPTR(MC(0)) and DEF SEG = BASIC's segment.
;   PR(0) = 0 : asks DOS for a 64K segment, returned in PR(1) (0 if there is not enough memory)
;   PR(0) = 3 : gives that segment back (before CHAIN, so playing again doesn't use up memory)
;   PR(0) = 2 : a site's scenery was just BLOADed at offset 0 of that segment: put it in place and
;               make the three copies shifted by 1, 2, 3 pixels (so drawing is plain byte copies)
;   PR(0) = 4 : show stored screen PR(2) (0..2) from segment PR(1), and its map into H() at PR(3) if <> 0
;   PR(0) = 6 : unpack an RLE screen at offset PR(3) of segment PR(1) into slot PR(2) (-1 = the screen)
;   PR(0) = 8 : copy PR(4) words inside BASIC's segment from PR(2) to PR(3) (GW-BASIC's PUT can't
;               take an array element, so sprites are copied into the arrays PUT uses)
;   PR(0) = 1 : draw one frame.  PR(1) segment, PR(2) altitude (0..127), PR(3) drift in pixels
;               (signed), PR(4) dust 0..3, PR(5) jolt (rows)
; The scenery segment (made by tools/mkckpit.py, CKn.DAT at 0 and CKCOM.DAT at C100h):
;   0000 ground strip, 4 copies (shift 0..3) x 64 rows x 64 bytes (256 px wide, wraps)
;   4000 rim strip, 4 copies x 128 rows x 64 bytes
;   C000 horizon row by altitude [128]    C080 horizon minus rim top by altitude [128]
;   C140 window rows: byte count, last-byte mask [96 x 2]
;   C200 ground slide speed per row in 1/16 [64]   C240 rim slide speed   C300 dust, 3 x 32 rows x 112
;   EF00 variables
; The window is screen x 64.., y 12..107; each row is copied with its own sideways slide
; (near ground slides faster than far), so the land moves past in the direction of travel.
bits 16
cpu 8086
org 0
GND    equ 0000h
RIM    equ 4000h
S_HZ   equ 0C000h
S_ROFF equ 0C080h
WTAB   equ 0C140h
GF     equ 0C200h
RIMF   equ 0C240h
DUST   equ 0C300h
V_HZ   equ 0EF00h
V_RY   equ 0EF02h
V_DR   equ 0EF04h
V_DU   equ 0EF06h
V_R    equ 0EF08h
V_PH   equ 0EF0Ah
V_N    equ 0EF10h

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
alloc:  mov ah, 48h                     ; mode 0: ask DOS for 64K (PR(1) = 0 if there isn't any)
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
        mov ax, [bx]
        cmp ax, 2
        jne w4
        jmp setup
w4:     cmp ax, 4
        jne w6
        jmp show
w6:     cmp ax, 6
        jne w8
        jmp unrle
w8:     cmp ax, 8
        jne draw
        mov si, [bx+4]                  ; mode 8: copy PR(4) words from DS:PR(2) to DS:PR(3)
        mov di, [bx+6]
        mov cx, [bx+8]
        push ds
        pop es
        rep movsw
        jmp finish

; ------------------------------------------------------------------ draw one frame
draw:   mov ax, [bx+4]
        cmp ax, 0
        jge z1
        xor ax, ax
z1:     cmp ax, 127
        jle z2
        mov ax, 127
z2:     mov si, ax
        mov cx, [bx+6]
        mov dx, [bx+8]
        mov di, [bx+10]
        mov ds, [bx+2]
        xor ax, ax
        mov al, [si+S_HZ]
        add ax, di
        mov [V_HZ], ax
        xor bx, bx
        mov bl, [si+S_ROFF]
        sub ax, bx
        mov [V_RY], ax
        mov [V_DR], cx
        xor ax, ax
        or dx, dx
        jz nodustf
        mov ax, [V_PH]
        add ax, 23
        and ax, 63
        mov [V_PH], ax
        mov bx, ax
        dec dx
        mov ax, 32*112
        mul dx
        add ax, DUST
        add ax, bx
nodustf:
        mov [V_DU], ax
        mov ax, 0B800h
        mov es, ax
        mov word [V_R], 0
rowloop:
        mov ax, [V_R]                   ; di = screen address of window row
        add ax, 12
        mov bx, ax
        shr ax, 1
        mov dx, 80
        mul dx
        add ax, 16
        test bl, 1
        jz even
        add ax, 2000h
even:   mov di, ax
        mov ax, [V_R]
        cmp ax, [V_HZ]
        jl notg
        sub ax, [V_HZ]                  ; ground row j
        cmp ax, 63
        jle g1
        mov ax, 63
g1:     mov bx, ax
        mov cl, 6
        shl ax, cl
        mov si, ax                      ; GND + j*64
        mov al, [bx+GF]
        mov bx, 1000h                   ; size of one ground copy
        jmp haveF
notg:   sub ax, [V_RY]
        jl black
        mov cl, 6
        shl ax, cl
        add ax, RIM
        mov si, ax
        mov al, [RIMF]
        mov bx, 2000h
haveF:  xor ah, ah
        imul word [V_DR]
        mov cl, 4
        shr ax, cl                      ; al = first texture pixel (mod 256)
        mov cl, al
        and cl, 3                       ; pixel shift -> which copy
        jz sh0
shl1:   add si, bx
        dec cl
        jnz shl1
sh0:    shr al, 1
        shr al, 1
        xor ah, ah                      ; ax = first byte b (0..63)
        mov bx, [V_R]                   ; byte count and last-byte mask for this row
        shl bx, 1
        mov dx, [bx+WTAB]               ; dl = count, dh = mask
        mov bp, si                      ; bp = row start
        add si, ax
        mov bx, 64
        sub bx, ax                      ; bytes before the wrap
        xor cx, cx
        mov cl, dl
        dec cx                          ; all but the last byte
        cmp cx, bx
        jbe nowrap
        sub cx, bx
        xchg cx, bx
        rep movsb
        mov si, bp
        mov cx, bx
nowrap: rep movsb
        mov ax, si                      ; last byte, wrapped, under the window mask
        sub ax, bp
        and ax, 63
        add ax, bp
        mov si, ax
        lodsb
        mov ah, [es:di]
        and al, dh
        not dh
        and ah, dh
        not dh
        or al, ah
        stosb
        jmp dust
black:
        mov bx, [V_R]                   ; byte count and last-byte mask for this row
        shl bx, 1
        mov dx, [bx+WTAB]               ; dl = count, dh = mask
        xor ax, ax
        xor cx, cx
        mov cl, dl
        dec cx
        rep stosb
        mov al, [es:di]
        not dh
        and al, dh
        not dh
        stosb
dust:   mov ax, [V_R]                   ; engine dust: XOR grains over the bottom 32 rows
        cmp ax, 64
        jl nextrow
        mov si, [V_DU]
        or si, si
        jz nextrow
        sub ax, 64
        mov bx, 112
        push dx
        mul bx
        pop dx
        add si, ax
        xor cx, cx
        mov cl, dl
        sub di, cx
        dec cx
        jz dlast
dloop:  lodsb
        xor [es:di], al
        inc di
        loop dloop
dlast:  lodsb
        and al, dh
        xor [es:di], al
nextrow:
        inc word [V_R]
        cmp word [V_R], 96
        jge finish
        jmp rowloop

; ------------------------------------------------------------------ setup a site
; staged at 0: ground 0000-0FFF, rim 1000-2FFF, tables 3000-30FF
setup:  mov ax, [bx+2]
        mov ds, ax
        mov es, ax
        mov si, 3000h                   ; tables -> C000
        mov di, S_HZ
        mov cx, 256
        rep movsb
        mov si, 1000h                   ; rim copy 0 -> 4000
        mov di, RIM
        mov cx, 2000h
        rep movsb
        xor bx, bx                      ; ground copies 1..3 from copy 0
        mov dx, 64
        call shifts
        mov bx, RIM                     ; rim copies 1..3
        mov dx, 128
        call shifts
        jmp finish

; bx = copy 0, dx = rows. Copy s (at bx + s*rows*64) = copy 0 shifted left s pixels, wrapping.
shifts: mov [V_N], dx
        mov cl, 6
        shl dx, cl                      ; dx = size of one copy
        mov di, bx
        add di, dx
        mov cl, 2                       ; shift in bits
shnext: mov si, bx                      ; source row start
        mov ax, [V_N]
        mov bp, ax                      ; rows left
shrow:  push bx
        xor bx, bx
shbyte: mov ah, [si+bx]
        inc bx
        and bx, 63
        mov al, [si+bx]
        shl ax, cl
        mov [di], ah
        inc di
        or bx, bx
        jnz shbyte
        pop bx
        add si, 64
        dec bp
        jnz shrow
        add cl, 2
        cmp cl, 8
        jb shnext
        ret

; ------------------------------------------------------------------ mode 4: show a stored screen
; PR(1) segment of the screen store, PR(2) slot k (0 left, 1 centre, 2 right) at k*4000h,
; PR(3) <> 0: also copy that slot's map (640 integers at C000h + k*500h) to BASIC's H() at DS:PR(3)
show:   mov dx, [bx+4]                  ; k
        mov di, [bx+6]                  ; H() address (0 = no map)
        mov ax, [bx+2]
        push ds
        pop es                          ; es = BASIC data (for the map copy)
        mov ds, ax
        or di, di
        jz nomap
        mov ax, 500h
        mul dx
        add ax, 0C000h
        mov si, ax
        mov cx, 640
        rep movsw
nomap:  mov bx, [bp+6]                  ; PR() is in BASIC's segment: read k again through es
        mov ax, [es:bx+4]
        mov cl, 14
        shl ax, cl                      ; k * 4000h
        mov si, ax
        mov ax, 0B800h
        mov es, ax
        xor di, di
        mov cx, 2000h
        rep movsw
        jmp finish

; ------------------------------------------------------------------ mode 6: unpack an RLE screen
; PR(1) segment, PR(2) slot k (or -1 for the screen at B800:0), PR(3) offset of the packed data.
; Packed: FEh n v = n copies of v (n = 0 means 256); any other byte is itself. 16384 bytes out.
unrle:  mov si, [bx+6]
        mov ax, [bx+4]
        mov dx, [bx+2]
        mov ds, dx
        cmp ax, -1
        jne toslot
        mov dx, 0B800h
        xor di, di
        jmp rl0
toslot: mov cl, 14
        shl ax, cl
        mov di, ax
rl0:    mov es, dx
        mov dx, di
        add dx, 4000h                   ; end of output
rlnext: cmp di, dx
        jae rldone
        lodsb
        cmp al, 0FEh
        jne rllit
        lodsb
        xor ch, ch
        mov cl, al
        or cx, cx
        jnz rlrun
        mov cx, 256
rlrun:  lodsb
        rep stosb
        jmp rlnext
rllit:  stosb
        jmp rlnext
rldone: jmp finish

finish: pop di
        pop si
        pop ds
        pop es
        pop bp
        retf 2
