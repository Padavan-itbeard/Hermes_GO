# Anki cards

Cards are written in Russian.

## 1. Main rule: one idea per card, however many cards that takes

The topic's content decides the number of cards, never a wish to save space. The card should be short, not the deck.

- If the lesson had 12 separate facts worth remembering, make 12 cards.
- Never merge two facts into one card to be compact. Splitting beats squeezing.
- **But do not split one fact into fragments either.** A sequence of steps («4 действия import») is one card with the whole list, not one card per step that just restates it. A separate card for an element is justified only when that element has its own "why" or its own pitfall.
- **Enumerations:** one card for the list as a whole, plus one card per element that has its own substance («Что делает транспортный уровень TCP/IP и какие протоколы на нём работают?»).
- **Volume.** Each taught step gives at least 4 cards, usually 5–8. Before writing, silently count the steps taught since the last batch and aim for that many cards times 5–6. Four steps means roughly 20–25 cards, not 13. A core topic gives 15–45 cards in total, a side topic 8–12. The learner loves a rich deck and picks the cards they want, so when in doubt, include the card. Volume never justifies filler: every card still holds one real idea.

Cards cover everything taught since the last batch of cards, not only the last message.

**Checklist of card sources.** Walk through the lesson top to bottom and make a card for each of these:
- every new term (what it is and what it is for);
- every "why" and every "what is the difference";
- every check question and experiment you asked during the lesson, with its answer: if it was worth asking, it is worth remembering;
- every point where the explanation had to be corrected or sharpened, phrased as the fact to remember;
- every contrast pair;
- every tier 2 detail;
- every analogy that carries the mechanism (for example «Почему code point похож на номер паспорта, а кодировка на способ его записи?»);
- one card per finished module: «Как коротко ответить на собесе: что такое X?», with an answer of 2–3 sentences ready to say aloud.

## 2. Format: a JSON file for Ivy, never cards in chat

Cards never go into the chat. They go into a JSON file that the learner reads in Ivy, a local card viewer, and transfers into Anki from there.

**Numbering starts at 1 inside every file.** Files never share or continue numbering: `n` is just the card's position in this batch, so the first card of every new file is `n: 1`. The learner numbers the deck themselves while moving cards into Anki, so a course-wide counter would only be a thing to keep in sync and get wrong.

**File:** `anki/<topic-slug>.json`, for example `anki/go-slices.json`. One file per batch of cards. List the folder once (`ls anki`) before you pick the name: if it is taken, add a short distinguishing word (`go-slices-practice.json`). Never edit or overwrite an older file — those are cards the learner already has.

```json
{
  "deck": "Go::Slices",
  "topic": "Слайсы в Go",
  "cards": [
    {
      "n": 1,
      "question": "Что копируется при b := a, если a это слайс?",
      "answer": "Только заголовок слайса: указатель на базовый массив, len и cap, 24 байта на 64-битной машине.\nЭлементы не копируются, a и b смотрят в один массив."
    },
    {
      "n": 2,
      "question": "Что выведет этот код и почему?",
      "answer": "[99 2 3]. b := a скопировал только заголовок, оба слайса смотрят в один базовый массив.",
      "code": "a := []int{1, 2, 3}\nb := a\nb[0] = 99\nfmt.Println(a)"
    }
  ]
}
```

- `n`, `question`, `answer` are required. `code` is optional: a runnable snippet, plain code without ``` fences, results in comments.
- `deck` is `Area::Topic` in English, `topic` is the Russian title.
- `question` and `answer` are plain text. No Markdown: no `**`, no ``` fences, no backticks. A line break is `\n`, a list item starts with `- `.
- The file must be valid JSON: escape `"` and line breaks inside strings.

**Answer layout: one thought per line.** The learner reads answers as a column, never as a paragraph. Put each sentence on its own line (`\n`). Separate logical blocks (definition, mechanism, consequence) with an empty line (`\n\n`). Enumerations go as `- ` list items. Never write an answer longer than one sentence as a single line.

Bad: `"answer": "Atomicity (атомарность). Слово происходит от греческого atomos (неделимый). Операция либо выполняется целиком, либо не выполняется вовсе."`

Good: `"answer": "Atomicity (атомарность).\nСлово от греческого atomos — неделимый.\n\nОперация либо выполняется целиком, либо не выполняется вовсе."`

**After writing the file**, run exactly this command and nothing else:

```
node ivy/show.js anki/<file>.json
```

