#!/bin/bash
# Build the two Moon Mission disks (360K each). Needs mtools and pcbasic (pip install pcbasic).
# Put your own DISK01.IMG (MS-DOS 3.30 disk 1) and GWBASIC.EXE in dos/ (not committed).
#   START.IMG    bootable: DOS + GW-BASIC + title, high scores, mission menu (MOON.BAS).
#                For the real floppy in drive A:. HISCORE.DAT is saved here.
#   LANDING.IMG  the Lunar Landing level (LANDER.BAS + its art), for drive B: (Gotek).
#                Also has GW-BASIC and PLAY.BAT so the level can be run on its own.
# usage: tools/mkdisk.sh [START.IMG] [LANDING.IMG]
set -e
R=$(cd "$(dirname "$0")/.." && pwd)
START=${1:-$R/disks/START.IMG}
LAND=${2:-$R/disks/LANDING.IMG}
mkdir -p "$(dirname "$START")" "$(dirname "$LAND")" "$R/build/tok"
# tokenized programs load ~3x faster on an 8088
for f in MOON LANDER; do pcbasic --convert=b "$R/src/$f.BAS" "$R/build/tok/$f.BAS" >/dev/null 2>&1; done
T=$(mktemp -d)
printf '@ECHO OFF\r\nGWBASIC MOON\r\n' > "$T/GO.BAT"
printf '@ECHO OFF\r\nECHO.\r\nECHO  MOON MISSION - put a mission disk in drive B: and type GO\r\nECHO.\r\n' > "$T/AUTOEXEC.BAT"
printf '@ECHO OFF\r\nGWBASIC LANDER\r\n' > "$T/PLAY.BAT"

# ---------- START disk ----------
cp "$R/dos/DISK01.IMG" "$START"
mattrib -i "$START" -r ::/*.* 2>/dev/null || true
for f in 4201.CPI 5202.CPI COUNTRY.SYS DISPLAY.SYS DRIVER.SYS APPEND.EXE ASSIGN.COM DISKCOMP.COM \
         EXE2BIN.EXE FASTOPEN.EXE FDISK.COM GRAFTABL.COM JOIN.EXE NLSFUNC.EXE PRINT.COM RECOVER.COM \
         SELECT.COM SUBST.EXE KEYB.COM GRAPHICS.COM EDLIN.COM SORT.EXE FIND.EXE COMP.COM LABEL.COM \
         ATTRIB.EXE ANSI.SYS; do mdel -i "$START" ::/$f 2>/dev/null || true; done
mattrib -i "$START" +r +h +s ::/IO.SYS ::/MSDOS.SYS
mcopy -o -i "$START" "$R/dos/GWBASIC.EXE" "$R/build/tok/MOON.BAS" "$R/assets/MOONBG.PIC" \
      "$R/assets/EARTH.SPR" "$R/assets/TITLE.SPR" "$T/GO.BAT" "$T/AUTOEXEC.BAT" ::/
mlabel -i "$START" ::MOONSTART
echo "START:   $(mdir -i "$START" ::/ | grep free | xargs)"

# ---------- LUNAR LANDING disk ----------
rm -f "$LAND"
dd if=/dev/zero of="$LAND" bs=1024 count=360 2>/dev/null
mformat -i "$LAND" -f 360 -v LUNARLAND ::
LEVEL=$(ls "$R"/assets/*.PIC "$R"/assets/*.SPR "$R"/assets/*.MAP | grep -v -E '/(MOONBG\.PIC|EARTH\.SPR|TITLE\.SPR|OFL\.SPR)$')
mcopy -o -i "$LAND" "$R/dos/GWBASIC.EXE" "$R/build/tok/LANDER.BAS" $LEVEL "$T/PLAY.BAT" ::/
echo "LANDING: $(mdir -i "$LAND" ::/ | grep free | xargs)"
rm -rf "$T"
