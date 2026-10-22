; LASERCHK.COM - is this a VTech Laser XT? Exits with ERRORLEVEL 1 if the BIOS ROM (segment F000)
; holds "Central Point" (the Laser XT's BIOS: "BIOS v1.21 Copyright 1986-1988 Central Point
; Software, Inc."), else 0. AUTOEXEC.BAT runs SPEED F only on a Laser XT, because SPEED.COM
; writes to port 1F0h, which is the hard disk controller on AT-class machines.
bits 16
cpu 8086
org 100h
        cld
        mov ax, 0F000h
        mov es, ax
        xor di, di
        mov cx, 65536 - 13
scan:   mov si, pat
        push di
        push cx
        mov cx, 13
        repe cmpsb
        pop cx
        pop di
        je found
        inc di
        loop scan
        mov ax, 4C00h
        int 21h
found:  mov ax, 4C01h
        int 21h
pat     db 'Central Point'
