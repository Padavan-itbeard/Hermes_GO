"""Поиск по архиву пройденного и проверка потолков памяти.

    python learner/covered.py <слово>      проходили ли эту тему
    python learner/covered.py --list       все темы с датами
    python learner/covered.py --check      потолки и согласованность (для /check)

Зачем это есть. В правила загружаются только profile.md (кто ученик) и now.md
(где мы сейчас) — у них жёсткие потолки, поэтому мешок правил не растёт никогда.
Полный список пройденного живёт в covered.md, в правила не попадает и может
расти сколько угодно: учитель узнаёт о нём только через этот поиск.

Файл одинаков у всех агентов: папку он берёт из своего пути.
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # русский вывод в любой консоли Windows

LEARNER = Path(__file__).resolve().parent
PROFILE, NOW, COVERED = LEARNER / "profile.md", LEARNER / "now.md", LEARNER / "covered.md"
PROFILE_LIMIT, NOW_LIMIT = 8_000, 3_000  # байт; потолки держат мешок правил плоским
MAX_BLOCKS, MAX_BULLETS = 5, 25          # пункты архива — псевдословарь: их больше и они длиннее
CHAR_BUDGET = 7_000                      # чтобы ответ поиска сам не раздул контекст


def blocks():
    """Темы из covered.md: список (заголовок, подпись с датой и карточками, детали)."""
    if not COVERED.exists():
        return []
    out, in_comment = [], False
    for line in COVERED.read_text(encoding="utf-8").splitlines():
        # html-комментарии в архиве — это пояснения и примеры формата, темами они не считаются
        if "<!--" in line:
            in_comment = "-->" not in line
            continue
        if in_comment:
            in_comment = "-->" not in line
            continue
        if line.startswith("## "):
            out.append([line[3:].strip(), "", []])
        elif not out:
            continue                      # шапка файла до первой темы
        elif line.startswith("- "):
            out[-1][2].append(line[2:].strip())
        elif line.strip() and not out[-1][1]:
            out[-1][1] = line.strip()     # первая обычная строка темы — подпись
    return [tuple(b) for b in out]


def search(query):
    q = query.lower()
    hits = [b for b in blocks() if q in b[0].lower() or q in b[1].lower()
            or any(q in d.lower() for d in b[2])]
    if not hits:
        print(f"НЕ ПРОЙДЕНО: «{query}» в архиве нет.")
        print("Значит эту тему вы не разбирали: так и скажи ученику и предложи разобрать.")
        return 0
    print(f"ПРОЙДЕНО: совпадений {len(hits)}.")
    spent, hidden = 0, 0
    for title, meta, details in hits[:MAX_BLOCKS]:
        head = f"\n## {title}" + (f"\n{meta}" if meta else "")
        print(head)
        spent += len(head)
        shown = [d for d in details if q in d.lower()] or details
        for d in shown[:MAX_BULLETS]:
            if spent > CHAR_BUDGET:
                hidden += 1
                continue
            print(f"- {d}")
            spent += len(d) + 3
        hidden += max(0, len(shown) - MAX_BULLETS)
    if hidden:
        print(f"\n… ещё {hidden} пунктов есть в covered.md, но здесь не показаны: уточни слово поиска или открой файл.")
    if len(hits) > MAX_BLOCKS:
        print(f"\n… ещё {len(hits) - MAX_BLOCKS} тем совпало, уточни слово поиска.")
    return 0


def list_all():
    bs = blocks()
    if not bs:
        print("Архив пуст: пройденных тем нет.")
        return 0
    print(f"Тем в архиве: {len(bs)}")
    for title, meta, details in bs:
        print(f"- {title}" + (f" — {meta}" if meta else "") + f" ({len(details)} пунктов)")
    return 0


def check():
    bad = False
    for f, limit in ((PROFILE, PROFILE_LIMIT), (NOW, NOW_LIMIT)):
        if not f.exists():
            print(f"FAIL {f.name} отсутствует -> создать файл памяти")
            bad = True
            continue
        size = len(f.read_bytes())
        if size > limit:
            print(f"FAIL {f.name}: {size} байт, потолок {limit} -> уплотнить: "
                  f"детали пройденного переносятся в covered.md, старые сессии из now.md выталкиваются")
            bad = True
        elif size > limit * 0.9:
            print(f"WARN {f.name}: {size} из {limit} байт -> скоро уплотнять")
        else:
            print(f"OK   {f.name}: {size} из {limit} байт")

    titles = [t.lower() for t, _, _ in blocks()]
    print(f"OK   covered.md: тем {len(titles)}, {len(COVERED.read_bytes()) if COVERED.exists() else 0} байт (без потолка, в правила не грузится)")

    # Темы, упомянутые в now.md как пройденные, обязаны быть в архиве:
    # иначе при выталкивании из окна они исчезнут совсем.
    if NOW.exists():
        lost = []
        for line in NOW.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\s*-\s*\d{4}-\d\d-\d\d\s*[·:—-]\s*([^·—]+)", line)
            if not m:
                continue
            topic = m.group(1).strip().rstrip(".").lower()
            # тема строки и заголовок архива могут отличаться уточнением: сравниваем в обе стороны
            # строка сессии может перечислять коды через запятую («GO-4.4.1–4.4.4, 4.4.А»),
            # а заголовок архива писать их иначе («GO-4.4.А»): тогда хватит, что каждый код найден
            parts = [s.strip() for s in topic.split(",") if s.strip()]
            if not any(topic in x or x in topic for x in titles)                     and not all(any(s in x for x in titles) for s in parts):
                lost.append(m.group(1).strip())
        if lost:
            print(f"WARN в now.md есть темы, которых нет в covered.md: {', '.join(lost[:5])}"
                  f" -> дописать их в covered.md, иначе они пропадут при выталкивании из окна")
    return 1 if bad else 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        sys.exit('usage: python learner/covered.py <слово> | --list | --check')
    if args[0] == "--check":
        sys.exit(check())
    if args[0] == "--list":
        sys.exit(list_all())
    sys.exit(search(" ".join(args)))
