"""Boot the disk in DOSBox-X (CGA, ~XT speed), run a command, then play a timed key script
while grabbing frames. usage: flytest.py IMG OUTDIR "command" "t:key t:key ..." total_seconds
keys are xdotool names (KP_8, Return, space...). Frames: OUTDIR/f###.png every 0.5 s from command start.
"""
import subprocess, sys, time, os, shutil
img, out, cmd, script, total = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], float(sys.argv[5])
shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
conf = f"""[sdl]
output=surface
[dosbox]
machine={os.environ.get("MACHINE", "cga")}
memsize=1
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
[autoexec]
imgmount a {img}{(" " + os.environ["SWAP"]) if os.environ.get("SWAP") else ""} -t floppy
{"imgmount b " + os.environ["IMGB"] + " -t floppy" if os.environ.get("IMGB") else ""}
boot a:
"""
open(f"{out}/dbx.conf", "w").write(conf)
env = dict(os.environ, DISPLAY=":96", SDL_AUDIODRIVER="dummy")
xv = subprocess.Popen(["Xvfb", ":96", "-screen", "0", "1024x768x24"], stderr=subprocess.DEVNULL)
time.sleep(2)
db = subprocess.Popen(["dosbox-x", "-conf", f"{out}/dbx.conf", "-nopromptfolder"], env=env,
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
import atexit
atexit.register(lambda: (db.kill(), xv.kill()))
time.sleep(10)
x = lambda *a: subprocess.run(["xdotool", *a], env=env, capture_output=True, text=True).stdout
ids = x("search", "--name", "DOSBox").split()
if not ids: time.sleep(5); ids = x("search", "--name", "DOSBox").split()
w = ids[0]
x("windowfocus", w)
x("key", "Num_Lock")                       # NumLock ON so the keypad sends digits
x("type", "--delay", "90", cmd); x("key", "Return")
pre, _, post = script.partition("SYNC")
if "SYNC" not in script: pre, post = "", script      # no sync: keys are timed from the start of capture
def parse(sc): return sorted((float(t), k) for t, k in (e.split(":") for e in sc.split()))
from PIL import Image
def grab(path):
    subprocess.run(["import", "-window", "root", "-crop", "640x400+192+201", "+repage", path], env=env)
t0 = time.time()
for t, k in parse(pre):
    while time.time() - t0 < t: time.sleep(0.05)
    x("key", k)
if "SYNC" in script:                       # wait for the game HUD divider (cyan line at row 17)
    while time.time() - t0 < 120:
        grab(f"{out}/sync.png")
        im = Image.open(f"{out}/sync.png").convert("RGB")
        row = [im.getpixel((x, 35)) for x in range(0, 640, 4)]
        blue = [im.getpixel((x, 20)) for x in range(0, 640, 4)]
        if sum(1 for p in row if p[1] > 120 and p[0] < 60 and p[2] > 120) > 150 and not any(p[2] > 120 and p[1] < 60 for p in blue): break
        time.sleep(0.2)
    print("synced at", round(time.time() - t0, 1))
events = parse(post) if post else []
t0 = time.time(); n = 0; nxt = 0.0
while time.time() - t0 < total:
    now = time.time() - t0
    while events and events[0][0] <= now:
        x("key", events.pop(0)[1])
    if now >= nxt:
        subprocess.run(["import", "-window", "root", "-crop", "640x400+192+201", "+repage", f"{out}/f{n:03d}.png"], env=env)
        n += 1; nxt += 0.5
    time.sleep(0.02)
db.kill(); xv.kill()
print(n, "frames")
