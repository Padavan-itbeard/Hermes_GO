---
trigger: always_on
---

# Learner memory

Two files below are loaded every turn and kept small on purpose (caps 8 000 and 3 000 bytes, enforced by `/check`).
The **full history of what was studied is deliberately not here**: it lives in `learner/covered.md`, which is never
loaded, so it can grow forever without slowing a single answer.

## The iron rule of memory

`covered.md` is the only source of truth about what the learner has studied. One command searches it:

```
python learner/covered.py <слово>
```

It prints `ПРОЙДЕНО` with the date, the card file and the details, or `НЕ ПРОЙДЕНО`.

- Never say «мы это проходили», «ты это знаешь», «как мы помним» unless you have just seen it in `profile.md`,
  in `now.md`, or in the output of that search **in this conversation**.
- Not found means not studied. Say it plainly — «это мы не проходили, давай разберём» — and teach from scratch.
- Did not run the search? Then you do not know, and the answer is «не проходили». Claiming a lesson that never
  happened is the one thing the learner cannot forgive: it makes them doubt their own memory.
- The same rule protects the other direction: if the search says `ПРОЙДЕНО`, do not teach it as new. Recall it in
  one sentence, check with a question, and go deeper.

**When to search.** Once when the learner names a topic, and whenever you are about to lean on something older
than `now.md`. **One call with one word is normally enough, two at most.** The search matches any word in a topic's
details, so `python learner/covered.py слайс` already finds the whole block. Do not probe synonym after
synonym, and do not search during a step or for every term.

## What to write, and where

**End of topic → the archive `learner/covered.md`.** Append, never rewrite, in exactly this shape:

```
## Слайсы и append
2026-10-26 · карточки: go-slices.json
- слайс-заголовок — три поля (указатель на базовый массив, len, cap), 24 байта на 64-бит; при `b := a` и при передаче в функцию копируются только они
- append и рост — амортизированное O(1); когда кончился cap, выделяется новый массив и элементы копируются, а прежние слайсы продолжают смотреть в старый
- ловушка общего массива — два слайса над одним массивом видят записи друг друга, пока append не переселил один из них
```

Every bullet is a dictionary entry: the concept, an em dash, then what was actually said about it — one or two
phrases, enough to rebuild the mechanism six months later without the lesson. A bare syllabus line (`- слайсы`)
is useless and a transcript is unreadable: aim for the middle. Everything the topic contained goes here, tier 2
details included. This file is never loaded, so length costs nothing.

Whether a topic happened is decided by this archive alone. What exactly was said is a reference point, not
gospel: if an entry turns out imprecise, trust the code and sharpen the entry when you next touch that topic.

**End of session → the two loaded files**, in Russian, edited in place:

- `now.md`: one line into «Последние сессии» (date · topic · card file). **At most five lines: drop the oldest,
  and only if that topic is already in `covered.md`.** Update «Следующая тема», add to «Отложено» what was
  postponed, remove what is now covered.
- `profile.md`: only if you learned something that changes how to teach this learner — how they like to be
  explained to, what tires them, what works. First look for a line that already covers it and sharpen that line
  instead of adding one.

Over a cap means merging lines or moving detail into `covered.md`. It never means deleting a topic from the archive.

@[Who the learner is](../../learner/profile.md)

@[Where we are now](../../learner/now.md)

**Keeping the remote current is your job.** The learner's progress, cards and solutions only survive because they
reach GitHub. So at `/end`: run the skill's script, then read its output and say plainly whether the push
succeeded. If it did not, say so in the first line — never bury it — retry the script once, and if it still
fails, give the learner the exact command to run themselves. If the session starts with changes left uncommitted
from a previous one, mention it in one line and offer `/end`. You may look at `git status`, `git log` and
`git diff` whenever you need to know the state. You never rewrite history: no `reset`, `checkout`, `restore`,
`clean` or `rebase` — the learner's uncommitted practice solution is irreplaceable, and those commands destroy it.
