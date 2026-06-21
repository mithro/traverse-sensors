#!/usr/bin/env python3
"""Derive the Debian/DKMS package version from git.

The version is ``0.<N>`` where N is the commit count (``git rev-list --count
HEAD``). It increments on every commit, so apt / unattended-upgrades always sees
a new CI build as an upgrade, and it sorts above the legacy hand-built ``0.01``
(``0.<N>`` with N>1 compares greater than ``0.01``).

This value is used for BOTH the .deb version and the DKMS ``PACKAGE_VERSION``
(``dkms.conf`` ships ``#MODULE_VERSION#``, which dh_dkms fills from the changelog;
``debian/rules`` installs the source to ``/usr/src/traverse-sensors-<version>``).
Keeping them identical is what makes ``apt upgrade`` trigger a real DKMS rebuild.

Usage:
    python3 packaging/deb-version.py                   # print the version
    python3 packaging/deb-version.py --write-changelog # regenerate debian/changelog
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CHANGELOG = REPO / "debian" / "changelog"
MAINTAINER = "Tim 'mithro' Ansell <me@mith.ro>"


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO), *args],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def version() -> str:
    try:
        return "0." + _git("rev-list", "--count", "HEAD")
    except Exception:  # noqa: BLE001 - any git failure -> safe fallback
        return "0.0"


def write_changelog() -> None:
    try:
        describe = _git("describe", "--tags", "--always", "--long")
        date = _git("log", "-1", "--format=%cd", "--date=rfc2822")
    except Exception:  # noqa: BLE001
        describe, date = "unknown", "Thu, 01 Jan 1970 00:00:00 +0000"
    CHANGELOG.write_text(
        f"traverse-sensors ({version()}) unstable; urgency=medium\n\n"
        f"  * Automated build from git ({describe}).\n\n"
        f" -- {MAINTAINER}  {date}\n"
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="Derive the package version from git")
    ap.add_argument("--write-changelog", action="store_true",
                    help="regenerate debian/changelog for the git-derived version")
    args = ap.parse_args()
    if args.write_changelog:
        write_changelog()
    else:
        print(version())


if __name__ == "__main__":
    main()
