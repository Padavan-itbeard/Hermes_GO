"""Сохранить состояние обучения в git: python .agents/skills/end/scripts/end.py

Коммитит всё внутри папки своего агента (прогресс, карточки, задачи, журнал) в ветку main и пушит, если есть origin.
Сообщение коммита собирается из сегодняшних записей журнала тем, если журнал у агента есть.

После сохранения проверяет потолки памяти (learner/covered.py --check, если он у агента есть). Превышение
не мешает коммиту: прогресс важнее. Но последней строкой печатается «ПАМЯТЬ: …», и учитель уплотняет файл
сразу, пока помнит сессию, а не через неделю по случайному /check.

Файл одинаков у всех агентов: папку и имя агента он берёт из своего пути, поэтому его не нужно
править под каждого и он не может разойтись между ними.
"""
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # русский вывод в любой консоли Windows

AGENT = Path(__file__).resolve().parents[4]  # <repo>/<Агент>/.agents/skills/end/scripts/end.py
NAME = AGENT.name
LOG = AGENT / "log" / "study_log.md"


def memory_note():
    """Строки «ПАМЯТЬ: …» про файлы памяти выше потолка. Пусто, если всё в порядке или памяти у агента нет."""
    checker = AGENT / "learner" / "covered.py"
    if not checker.exists():
        return
    r = subprocess.run([sys.executable, str(checker), "--check"], cwd=AGENT, capture_output=True, text=True, encoding="utf-8")
    for line in r.stdout.splitlines():
        if line.startswith("FAIL"):
            print(f"ПАМЯТЬ: {line[4:].strip()}. Уплотни сейчас и запусти эту команду ещё раз.")


def git(*args):
    r = subprocess.run(["git", *args], cwd=AGENT, capture_output=True, text=True, encoding="utf-8")
    return r.returncode == 0, (r.stdout + r.stderr).strip()


ok, branch = git("rev-parse", "--abbrev-ref", "HEAD")
if not ok:
    sys.exit(f"СТОП: это не git-репозиторий ({branch})")
if branch != "main":
    sys.exit(f"СТОП: текущая ветка {branch}, а прогресс обучения живёт в main. Переключись: git checkout main")

git("add", "-A", "--", ".")
ok, staged = git("diff", "--cached", "--name-only", "--", ".")
if not staged:
    print("Нечего сохранять: изменений нет.")
    memory_note()
    sys.exit(0)

today = date.today().isoformat()
topics = []
if LOG.exists():
    for line in LOG.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) == 3 and cells[1] == today and cells[0] not in topics:
            topics.append(cells[0])
head = f"Сессия {today}" if NAME == "Hermes" else f"{NAME}: сессия {today}"
subject = head + (f": {'; '.join(topics[:4])}" + (" …" if len(topics) > 4 else "") if topics else "")
body = "\n".join(f"- {f}" for f in staged.splitlines())
ok, out = git("commit", "-q", "-m", subject, "-m", f"Изменённые файлы:\n{body}")
if not ok:
    sys.exit(f"СТОП: коммит не удался: {out}")
print(f"Коммит: {subject} (файлов: {len(staged.splitlines())})")

ok, _ = git("remote", "get-url", "origin")
if not ok:
    print("Push пропущен: нет remote origin.")
    memory_note()
    sys.exit(0)
ok, out = git("push", "origin", "main")
print("Push в origin/main: готово." if ok else f"Push не удался: {out.splitlines()[-1] if out else '?'} (коммит сохранён локально)")
memory_note()
