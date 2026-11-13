---
trigger: always_on
---

# Practice environment: adapt, do not assume

Everything you need to know about `practice/_infra/` and `log/` is written here. Never open those files to read them; just run them.

Before a task that needs anything beyond the standard library, a database or Docker, run once: `python practice/_infra/env.py`. It prints the Go version, whether Docker runs and whether the practice PostgreSQL is up. Do not probe the environment with other commands.

- **Go is missing:** say so and give the link `https://go.dev/dl/`; no task until the learner says «поставил».
- **A third-party module is needed** (only a database driver so far): do not create the task yet. Give the learner the exact line, for example `go get -C practice/<task> github.com/jackc/pgx/v5`, and wait for «поставил». Never run `go get` or `go install` yourself and never offer to.
- **Docker is missing or not running:** say so plainly («Docker не найден: поставь Docker Desktop, запусти и скажи мне») and offer a task without the database meanwhile.
- **PostgreSQL is down:** start it yourself with `python practice/_infra/pg.py up` (it waits until the database is ready).

**PostgreSQL tasks.** The practice database runs in Docker on port 5433. Never use `localhost` (on Windows it costs 3 seconds per connection), always `127.0.0.1`. Use the helper instead of improvising with psql:
- `python practice/_infra/pg.py load <file.sql>` loads a schema with data.
- Pure SQL tasks need no Go at all: the learner writes queries into `.sql` files, and a `check.py` loads the schema with `from pg import load, query` (`sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_infra"))`), runs the learner's query through `query()` and compares rows. `query(sql)` returns rows as lists of strings.
- Go code that talks to the database uses the driver `github.com/jackc/pgx/v5` through `database/sql` (`import _ "github.com/jackc/pgx/v5/stdlib"`, `sql.Open("pgx", dsn)`) and this DSN, written into the test as a constant: `postgres://hermes:hermes@127.0.0.1:5433/practice?connect_timeout=3&lock_timeout=3000&statement_timeout=10000`.

Every task must create its own tables (`DROP TABLE IF EXISTS …` first) so tasks never depend on each other.

**Checks must never hang.** A test that waits on a row lock blocks the whole session. Every DB connection uses the DSN above (it sets the lock and statement timeouts), every test closes what it opened with `t.Cleanup`, every query takes a `context.WithTimeout`, and concurrency tests wait with a timeout, never a bare `wg.Wait()`. Always run checks with `-timeout 30s`; if a check hits it, fix the check, not the solution.
