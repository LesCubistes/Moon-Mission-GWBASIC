# Moon Mission (GW-BASIC)

A space game written in GW-BASIC for a VTech Laser XT (8088, CGA), run from a Gotek floppy emulator.

![Title sequence](earthrise_preview.gif)

## Running
Copy `src/*.BAS` and `assets/*` to a disk with `GWBASIC.EXE`, then from that drive:
```
GWBASIC MOON
```

## Files
| File | What it is |
|---|---|
| `src/MOON.BAS` | Title screen: Earthrise animation, *Also sprach Zarathustra* fanfare, mission menu |
| `src/LANDER.BAS` | Moon Landing mission (placeholder for now) |
| `src/MOONPAL.BAS` | CGA palette test scene |
| `assets/MOONBG.PIC` | `BLOAD` image of CGA video RAM: moon and stars |
| `assets/EARTH.SPR`, `assets/TITLE.SPR` | `GET`/`PUT` sprites loaded with `BLOAD` |
| `tools/mkart.py` | Converts the Earthrise photo into the CGA assets |
| `tools/mkdisk.sh` | Builds a bootable 360K disk image (needs your own DOS disk, not included) |
| `tools/mml2wav.py` | Renders the `PLAY` music to a WAV preview |

## Conventions
- Graphics: `SCREEN 1`, palette "1/6" = cyan / red / grey (`OUT &H3D8,&HE : OUT &H3D9,0`).
- Source files are ASCII with CRLF line endings (enforced by `.gitattributes`).
- Missions are separate programs launched from the menu with `CHAIN`; `SK%` is passed back via `COMMON` to skip the intro.
- Time things with `TIMER`, never `FOR` delay loops: the real XT is far slower than emulators.
- Feed background music with small `PLAY` chunks; a full queue makes `PLAY` block.

MS-DOS and GW-BASIC binaries are Microsoft's and are not included.
