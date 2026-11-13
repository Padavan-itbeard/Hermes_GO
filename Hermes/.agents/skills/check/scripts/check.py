"""Проверка готовности Hermes к работе. Запуск из папки Hermes/: python .agents/skills/check/scripts/check.py

Каждая строка: OK, WARN (работать можно, но чего-то не хватает) или FAIL (работать нельзя) и что сделать.
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # русский вывод в любой консоли Windows

HERMES = Path(__file__).resolve().parents[4]
RULE_LIMIT = 24_000  # лимит agy на файл правил после раскрытия импортов
results = []


def report(level, what, fix=""):
    results.append(level)
    print(f"{level:4} {what}" + (f" -> {fix}" if fix else ""))


def run(*cmd, cwd=HERMES):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", timeout=30)
        return r.returncode == 0, (r.stdout + r.stderr).strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        return False, str(e)


def expanded_size(path):
    text = path.read_text(encoding="utf-8")
    for label, rel in re.findall(r"@\[([^\]]*)\]\(([^)]+)\)", text):
        target = path.parent / rel
        text += target.read_text(encoding="utf-8") if target.exists() else ""
    return len(text.encode("utf-8"))


# 1. Файлы системы
required = ["GEMINI.md", "AGENTS.md", ".agents/rules/learner.md", "rules/teaching.md", ".agents/rules/cards.md", "rules/practice.md",
            "learner/profile.md", "learner/now.md", "learner/covered.md", "learner/covered.py",
            "ivy/server.js", "ivy/show.js", "ivy/open.js", "ivy/ui/index.html",
            "log/study_log.py", "practice/_infra/env.py", "practice/_infra/pg.py",
            "practice/_infra/docker-compose.yml", ".agents/skills/end/SKILL.md"]
missing = [f for f in required if not (HERMES / f).exists()]
report("FAIL" if missing else "OK", "файлы системы" + (f": нет {', '.join(missing)}" if missing else ""),
       "восстановить: git checkout -- Hermes" if missing else "")
for d in ("anki", "practice"):
    (HERMES / d).mkdir(exist_ok=True)

# 2. Правила влезают в лимит agy
always_on = sorted(f".agents/rules/{p.name}" for p in (HERMES / ".agents" / "rules").glob("*.md"))
for entry in ("GEMINI.md", "AGENTS.md", *always_on):
    if (HERMES / entry).exists():
        size = expanded_size(HERMES / entry)
        level = "FAIL" if size > RULE_LIMIT else "WARN" if size > RULE_LIMIT * 0.9 else "OK"
        fix = {"OK": "", "WARN": "близко к лимиту: сжать этот файл правил или вынести раздел",
               "FAIL": "правила обрезаются: уплотнить profile.md и now.md или вынести раздел правил"}[level]
        report(level, f"{entry} с импортами: {size} из {RULE_LIMIT} байт (лимит agy; у Claude Code его нет)", fix)

# 2б. Задачи практики: не забыта ли папка самопроверки
verify = HERMES / "practice" / ".verify"
report("WARN" if verify.exists() else "OK", "practice/.verify" + (" остался на диске" if verify.exists() else " убран"),
       "удалить practice/.verify: там лежит эталонное решение, ученик не должен его видеть" if verify.exists() else "")

# 2в. Карточки: валидный JSON и нумерация по порядку
bad = []
for f in sorted((HERMES / "anki").glob("*.json")):
    try:
        nums = [c.get("n") for c in json.loads(f.read_text(encoding="utf-8")).get("cards") or []]
        if nums != sorted(set(nums)):
            bad.append(f"{f.name} (номера не по порядку)")
    except ValueError as e:
        bad.append(f"{f.name} ({e.__class__.__name__})")
report("WARN" if bad else "OK", "файлы карточек" + (f": {', '.join(bad)}" if bad else ""),
       "починить номера карточек" if bad else "")

# 3. Память ученика: потолки загружаемых файлов и согласованность с архивом.
# Это главная проверка: когда profile.md или now.md перерастают потолок,
# agy молча обрезает правила, и учитель начинает «вести себя странно».
ok, out = run(sys.executable, "learner/covered.py", "--check")
for line in out.splitlines():
    if line[:4].strip() in ("OK", "WARN", "FAIL"):
        results.append(line[:4].strip())
        print(line)
    elif line.strip():
        print(f"     {line.strip()}")

now = HERMES / "learner/now.md"
if now.exists():
    text = now.read_text(encoding="utf-8")
    has = all(s in text for s in ("## Последние сессии", "## Отложено", "## Следующая тема"))
    report("OK" if has else "WARN", "now.md: разделы на месте" if has else "now.md: не хватает разделов",
           "" if has else "нужны «## Последние сессии», «## Отложено», «## Следующая тема»")
prof = HERMES / "learner/profile.md"
if prof.exists():
    text = prof.read_text(encoding="utf-8")
    has = all(s in text for s in ("## Кто ты", "## Сильные стороны"))
    report("OK" if has else "WARN", "profile.md: разделы на месте" if has else "profile.md: не хватает разделов",
           "" if has else "нужны «## Кто ты» и «## Сильные стороны»")
    # Записи об ошибках ученика больше не ведутся: раздел для них — остаток старых правил.
    if "## На что обращать внимание" in text:
        report("WARN", "profile.md: раздел «На что обращать внимание» снова на диске",
               "ошибки ученика не записываются: перенеси живые строки о стиле работы в «## Кто ты» и удали раздел")

# Остаток старой памяти: сессия, запущенная до перехода, могла заново создать progress.md.
stale = HERMES / "learner" / "progress.md"
if stale.exists():
    report("WARN", "learner/progress.md снова на диске (файл старой памяти)",
           "перенеси из него что нужно в covered.md и удали: память теперь в profile.md, now.md, covered.md")

# 3б. Два движка, одна память. Персоны (rules/ под Gemini и rules-claude/ под Claude) могут расходиться,
# файлы памяти — нет: вторая копия профиля означает, что агенты начнут помнить разное.
entries = {"GEMINI.md": HERMES / "GEMINI.md", "CLAUDE.md": HERMES / "CLAUDE.md"}
present = {k: v for k, v in entries.items() if v.exists()}
report("OK" if present else "FAIL", "точки входа: " + (", ".join(present) if present else "ни одной"),
       "" if present else "нужен GEMINI.md (для agy) и/или CLAUDE.md (для Claude Code)")

# 3в. Третья точка входа: Codex. Codex не раскрывает импорты и читает AGENTS.override.md вместо AGENTS.md,
# поэтому его персона держит инварианты буквальным текстом. Дубль допустим только под присмотром: если он
# разъедется с rules-claude/memory.md, Codex будет учить по памяти о правилах, а не по правилам.
codex_entry = HERMES / "AGENTS.override.md"
CODEX_DOC_LIMIT = 32 * 1024  # project_doc_max_bytes: дальше Codex молча обрезает инструкции
if not codex_entry.exists():
    report("WARN", "AGENTS.override.md нет (точка входа Codex)",
           "движок Codex не настроен; остальные два работают")
else:
    text = codex_entry.read_text(encoding="utf-8")
    size = len(text.encode("utf-8"))
    report("FAIL" if size > CODEX_DOC_LIMIT else "WARN" if size > CODEX_DOC_LIMIT * 0.9 else "OK",
           f"AGENTS.override.md: {size} из {CODEX_DOC_LIMIT} байт (лимит Codex; у agy и Claude его нет)",
           "" if size <= CODEX_DOC_LIMIT * 0.9 else "сжать: сверх лимита Codex обрезает инструкции без предупреждения")
    lost = [m for m in ['learner/covered.py', 'мы это проходили', 'rules-claude/memory.md', 'learner/now.md'] if m not in text]
    report("OK" if not lost else "FAIL",
           "инварианты в персоне Codex на месте" if not lost else f"в AGENTS.override.md потеряно: {', '.join(lost)}",
           "" if not lost else "вернуть инвариант в AGENTS.override.md: Codex видит только этот файл постоянно")
    if "@[" in text or re.search(r"^@\S", text, re.M):
        report("FAIL", "в AGENTS.override.md есть импорт (@...)",
               "Codex импорты не раскрывает: заменить на явное «прочитай файл» или вписать текстом")

missing_mem = [k for k, v in present.items()
               if not all(s in v.read_text(encoding="utf-8") for s in ("learner/profile.md", "learner/now.md"))]
report("OK" if not missing_mem else "FAIL",
       "обе персоны подключают общую память" if not missing_mem else f"память не подключена в {', '.join(missing_mem)}",
       "" if not missing_mem else "точка входа обязана импортировать learner/profile.md и learner/now.md")

dups = [str(p.relative_to(HERMES)) for p in HERMES.rglob("*.md")
        if p.name in ("profile.md", "now.md", "covered.md") and p.parent.name != "learner"]
report("OK" if not dups else "FAIL", "копий памяти нет" if not dups else f"вторая копия памяти: {', '.join(dups)}",
       "" if not dups else "память живёт только в learner/: удалить копии, иначе движки будут помнить разное")

# 4. Инструменты
report("OK" if sys.version_info >= (3, 10) else "FAIL", f"python {sys.version.split()[0]}",
       "" if sys.version_info >= (3, 10) else "поставить Python 3.10+")
node = shutil.which("node")
if node:
    ok, out = run("node", "--version")
    major = int(re.sub(r"\D", "", out.split(".")[0]) or 0)
    report("OK" if major >= 20 else "FAIL", f"node {out}", "" if major >= 20 else "обновить Node.js до 20+ (нужен Ivy)")
else:
    report("FAIL", "node не найден", "поставить Node.js 20+: https://nodejs.org (без него не открываются карточки)")
engines = [name for name in ("codex", "claude", "agy") if shutil.which(name)]
report("OK" if engines else "WARN", "движки: " + (", ".join(engines) if engines else "ни одного в PATH"),
       "" if engines else "поставить хотя бы один: Codex CLI, Claude Code или Antigravity CLI (agy)")

# 5. Ivy
if node:
    ok, out = run("node", "-e", "fetch('http://127.0.0.1:' + (process.env.IVY_PORT || 4317) + '/api/state')"
                  ".then(r => r.json()).then(s => console.log('up ' + s.workspace)).catch(() => console.log('down'))")
    report("OK", f"Ivy: {'запущен' if out.startswith('up') else 'не запущен, поднимется сам при первых карточках'}")

# 6. Git и сохранение прогресса
if shutil.which("git"):
    ok, branch = run("git", "rev-parse", "--abbrev-ref", "HEAD")
    report("OK" if branch == "main" else "WARN", f"git: ветка {branch}",
           "" if branch == "main" else "учиться нужно на main: git checkout main (dev — для разработки)")
    ok, remote = run("git", "remote", "get-url", "origin")
    report("OK" if ok else "WARN", f"git remote: {remote if ok else 'нет'}", "" if ok else "/end будет только коммитить, без push")
    ok, dirty = run("git", "status", "--porcelain", "--", ".")
    if dirty:
        report("WARN", f"несохранённых изменений в Hermes/: {len(dirty.splitlines())}", "сохранить: /end")
else:
    report("FAIL", "git не найден", "поставить Git: https://git-scm.com")

# 7. Практика: Go, Docker, Postgres
if not shutil.which("go"):
    report("FAIL", "go не найден", "поставить Go: https://go.dev/dl/")
else:
    ok, ver = run("go", "env", "GOVERSION")
    report("OK" if ok else "FAIL", f"go: {ver.removeprefix('go') if ok else 'не отвечает'}")
if not shutil.which("docker"):
    report("WARN", "docker не найден", "для практики с PostgreSQL: поставить Docker Desktop")
else:
    ok, _ = run("docker", "info", "--format", "{{.ServerVersion}}")
    if not ok:
        report("WARN", "docker не запущен", "запустить Docker Desktop (нужен для практики с PostgreSQL)")
    else:
        ok, status = run("docker", "ps", "--filter", "name=hermes-practice-pg", "--format", "{{.Status}}")
        report("OK", "PostgreSQL для практики: " + ("запущен" if status.startswith("Up") else "не запущен, Hermes поднимет сам"))

fails, warns = results.count("FAIL"), results.count("WARN")
print()
print("ИТОГ: " + ("НЕ ГОТОВ" if fails else "ГОТОВ" + (" (с замечаниями)" if warns else "")) + f" · FAIL {fails}, WARN {warns}")
sys.exit(1 if fails else 0)
