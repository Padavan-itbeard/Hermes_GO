---
name: practice
description: >-
  Practice report for a period: every practice task done (name, kind, start, finish, minutes) and the total time,
  as one JSON. Use when the learner types /practice or /практика, or asks for «практика» / «отчёт по практике»
  for a day, a week or a date range. Read-only, never during a lesson step.
---

# Отчёт по практике

1. Turn the learner's words into one period argument: `сегодня`, `вчера`, `неделя` (Monday to today), `месяц`
   (from the 1st to today), a date `2026-11-06` or a range `2026-11-01..2026-11-06`. No period named means `сегодня`.

2. Run exactly one command from the `Hermes/` folder (the script is shared with the Gemini persona):

   ```
   python .agents/skills/practice/scripts/practice.py <период>
   ```

3. Reply with the script output unchanged, inside one ```json block, and nothing else: no retelling, no comments.
   If the output starts with «СТОП», show that line in Russian and ask for the period again.
