#!/usr/bin/env python3
"""Apply Moon Mission's keyboard layout to a connected DualSense in local Steam.

Requires the local Steam CEF debugging endpoint, as configured on this desktop.
Does not change Steam's global controller defaults or another game's layout.
"""
import argparse
import json
from pathlib import Path
import time
from steam_client import evaluate

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--appid', type=int, required=True, help='Moon Mission non-Steam shortcut appid')
a = p.parse_args()
if a.appid <= 0:
    p.error('appid must be positive')
root = Path(__file__).resolve().parents[1]
backup = root / 'build/steam-input' / time.strftime('%Y%m%d-%H%M%S')
backup.mkdir(parents=True, exist_ok=True)
evaluate(f'controllerConfiguratorStore.LoadEditingConfiguration({a.appid},0)')
for _ in range(40):
    raw = evaluate('JSON.stringify(controllerConfiguratorStore.EditedConfiguration)')
    config = json.loads(raw) if raw else {}
    if config.get('sets'):
        break
    time.sleep(.25)
else:
    raise SystemExit('Connect the DualSense and open Steam before installing its layout.')
if config.get('controller_type') != 45:
    raise SystemExit('The selected controller is not a DualSense; no bindings changed.')
(backup / 'before.json').write_text(json.dumps(config, indent=2) + '\n')
# USB keyboard usages, not host-specific keycodes. Plain digits ignore NumLock.
# Left stick: lateral thrust and main throttle. D-pad: keyboard menu navigation.
modes = [[3, 1], [13, 1], [4, 3], [5, 16], [6, 10], [7, 10]]
keys = [[3, 1, 1, 37], [3, 5, 1, 34], [3, 3, 1, 35], [3, 7, 1, 33]]
keys += [[13, 1, 1, 82], [13, 5, 1, 81], [13, 3, 1, 79], [13, 7, 1, 80]]
# Cross=Enter; Circle=Escape; Square=Space (cut engine); Triangle=2 (downward thruster).
keys += [[4, 12, 3, 40], [4, 11, 3, 41], [4, 10, 3, 44], [4, 9, 3, 31]]
# R2/R1 increase main throttle; L2/L1 decrease it. Options backs out; Create confirms.
keys += [[7, 15, 10, 37], [6, 15, 10, 34], [5, 54, 16, 37],
         [5, 53, 16, 34], [5, 52, 16, 41], [5, 51, 16, 40]]
expression = '''(async()=>{const s=controllerConfiguratorStore,id=APP;
for(const [source,mode] of MODES){s.SetControllerSourceMode(id,{action_set_key:'Default',source_binding_key:source,new_mode:mode,enable_virtual_menu_support:true});await s.m_updatingEditingConfigurationPromise;}
for(const [source,input,mode,key] of KEYS){s.SetControllerInputBinding(id,{action_set_key:'Default',source_binding_key:source,input_key:input,activator_index:0,binding_index:0,source_mode:mode,new_binding:{type:1,keyboard_key:{key}}});await s.m_updatingEditingConfigurationPromise;}
s.SaveEditingConfiguration(id);return JSON.stringify(s.EditedConfiguration);})()'''
for token, value in [('APP', a.appid), ('MODES', modes), ('KEYS', keys)]:
    expression = expression.replace(token, json.dumps(value))
after = json.loads(evaluate(expression, timeout=60))
(backup / 'after.json').write_text(json.dumps(after, indent=2) + '\n')
# Check readback rather than treating a successful API call as sufficient.
for source, input_key, mode, keyboard in keys:
    group = next(s['active_group'] for s in after['sets'][0]['source_bindings'] if s['key'] == source)
    inp = next(i for i in group['inputs'] if i['key'] == input_key)
    bindings = inp['activators'][0]['bindings']
    if not any(b.get('keyboard_key', {}).get('key') == keyboard for b in bindings):
        raise SystemExit(f'Binding readback failed for source {source}, input {input_key}')
print(f'Saved and verified {len(keys)} DualSense bindings. Backup: {backup}')
