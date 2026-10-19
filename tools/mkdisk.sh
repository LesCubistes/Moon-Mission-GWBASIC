#!/bin/bash
# Build a bootable 360K disk: your own MS-DOS 3.30 disk 1 image + GWBASIC.EXE + the game.
# Needs mtools. Put DISK01.IMG and GWBASIC.EXE in dos/ (not committed).
set -e
R=$(cd "$(dirname "$0")/.." && pwd)
OUT=${1:-$R/disks/MOONMISS.IMG}
mkdir -p "$(dirname "$OUT")"
cp "$R/dos/DISK01.IMG" "$OUT"
mattrib -i "$OUT" -r ::/*.* 2>/dev/null || true
for f in 4201.CPI 5202.CPI COUNTRY.SYS DISPLAY.SYS DRIVER.SYS APPEND.EXE ASSIGN.COM DISKCOMP.COM \
         EXE2BIN.EXE FASTOPEN.EXE FDISK.COM GRAFTABL.COM JOIN.EXE NLSFUNC.EXE PRINT.COM RECOVER.COM \
         SELECT.COM SUBST.EXE KEYB.COM GRAPHICS.COM; do mdel -i "$OUT" ::/$f 2>/dev/null || true; done
mattrib -i "$OUT" +r +h +s ::/IO.SYS ::/MSDOS.SYS
printf '@ECHO OFF\r\nGWBASIC MOON\r\n' > /tmp/GO.BAT
printf '@ECHO OFF\r\nECHO.\r\nECHO  MOON MISSION - type GO to start\r\nECHO.\r\n' > /tmp/AUTOEXEC.BAT
mcopy -o -i "$OUT" "$R/dos/GWBASIC.EXE" "$R"/src/*.BAS "$R"/assets/*.PIC "$R"/assets/*.SPR \
      /tmp/GO.BAT /tmp/AUTOEXEC.BAT ::/
mlabel -i "$OUT" ::MOONMISSN
mdir -i "$OUT" ::/ | tail -2
