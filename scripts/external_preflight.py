#!/usr/bin/env python3
import shutil, sys
for tool in ['docker']:
    print(f'{tool}: {shutil.which(tool) or "MISSING"}')
print('This script is informational; external benchmark execution requires Docker-capable hardware.')
