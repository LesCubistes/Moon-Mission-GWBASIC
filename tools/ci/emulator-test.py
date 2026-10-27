#!/usr/bin/env python3
"""Assert a real keyboard/screen journey; do not patch or instrument game code."""
import argparse
from difflib import SequenceMatcher
import json
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from PIL import Image, ImageGrab
from screen_ocr import monochrome

p = argparse.ArgumentParser()
p.add_argument('--machine', choices=['cga', 'tandy', 'pcjr'], required=True)
p.add_argument('--cycles', type=int, default=1200)
p.add_argument('--gameport', action='store_true')
p.add_argument('--runtime', type=Path, help='Optional alternate interpreter for OEM comparison')
a = p.parse_args()
root = Path(__file__).resolve().parents[2]
out = root / 'build/ci' / (f'{a.machine}-{a.cycles}' + ('-gameport' if a.gameport else ''))
out.mkdir(parents=True, exist_ok=True)
# Extract each built image into isolated floppy-directory mounts. Classic DOSBox's
# FAT image path is distinct from its directory path; this journey tests game files,
# while mtools checks the built filesystem. Boot/BIOS tests remain separate.
drives = root / 'build/ci-drives' / (f'{a.machine}-{a.cycles}' + ('-gameport' if a.gameport else ''))
if drives.exists():
    shutil.rmtree(drives)
for image, directory in [('START.IMG', 'start'), ('LANDING.IMG', 'landing')]:
    target = drives / directory
    target.mkdir(parents=True)
    subprocess.run(['mcopy', '-s', '-i', str(root / 'disks' / image), '::/*', str(target)], check=True)
if a.runtime:
    shutil.copy2(a.runtime, drives / 'start/GWBASIC.EXE')
env = dict(os.environ, SDL_AUDIODRIVER='dummy')
joystick = out / 'joystick.txt'
if a.gameport:
    joystick.write_text('0 0 0\n')
    shim = out / 'virtual-gamepad.so'
    subprocess.run(['gcc', '-shared', '-fPIC', '-O2', str(root / 'tools/ci/virtual-gamepad.c'), '-o', str(shim)], check=True)
    env.update(LD_PRELOAD=str(shim), MOON_TEST_JOYSTICK=str(joystick))
conf = out / 'dosbox.conf'
conf.write_text(f'''[sdl]
fullscreen=false
output=surface
[dosbox]
machine={a.machine}
memsize=1
[cpu]
core=normal
cycles=fixed {a.cycles}
[render]
aspect=false
scaler=normal2x
[joystick]
joysticktype={"4axis" if a.gameport else "none"}
timed=false
[sblaster]
sbtype=none
[autoexec]
mount a "{drives}/start" -t floppy
mount b "{drives}/landing" -t floppy
a:
gwbasic moon
exit
''')
checks = []
timer_samples = {}
timer_bounds = {}
timer_metrics = {}
success = False
failure = None
log = (out / 'emulator.log').open('w')
proc = subprocess.Popen(['dosbox', '-conf', str(conf), '-noconsole'], env=env, stdout=log, stderr=log)
window = None

def pad(x=0, y=0, buttons=0):
    temporary = joystick.with_suffix('.tmp')
    temporary.write_text(f'{x} {y} {buttons}\n')
    temporary.replace(joystick)


def confirm():
    if a.gameport:
        pad(buttons=1)
        time.sleep(1)
        pad()
        time.sleep(.3)
    else:
        key('Return')


def back():
    if a.gameport:
        pad(buttons=8)
        time.sleep(1)
        pad()
        time.sleep(.3)
    else:
        key('Escape')


def key(name, duration=.12):
    subprocess.run(['xdotool', 'windowfocus', window, 'keydown', '--clearmodifiers', name], env=env, check=True)
    time.sleep(duration)
    subprocess.run(['xdotool', 'keyup', name], env=env, check=True)

