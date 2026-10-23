#!/usr/bin/env python3
"""Wrzuca nową wersję ev.html na GitHub (GitHub Pages).

Użycie (w folderze projektu):
    python deploy.py
    python deploy.py "opis zmian"

Przy pierwszym uruchomieniu sam zrobi git init, doda remote i wypchnie pliki.
Wymaga zainstalowanego gita i zalogowania do GitHuba przy pierwszym pushu.
"""
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO_URL = "https://github.com/maciekpacynski/EV.git"
BRANCH = "main"
FILES = ["ev.html"]
PAGE_URL = "https://maciekpacynski.github.io/EV/ev.html"

ROOT = Path(__file__).resolve().parent


def git(*args, check=True, capture=False):
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=check,
        text=True,
        capture_output=capture,
    )
    return result.stdout.strip() if capture else None


def fail(msg):
    print(f"BŁĄD: {msg}")
    sys.exit(1)


def main():
    message = sys.argv[1] if len(sys.argv) > 1 else f"Aktualizacja {datetime.now():%Y-%m-%d %H:%M}"

    try:
        git("--version", capture=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        fail("git nie jest zainstalowany (git-scm.com).")

    for f in FILES:
        if not (ROOT / f).exists():
            fail(f"brak pliku {f} w {ROOT}")

    if not (ROOT / ".git").exists():
        print("Inicjuję repozytorium...")
        git("init", "-b", BRANCH)

    remotes = git("remote", capture=True).split()
    if "origin" not in remotes:
        git("remote", "add", "origin", REPO_URL)
    elif git("remote", "get-url", "origin", capture=True) != REPO_URL:
        git("remote", "set-url", "origin", REPO_URL)

    git("add", *FILES)

    if git("status", "--porcelain", capture=True):
        git("commit", "-m", message)
        print(f"Commit: {message}")
    else:
        print("Brak zmian do zatwierdzenia.")

    # Upewnij się, że lokalna gałąź nazywa się tak jak na GitHubie.
    git("branch", "-M", BRANCH)

    print("Wypycham na GitHuba...")
    try:
        git("push", "-u", "origin", BRANCH)
    except subprocess.CalledProcessError:
        fail(
            "push się nie udał. Sprawdź logowanie do GitHuba i czy repo "
            "maciekpacynski/EV istnieje. Jeśli na GitHubie jest już inna "
            "historia (np. README), zrób najpierw: git pull origin main --rebase"
        )

    print(f"\nGotowe. Strona odświeży się w ciągu 1-2 minut:\n{PAGE_URL}")


if __name__ == "__main__":
    main()
