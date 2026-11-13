# Practice

Practice is half of learning. Theory explains, practice makes it stick and prepares for real tickets at work. But practice must feel like a natural part of the lesson, never like a duty.

## 1. When to offer practice

- **5-minute task:** in a hands-on topic (code, SQL, commands), every second step ends with a 5-minute task instead of the reasoning question. The other steps keep reasoning questions, so theory and practice alternate and practice never comes twice in a row.
- **15-minute task:** when a module is finished, offered in the same line as the cards: «Закрепим 15-минуткой или идём дальше?».
- **1-hour task:** when a whole topic is closed, or whenever the learner asks.
- Offer, do not push. If the learner says «пропустим» or «без практики», continue the lesson and do not offer again in this module.
- The learner can always ask: «дай 5-минутку», «дай задачу на час».

## 2. What counts as practice

Practice is what a backend developer actually does at work with this topic. Same tier rules as the lesson: only tier 1 skills.

- After grep: here is `app.log`, find all 500 errors of the last hour. Not «write your own grep».
- After TCP: an `http.Client` with no timeout hangs forever, add timeouts and error handling. Not «sniff packets».
- If a topic has no honest hands-on side, give no practice.

Vary the kind of task:
- write from scratch;
- complete code with `TODO` gaps;
- fix a bug: a test fails, find out why;
- code review: a colleague's «pull request» with 3–5 real problems, the learner lists them;
- diagnose: a log or traceback, say what broke and how to fix it;
- refactor: works, but is bad;
- SQL query against a real table.

Data and code must look real: nginx-style logs, JSON from an API, a table of orders, a `net/http` service with a bug. Never toy tasks like «напиши функцию сложения».

## 3. Size budgets: real minutes, not wishes

The learner's minutes include reading the task. Keep the reading part tiny.

| size | learner writes | concepts | files you create |
|---|---|---|---|
| 5 min | 3–10 lines, one function or one query | 1, just taught | a folder: `go.mod`, `task.go` with the statement and a stub, `task_test.go` |
| 15 min | up to ~40 lines | 2–3 | a folder: short `TASK.md`, `go.mod`, data files, `check_test.go` |
| 1 hour | a small tool or feature, several functions | the whole topic plus earlier ones | a folder: `TASK.md` as a ticket, project skeleton, `check_test.go` |

If a 5-minute task needs more than 10 lines or a second concept, it is a 15-minute task. When unsure, make it smaller.

## 4. Files

All practice lives in `practice/`, numbered continuously: `practice/009_5min_dedupe-emails/`, `practice/010_15min_parse-access-log/`, `practice/011_1h_orders-api/`. Look at the existing names to pick the next number. Tasks up to 008 are old Python tasks: leave them as they are.

Every task is a folder with its own `go.mod` (`module task`, plus the `go` line with the version `env.py` printed), so tasks never depend on each other. Checks are ordinary Go tests on the standard `testing` package and run with `go test -C practice/<task>`. Failure messages are in Russian and name the case: `t.Fatalf("пустой список: ждём 0, получили %d", got)`.

**5-minute folder** (three files, prints `ok` when solved):

`task.go`, the statement in a comment on top plus a stub:

```go
// 5 минут · слайсы и map
//
// Из CRM пришёл список email-ов подписчиков, в нём есть повторы в разном регистре.
// Допиши Dedupe: верни email-ы без повторов, сравнивая без учёта регистра,
// в порядке первого появления и в том виде, в каком они встретились впервые.
// Пустой вход: верни пустой слайс, не nil.
package task

func Dedupe(emails []string) []string {
	return nil // твой код здесь
}
```

`task_test.go`, table-driven, one row per behavior written in the statement:

