RYAN BARRINEAU'S MOON MISSION
=============================

Land the lunar module on the Moon. A GW-BASIC game for the IBM PC/XT
and compatibles with CGA graphics, first written for a VTech Laser XT.

Pick a landing site from orbit (Tranquility Base, Fra Mauro or Hadley
Rille), ride the braking burn down, then fly the lander onto a pad with
the engine and side jets. Three landers per mission. A safe touchdown is
replayed out of the commander's window.


WHAT YOU NEED
-------------
* An IBM PC, XT, AT or compatible (8088 or better), or the DOSBox
  emulator on a modern computer.
* CGA graphics (a Tandy 1000 works too).
* 512K of memory. With less, the title Moon stands still and the
  touchdown replay is skipped.
* MS-DOS or PC-DOS 3.0 or later (2.1 works if you skip MAKEBOOT).
* Your own copy of GW-BASIC (version 3.22 is tested; Tandy's BASIC
  2.02 runs it too). GWBASIC.EXE is NOT included, and neither is DOS.
* Two 360K floppy drives, or one (the game asks you to swap), or a
  hard disk.


WHAT'S IN THE ZIP
-----------------
FLOPPY\START.IMG     the START disk (title, high scores, mission menu)
FLOPPY\LANDING.IMG   the LUNAR LANDING disk (the Moon Landing mission)
MOON\                every game file in one folder, for a hard disk or
                     DOSBox
README.TXT           this file

The disk images are plain 360K floppy images. Write them to real
floppies with a tool such as WinImage, dd or Greaseweazle, or load them
on a Gotek. They are data disks: they do not boot by themselves.


PLAYING FROM FLOPPIES
---------------------
1. Copy GWBASIC.EXE onto the START disk (there is room).
2. Boot your computer into DOS.
3. Put START in drive A: and LUNAR LANDING in drive B:.
4. Type   A:   and press Enter, then type   GO   and press Enter.

With one floppy drive, use A: for both; the game tells you when to swap.
Leave START's write-protect tab off so high scores can be saved.

To make START boot straight into the game, run MAKEBOOT from DOS. It
puts your DOS system files, COMMAND.COM and GW-BASIC on the disk and
writes an AUTOEXEC.BAT that starts the game:

    B:MAKEBOOT B: C:\DOS\GWBASIC.EXE

The first word is the START disk's drive, the second is where your
GWBASIC.EXE is. If SYS says there is no room for the system, format a
blank disk with   FORMAT B: /S   , copy everything from START onto it,
and run MAKEBOOT on the new disk.


PLAYING FROM A HARD DISK OR DOSBOX
----------------------------------
Copy the MOON folder to your hard disk and put GWBASIC.EXE in it. Then:

    CD \MOON
    GO

In DOSBox, set the machine to CGA (machine=cga in the DOSBox settings)
and about 300 cycles for real XT speed, then:

    MOUNT C C:\GAMES      (the folder that holds MOON)
    C:
    CD \MOON
    GO


CONTROLS
--------
Use the number pad. The arrow keys work too.

  Orbit:    4 / 6 drift left and right, 2 or Enter descends, Esc menu
  Landing:  8 or +      more main engine (+10%)
            5 or -      less main engine (-10%)
            0 or Space  engine off
            4 6         push left / right
            7 9         lift up-left / up-right
            1 2 3       push down
            Esc         back to orbit

A gameport joystick or gamepad works too: press J on the title screen
to set it up. Answer Y to HOLD A TO BURN if you want the engine to fire
only while the A button is held.

The game opens with a three-page briefing on the controls, the gauges
and the scoring.


THE GAUGES
----------
  ALT   height above the ground
  H     sideways speed: +1.5 means moving right
  V     up/down speed: -3.2 means moving down
  THR   main engine power, in percent
  The bar at the top left is your fuel.

A safe landing: V no faster than -4.0, H within 2.0, and both feet on
level ground.


SCORING
-------
  (soft landing + time bonus) x pad x lander used

  Soft landing   up to 500, less for speed at touchdown
  Time bonus     2000, less 50 for every second
  Pad            x2 to x10 (the narrowest pads pay most; off a pad x1)
  Lander used    1st full score, 2nd half, 3rd a quarter

  Tranquility Base   EASY     fuel 800   pads x2 x3 x5
  Fra Mauro          MEDIUM   fuel 700   pads x3 x5 x7
  Hadley Rille       HARD     fuel 650   pads x4 x7 x10

The top ten scores are kept on the START disk (LANDHS.DAT).


MORE
----
Source code, art tools and the developer notes:
https://github.com/LesCubistes/Moon-Mission-GWBASIC

MS-DOS and GW-BASIC are trademarks of Microsoft. Neither is included.
The title credit uses the Dancing Script font (SIL Open Font License).
