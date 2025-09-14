---
title: "Using Github Actions with pip-audit to audit pip library versions"
layout: post
categories: [technical, security]
tags: [github-actions, python, security, automation, ci-cd, pip]
published: true
---

I've got several Python and TypeScript projects scattered around that need constant dependency babysitting. Dependabot does a decent job but keeps missing Python pip security issues that `pip-audit` catches. The problem is `pip-audit` wants everything pinned to exact versions, but I prefer flexible `>=` constraints in my requirements files.

After getting tired of manually running security audits and then forgetting about them for months, I built this GitHub Actions workflow to handle it automatically. You can see it in action on my [Shiny Quiz](https://github.com/mcgarrah/shiny-quiz) repository and Django demo application.

<!-- excerpt-end -->

## Problems to solve

1. Alert me to security vulnerabilities in my python dependencies
2. Allow for flexible versions with `>=` rather than `==` versions
3. Automatically scan and alert me at least weekly
4. Automatically create PRs to update dependencies

## Solution

The `pip-audit-pr.yaml` Github Actions Workflow does the following:

1. Runs weekly and on-demand via workflow_dispatch
2. Sets up a python environment with the required dependencies
3. Pins flexible version requirements (`>=` to `==`) for accurate vulnerability detection
4. Runs `pip-audit` with automatic fixes
5. Converts requirements back to flexible versioning
6. Creates a pull request if vulnerabilities were found and fixed

## What it does

The workflow is pretty straightforward - it temporarily pins my flexible version requirements so `pip-audit` can do its thing, then converts everything back to `>=` constraints after applying security fixes. It runs weekly (because I'll definitely forget otherwise) and creates pull requests when it finds vulnerabilities. Those PRs end up with an email sent to me so I can see I need to do something.

## Getting it working

You'll need a few things set up first:

1. A `requirements.txt` file (obviously)
2. The helper script in a `scripts/` directory
3. GitHub Actions permissions - go to Settings > Actions > General and enable "Allow GitHub Actions to create and approve pull requests" or you'll get cryptic errors

## The Workflow

{% comment %}
{% raw %}
The next code block section has {{ }} variables that required setting
RAW and ENDRAW to show those variables correctly inline. It was a pain
to figure this out so leaving myself a note here.
{% endraw %}
{% endcomment %}

``` yaml
name: pip-audit pull request
{% raw %}
# This workflow uses pip-audit to check for vulnerabilities in Python dependencies
# and automatically creates a pull request with fixes if any vulnerabilities are found.
#
# **Note**: If you have errors for PR (merge request) creation, you may need to:
#   1. Go to Settings > Actions > General
#   2. Under "Pull request workflows" enable "Allow GitHub Actions to create and approve pull requests"

on:
  # Runs weekly on Sundays at midnight UTC
  schedule:
    - cron: '0 0 * * 0'
  # Allows manual runs from the Actions tab
  workflow_dispatch:

permissions:
  contents: write
  pull-requests: write

concurrency:
  group: pip-audit-${{ github.ref }}
  cancel-in-progress: true

jobs:
  pip-audit-fixes:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.13'
        cache: 'pip'

    - name: Create virtual environment
      run: python -m venv .venv

    - name: Install dependencies for audit
      run: |
        source .venv/bin/activate
        pip install -r requirements.txt

    - name: Pin requirements to exact versions
      run: |
        source .venv/bin/activate
        python scripts/pin_requirements.py pin

    - name: Install pip-audit
      run: |
        source .venv/bin/activate
        pip install pip-audit

    - name: Perform pip-audit with fixes
      id: audit
      # Run pip-audit directly with --fix flag on pinned requirements
      run: |
        source .venv/bin/activate
        pip-audit --fix -o audit-output.txt -r requirements-pinned.txt
        exit_code=$?
        echo "exit_code=$exit_code" >> $GITHUB_OUTPUT
        # Copy the potentially updated pinned requirements back to main requirements file
        cp requirements-pinned.txt requirements.txt
        # Remove the defunct pinned requirements file
        rm requirements-pinned.txt
      # The `continue-on-error` ensures the workflow continues to the next step
      # if a vulnerability was found and fixed, which triggers the non-zero exit code.
      continue-on-error: true

    - name: Convert fixed pinned requirements back to flexible versioning
      run: |
        source .venv/bin/activate
        # Convert requirements back to flexible versioning
        python scripts/pin_requirements.py unpin

    - name: Check for changes
      id: changes
      run: |
        if git diff --quiet; then
          echo "has_changes=false" >> $GITHUB_OUTPUT
        else
          echo "has_changes=true" >> $GITHUB_OUTPUT
        fi

    - name: Read audit output
      id: audit_output
      if: steps.changes.outputs.has_changes == 'true'
      run: |
        if [ -f audit-output.txt ]; then
          echo "audit_details<<EOF" >> $GITHUB_OUTPUT
          cat audit-output.txt >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT
          rm audit-output.txt
        else
          echo "audit_details=No audit output file found" >> $GITHUB_OUTPUT
        fi

    - name: Create Pull Request with fix
      # This step only runs if pip-audit made changes
      if: steps.changes.outputs.has_changes == 'true'
      uses: peter-evans/create-pull-request@v6
      continue-on-error: true
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
        commit-message: 'fix: Apply security fixes via pip-audit'
        title: 'Security updates from pip-audit'
        body: |
          This PR automatically applies security fixes found by `pip-audit`.
          It's generated by the `pip-audit-pr` GitHub Action.
          
          ---
          
          **Audit Results:**
          Changes Detected: ${{ steps.changes.outputs.has_changes }}
          Exit Code: ${{ steps.audit.outputs.exit_code }}
          
          **Audit Details:**
          ${{ steps.audit_output.outputs.audit_details }}

          ---
                    
        branch: 'automated-pip-audit-fixes'
        # Ensures a clean branch for the PR
        delete-branch: true
{% endraw %}
```

## The Helper Script

The workflow relies on a Python helper script that handles the conversion between flexible and pinned versions:

``` python
#!/usr/bin/env python3
"""
Pin/unpin requirements.txt versions for security auditing.
"""

import argparse
import re
from pathlib import Path

def extract_version_from_requirement(requirement_line):
    """Extract the minimum version from a requirement line."""
    # Match patterns like package>=1.2.3 or package==1.2.3
    match = re.search(r'([a-zA-Z0-9_-]+)([><=!]+)([0-9.]+)', requirement_line)
    if match:
        package_name, operator, version = match.groups()
        return package_name, version
    return None, None

def unpin_requirements(filename='requirements.txt'):
    """Convert pinned requirements back to flexible versions."""
    requirements_file = Path.cwd() / filename
    
    print(f"Looking for requirements.txt at: {requirements_file.absolute()}")
    if not requirements_file.exists():
        print("requirements.txt not found!")
        return False
    
    # Read current requirements
    with open(requirements_file, 'r') as f:
        lines = f.readlines()
    
    print(f"Read {len(lines)} lines from requirements.txt")
    unpinned_lines = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            unpinned_lines.append(line)
            continue
            
        # Convert == to >=
        if '==' in line:
            unpinned_line = line.replace('==', '>=')
            unpinned_lines.append(unpinned_line)
            package_name = line.split('==')[0]
            print(f"Unpinned {package_name}")
        else:
            unpinned_lines.append(line)
    
    # Write unpinned requirements back to file
    with open(requirements_file, 'w') as f:
        for line in unpinned_lines:
            f.write(line + '\n')
    
    print(f"Updated {requirements_file} with flexible versions")
    return True

def pin_requirements(filename='requirements.txt'):
    """Convert flexible requirements to pinned versions in a temporary file."""
    requirements_file = Path.cwd() / filename
    base_name = Path(filename).stem
    pinned_file = Path.cwd() / f'{base_name}-pinned.txt'
    
    print(f"Looking for requirements.txt at: {requirements_file.absolute()}")
    if not requirements_file.exists():
        print("requirements.txt not found!")
        return False
    
    # Read current requirements
    with open(requirements_file, 'r') as f:
        lines = f.readlines()
    
    print(f"Read {len(lines)} lines from requirements.txt")
    pinned_lines = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            pinned_lines.append(line)
            continue
            
        # Extract package name and version from requirement
        package_name, version = extract_version_from_requirement(line)
        
        if package_name and version:
            pinned_lines.append(f"{package_name}=={version}")
            print(f"Pinned {package_name} to minimum version {version}")
        else:
            print(f"Warning: Could not parse requirement '{line}', keeping original")
            pinned_lines.append(line)
    
    # Write pinned requirements to temporary file
    with open(pinned_file, 'w') as f:
        for line in pinned_lines:
            f.write(line + '\n')
    
    print(f"Created {pinned_file} with pinned versions")
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Pin or unpin requirements file versions for security auditing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python pin_requirements.py pin
  python pin_requirements.py unpin
  python pin_requirements.py pin requirements-dev.txt
  python pin_requirements.py unpin my-requirements.txt"""
    )
    parser.add_argument('action', choices=['pin', 'unpin'], 
                       help='pin: convert >= to == using minimum versions; unpin: convert == to >=')
    parser.add_argument('filename', nargs='?', default='requirements.txt',
                       help='requirements file to process (default: requirements.txt)')
    args = parser.parse_args()
    
    if args.action == 'pin':
        if pin_requirements(args.filename):
            print("Requirements successfully pinned!")
        else:
            print("Failed to pin requirements")
            exit(1)
    elif args.action == 'unpin':
        if unpin_requirements(args.filename):
            print("Requirements successfully unpinned!")
        else:
            print("Failed to unpin requirements")
            exit(1)
```

## How It Works

The workflow follows this process:

1. **Setup**: Checks out code and sets up Python 3.13 environment
2. **Pin versions**: Converts `package>=1.2.3` to `package==1.2.3` for accurate vulnerability detection
3. **Audit**: Runs pip-audit on pinned requirements to find and fix vulnerabilities
4. **Unpin**: Converts fixed requirements back to flexible versioning (`package>=1.4.0`)
5. **PR creation**: If changes were made, creates a pull request with detailed audit results

## Why not just use Dependabot?

Dependabot is great for keeping things updated, but it's not specifically focused on security vulnerabilities. This workflow uses PyPA's official security database and only bothers you when there are actual security issues, not just because a new version exists. Plus it maintains my preferred `>=` version constraints instead of pinning everything.

## The gotchas

Like any automated tool, this isn't perfect:

- You still need to review the PRs before merging (which is probably a good thing)
- Sometimes it updates packages more than strictly than necessary for the security fix
- It's only as good as pip-audit's vulnerability database
- Python projects only - no help for your Node.js mess
- Forces the use of the flexible version `>=` for your file

## Setting it up

1. Drop the workflow file into `.github/workflows/pip-audit-pr.yaml`
2. Create the helper script at `scripts/pin_requirements.py`
3. Make sure your requirements use `>=` instead of `==` (if you're already pinning everything, then this might not be for you)
4. Fix the GitHub permissions mentioned above
5. Test it manually first - trust me on this one

## Wrapping up

This setup has been working well for me across several projects. It catches security issues I would have missed and creates reasonable PRs without being too noisy. The weekly schedule means I don't forget about it, and the manual trigger is handy when I'm actively working on dependency updates.

The helper script could probably be smarter about version parsing, but it handles the common cases I run into. If you find bugs or have improvements, the code is straightforward enough to modify.

I have not made this generic for non-flexible version checks. That is another enhancement worth thinking about.

Not the most exciting automation, but it's one less thing to worry about manually.
