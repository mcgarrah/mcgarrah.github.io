# Git Credential Configuration Context

## User's Git Authentication Setup

The user's macOS workstation has multiple Git credential helpers scoped by host.
This was resolved after repeated HTTP 403 errors on `git push` caused by a global
`git-credential-manager` (GCM) intercepting GitHub requests before the `gh` CLI
credential helper could handle them.

### Credential Helper Configuration (~/.gitconfig)

| Host | Credential Helper | Source |
|------|-------------------|--------|
| `github.com` | `!/opt/homebrew/bin/gh auth git-credential` | `gh auth setup-git` |
| `gist.github.com` | `!/opt/homebrew/bin/gh auth git-credential` | `gh auth setup-git` |
| `gitlab.env.io` | `/usr/local/share/gcm-core/git-credential-manager` | Scoped GCM |
| Everything else | `osxkeychain` | Homebrew global gitconfig |

### Key Details

- GitHub CLI (`gh`) is installed via Homebrew at `/opt/homebrew/bin/gh`
- `gh auth status` confirms valid token with scopes: `gist`, `read:org`, `repo`, `workflow`
- GCM (git-credential-manager) is installed but must NOT be set as a global catch-all
- The homebrew-level gitconfig (`/opt/homebrew/etc/gitconfig`) sets `osxkeychain` as fallback

### Common Issue: HTTP 403 on git push

**Symptom:**
```
error: RPC failed; HTTP 403 curl 22 The requested URL returned error: 403
send-pack: unexpected disconnect while reading sideband packet
fatal: the remote end hung up unexpectedly
Everything up-to-date
```

**Root Cause:** A global `credential.helper` entry for GCM in `~/.gitconfig` intercepts
GitHub requests before the host-scoped `gh auth git-credential` helper runs. GCM returns
a stale or invalid token, causing the 403.

**Diagnosis:**
```bash
git config --show-origin --list | grep -i cred
```
Look for a non-scoped `credential.helper` pointing to GCM. If present, it's the problem.

**Fix:**
```bash
# Remove global GCM (breaks nothing if host-scoped entries exist)
git config --global --unset credential.helper "/usr/local/share/gcm-core/git-credential-manager"

# Ensure GitHub uses gh CLI (gh auth setup-git does this)
gh auth setup-git

# Scope GCM to GitLab only
git config --global credential.https://gitlab.env.io.helper "/usr/local/share/gcm-core/git-credential-manager"
```

**Do NOT suggest:**
- Setting GCM as a global credential helper (causes 403 on GitHub)
- Removing all credential helpers (breaks GitLab auth)
- Using personal access tokens directly in URLs (security risk)

### Corporate Split VPN / TLS Proxy Requirement

The user's macOS workstation runs a corporate VPN with TLS inspection (split tunnel).
GitHub HTTPS operations (push, pull, fetch) require the corporate VPN tunnel to be
active. When the VPN is off or the split tunnel is disabled, git push to GitHub fails
with the same HTTP 403 symptom described above.

**Diagnosis:**
```bash
GIT_CURL_VERBOSE=1 git push origin main 2>&1 | grep -i "issuer\|certificate"
```
If the TLS certificate issuer shows a corporate proxy CA (not GitHub's own CA), the
corporate VPN is intercepting the connection. If it does NOT show the corporate CA
and you're getting 403s, the split VPN may be off and traffic is routing incorrectly.

**Fix:** Re-enable the corporate split VPN, then retry the push.

**Key point:** The 403 from VPN/proxy issues looks identical to the 403 from credential
helper misconfiguration. Check VPN status first before debugging credential helpers.

### Prevention

If the user installs or updates GCM (e.g., via `brew upgrade`), it may re-add itself
as a global credential helper. Check for this if 403 errors recur after software updates.

If 403 errors appear after no credential changes, check corporate VPN/proxy status before
investigating credential helpers.
