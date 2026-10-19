#!/bin/bash
# Boot a disk image in DOSBox-X (CGA, 8088-ish speed), type a command, capture frames + speaker audio.
# usage: dbtest.sh IMG "command" seconds outdir
IMG=$1; CMD=$2; SECS=$3; OUT=$4
mkdir -p $OUT; rm -f $OUT/*
cat > $OUT/dbx.conf <<EOF
[sdl]
output=surface
[dosbox]
machine=cga
memsize=1
captures=$OUT
[cpu]
cputype=8086
core=normal
cycles=fixed 300
[render]
aspect=false
[speaker]
pcspeaker=true
[sblaster]
sbtype=none
[mixer]
rate=22050
[autoexec]
imgmount a $IMG -t floppy
boot a:
EOF
export DISPLAY=:97
Xvfb :97 -screen 0 1024x768x24 >/dev/null 2>&1 & XV=$!
sleep 2
SDL_AUDIODRIVER=dummy dosbox-x -conf $OUT/dbx.conf -nopromptfolder >$OUT/dbx.log 2>&1 & DB=$!
sleep 10
W=$(xdotool search --name "DOSBox" | head -1)
xdotool windowfocus $W
xdotool key --delay 50 ctrl+F6        # start wave capture
xdotool type --delay 90 "$CMD"; xdotool key Return
N=$((SECS*2))
for i in $(seq -w 1 $N); do sleep 0.5; import -window root $OUT/f$i.png; done
shift 4
j=0
for k in "$@"; do j=$((j+1)); xdotool key $k; sleep 4; import -window root $OUT/k$j.png; done
xdotool key ctrl+F6
sleep 1
kill $DB $XV 2>/dev/null; wait 2>/dev/null
ls $OUT | grep -v '^f'
