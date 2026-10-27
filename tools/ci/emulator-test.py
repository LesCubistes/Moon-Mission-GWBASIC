#!/usr/bin/env python3
"""Assert a real keyboard/screen journey; do not patch or instrument game code."""
import argparse
from difflib import SequenceMatcher
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from PIL import Image, ImageGrab, ImageOps

p = argparse.ArgumentParser()
p.add_argument('--machine', choices=['cga', 'tandy', 'pcjr'], required=True)
p.add_argument('--cycles', type=int, default=1200)
p.add_argument('--gameport', action='store_true')
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


def key(name):
    subprocess.run(['xdotool', 'windowfocus', window, 'key', '--clearmodifiers', name], env=env, check=True)

def screenshot(label):
    image = ImageGrab.grab()
    image.save(out / f'{label}.png')
    # OCR a monochrome copy; evidence always retains the original palette.
    geometry = subprocess.run(['xdotool', 'getwindowgeometry', '--shell', window], env=env, capture_output=True, text=True, check=True).stdout
    g = dict(line.split('=', 1) for line in geometry.splitlines() if '=' in line)
    x, y, width, height = (int(g[k]) for k in ['X', 'Y', 'WIDTH', 'HEIGHT'])
    crop = image.crop((x, y, x + width, y + height))
    crop = crop.resize((width * 3, height * 3), Image.Resampling.NEAREST)
    channels = crop.convert('RGB').split()
    from PIL import ImageChops
    bright = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]), channels[2])
    gray = bright.point(lambda x: 0 if x > 80 else 255)
    full_gray = gray
    regions = {'title': (0, 0, 1, .4), 'menu': (.225, .74, .775, .99),
               'return-menu': (.225, .74, .775, .99),
               'orbit': (0, 0, 1, .09), 'return-orbit': (0, 0, 1, .09),
               'flight': (0, 0, 1, .12), 'retry': (0, 0, 1, .12),
               'crash': (.2, .3, .8, .55)}
    left, top, right, bottom = regions.get(label, (0, 0, 1, 1))
    gray = gray.crop((int(gray.width * left), int(gray.height * top),
                      int(gray.width * right), int(gray.height * bottom)))
    gray = ImageOps.expand(gray, border=40, fill=255)
    gray.save(out / 'ocr.png')
    result = subprocess.run(['tesseract', str(out / 'ocr.png'), 'stdout', '--psm', '6'], capture_output=True, text=True, check=True)
    text = result.stdout.upper()
    errors = ImageOps.expand(full_gray.crop((0, int(full_gray.height * .7), full_gray.width, full_gray.height)), border=40, fill=255)
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
    # The IBM bitmap font produces occasional OCR substitutions. Require >=85%
    # agreement within a short substring, never a whole-screen similarity score.
    for size in range(max(1, len(expected) - 2), len(expected) + 3):
        for start in range(len(text) - size + 1):
            if SequenceMatcher(None, expected, text[start:start + size]).ratio() >= .85:
                return True
    return False


def wait_for(label, patterns, timeout=100, leave_orbit=False):
    end = time.monotonic() + timeout
    matched = False
    next_back = time.monotonic() + 3
    while time.monotonic() < end:
        if proc.poll() is not None:
            raise AssertionError(f'Emulator exited before {label}: {proc.returncode}')
        text = screenshot(label)
        if any(re.search(x, text) for x in ['SYNTAXERROR', 'ILLEGALFUNCTION', 'OUTOFMEMORY', 'OUTOFDATA', 'FILENOTFOUND', 'UNDEFINEDLINE']):
            raise AssertionError(f'BASIC error during {label}: {text}')
        if all(contains(text, pattern) for pattern in patterns):
            if not matched:
                matched = True
                time.sleep(1)
                continue
            checks.append(label)
            print(f'PASS {a.machine}/{a.cycles}: {label}', flush=True)
            return
        matched = False
        if leave_orbit and time.monotonic() >= next_back:
            # Orbit drains keys buffered while loading. Retry only when its
            # header is still visible, never blindly send Escape at a menu.
            header = screenshot('return-orbit')
            if contains(header, 'SELECTLANDINGSITE'):
                back()
            next_back = time.monotonic() + 3
        time.sleep(1)
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
    wait_for('title', ['GRAPHICSSCENEREADY'])
    key('space')
    wait_for('menu', ['SELECTMISSION', 'MOONLANDING'])
    if a.gameport:
        key('j')
        wait_for('setup-center', ['GAMEPORT', 'CENTER'])
        pad()
        key('Return')
        wait_for('setup-up-left', ['HOLDUPLEFT'])
        pad(-32767, -32767)
        key('Return')
        wait_for('setup-down-right', ['HOLDDOWNRIGHT'])
        pad(32767, 32767)
        key('Return')
        wait_for('setup-enabled', ['GAMEPADENABLED'])
        pad()
        key('Return')
        wait_for('setup-return', ['SELECTMISSION'])
    confirm()
    wait_for('orbit' , ['SELECTLANDINGSITE', 'DESCEND'])
    confirm()
    wait_for('flight', ['ALT', 'LANDER', 'THR'])
    # An unpowered descent must reach the crash/report path rather than hang.
    wait_for('crash', ['LANDERSLEFT', 'ENTER'], timeout=120)
    confirm()
    wait_for('retry', ['ALT', 'LANDER', 'THR'])
    back()
    wait_for('return-orbit', ['SELECTLANDINGSITE'])
    back()
    wait_for('return-menu', ['SELECTMISSION'], leave_orbit=True)
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
    (out / 'results.json').write_text(json.dumps({'machine': a.machine, 'cycles': a.cycles, 'gameport': a.gameport, 'success': success, 'failure': failure, 'passed': checks}, indent=2) + '\n')
