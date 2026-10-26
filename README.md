# Moon Mission (GW-BASIC)

A space game written in GW-BASIC for a VTech Laser XT (8088, CGA), played from a real floppy in A: and a Gotek floppy emulator in B:.

![Title sequence](earthrise_preview.gif)

The first mission is **Moon Landing**: pick a landing site from orbit, then fly the lunar module down onto a landing pad. Every screen of the level is shown in [`docs/screens.png`](docs/screens.png).

## The disks
The game is split into one start disk and one disk per mission, built by `tools/mkdisk.sh`.

| Disk | Drive | What's on it |
|---|---|---|
| `START.IMG` (label MOONSTART) | A: | A game disk: only the DOS boot files, GW-BASIC and the game. It boots straight into Moon Mission (title, high scores, mission menu: `MOON.BAS`). On a Laser XT it switches to fast mode first (`LASERCHK` finds the Laser's Central Point BIOS, then `SPEED F`); other PCs skip that, since SPEED writes to a port that is the hard disk controller on AT-class machines. High scores are saved here as `LANDHS.DAT`. |
| `LANDING.IMG` (label LUNARLAND) | B: | The Moon Landing level (`LANDER.BAS`) and all of its art. No GW-BASIC: the START disk runs it, so the space goes to the level. Future levels get their own disk, or share one, depending on size. |

Both disks work as real 360K floppies in two drives, or with a Gotek as B:. To make a floppy from an image on the Gotek: `DISKCOPY B: A:`. Leave the START floppy's write-protect tab off so high scores can be saved.

## Playing
Boot from the START floppy in A: with the LUNAR LANDING disk in B:. The game starts on its own (fast mode is switched on for a Laser XT). After EXIT TO DOS, `GO` starts it again.

One floppy drive is fine too: the game notices (BIOS equipment word) and asks you to swap disks in A: when it needs the other one, going into the landing, to save a high score, and going back to the menu. On a Tandy 1000 the game sets the Tandy's own palette registers so the colors match the CGA (cyan, red, grey).

The title plays an Earthrise to *Also sprach Zarathustra*, then shows the high scores. Any key goes to the mission menu. If the level disk isn't in B:, the menu asks for it instead of stopping.

**Orbit (choose a site).** The Moon's horizon is split into three zones: Tranquility (Easy), Fra Mauro (Medium), Hadley Rille (Hard). 4/6 or the arrow keys drift left and right (no fuel used, no points). 2, down arrow or Enter fires the descent. Esc returns to the menu.

**Braking burn.** A short hands-off cutscene: zoomed far out, the small lander flies over the Moon engine-first to slow down (POWERED DESCENT), swings upright (PITCHOVER) and heads for the site marked on the limb (APPROACH PHASE). No fuel used. Any key skips it.

**Landing (keypad, NumLock on).**

| Key | Action |
|---|---|
| 8 / 5 (or grey + / -) | Main engine throttle up / down, 10% a press |
| 0 or Space | Main engine off |
| 7 9 4 6 1 2 3 | Maneuvering thrusters (hold for a steady burn) |
| Esc | Back to orbit |

No walls at the top or sides. Climb off the top and the lander hides while a marker on the top edge shows where it is (the HUD keeps the altitude); gravity brings it back, and fuel limits how far you can go. Fly off the left or right edge and the screen flips to danger ground on that side: boulders, crevasses and steep slopes with nowhere safe to land, ending in a natural wall (a crater rim, a ridge, Mount Hadley's flank). Fly back to return to the site.

Land on a flat patch slowly and nearly level. Touching down too fast, drifting, landing on a slope or flying into terrain all crash, in five different ways (hard landing, impact, tipping over, sliding off a rim, and a rare runaway thruster).

## Scoring
Each level gives 3 landers. A crash with landers left shows a short report and the next lander starts. Losing all three ends the level with a picture: the wreck (last one crashed) or a crater (last one exploded).

**Touchdown, from the cockpit.** A safe landing replays the last 10 seconds of your own descent out of the commander's window: helmet visor at the edges, glove on the throttle, a glass panel counting down altitude and speeds. The horizon rises as you sink toward the surface, the land slides past in the direction you were drifting (near ground faster than far), engine dust streaks across the bottom, then the touchdown jolt, CONTACT and ENGINE STOP. The score comes up on the panel. Each site has its own view: the flat dark mare at Tranquility, Cone crater's rim and the boulder field at Fra Mauro, Mount Hadley and the rille at Hadley. Any key skips to the score.

**Score = (soft landing + time bonus) x pad x lander used**
- Soft landing: up to 500, less for vertical speed and drift at touchdown
- Time bonus: 2000, minus 50 per second
- Pad: each site has three pads. Black is the easiest and pays least, dark grey is the middle, solid grey is the narrowest and pays most
- Lander used: 1st 100%, 2nd 50%, 3rd 25%

| Site | Fuel | Pads (black / dark grey / grey) |
|---|---|---|
| Tranquility Base (Easy) | 800 | x2 / x3 / x5 |
| Fra Mauro (Medium) | 700 | x3 / x5 / x7 |
| Hadley Rille (Hard) | 650 | x4 / x7 / x10 |

A fast pilot does best on the far, high-paying pad; a slower one often scores more on a closer pad. The top 10 (initials, score, site) are saved on the START disk. The table starts empty and fills as you play.

## Files
| File | What it is |
|---|---|
| `src/MOON.BAS` | START disk: title (Earthrise, music, twinkling stars, shooting stars), high scores, mission menu |
| `src/LANDER.BAS` | Moon Landing: orbit site selection, landing physics, crashes, scoring, high score entry, end pictures |
| `src/MOONPAL.BAS` | CGA palette test scene (not on the disks) |
| `assets/*.PIC` | `BLOAD` images of CGA video RAM: title moon, orbit, the three landing sites, landed / wreck / crater pictures |
| `assets/*.MAP` | Collision maps for each site: ground height per column, and the highest ground under the lander's footprint |
| `assets/*.SPR` | `GET`/`PUT` sprites: lander and mask, engine flames, thruster puffs, crash poses, dust plumes, Earth, title |
| `asm/laserchk.asm` | `LASERCHK.COM`: exits with ERRORLEVEL 1 on a Laser XT (looks for "Central Point" in the BIOS ROM) |
| `tools/mkdisk.sh` | Builds `START.IMG` and `LANDING.IMG` (needs your own DOS disk, GW-BASIC and SPEED.COM in `dos/`) |
| `tools/mkart.py`, `tools/earth.py` | Title art: cratered moon, starfield, title, the lit Earth from real coastline data (`pip install global-land-mask`) |
| `tools/mklevel.py`, `tools/mksites.py` | Tranquility, and Fra Mauro / Hadley Rille terrain, pads and collision maps; lander, flame and crash sprites |
| `tools/mkorbit.py` | The orbit screen |
| `tools/mkbrake.py` | The braking burn cutscene: `BRAKE.RLE` (scene) and `BRAKE.SPR` (small lander in four poses, each with mask and flame) |
| `tools/mkdanger.py` | The danger screens left and right of each site: `EASYL.RLE`, `EASYR.RLE`, ... and their `.MAP` collision maps |
| `tools/mklanded.py` | The landed, wreck and crater pictures (based on an Apollo surface photo, drawn in our lander's style). LANDED.PIC is kept for the surface mission |
| `tools/mkckpit.py` | The cockpit ending: `COCKPIT.PIC`, each site's scenery (`CK1.DAT`..`CK3.DAT`: a ground strip and a rim strip that wrap around, plus horizon tables), the shared `CKCOM.DAT` (window shape, slide speeds, dust) and `CKPIT.BIN`. Also writes preview GIFs drawn by a Python copy of the machine code |
| `tools/mkcockpit.py` | The cockpit picture and site scenery shared with `mkckpit.py`; run on its own it makes the design mockups |
| `asm/ckpit.asm` | `CKPIT.BIN`, the small 8086 routine LANDER `CALL`s for jobs BASIC is too slow or can't do: drawing the cockpit window view each frame, unpacking RLE screens, flipping to a stored screen and its map, and copying sprites between arrays |
| `tools/mkdust.py`, `tools/mkstars.py` | Engine dust sprites; picks the stars that twinkle |
| `tools/flytest.py` | Boots disks in DOSBox-X at XT speed, plays a timed key script and saves screenshots (`IMGB=` mounts a second disk as B:) |
| `tools/mml2wav.py` | Renders the `PLAY` music to a WAV preview |
| `docs/design/` | Design mockups made along the way |

## Building
Needs Python 3 (numpy, Pillow), mtools, PC-BASIC (`pip install pcbasic`, used to tokenize the programs) and NASM to rebuild `asm/ckpit.asm` (`nasm -f bin asm/ckpit.asm -o build/ckpit.bin`, then `tools/mkckpit.py assets build/ckpit.bin`; add `--preview` for GIFs of each site). Put your own `DISK01.IMG` (MS-DOS 3.30 disk 1), `GWBASIC.EXE` and the Laser XT `SPEED.COM` in `dos/`, then run `tools/mkdisk.sh`. The images land in `disks/`.

## Conventions
- Graphics: `SCREEN 1`, palette cyan / red / grey (`OUT &H3D8,&HE : OUT &H3D9,0`).
- Source files are ASCII with CRLF line endings (enforced by `.gitattributes`).
- GW-BASIC lines must stay under 255 characters. A longer line silently cuts off the rest of the program when it's tokenized, so `mkdisk.sh` refuses to build if one appears.
- The disks carry tokenized programs: they load about 3x faster on an 8088 than plain text.
- Missions are separate programs started from the menu with `CHAIN` from the drive in `LD$` (B:). `COMMON` passes `SK%` (skip the intro on return), `LS%` (landing site chosen, for the future surface mission) and `LD$`. LANDER creates all three at its start too, so they exist even when it is run on its own.
- Create every simple variable before any `BLOAD ... VARPTR`, so arrays don't move under a load. This matters even more for `CKPIT.BIN`: it lives in an array, and if a new variable appears later the array moves and `CALL` jumps into the wrong place.
- Before `CHAIN`, LANDER erases its arrays (newest first). Otherwise `CHAIN` drops each non-COMMON variable one at a time, shifting every array each time, which took minutes on an XT.
- GW-BASIC looks variables up in the order they were created, so the ones a tight loop uses are created first (line 55 for the cockpit replay).
- Two 64K blocks are asked from DOS (`CKPIT.BIN` mode 0) and handed back before `CHAIN` (mode 3): one for the cockpit scenery, one holding the site and its two danger screens with their maps (slots at 0000h, 4000h, 8000h; maps at C000h + slot x 500h; packed files land at D000h). The site's screens load once; a lander after a crash starts from memory, and the side flips are instant.
- Danger screens and the cutscene are RLE-packed (`FEh n v` = n copies of v). Dithered ground packs to about 3K a screen.
- GW-BASIC's `PUT` and `GET` take only a whole array, never `A(n)`, so sprites stored together in one array are copied out with `CKPIT.BIN` mode 8 before drawing.
- Every line that can be fallen into needs a `GOTO` before the next block (line 1096): new subroutines dropped in after a block run by accident otherwise. If DOS has no 64K to spare, the score still shows on the cockpit panel, just without the replay.
- The flight recorder keeps 25 samples (every HUD update, 0.4 s) of altitude, position, speeds and throttle for the replay.
- Time things with `TIMER`, never `FOR` delay loops: the real XT is far slower than emulators.
- Every BASIC statement costs real time at 4.77 MHz (an extra line checked each frame is noticeable). Per-frame work stays minimal; ambient effects run on a one-second tick.
- Moving things are drawn so they never smear the scene: the lander saves and restores the area under it with `GET`/`PUT`; dust is `PUT ... XOR` (drawing twice restores the ground); the module overhead and the shadow keep a copy of what they cover.
- Load screens with the display switched off (`OUT &H3D8,&H6`) and turn it back on when drawn.
- Feed background music with small `PLAY` chunks; a full queue makes `PLAY` block.

MS-DOS, GW-BASIC and SPEED.COM are not included.
