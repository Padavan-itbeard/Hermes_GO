"""Дописывает строку в журнал тем: python log/study_log.py "тема"."""
import sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # русский вывод в любой консоли Windows

LOG = Path(__file__).with_name("study_log.md")

topic = " ".join(sys.argv[1:]).strip().replace("|", "/")
if not topic:
    sys.exit('usage: python log/study_log.py "тема"')
if not LOG.exists():
    LOG.write_text("| Тема | Дата | Время |\n|---|---|---|\n", encoding="utf-8")
now = datetime.now()
with LOG.open("a", encoding="utf-8") as f:
    f.write(f"| {topic} | {now:%Y-%m-%d} | {now:%H:%M} |\n")
print("ok")
