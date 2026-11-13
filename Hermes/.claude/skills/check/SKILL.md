---
name: check
description: >-
  Checks that Hermes is ready to work: files, rule sizes, the caps on the learner memory, Node, Ivy, the git
  branch and the packages practice needs. Use when the learner types /check or says something is broken.
---

# Проверка готовности

The script is shared with the Gemini persona, so both engines report the same state. Run exactly one command
from the `Hermes/` folder:

```
python .agents/skills/check/scripts/check.py
```

Then retell the result in Russian, briefly. For every FAIL and WARN say what to do (the script prints the fix
after `->`). If everything is OK, one line is enough. Note that the line about the `agy` rule-size limit does
not apply to you: Claude Code has no such cap. The memory caps do apply — they are what keeps the lesson fast.

Do not fix anything yourself and do not install anything: only report.
