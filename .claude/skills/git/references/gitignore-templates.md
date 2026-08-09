# Paste-ready ignore blocks

Compose these: the universal baseline plus whichever ecosystem blocks apply. Keep
the section comments; a `.gitignore` that is one unlabelled wall of patterns is one
nobody dares to edit later.

## Universal baseline

```gitignore
# Secrets and environment
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
.netrc

# macOS
.DS_Store

# Editors
.idea/
.vscode/
*.swp
*~

# Logs
*.log
```

## Python

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
build/
dist/

# Virtualenvs
venv/
.venv/

# Tooling caches
.pytest_cache/
.ruff_cache/
.mypy_cache/
.tox/

# Coverage
.coverage
.coverage.*
htmlcov/
coverage.xml
```

Keep `uv.lock` / `poetry.lock` / `requirements.txt` **tracked**.

## Django

Add to the Python block:

```gitignore
# Django
db.sqlite3
db.sqlite3-journal
*.sqlite3
media/          # user uploads: local only, real storage is S3 / Spaces / blob
staticroot/     # collectstatic output, regenerated at build time
local_settings.py
```

Two Django-specific cautions:

- **Migrations stay tracked.** `*/migrations/*.py` in a `.gitignore` is always a
  mistake. It is also what makes `makemigrations --check` fail in CI for reasons
  nobody can reproduce locally.
- **Check the static story before ignoring build output.** A project that compiles
  Tailwind and commits the result so its production image needs no Node will break
  if you ignore the compiled CSS. Ignore `staticroot/` (collectstatic output),
  not the compiled source assets that the build depends on.

## Node and frontend

```gitignore
# Dependencies
node_modules/

# Build output
dist/
build/
.next/
.nuxt/
.astro/
.cache/

# Env (framework variants)
.env.local
.env.*.local
```

Keep `package-lock.json` / `pnpm-lock.yaml` / `yarn.lock` **tracked**.

## Terraform and infrastructure

```gitignore
.terraform/
*.tfstate
*.tfstate.*
*.tfvars        # often holds credentials
!example.tfvars
crash.log
```

State files can contain secrets in plaintext. Use a remote backend rather than
committing state, even to a private repo.

## `.dockerignore`

Not the same file, same reasoning, and it is easy to write the first and forget the
second. Without it, `COPY . .` bakes whatever is in the build context into a layer
that anyone who can pull the image can read.

```dockerignore
.git
.env
.env.*
*.pem
*.key
credentials.json
client_secret*.json

venv/
.venv/
node_modules/
__pycache__/
*.py[cod]

.pytest_cache/
htmlcov/
.coverage

.DS_Store
.idea/
.vscode/
```

`.git` belongs at the top: it is often the largest thing in the context, and it
carries the full history of every file, including anything deleted in a later commit.