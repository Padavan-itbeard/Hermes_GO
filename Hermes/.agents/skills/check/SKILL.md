---
name: check
description: >-
  Checks whether Hermes is ready to work: system files, rule sizes, learner progress, Node/Ivy, git branch,
  practice packages, Docker and PostgreSQL. Use when the learner types /check or asks whether everything is ready.
---

# Проверка системы

1. Run exactly one command from the `Hermes/` folder:

   ```
   python .agents/skills/check/scripts/check.py
   ```

2. Reply in Russian, short:
   - the final line (ГОТОВ / НЕ ГОТОВ);
   - every FAIL and WARN line as a list item, each with its fix command exactly as printed;
   - nothing about OK lines except «остальное в порядке».

Do not run the install commands yourself. Do not open other files. After the reply, continue with whatever the learner wants.
