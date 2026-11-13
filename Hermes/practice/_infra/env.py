"""Что есть для практики (Go, Docker, PostgreSQL): python practice/_infra/env.py — одна строка на пункт, без побочных эффектов."""
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")  # русский вывод в любой консоли Windows


def run(*cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return r.returncode == 0, r.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return False, ""


if not shutil.which("go"):
    print("go: MISSING (поставить с https://go.dev/dl/)")
else:
    ok, out = run("go", "env", "GOVERSION")
    print(f"go: {out.removeprefix('go') if ok else 'ERROR (go env не отвечает)'}")

# Python нужен только старым задачам до 008 и SQL-проверкам, пакеты им не нужны.
print(f"python: {sys.version.split()[0]}")

if not shutil.which("docker"):
    print("docker: MISSING (поставить Docker Desktop)")
else:
    ok, _ = run("docker", "info", "--format", "{{.ServerVersion}}")
    print(f"docker: {'ok' if ok else 'NOT RUNNING (запустить Docker Desktop)'}")
    if ok:
        _, status = run("docker", "ps", "--filter", "name=hermes-practice-pg", "--format", "{{.Status}}")
        print(f"postgres: {'up' if status.startswith('Up') else 'down (python practice/_infra/pg.py up)'}")