It validates the file, starts Ivy if needed and opens the cards in the browser. If it prints an error, fix the file and run it again.

Then write one line in chat: «Карточки N–M (X шт.) открыты в Ivy. Что дальше?». If the topic is hands-on (code, SQL, commands), always replace «Что дальше?» with the practice offer: «Карточки N–M (X шт.) открыты в Ivy. Закрепим 15-минуткой или идём дальше?».

## 3. The question

- Requires reasoning: «почему», «чем отличается», «что произойдёт, если», «зачем». A plain «что такое X» is fine for basic definitions.
- Unambiguous: there is one correct answer.
- Understandable without the lesson. Six months later the card must stand on its own.
- Does not contain the answer.

## 4. The answer

- As long as the idea. Usually 1–4 sentences. If the idea is a table of four ranges, give the table or list.
- The first sentence answers directly. Then a clarification or consequence.
- Concrete: a number, an example, a line of code. «я это 1103 (U+044F)» beats «у каждого символа свой номер».
- States version and platform when the fact is false without them: «Go 1.22+, 64-бит».
- Spoken language, not bureaucratese (see the language rules). No filler.

## 5. Reference cards

This is the content level to hold. They are shown as Q/A for readability only: in the file, Q goes to `question`, A to `answer`, and a code block to `code`.

Q: Чем code point отличается от кодировки?
A: Code point отвечает на вопрос "какой это символ?" (номер). Кодировка отвечает на вопрос "как записать этот номер в байты?". Номер один и тот же везде, а байты зависят от выбранной кодировки.

Q: Что такое UTF-8 и сколько байт он тратит на символ?
A: Самая распространённая кодировка Unicode с переменной длиной, от 1 до 4 байт на символ:
- U+0000..U+007F: 1 байт (латиница, цифры, знаки)
- U+0080..U+07FF: 2 байта (кириллица, греческий)
- U+0800..U+FFFF: 3 байта (большинство иероглифов)
- U+10000 и выше: 4 байта (эмодзи)

Q: Почему len("привет") равно 12, а range по той же строке делает 6 шагов?
A: string в Go это байты в UTF-8, и len считает байты: каждая кириллическая буква занимает 2.
for i, r := range s декодирует UTF-8 и идёт по рунам, поэтому шагов 6.
```go
s := "привет"
fmt.Println(len(s), len([]rune(s)))   // 12 6
```

Q: Почему s[i] у строки это байт, а не символ, и чем это грозит?
A: Индекс строки это смещение в байтах, а не номер символа: у "привет" s[0] равно 208, первый байт буквы «п».
Резать строку s[a:b] безопасно только по границам рун, иначе получится битый UTF-8.

Q: Что будет, если в строке лежат байты не в UTF-8, и как это заметить?
A: Ошибки не будет: string это просто байты, никто их не проверяет.
При обходе range каждый невалидный байт отдаётся как руна-замена U+FFFD — те самые кракозябры вместо падения.
Проверить заранее: utf8.ValidString(s).
```go
s := string([]byte{0xD0, 0x9F, 0xFF})
fmt.Println(utf8.ValidString(s))   // false
for _, r := range s {
    fmt.Printf("%U ", r)           // U+041F U+FFFD
}
```

Q: Почему s += ch в цикле это O(N^2), а strings.Builder даёт O(N)?
A: Строки неизменяемы: каждое += выделяет новую строку и копирует всё накопленное, то есть работа идёт квадратом.
strings.Builder пишет в растущий буфер и отдаёт готовую строку один раз, в конце.

## 6. Anti-examples

Too squeezed: one card instead of five, no mechanisms.

**999**
Q: Какие уровни у TCP/IP?
A: Канальный, сетевой, транспортный, прикладной. Каждый отвечает за своё.

Correct: one card for the list of layers, one card per layer (what it does, which protocols, which address or data unit), plus a card «зачем бэкендеру знать уровни».

Too fragmented: «Что делает import на первом шаге?», «…на третьем шаге?», «…на четвёртом шаге?». Correct: one card «Какие 4 действия выполняет import?» with the full list, plus separate cards only for what has its own "why" (for example «Почему второй import того же модуля не выполняет файл заново?»).

## 7. After the cards

The learner picks the cards they want right in Ivy while moving them to Anki. Do not ask which cards they take and do not repeat cards in chat.

Nothing else to update after the cards: the file name is the only record of the batch, and the progress gets its line when the topic closes.
