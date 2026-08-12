---
layout: post
title: "The Homelab Install Script Bug That Still Works: Homepage's Silent 7x Bloat"
image: /assets/images/og/homepage-lxc-standalone-nextjs-bug.png
categories: [technical, homelab, troubleshooting]
tags: [homelab, proxmox, lxc, nodejs, systemd, debugging, opensource, community-scripts]
excerpt: "A one-click Proxmox LXC installer for Homepage starts cleanly, serves 200s, and looks completely fine — while running the wrong Next.js startup command the entire time, at roughly 7x the disk footprint the project's own Dockerfile uses. This is the kind of bug that survives because nothing ever actually breaks."
description: "Diagnosing a real, confirmed bug in community-scripts/ProxmoxVE's Homepage installer: the systemd unit runs `next start` against a Next.js build produced with `output: standalone`, a combination the framework itself warns is unsupported. Traces the root cause through three independent sources — the live service log, Homepage's own next.config.js, and its official Dockerfile — quantifies the impact (771MB vs ~105MB), and works through the correct fix before contributing it back upstream."
date: 2026-08-12
last_modified_at: 2026-08-12
seo:
  type: BlogPosting
  date_published: 2026-08-12
  date_modified: 2026-08-12
---

Some bugs announce themselves. A stack trace, a 500, a container that won't start. This one didn't — the dashboard came up, served every request with a clean `200`, and would have stayed that way indefinitely if the service log hadn't been read closely enough to catch a single warning line sitting between two "success" messages.

<!-- excerpt-end -->

## The setup

Migrating a Proxmox homelab's dashboard from Homarr to [Homepage](https://gethomepage.dev/) — [a different post covers why](/homepage-homelab-dashboard/) — the actual container came from [community-scripts/ProxmoxVE](https://github.com/community-scripts/ProxmoxVE)'s `ct/homepage.sh`, the same one-line-curl installer pattern used for a dozen other services on this cluster already. It ran, it finished, the dashboard loaded. Nothing about the install output suggested a problem.

## What the log actually said

Buried in `journalctl -u homepage` between "Ready in 178ms" and normal operation:

```
⚠ "next start" does not work with "output: standalone" configuration. Use "node .next/standalone/server.js" instead.
```

Next.js — the framework Homepage is built on — was actively warning that its own production server was starting up the wrong way. Not failing. Warning, then proceeding anyway, because `next start` degrades gracefully into a slower, heavier mode rather than refusing to run. That graceful degradation is exactly what let this ship unnoticed: a hard failure gets fixed immediately, a warning next to a "Ready" message gets scrolled past.

## Tracing the actual cause, not just the symptom

The warning names two things — `output: standalone` and the wrong start command — but confirming which side was actually wrong meant going to primary sources rather than assuming.

**First, Homepage's own `next.config.js`** (pulled directly from `gethomepage/homepage`, not inferred):
```js
const nextConfig = {
  reactStrictMode: true,
  output: "standalone",
  // ...
};
```
Confirmed: this is how the upstream project builds itself. Not a stray flag from the install script.

**Second, Homepage's own Dockerfile** — the canonical, maintainer-authored deployment method:
```dockerfile
COPY --link --from=builder --chown=1000:1000 /app/.next/standalone/ ./
COPY --link --from=builder --chown=1000:1000 /app/.next/static/ ./.next/static
# ...
CMD ["node", "server.js"]
```
Two things confirmed at once here. The correct startup command is `node server.js` run from the standalone output — not `next start`. And critically, **the standalone build alone isn't sufficient** — Next.js's standalone output traces and bundles only the server-side JavaScript and its runtime dependencies; it does not automatically include `.next/static` (the CSS/JS chunks actually served to a browser) or the `public/` directory. Both need an explicit copy step alongside the build. Miss that step and even a *correctly*-started standalone server would 404 on every static asset.

