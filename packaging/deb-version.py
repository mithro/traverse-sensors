#!/usr/bin/env python3
"""Derive the Debian/DKMS package version from ``git describe``.

Same *shape* as mithro/sensors2mqtt's post-release versioning, but computed
directly from git (no setuptools_scm needed): at tag ``vX.Y`` the version is
``X.Y``; N commits later ``X.Y.postN``. It increments on every commit, so each
push publishes a new package. These are valid Debian versions verbatim.

The value is used for BOTH the .deb version and the DKMS ``PACKAGE_VERSION``
(``dkms.conf`` ships ``#MODULE_VERSION#``, filled by dh_dkms from the changelog;
``debian/rules`` installs the source to ``/usr/src/traverse-sensors-<version>``).
Keeping them identical is what makes ``apt upgrade`` trigger a real DKMS rebuild.

Usage:
    python3 packaging/deb-version.py                   # print the version
    python3 packaging/deb-version.py --write-changelog # regenerate debian/changelog
"""
from __future__ import annotations

import argparse
import re
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
    """git-describe derived version: vX.Y -> X.Y, N commits later -> X.Y.postN."""
    try:
        describe = _git("describe", "--tags", "--long", "--match", "v[0-9]*")
        m = re.match(r"^v(.+)-(\d+)-g[0-9a-f]+$", describe)
        if m:
            base, n = m.group(1), int(m.group(2))
            return base if n == 0 else f"{base}.post{n}"
    except subprocess.CalledProcessError:
        pass
    # No matching tag yet: fall back to a monotonic count-based version.
    try:
        return "0.0.post" + _git("rev-list", "--count", "HEAD")
    except Exception:  # noqa: BLE001
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
