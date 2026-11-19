#!/usr/bin/env python3
"""Reconcile configured GitHub and Gitea branches without force-pushing.

Run from a complete checkout of the writable Gitea repository. GitHub changes
that would advance or diverge from Gitea are staged on sync/github/<branch>
and opened as a Gitea pull request. Gitea-only fast-forwards are pushed to
GitHub. No merge, rebase, branch deletion, or forced update is performed.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


class SyncError(RuntimeError):
    pass


def run_git(args: list[str], *, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        ["git", *args],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    if result.returncode:
        # Git errors are useful operational evidence. Never include environment
        # values or credentials in diagnostics.
        detail = result.stderr.strip() or result.stdout.strip()
        raise SyncError(f"git {' '.join(args[:2])} failed: {detail}")
    return result.stdout.strip()


def remote_url(remote: str) -> str:
    url = run_git(["remote", "get-url", remote])
    parsed = urllib.parse.urlparse(url)
    if parsed.username or parsed.password:
        raise SyncError(f"Remote {remote!r} embeds credentials; remove them from .git/config")
    return url


def askpass_environment(github_url: str) -> tuple[dict[str, str], tempfile.TemporaryDirectory[str]]:
    """Return an ephemeral askpass helper for GitHub HTTPS authentication."""
    parsed = urllib.parse.urlparse(github_url)
    token = os.environ.get("GITHUB_SYNC_TOKEN", "")
    if parsed.username or parsed.password:
        raise SyncError("GITHUB_REMOTE_URL must not embed credentials")
    if parsed.scheme not in {"http", "https"}:
        if token:
            raise SyncError("GitHub credentials are supported only with an HTTP(S) GitHub URL")
        return os.environ.copy(), tempfile.TemporaryDirectory(prefix="gitea-sync-")
    if not parsed.hostname:
        raise SyncError("GITHUB_REMOTE_URL must be an HTTPS URL")
    if parsed.scheme != "https" or parsed.hostname.casefold() != "github.com":
        raise SyncError("GITHUB_REMOTE_URL must use https://github.com for this deployment")

    tempdir: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory(prefix="gitea-sync-")
    helper = Path(tempdir.name) / "askpass"
    helper.write_text(
        "#!/bin/sh\n"
        "case \"$1\" in\n"
        f"  *Username*{parsed.hostname}*|*{parsed.hostname}*Username*) printf '%s\\n' 'x-access-token' ;;\n"
        f"  *Password*{parsed.hostname}*|*{parsed.hostname}*Password*) printf '%s\\n' \"$GITHUB_SYNC_TOKEN\" ;;\n"
        "  *) exit 1 ;;\n"
        "esac\n",
        encoding="utf-8",
    )
    helper.chmod(0o700)
    env = os.environ.copy()
    env.update(
        {
            "GIT_ASKPASS": str(helper),
            "GIT_ASKPASS_REQUIRE": "force",
            "GIT_TERMINAL_PROMPT": "0",
        }
    )
    if token:
        env["GITHUB_SYNC_TOKEN"] = token
    return env, tempdir


def fetch_refs(url: str, namespace: str, *, env: dict[str, str] | None = None) -> None:
    run_git(
        [
            "fetch",
            "--no-tags",
            "--prune",
            url,
            f"+refs/heads/*:refs/remotes/{namespace}/*",
        ],
        env=env,
    )


def branches(namespace: str) -> dict[str, str]:
    output = run_git(
        ["for-each-ref", "--format=%(refname:strip=3) %(objectname)", f"refs/remotes/{namespace}"]
    )
    result: dict[str, str] = {}
    for line in output.splitlines():
        name, sha = line.split(maxsplit=1)
        if name != "HEAD":
            result[name] = sha
    return result


def is_ancestor(ancestor: str, descendant: str) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    raise SyncError(f"git merge-base failed: {result.stderr.strip()}")


def branch_ref(namespace: str, name: str) -> str:
    return f"refs/remotes/{namespace}/{name}"


def api_request(
    method: str,
    url: str,
    token: str,
    payload: dict[str, Any] | None = None,
) -> tuple[int, Any]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, method=method)
    request.add_header("Authorization", f"token {token}")
    request.add_header("Accept", "application/json")
    if body is not None:
        request.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read()
            return response.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as error:
        # Do not include request headers or token values in failures.
        raw = error.read().decode("utf-8", errors="replace")
        raise SyncError(f"Gitea API {method} {url} returned HTTP {error.code}: {raw[:500]}") from error
    except urllib.error.URLError as error:
        raise SyncError(f"Gitea API request failed: {error.reason}") from error


def ensure_pull_request(
    *, api_base: str, token: str, repository: str, base: str, head: str, web_base: str
) -> str:
    owner, repo = repository.split("/", 1)
    api_repo = urllib.parse.quote(owner, safe="") + "/" + urllib.parse.quote(repo, safe="")
    for page in range(1, 101):
        pulls_url = f"{api_base.rstrip('/')}/repos/{api_repo}/pulls?state=open&limit=50&page={page}"
        _, pulls = api_request("GET", pulls_url, token)
        if not pulls:
            break
        for pull in pulls:
            source_repo = pull.get("head", {}).get("repo") or {}
            if (
                pull.get("base", {}).get("ref") == base
                and pull.get("head", {}).get("ref") == head
                and source_repo.get("full_name", "").casefold() == repository.casefold()
            ):
                return str(pull.get("html_url") or "")

    title = f"Sync GitHub {head.removeprefix('sync/github/')} into {base}"
    body = (
        "This pull request stages commits fetched from GitHub. Review and merge it "
        "in Gitea to reconcile upstream changes. The sync job never merges, rebases, "
        "or force-pushes branches automatically. Once merged, the resulting Gitea "
        "branch can be fast-forwarded back to GitHub."
    )
    _, pull = api_request(
        "POST",
        f"{api_base.rstrip('/')}/repos/{api_repo}/pulls",
        token,
        {"title": title, "head": head, "base": base, "body": body},
    )
    return str(pull.get("html_url") or "")


def gitea_compare_url(web_base: str, repository: str, base: str, head: str) -> str:
    owner, repo = repository.split("/", 1)
    path = "/".join(urllib.parse.quote(part, safe="") for part in (owner, repo))
    compare = urllib.parse.quote(base, safe="/._-+") + "..." + urllib.parse.quote(head, safe="/._-+")
    return f"{web_base.rstrip('/')}/{path}/compare/{compare}"


def push_ref(url: str, sha: str, branch: str, *, env: dict[str, str] | None = None) -> None:
    run_git(
        ["-c", "push.followTags=false", "push", url, f"{sha}:refs/heads/{branch}"],
        env=env,
    )


def sync() -> int:
    if os.environ.get("GITEA_EVENT_NAME") == "push" and os.environ.get("GITEA_REF", "").startswith(
        "refs/heads/sync/github/"
    ):
        print("SKIP bot review-branch push event")
        return 0

    github_url = os.environ.get("GITHUB_REMOTE_URL", "")
    gitea_remote = os.environ.get("GITEA_REMOTE", "origin")
    if not github_url:
        raise SyncError("Set GITHUB_REMOTE_URL to the repository's GitHub HTTPS URL")

    gitea_url = remote_url(gitea_remote)
    if gitea_url == github_url:
        raise SyncError("GitHub and Gitea remotes resolve to the same URL")

    askpass_env, tempdir = askpass_environment(github_url)
    review_needed = False
    pushed = 0
    try:
        fetch_refs(github_url, "sync-github", env=askpass_env)
        fetch_refs(gitea_url, "sync-gitea")
        github_branches = branches("sync-github")
        gitea_branches = branches("sync-gitea")
        reserved_source = [name for name in github_branches if name.startswith("sync/github/")]
        if reserved_source:
            raise SyncError(
                "The branch name prefix sync/github/ is reserved for Gitea review branches: "
                + ", ".join(reserved_source)
            )
        # Ignore bot review branches when calculating source branches.
        gitea_branches = {
            name: sha for name, sha in gitea_branches.items() if not name.startswith("sync/github/")
        }
        names = sorted(set(github_branches) | set(gitea_branches))

        for name in names:
            github_sha = github_branches.get(name)
            gitea_sha = gitea_branches.get(name)
            if github_sha is None:
                push_ref(github_url, gitea_sha, name, env=askpass_env)
                pushed += 1
                print(f"PUSHED Gitea-only branch {name} to GitHub")
                continue
            if gitea_sha is None:
                push_ref(gitea_url, github_sha, name)
                print(f"COPIED GitHub-only branch {name} to Gitea")
                continue
            if github_sha == gitea_sha:
                print(f"IN SYNC {name}")
                continue
            if is_ancestor(github_sha, gitea_sha):
                push_ref(github_url, gitea_sha, name, env=askpass_env)
                pushed += 1
                print(f"PUSHED Gitea fast-forward {name} to GitHub")
                continue

            # GitHub is ahead or the histories diverged. Preserve the upstream
            # tip on a review branch; never alter either side's working branch.
            review_branch = f"sync/github/{name}"
            existing_ref = branch_ref("sync-gitea", review_branch)
            try:
                existing_sha = run_git(["rev-parse", "--verify", f"{existing_ref}^{{commit}}"])
            except SyncError:
                existing_sha = None
            if existing_sha is not None and not is_ancestor(existing_sha, github_sha):
                raise SyncError(
                    f"GitHub rewrote {name} or the review branch changed independently; "
                    f"left both sides unchanged. Inspect Gitea branch {review_branch}."
                )
            if existing_sha != github_sha:
                push_ref(gitea_url, github_sha, review_branch)
            review_needed = True
            print(f"REVIEW REQUIRED {name}: compare {name} with {review_branch}")

            api_base = os.environ.get("GITEA_API_URL", "").rstrip("/")
            api_token = os.environ.get("GITEA_TOKEN", "")
            repository = os.environ.get("GITEA_REPOSITORY", "")
            web_base = os.environ.get("GITEA_WEB_URL", os.environ.get("GITEA_SERVER_URL", ""))
            if api_base and api_token and repository:
                pr_url = ensure_pull_request(
                    api_base=api_base,
                    token=api_token,
                    repository=repository,
                    base=name,
                    head=review_branch,
                    web_base=web_base,
                )
                if pr_url:
                    print(f"GITEA PR {pr_url}")
            elif web_base and repository:
                print(
                    "OPEN GITEA PR "
                    + gitea_compare_url(web_base, repository, name, review_branch)
                )
    finally:
        tempdir.cleanup()

    if pushed:
        print(f"OUTBOUND fast-forward pushes: {pushed}")
    if review_needed:
        print("Human review is required before GitHub updates are applied to Gitea branches.")
    return 0


def main() -> int:
    try:
        return sync()
    except SyncError as error:
        print(f"SYNC ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
