import os, subprocess, sys
from pathlib import Path
root=Path.cwd()
logs=root/'diagnostic-results';logs.mkdir(exist_ok=True)
test='tests/functional/autoprompt/test_prompttoolkit.py::TestDebugPanel::test_open_save_dialog_on_control_s'
def run(name,args,expected=0,extra=None):
 env={**os.environ,'PYTHONPATH':str(root/'ci-probes')+os.pathsep+str(root),**(extra or {})}
 r=subprocess.run([sys.executable,'-m','pytest',*args,'-q'],env=env,text=True,capture_output=True)
 (logs/(name+'.log')).write_text(r.stdout+r.stderr)
 print(name,'exit',r.returncode,'expected',expected,flush=True)
 print(r.stdout[-1500:],flush=True)
 assert r.returncode==expected, name
run('original-isolated',[test])
run('original-delayed',[test,'-p','oca_macos_delay_probe'],1)
subprocess.run(['git','apply','ci-probes/autoprompt-wait.patch'],check=True)
run('fixed-delayed',[test,'-p','oca_macos_delay_probe'])
run('broken-handler-still-fails',[test,'-p','oca_macos_delay_probe'],1,{'OCA_DISABLE_DIALOG':'1'})
run('fixed-whole-module',['tests/functional/autoprompt/test_prompttoolkit.py','-n','3','--dist=loadfile'])
for i in range(10):
 run('fixed-delayed-repeat-'+str(i),[test,'-p','oca_macos_delay_probe'])
