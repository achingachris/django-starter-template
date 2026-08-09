# What to ignore, and what people ignore by mistake

Companion to the "What never belongs in version control" practice in `SKILL.md`.
Paste-ready blocks per ecosystem are in `gitignore-templates.md`.

## Always ignore

**Secrets and environment.** The category that matters.

```gitignore
.env
.env.*
!.env.example
*.pem
*.key
*.p12
*.pfx
credentials.json
client_secret*.json
service-account*.json
secrets.yaml
.netrc
```

**Local state that is regenerated.** Virtualenvs (`venv/`, `.venv/`), dependency
directories (`node_modules/`), build output (`dist/`, `build/`, `*.egg-info/`),
caches (`__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`), coverage
(`.coverage`, `htmlcov/`), local databases (`*.sqlite3`, `db.sqlite3`), collected
static and uploaded media (`staticroot/`, `media/`), and logs (`*.log`).

**Machine noise.** `.DS_Store`, `Thumbs.db`, `*.swp`, `.idea/`, `.vscode/`.

Editor and OS entries can go in your personal global ignore file instead, which
keeps other people's tooling out of your repo's config:

```bash
git config --global core.excludesFile ~/.config/git/ignore
```

Both work. Repo-level is more discoverable for collaborators; global is tidier. Put
project artifacts in the repo file either way.

## Do not ignore

Four things people ignore by mistake, each of which breaks something later:

- **Lockfiles.** `uv.lock`, `poetry.lock`, `package-lock.json`, `Cargo.lock`. They
  are how a build reproduces. Ignoring one means CI and production silently resolve
  different versions than you did. (A library that is published for others to
  consume is the one exception, and even then only for its own lockfile.)
- **Migrations.** Django and Rails migrations are source code and a schema change
  without its migration is an incomplete commit.
- **`.env.example`.** Track it, with placeholder values, so a new checkout can see
  which variables exist without learning it from a stack trace. Note the `!` line in
  the block above: the negation has to come after the `.env.*` pattern that would
  otherwise match it.
- **Committed compiled assets that the build image depends on.** If a project
  deliberately commits compiled CSS so the production image needs no Node, ignoring
  it breaks the deploy. Check before assuming build output is disposable.

## Diagnostics

Useful when something is not behaving as expected:

```bash
git check-ignore -v path/to/file   # which rule (and which line) matched
git status --ignored               # what is being ignored right now
git ls-files | grep -iE 'env|secret|credential|\.pem$'   # already tracked?
```