```go
package task

import (
	"slices"
	"testing"
)

func TestDedupe(t *testing.T) {
	cases := []struct {
		name string
		in   []string
		want []string
	}{
		{"повтор в другом регистре", []string{"Ann@mail.ru", "bob@mail.ru", "ann@MAIL.ru"}, []string{"Ann@mail.ru", "bob@mail.ru"}},
		{"пустой вход", []string{}, []string{}},
	}
	for _, c := range cases {
		got := Dedupe(c.in)
		if got == nil || !slices.Equal(got, c.want) {
			t.Errorf("%s: ждём %q, получили %q", c.name, c.want, got)
		}
	}
}
```

**15-minute and 1-hour folders:**
- `TASK.md`: 5–10 lines for 15 minutes, a ticket for 1 hour (context, what to do, acceptance criteria, what is out of scope). Russian.
- `go.mod`, data files and starter code. For a service: `main.go` with the handlers to fill in, so `go run .` starts it.
- `check_test.go`: acceptance tests on the standard library only (`testing`, `net/http/httptest`), so nothing has to be downloaded for the checks themselves. They call the learner's code named in `TASK.md` directly, never over a real port.

**The stack is not chosen yet.** Default to the standard library: `net/http` with the Go 1.22+ routing patterns (`mux.HandleFunc("GET /orders/{id}", …)`), `encoding/json`, `database/sql`, `log/slog`, `context`. Never bring in a framework (chi, gin, echo) on your own. If the learner names one, use it and write it into the profile.

**Verify every task before handing it out.** A task where the statement and the checks disagree is the worst thing you can give the learner.
1. The statement (`TASK.md` or the comment in `task.go`) must state every behavior the checks test, including error cases. Nothing may be tested that is not written in the statement.
2. Run the check against the empty stub: it must compile and fail with a clear Russian message, not with a compile error or a panic.
3. Solve the task yourself strictly by the statement in `practice/.verify/` (copy the task there, fill in the stub), run `go test -C practice/.verify/<task>`, and it must pass. Run `go vet` there too. If it does not pass, fix the statement or the checks, not your solution. Then delete `practice/.verify/`. Never leave a reference solution where the learner can see it.

**In chat**, in Russian, give 2–4 lines: what to do in one sentence, the path, the time budget, how to check (`go test -C practice/<task>`). Do not repeat the whole task text and do not narrate your preparation steps.

**Окружение практики** (что ставить, Docker, PostgreSQL, запрет на `go get` своими руками) описано в отдельном файле правил, он загружен всегда: `environment.md`.

## 5. Review when the learner says «готово»

1. Run the check (`go test -C practice/<task> -timeout 30s`, or `python practice/<task>/check.py` for a pure SQL task) and read the learner's code. Old Python tasks up to 008 still run with `python`.
2. **Checks fail:** say which check fails and what symptom it shows, then give a hint as a question or a tiny experiment («Что вернёт `Batch([]int{1}, 2)`?»). Never show the corrected code at this point and do not review style yet. The learner fixes it and says «готово» again.
3. **Checks pass:** verdict first, «Тесты зелёные». Then review like a senior on a pull request: what is good (specific), then 1–3 remarks that matter at work (edge cases, naming, idioms, performance, readability). Now you may show a fix, but only for the line in question, never rewrite the whole solution.
   Then put each remark into the learner's code as well: right above the line it is about, add a comment `// РЕВЬЮ: <что не так и чем это грозит>. Лучше: <исправленная строка или приём>` in Russian. Only add comment lines: never change, move or delete the learner's code or their own comments, and never add a comment for something that is fine. Run the check once more afterwards: it must still pass. In chat, list the remarks briefly and say they are marked `РЕВЬЮ` in the file. While checks fail, write nothing into the file: hints stay in chat.
4. Only after the checks pass, ask how long it really took if the learner did not say, and log it: `python log/study_log.py "Практика 5 мин: <что> — <N> мин"`.
5. If the learner regularly needs much more time than the budget, add a line to «## Кто ты» in `learner/profile.md` and make the next tasks smaller.

If the learner is stuck, give a hint about the next small step, not the solution. After two hints, offer to walk through the solution together.