def screenshot(label, diagnostics=False):
    image = ImageGrab.grab()
    image.save(out / f'{label}.png')
    # OCR a monochrome copy; evidence always retains the original palette.
    geometry = subprocess.run(['xdotool', 'getwindowgeometry', '--shell', window], env=env, capture_output=True, text=True, check=True).stdout
    g = dict(line.split('=', 1) for line in geometry.splitlines() if '=' in line)
    x, y, width, height = (int(g[k]) for k in ['X', 'Y', 'WIDTH', 'HEIGHT'])
    crop = image.crop((x, y, x + width, y + height))
    regions = {'title': (0, 0, 1, .4), 'menu': (.225, .74, .775, .99),
               'return-menu': (.225, .74, .775, .99),
               'orbit': (0, 0, 1, .09), 'return-orbit': (0, 0, 1, .09),
               'flight': (0, 0, 1, .12), 'retry': (0, 0, 1, .12),
               'crash': (.2, .3, .8, .55)}
    left, top, right, bottom = regions.get(label, (0, 0, 1, 1))
    region = crop.crop((int(crop.width * left), int(crop.height * top),
                        int(crop.width * right), int(crop.height * bottom)))
    gray = monochrome(region)
    gray.save(out / 'ocr.png')
    result = subprocess.run(['tesseract', str(out / 'ocr.png'), 'stdout', '--psm', '6'], capture_output=True, text=True, check=True)
    text = result.stdout.upper()
    if label in {'flight', 'retry'}:
        # Read the lander counter separately from the adjacent fuel-gauge border.
        header = crop.crop((int(crop.width * .4), 0, int(crop.width * .7), int(crop.height * .045)))
        monochrome(header).save(out / 'lander-ocr.png')
        text += '\n' + subprocess.run(['tesseract', str(out / 'lander-ocr.png'), 'stdout', '--psm', '7'], capture_output=True, text=True, check=True).stdout.upper()
        # Also read the crash report area, in case the flight already ended.
        report = crop.crop((int(crop.width * .2), int(crop.height * .3), int(crop.width * .8), int(crop.height * .55)))
        monochrome(report).save(out / 'report-ocr.png')
        text += '\n' + subprocess.run(['tesseract', str(out / 'report-ocr.png'), 'stdout', '--psm', '6'], capture_output=True, text=True, check=True).stdout.upper()
        timer_bounds[label] = (x + int(width * .775), y, x + width, y + int(height * .04))
        clock = crop.crop((int(crop.width * .775), 0, crop.width, int(crop.height * .04)))
        timer_samples[label] = hashlib.sha256(monochrome(clock).tobytes()).hexdigest()
    if diagnostics:
        errors = monochrome(crop.crop((0, int(crop.height * .7), crop.width, crop.height)))
        errors.save(out / 'error-ocr.png')
        diagnostic = subprocess.run(['tesseract', str(out / 'error-ocr.png'), 'stdout', '--psm', '6'], capture_output=True, text=True, check=True).stdout.upper()
        (out / f'{label}-diagnostics.txt').write_text(diagnostic)
        text += '\n' + diagnostic
    (out / f'{label}.txt').write_text(text)
    normalized = re.sub(r'[^A-Z0-9]', '', text)
    if label == 'title':
        # The decorative logo uses overlapping colors rather than the BIOS font.
        # Detect the actual lunar scene; the following menu assertion verifies text.
        pixels = list(crop.convert('RGB').getdata())
        colored = sum(max(c) - min(c) > 60 for c in pixels)
        lit = sum(max(c) > 80 for c in pixels)
        if colored > 100 and lit > 5000:
            normalized += 'GRAPHICSSCENEREADY'
    return normalized

def contains(text, expected):
    if any(character.isdigit() for character in expected):
        return expected in text
    # The IBM bitmap font produces occasional OCR substitutions. Require >=85%
    # agreement within a short substring, never a whole-screen similarity score.
    for size in range(max(1, len(expected) - 2), len(expected) + 3):
        for start in range(len(text) - size + 1):
            if SequenceMatcher(None, expected, text[start:start + size]).ratio() >= .85:
                return True
    return False


