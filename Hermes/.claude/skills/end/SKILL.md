---
name: end
description: >-
  Ends a study session: updates the learner memory, then commits and pushes all learning state (memory, cards,
  practice, topic log) to git. Use when the learner types /end or says the session is over.
---

# Конец сессии

1. If the memory files do not yet reflect this session, update them first, exactly as the memory rules say: the
   topic goes into `learner/covered.md` (append the block with date, card file and details), then `learner/now.md`
   gets the session line, the next topic and the postponed items, and `learner/profile.md` only if you learned
   something that changes how to teach. Skip what is already up to date.

2. Run exactly one command from the `Hermes/` folder (the script is shared with the Gemini persona):

   ```
   python .agents/skills/end/scripts/end.py
   ```

3. Reply in Russian in one or two lines: what was saved (the commit line from the output) and whether the push
   succeeded. If the output starts with «СТОП», show that line and the fix it names, and do nothing else.
   If a line starts with «ПАМЯТЬ», the session is already saved: compact the file it names as the memory
   rules say (merge lines, move detail into `learner/covered.md`, lose no fact), then run the command once more.

Do not run any other git commands.
