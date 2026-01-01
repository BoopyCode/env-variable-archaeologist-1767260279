#!/usr/bin/env python3
"""EnvVar Archaeologist - Digs through your config mess so you don't have to."""

import os
import sys
from pathlib import Path
from collections import defaultdict

# Where secrets go to die (or multiply like rabbits)
ENV_FILES = [
    '.env',
    '.env.local',
    '.env.production',
    '.env.development',
    '.env.test',
    '.env.staging'
]

SHELL_CONFIGS = [
    '~/.bashrc',
    '~/.bash_profile',
    '~/.zshrc',
    '~/.profile'
]

def dig_for_env_vars():
    """Unearths environment variables from their various hiding spots."""
    findings = defaultdict(list)
    
    # Check actual environment (the "source of truth" that lies to you)
    for key, value in os.environ.items():
        findings[key].append(f"ENV: {value}")
    
    # Dig through .env files (where duplicates go to party)
    for env_file in ENV_FILES:
        path = Path(env_file)
        if path.exists():
            try:
                with open(path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            findings[key].append(f"{env_file}: {value}")
            except Exception as e:
                print(f"Failed to read {env_file}: {e}", file=sys.stderr)
    
    # Peek into shell configs (where forgotten exports live forever)
    for shell_file in SHELL_CONFIGS:
        path = Path(shell_file).expanduser()
        if path.exists():
            try:
                with open(path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if 'export ' in line and '=' in line:
                            # Extract from "export KEY=VALUE" or "export KEY='VALUE'"
                            parts = line.replace('export ', '').split('=', 1)
                            if len(parts) == 2:
                                key, value = parts
                                findings[key].append(f"{shell_file}: {value}")
            except Exception as e:
                print(f"Failed to read {shell_file}: {e}", file=sys.stderr)
    
    return findings

def present_findings(findings):
    """Displays the archaeological dig results (prepare for disappointment)."""
    print("\n🔍 ENVIRONMENT VARIABLE ARCHAEOLOGY REPORT 🔍\n")
    print("=" * 60)
    
    for key, sources in sorted(findings.items()):
        print(f"\n{key}:")
        if len(sources) > 1:
            print(f"  ⚠️  CONFLICT! Found {len(sources)} different values:")
        for source in sources:
            print(f"  • {source}")
    
    print("\n" + "=" * 60)
    print("\n💡 Tip: If your app is broken, it's probably the 4th value you checked.")

if __name__ == "__main__":
    findings = dig_for_env_vars()
    present_findings(findings)