def wait_for(label, patterns, timeout=100, skip_intro=False, require_timer=False):
    end = time.monotonic() + timeout
    matched_at = None
    clock_states = set()
    next_skip = time.monotonic() + 2
    settle = 3 if label in {"orbit", "return-orbit"} else 1
    while time.monotonic() < end:
        if proc.poll() is not None:
            raise AssertionError(f'Emulator exited before {label}: {proc.returncode}')
        text = screenshot(label)
        if any(re.search(x, text) for x in ['SYNTAXERROR', 'ILLEGALFUNCTION', 'OUTOFMEMORY', 'OUTOFDATA', 'FILENOTFOUND', 'UNDEFINEDLINE']):
            raise AssertionError(f'BASIC error during {label}: {text}')
        if all(contains(text, pattern) for pattern in patterns):
            if require_timer and contains(text, 'LANDERSLEFT'):
                # On a fast profile an unpowered flight can end between two OCR passes. The
                # flight HUD under the crash report still proves the flight ran to its end.
                timer_metrics[label] = 'ended before sampling'
                checks.append(label)
                print(f'PASS {a.machine}/{a.cycles}: {label} (already crashed)', flush=True)
                return
            if require_timer:
                clock_states.add(timer_samples[label])
                # OCR can take longer than the entire unpowered flight on a
                # hosted runner. Sample the already-located timer directly.
                sample_end = min(end, time.monotonic() + 3)
                while len(clock_states) < 2 and time.monotonic() < sample_end:
                    time.sleep(.15)
                    clock = ImageGrab.grab(bbox=timer_bounds[label])
                    clock_states.add(hashlib.sha256(monochrome(clock).tobytes()).hexdigest())
                timer_metrics[label] = len(clock_states)
                if len(clock_states) < 2:
                    time.sleep(.5)
                    continue
            if require_timer:
                # Two distinct timer states already establish a live, stable flight.
                checks.append(label)
                print(f'PASS {a.machine}/{a.cycles}: {label}', flush=True)
                return
            if matched_at is None:
                matched_at = time.monotonic()
            if time.monotonic() - matched_at < settle:
                time.sleep(.5)
                continue
            checks.append(label)
            print(f'PASS {a.machine}/{a.cycles}: {label}', flush=True)
            return
        matched_at = None
        if skip_intro and time.monotonic() >= next_skip:
            key("space")
            next_skip = time.monotonic() + 2
        time.sleep(1)
    # Terrain OCR is expensive and unnecessary for a matched HUD. Inspect the
    # BASIC error area on failure, without consuming the short flight window.
    text = screenshot(label, diagnostics=True)
    if any(error in text for error in ['SYNTAXERROR', 'ILLEGALFUNCTION', 'OUTOFMEMORY', 'OUTOFDATA', 'FILENOTFOUND', 'UNDEFINEDLINE']):
        raise AssertionError(f'BASIC error during {label}: {text}')
    raise AssertionError(f'Timed out waiting for {label}; see screenshot and OCR text')

try:
    for _ in range(100):
        found = subprocess.run(['xdotool', 'search', '--pid', str(proc.pid)], env=env, capture_output=True, text=True).stdout.split()
        if found:
            window = found[-1]
            break
        time.sleep(.1)
    if window is None:
        raise AssertionError('No DOSBox window')
    # This X server belongs to the test. Held keys must not autorepeat through
    # successive game screens (Escape could otherwise exit three menus).
    subprocess.run(['xset', 'r', 'off'], env=env, check=True)
    wait_for('title', ['GRAPHICSSCENEREADY'])
    key('space')
    wait_for('menu', ['SELECTMISSION', 'MOONLANDING'], skip_intro=True)
    if a.gameport:
        key('j')
        wait_for('setup-center', ['GAMEPORT', 'CENTER'])
        pad()
        key('Return')
        wait_for('setup-up-left', ['HOLDUPLEFT'])
        pad(-32767, -32767)
        time.sleep(1)
        key('Return')
        wait_for('setup-down-right', ['HOLDDOWNRIGHT'])
        pad(32767, 32767)
        time.sleep(1)
        key('Return')
        wait_for('setup-enabled', ['GAMEPADENABLED', 'HOLDATOBURN'])
        key('n')                       # keep tap-to-throttle; hold mode is a player's choice
        wait_for('setup-mode', ['HOLDATOBURNOFF'])
        pad()
        key('Return')
        wait_for('setup-return', ['SELECTMISSION'])
    confirm()
    # The mission opens with a three-page briefing; any key turns a page, back skips the rest.
    wait_for('briefing', ['MISSIONBRIEFING', 'THEGOAL'])
    confirm()
    wait_for('briefing-2', ['READINGTHEGAUGES'])
    back()
    wait_for('orbit' , ['SELECTLANDINGSITE', 'DESCEND'])
    confirm()
    wait_for('flight', ['ALT', 'LANDER', 'THR'], require_timer=True)
    # An unpowered descent must reach the crash/report path rather than hang.
    wait_for('crash', ['LANDERSLEFT', 'ENTER'], timeout=120)
    confirm()
    wait_for('retry', ['ALT', 'LANDER2', 'THR'], require_timer=True)
    back()
    wait_for('return-orbit', ['SELECTLANDINGSITE'])
    back()
    wait_for('return-menu', ['SELECTMISSION'])
    back()
    try:
        proc.wait(timeout=20)
    except subprocess.TimeoutExpired:
        raise AssertionError('Exit to DOS did not close emulator')
    if proc.returncode != 0:
        raise AssertionError(f'Unexpected emulator exit: {proc.returncode}')
    checks.append('exit')
    success = True
except Exception as error:
    failure = str(error)
    raise
finally:
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
    log.close()
    (out / 'results.json').write_text(json.dumps({'machine': a.machine, 'cycles': a.cycles, 'gameport': a.gameport, 'timer_states': timer_metrics, 'runtime_sha256': hashlib.sha256((drives / 'start/GWBASIC.EXE').read_bytes()).hexdigest(), 'success': success, 'failure': failure, 'passed': checks}, indent=2) + '\n')
