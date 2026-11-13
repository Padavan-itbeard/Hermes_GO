"""PostgreSQL для практики через docker exec, без Python-драйвера.

    python practice/_infra/pg.py up              # поднять контейнер и дождаться готовности
    python practice/_infra/pg.py load file.sql   # выполнить SQL-файл (схема, данные)
    python practice/_infra/pg.py query "SQL"     # выполнить запрос, строки через |

Из check.py: sys.path.insert(0, <путь к practice/_infra>); from pg import load, query, DSN, PG_OPTIONS
"""
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # русский вывод в любой консоли Windows

# Для psycopg в check.py: from pg import DSN, PG_OPTIONS; psycopg.connect(DSN, options=PG_OPTIONS).
# Только 127.0.0.1: на Windows "localhost" сначала пробует IPv6 и теряет 3 секунды на каждом подключении.
DSN = "postgresql://hermes:hermes@127.0.0.1:5433/practice?connect_timeout=3"
PG_OPTIONS = "-c lock_timeout=3000 -c statement_timeout=10000"

CONTAINER = "hermes-practice-pg"
COMPOSE = Path(__file__).with_name("docker-compose.yml")
PSQL = ["docker", "exec", "-i", CONTAINER, "psql", "-U", "hermes", "-d", "practice", "-v", "ON_ERROR_STOP=1", "-q"]


def up():
    subprocess.run(["docker", "compose", "-f", str(COMPOSE), "up", "-d"], check=True, capture_output=True)
    for _ in range(60):
        if subprocess.run(["docker", "exec", CONTAINER, "pg_isready", "-U", "hermes", "-d", "practice"],
                          capture_output=True).returncode == 0:
            return
        time.sleep(1)
    raise RuntimeError("PostgreSQL не поднялся за 60 секунд")


def _psql(sql, *flags):
    r = subprocess.run(PSQL + list(flags), input=sql, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip())
    return r.stdout


def load(path):
    """Выполнить SQL-файл целиком."""
    _psql(Path(path).read_text(encoding="utf-8"))


def query(sql):
    """Выполнить запрос и вернуть строки как списки строковых значений."""
    out = _psql(sql, "-A", "-t", "-F", "|")
    return [line.split("|") for line in out.splitlines() if line]


if __name__ == "__main__":
    cmd, *rest = sys.argv[1:] or ["help"]
    if cmd == "up":
        up()
        print("postgres: up")
    elif cmd == "load":
        load(rest[0])
        print("ok")
    elif cmd == "query":
        for row in query(rest[0]):
            print("|".join(row))
    else:
        print(__doc__)
