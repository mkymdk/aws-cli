import os
from pathlib import Path
import subprocess
import sys

root = Path.cwd()
out = root / 'diagnostic-results'
out.mkdir(exist_ok=True)
target = 'tests/functional/autoprompt/test_prompttoolkit.py'
node = target + '::TestOutputPanel::test_output_panel_and_doc_panel_can_be_visible_together'
fixed = Path(target).read_bytes()
old = subprocess.check_output(['git', 'show', '3f64e1fbc:' + target])

def run(label, mode, expected, scope=node):
    env = dict(os.environ, TRACE_FILE=str(out / (label + '.jsonl')),
               TRACE_MODE=mode, PYTHONPATH=str(root / 'diagnostic'))
    with (out / (label + '.log')).open('w') as log:
        result = subprocess.run([sys.executable, '-m', 'pytest', '-p',
                                 'output_trace', scope, '-q', '-s'],
                                env=env, stdout=log, stderr=subprocess.STDOUT,
                                timeout=180)
    print(label, 'exit', result.returncode, 'expected', expected, flush=True)
    if result.returncode != expected:
        raise RuntimeError(label)
try:
    Path(target).write_bytes(old)
    for i in range(10):
        run('original-natural-' + str(i), 'natural', 0)
    run('original-controlled', 'controlled', 1)
    Path(target).write_bytes(fixed)
    run('fixed-controlled', 'controlled', 0)
    run('fixed-broken-binding', 'broken', 1)
    run('fixed-module', 'natural', 0, target)
finally:
    Path(target).write_bytes(fixed)