**Third, the install script itself** (`community-scripts/ProxmoxVE`'s `install/homepage-install.sh`):
```bash
$STD pnpm build
# ...
cat <<EOF >/etc/systemd/system/homepage.service
[Service]
WorkingDirectory=/opt/homepage/
ExecStart=pnpm start
EOF
```
`pnpm start` resolves to `next start` per Homepage's own `package.json`. No copy step for `.next/static` or `public/`. Both halves of the bug, confirmed directly in the script that ships to every user who runs this installer — not a one-off misconfiguration on this specific box.

## Quantifying "it still works, but wrong"

The honest question after finding a bug like this: does it actually matter if nothing's broken? Measured directly rather than assumed:

| Directory | Size |
|---|---|
| `node_modules` (what `next start` actually runs against) | **771 MB** |
| `.next/standalone` (what should be running instead) | 102 MB |
| `.next/static` (needs manual copying alongside it) | 2.6 MB |

**~7.3x more disk than necessary**, on every single container this script creates. Not a rounding error — the entire point of a standalone Next.js build is shedding the full `node_modules` tree down to only the runtime dependencies actually needed in production. `next start` quietly opts back into the thing standalone output exists to avoid, and does it silently enough that a working dashboard gives no reason to look closer.

## The actual fix — and a second bug hiding behind the first

Reading the Dockerfile suggested a two-step fix: copy `.next/static` and `public/` into the standalone output, then point the systemd unit at `node server.js`. Applying it to a real, already-configured deployment surfaced a third step the Dockerfile comparison alone wouldn't have caught.

```bash
cp -r /opt/homepage/.next/static /opt/homepage/.next/standalone/.next/static
cp -r /opt/homepage/public /opt/homepage/.next/standalone/public
```

`.next/standalone/config/` does exist after a build — but diffing it against the real, edited `/opt/homepage/config/` showed it was a **stale skeleton**: the default placeholder services from install time, not the actual dashboard configuration. Pointing `WorkingDirectory` there as-is would have silently reset a working, hand-configured dashboard back to factory defaults on the very next restart — a worse bug than the one being fixed, and one that a Dockerfile-only reading of the problem would never have surfaced, because Homepage's official image dodges it entirely by volume-mounting `config/` at container runtime. Outside a container, the equivalent is a symlink:

```bash
rm -rf /opt/homepage/.next/standalone/config
ln -s /opt/homepage/config /opt/homepage/.next/standalone/config
```

```ini
# systemd unit, corrected
WorkingDirectory=/opt/homepage/.next/standalone
ExecStart=/usr/bin/node server.js
EnvironmentFile=/opt/homepage/.env
```

(The `EnvironmentFile` line matters too — `next start`'s automatic dotenv loading doesn't carry over to a bare `node server.js` call from a different working directory.)

Verified on a live, already-running deployment rather than a clean test box: after the switch, `/api/services` — a JSON endpoint, sidestepping the fact that Homepage's UI itself is client-rendered and won't show up in a plain `curl` of the homepage — returned byte-identical output to before the change. Process count dropped from three (`pnpm` → `next start` → `next-server`) to one. Memory dropped about 20%. The now-orphaned 771MB `node_modules` came out cleanly, with the running service unaffected, since the standalone output carries its own much smaller copy.

## A fix that doesn't survive its own update mechanism

The installer script has a companion `update_script()` — re-running the same one-line installer against an existing container detects it and updates in place instead of creating a new one. Worth checking before calling this fix "done": does a hand-applied patch survive that path, or does it need to be redone by hand forever?

Reading `update_script()` directly answered it. It never rewrites the systemd unit — only `systemctl stop`/`systemctl start` — so the corrected `ExecStart` line itself is safe. But it does run the update with `CLEAN_INSTALL=1`, which wipes the entire install directory, dotfiles included, before re-extracting a fresh release. Only `.env`, `config/`, and two subfolders of `public/` get backed up and restored around that wipe. Everything this fix touched inside `.next/standalone` — the copied static assets, the copied public folder, the config symlink — is not on that list. One update run and the manual fix is gone again, silently, the exact same way the original bug was silent.

Rather than write "redo these three commands after every update" into the deployment notes, the better fix is making the unit repair itself:

```ini
ExecStartPre=/bin/bash -c "mkdir -p /opt/homepage/.next/standalone/.next && cp -r /opt/homepage/.next/static /opt/homepage/.next/standalone/.next/static"
ExecStartPre=/bin/bash -c "rm -rf /opt/homepage/.next/standalone/public && cp -r /opt/homepage/public /opt/homepage/.next/standalone/public"
ExecStartPre=/bin/bash -c "rm -rf /opt/homepage/.next/standalone/config && ln -s /opt/homepage/config /opt/homepage/.next/standalone/config"
ExecStart=/usr/bin/node server.js
```

Each line is idempotent — cheap to run every time, not just the first. Tested by deliberately deleting all three (`config`, `public`, and `.next/static` inside `.next/standalone`) to simulate exactly what the update path's `CLEAN_INSTALL` wipe does, then restarting the service: all three were regenerated correctly before the server came back up, with `/api/services` and static assets both confirmed unchanged afterward. Since the update function's last step is exactly `systemctl start homepage`, this closes the loop — a future update self-repairs instead of silently reintroducing the same bug.

## Why this is worth fixing upstream, not just locally

The local fix takes five minutes. Writing this up and sending it back to `community-scripts/ProxmoxVE` takes longer, and matters more — this installer is the same one-line `curl | bash` a lot of homelabs run, and every one of them is currently provisioning a Homepage container at roughly 7x the disk it needs, running a server mode the framework's own maintainers explicitly moved away from. That's a small, quiet tax paid by everyone who's ever run this script, entirely invisible unless something prompts a closer look at a log file that says "success" right next to it.

Diagnosing it required checking three independent sources against each other rather than trusting any single one — the running service's own warning, the upstream framework's build config, and the upstream project's own reference deployment. None of those three alone would have been fully convincing; together, they left no ambiguity about either the cause or the fix. And the fix itself needed one more round of scrutiny before it earned the word "done": checking whether it would survive the installer's own update path, finding out it wouldn't, and closing that gap instead of documenting it as a known limitation.
