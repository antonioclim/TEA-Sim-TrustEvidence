
from __future__ import annotations
import os, subprocess, sys
cmds = [
    [sys.executable, '-m', 'compileall', 'src', '04_formalisation'],
    [sys.executable, '-m', 'pytest', '-q', '04_formalisation/hypothesis_tests/test_merkle_properties.py', '--hypothesis-show-statistics', '-p', 'no:cacheprovider'],
    [sys.executable, '04_formalisation/bounded_model/bounded_model_check.py'],
    [sys.executable, 'scripts/repository_check.py'],
    [sys.executable, 'scripts/verify_sha256sums.py', 'SHA256SUMS.txt'],
]
env = os.environ.copy(); env['PYTHONPATH'] = str((__import__('pathlib').Path.cwd()/'src'))
for cmd in cmds:
    print('$', ' '.join(cmd))
    p = subprocess.run(cmd, env=env)
    if p.returncode:
        raise SystemExit(p.returncode)
