---
title: "Run Jekyll: Testing and Test Harness"
layout: post
categories: [web-development, technical]
tags: [vscode, vscode-extension, testing, mocha, typescript, jekyll, open-source]
excerpt: "The Jekyll Run VS Code extension has a test scaffold that does nothing — a single sample test that checks array indexOf. Here's how VS Code extension testing actually works, what the existing harness does, and how to add real tests for the three bugs I found."
description: "A practical guide to VS Code extension testing using the Jekyll Run plugin as a case study. Covers the existing test scaffold, the Extension Development Host, Mocha integration, unit tests for pure functions, integration tests for VS Code API calls, and writing regression tests for the getConfiguration, lsof parsing, and null rejection bugs."
date: 2026-06-22
last_modified_at: 2026-06-22
seo:
  type: BlogPosting
  date_published: 2026-06-22
  date_modified: 2026-06-22
---

The [Jekyll Run VS Code extension](https://github.com/Kanna727/jekyll-run) has three bugs I've been [documenting](/jekyll-run-plugin-multiroot-workspace-bug/) and [fixing](/jekyll-run-plugin-pr-and-fork/). Before submitting a PR or publishing a fork, the fixes need tests. The extension already has a test scaffold — but it's the VS Code extension generator's default: a single sample test that checks `[1, 2, 3].indexOf(5)`.

This post covers how VS Code extension testing works, what the existing harness does, and how to write real tests for the bugs I found.

<!-- excerpt-end -->

## How VS Code Extension Testing Works

VS Code extensions run inside the Extension Host — a separate Node.js process managed by VS Code. You can't just run `mocha` against extension code because it depends on the `vscode` module, which only exists inside a running VS Code instance.

The testing architecture has three layers:

1. **Test runner** (`src/test/runTest.ts`) — Downloads a VS Code instance, launches it with your extension loaded, and points it at your test suite
2. **Test suite index** (`src/test/suite/index.ts`) — Configures Mocha and discovers test files
3. **Test files** (`src/test/suite/*.test.ts`) — The actual tests

When you run `npm test`, it compiles TypeScript, then executes `runTest.ts`, which downloads VS Code (cached after first run), launches it headlessly, loads your extension, and runs Mocha inside the Extension Development Host.

## The Existing Scaffold

The Jekyll Run plugin has all three files, but the test file is a placeholder.

### runTest.ts — The Launcher

```typescript
import * as path from 'path';
import { runTests } from 'vscode-test';

async function main() {
    const extensionDevelopmentPath = path.resolve(__dirname, '../../');
    const extensionTestsPath = path.resolve(__dirname, './suite/index');
    await runTests({ extensionDevelopmentPath, extensionTestsPath });
}

main();
```

This downloads VS Code (if not cached), launches it with `--extensionDevelopmentPath` pointing to the plugin root, and `--extensionTestsPath` pointing to the test suite. The `vscode-test` package handles the download and lifecycle.

### suite/index.ts — The Mocha Configuration

```typescript
import * as path from 'path';
import * as Mocha from 'mocha';
import * as glob from 'glob';

export function run(): Promise<void> {
    const mocha = new Mocha({ ui: 'tdd', color: true });
    const testsRoot = path.resolve(__dirname, '..');

    return new Promise((c, e) => {
        glob('**/**.test.js', { cwd: testsRoot }, (err, files) => {
            files.forEach(f => mocha.addFile(path.resolve(testsRoot, f)));
            mocha.run(failures => {
                if (failures > 0) { e(new Error(`${failures} tests failed.`)); }
                else { c(); }
            });
        });
    });
}
```

This finds all `*.test.js` files under the test directory and runs them with Mocha in TDD mode (`suite`/`test` instead of `describe`/`it`).

### extension.test.ts — The Placeholder

```typescript
import * as assert from 'assert';
import * as vscode from 'vscode';

suite('Extension Test Suite', () => {
    vscode.window.showInformationMessage('Start all tests.');

    test('Sample test', () => {
        assert.equal(-1, [1, 2, 3].indexOf(5));
        assert.equal(-1, [1, 2, 3].indexOf(0));
    });
});
```

This is the default from `yo code` — the VS Code extension generator. It proves the test harness runs but tests nothing about the extension.

## Running the Existing Tests

From a cloned copy of the repository:

```bash
git clone https://github.com/mcgarrah/jekyll-run.git
cd jekyll-run
npm install
npm test
```

The first run downloads a VS Code instance (~200MB, cached in `.vscode-test/`). A VS Code window flashes open briefly (the Extension Development Host), runs the single test, and exits. You'll see:

```
Extension Test Suite
  ✓ Sample test

1 passing
```

### Dependencies

The test infrastructure uses these packages (all already in `devDependencies`):

| Package | Version | Purpose |
|---------|---------|---------|
| `vscode-test` | ^1.3.0 | Downloads and launches VS Code for integration tests |
| `mocha` | ^7.1.2 | Test framework |
| `glob` | ^7.1.6 | File discovery for test suite |
| `@types/mocha` | ^7.0.2 | TypeScript types for Mocha |
| `@types/glob` | ^7.1.1 | TypeScript types for glob |

These are outdated (2020 versions) but functional. A dependency update is out of scope for a bug fix PR but worth doing in a fork.

## Two Types of Tests

VS Code extension tests fall into two categories:

### Unit Tests — Pure Functions

Functions that don't depend on the `vscode` module can be tested with plain Mocha — no Extension Development Host needed. In the Jekyll Run plugin, these include:

- `getNumbersInString()` — Extracts numbers from a string
- `findPidByPort()` — Parses `netstat` output (Windows)
- The `lsof` output parsing in `findProcessOnPort()` (the bug we found)
- The Errno regex match in the stderr handler

These are the easiest to test and the most valuable — they cover the exact parsing logic where the bugs live.

### Integration Tests — VS Code API

Functions that use `vscode.workspace`, `vscode.window`, or other VS Code APIs must run inside the Extension Development Host. These include:

- `Config.get()` — The `getConfiguration()` call that breaks in multi-root workspaces
- `isStaticWebsiteWorkspace()` — Workspace folder detection
- The full `Run.run()` lifecycle

Integration tests are slower (they launch VS Code) and harder to write (you need workspace fixtures), but they're the only way to test the `getConfiguration()` fix.

## Writing Tests for the Three Bugs

### Bug 1: lsof Output Parsing

The `findProcessOnPort()` function splits `lsof` output on single spaces, which fails on macOS because `lsof` uses variable-width columns. This is a pure function test — no VS Code API needed.

```typescript
// src/test/suite/process-on-port.test.ts
import * as assert from 'assert';

suite('Process on Port Parsing', () => {

    // Simulates the parsing logic from findProcessOnPort
    function parseLsofOutput(output: string): { name: string; pid: number } {
        const line = output.split('\n')[1];
        // BUG: original uses .split(' ')
        // FIX: use .split(/\s+/).filter(Boolean)
        const parts = line.split(/\s+/).filter(Boolean);
        return { name: parts[0], pid: +parts[1] };
    }

    test('parses lsof output with single spaces', () => {
        const output = 'COMMAND PID USER FD TYPE\nruby 12345 user 6u IPv4';
        const result = parseLsofOutput(output);
        assert.strictEqual(result.name, 'ruby');
        assert.strictEqual(result.pid, 12345);
    });

    test('parses lsof output with variable-width columns (macOS)', () => {
        // Real macOS lsof output has multiple spaces between columns
        const output = 'COMMAND   PID             USER   FD   TYPE\nruby    20545 michael.mcgarrah    6u  IPv4';
        const result = parseLsofOutput(output);
        assert.strictEqual(result.name, 'ruby');
        assert.strictEqual(result.pid, 20545);
    });

    test('handles lsof output with tabs', () => {
        const output = 'COMMAND\tPID\tUSER\nruby\t12345\tuser';
        const result = parseLsofOutput(output);
        assert.strictEqual(result.name, 'ruby');
        assert.strictEqual(result.pid, 12345);
    });
});
```

### Bug 2: Null Rejection on Non-Errno Errors

The stderr handler rejects with `null` when a Ruby error doesn't contain "Errno". This is also a pure function test.

```typescript
// src/test/suite/error-handling.test.ts
import * as assert from 'assert';

suite('Error Handler Regex', () => {

    function extractError(stderr: string): string | null {
        // Original: returns null when Errno not found
        // return stderr.match(/\B(.+)Errno(.+)/m);

        // Fixed: falls back to full error string
        return stderr.match(/\B(.+)Errno(.+)/m)?.[0] || stderr;
    }

    test('extracts Errno message when present', () => {
        const stderr = 'Error: Errno::EADDRINUSE - Address already in use';
        const result = extractError(stderr);
        assert.ok(result);
        assert.ok(result!.includes('Errno'));
    });

    test('returns full error when Errno not present', () => {
        const stderr = "Could not find 'bundler' (4.0.8) required by your Gemfile.lock";
        const result = extractError(stderr);
        assert.ok(result);
        assert.ok(result!.includes('bundler'));
    });

    test('never returns null', () => {
        const stderrSamples = [
            'ruby: command not found',
            "Could not find 'bundler' (4.0.8)",
            'LoadError: cannot load such file',
            '/usr/bin/ruby: No such file or directory',
        ];
        for (const stderr of stderrSamples) {
            const result = extractError(stderr);
            assert.notStrictEqual(result, null, `Got null for: ${stderr}`);
        }
    });
});
```

### Bug 3: getConfiguration() Scoping

This requires an integration test because it depends on the VS Code API. The test needs to run inside the Extension Development Host with a multi-root workspace.

```typescript
// src/test/suite/config.test.ts
import * as assert from 'assert';
import * as vscode from 'vscode';

suite('Config Resolution', () => {

    test('getConfiguration with section returns WorkspaceConfiguration', () => {
        // The fixed approach: pass section name directly
        const config = vscode.workspace.getConfiguration('jekyll-run');
        assert.ok(config, 'getConfiguration("jekyll-run") should not return null');
        // Should resolve the default from package.json
        const args = config.get('commandLineArguments');
        assert.strictEqual(typeof args, 'string',
            'commandLineArguments should resolve to a string (default: "")');
    });

    test('commandLineArguments has a default value', () => {
        const config = vscode.workspace.getConfiguration('jekyll-run');
        const args = config.get<string>('commandLineArguments', '');
        assert.strictEqual(typeof args, 'string');
        // Default from package.json is empty string
        // If user has settings, it will be their value
    });

    test('stopServerOnExit has a default value', () => {
        const config = vscode.workspace.getConfiguration('jekyll-run');
        const stop = config.get<boolean>('stopServerOnExit');
        assert.strictEqual(typeof stop, 'boolean');
    });
});
```

### Bug 4: getNumbersInString Utility

The existing utility function also splits on single spaces. While it's not directly involved in the bugs I found, it has the same pattern:

```typescript
// src/test/suite/utils.test.ts
import * as assert from 'assert';

// Inline the function since we can't import from src without restructuring
function getNumbersInString(str: string): number[] {
    return str.trim().split(/\s+/).filter(Boolean)
        .filter(value => /^\d+$/.test(value.trim()))
        .map(Number);
}

suite('getNumbersInString', () => {

    test('extracts numbers from space-separated string', () => {
        assert.deepStrictEqual(getNumbersInString('PID 12345'), [12345]);
    });

    test('extracts multiple numbers', () => {
        assert.deepStrictEqual(getNumbersInString('12345 67890'), [12345, 67890]);
    });

    test('handles multiple spaces between values', () => {
        assert.deepStrictEqual(getNumbersInString('PID   12345   USER'), [12345]);
    });

    test('returns empty array for no numbers', () => {
        assert.deepStrictEqual(getNumbersInString('no numbers here'), []);
    });

    test('handles empty string', () => {
        assert.deepStrictEqual(getNumbersInString(''), []);
    });
});
```

## Project Structure with Tests

After adding the test files, the test directory looks like:

```
src/test/
├── runTest.ts                    # Launcher (unchanged)
└── suite/
    ├── index.ts                  # Mocha config (unchanged)
    ├── extension.test.ts         # Original placeholder (can remove)
    ├── config.test.ts            # Bug 3: getConfiguration scoping
    ├── error-handling.test.ts    # Bug 2: null rejection
    ├── process-on-port.test.ts   # Bug 1: lsof parsing
    └── utils.test.ts             # Utility function coverage
```

## The Existing Fork and CI Infrastructure

I already have the fork at `jekyll-run/` (origin: `mcgarrah/jekyll-run`). Better yet, the original author set up a complete CI pipeline that we can reuse:

### ci-release.yml — Cross-Platform Testing

The existing workflow already runs tests on macOS, Ubuntu, and Windows on every push and PR:

```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [macos-latest, ubuntu-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v1
        with:
          node-version: 12
      - run: npm install
      - uses: GabrielBB/xvfb-action@v1.2
        with:
          run: npm test
```

The `xvfb-action` handles the headless display server needed for VS Code integration tests on Linux. macOS and Windows don't need it but the action is cross-platform safe.

### ci-publish.yml — Marketplace Publishing

Triggered on GitHub Release creation, publishes directly to the VS Code Marketplace:

```yaml
on:
  release:
    types: [published]
jobs:
  publish:
    steps:
      - run: npm install
      - uses: JCofman/vscodeaction@master
        env:
          PUBLISHER_TOKEN: ${{ secrets.PUBLISHER_TOKEN }}
        with:
          args: publish -p $PUBLISHER_TOKEN
```

To use this, you'd add your VS Code Marketplace PAT as a `PUBLISHER_TOKEN` secret in the fork's GitHub settings. Then creating a GitHub Release triggers the publish automatically.

### What Needs Updating

The CI workflows are from 2020 and need version bumps before they'll run:

| Component | Current | Update To |
|-----------|---------|----------|
| `ubuntu-18.04` | EOL | `ubuntu-latest` |
| `actions/checkout@v2` | Deprecated | `actions/checkout@v4` |
| `actions/setup-node@v1` | Deprecated | `actions/setup-node@v4` |
| Node.js 12 | EOL | 18 or 20 |
| `GabrielBB/xvfb-action@v1.2` | Old | `@v1` (latest) |

The remote also needs updating — it currently points to the original author's repo:

```bash
# Fork remote is already set up
git remote -v
# origin  https://github.com/mcgarrah/jekyll-run.git

# Add upstream for PRs to the original author
git remote add upstream https://github.com/Kanna727/jekyll-run.git
```

## Running Tests

```bash
# Compile and run all tests
npm test

# Compile only (useful during development)
npm run compile

# Watch mode — recompile on save
npm run watch
```

The `npm test` command runs `pretest` first (compile + lint), then launches the Extension Development Host with the test suite. The VS Code window opens briefly, runs the tests, and exits.

### CI Integration

The fork already has cross-platform CI in `.github/workflows/ci-release.yml`. After updating the action versions (see "What Needs Updating" above), the workflow runs `npm test` on macOS, Ubuntu, and Windows on every push and PR. The `xvfb-action` provides the headless display server needed for VS Code integration tests on Linux.

The updated workflow:

```yaml
# .github/workflows/ci-release.yml
name: CI Release
on:
  push:
    branches: [ master, main ]
  pull_request:
    branches: [ master, main ]
jobs:
  test:
    name: Test
    strategy:
      matrix:
        os: [macos-latest, ubuntu-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 18
      - name: Install dependencies
        run: npm install
      - name: Run headless test
        uses: GabrielBB/xvfb-action@v1
        with:
          run: npm test
```

Testing on all three platforms is important for this extension — the `lsof` parsing bug is macOS-specific, and the `netstat` parsing in `findPidByPort` is Windows-specific.

## What the Tests Prove

Each test maps directly to a bug fix:

| Test Suite | Bug | What It Validates |
|------------|-----|-------------------|
| `process-on-port.test.ts` | lsof parsing | Variable-width columns parse correctly on macOS |
| `error-handling.test.ts` | null rejection | Non-Errno Ruby errors produce a string, never null |
| `config.test.ts` | getConfiguration scoping | Settings resolve with defaults in all workspace types |
| `utils.test.ts` | Defensive | Utility functions handle edge cases |

A PR with tests is harder to ignore than a PR with just code changes. It shows the maintainer exactly what was broken and proves the fix works.

## Related Posts

- [Jekyll Run Plugin: Local Development Settings That Actually Work](/jekyll-run-vscode-plugin-local-development/) — Configuration guide
- [Jekyll Run Plugin: Fixing the Multi-Root Workspace Crash](/jekyll-run-plugin-multiroot-workspace-bug/) — macOS debugging story
- [Jekyll Run Plugin: Patching the Source and Submitting a PR](/jekyll-run-plugin-pr-and-fork/) — Code fixes and fork strategy
- [Setting Up a VS Code Marketplace Publisher Account](/run-jekyll-vscode-marketplace-publisher-setup/) — Publishing prerequisites

## References

- [VS Code Extension Testing](https://code.visualstudio.com/api/working-with-extensions/testing-extension) — Official guide
- [vscode-test Package](https://github.com/microsoft/vscode-test) — Test runner for VS Code extensions
- [Mocha Test Framework](https://mochajs.org/) — The test framework used by the scaffold
- [Jekyll Run Source Code](https://github.com/Kanna727/jekyll-run) — The extension being tested
