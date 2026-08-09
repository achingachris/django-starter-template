# Starting a repository

The full sequence behind the practice in `SKILL.md`. Read it when creating a
repository, or when an existing one needs to be brought up to the same settings.

Replace `OWNER/REPO` throughout. Everything here uses the `gh` CLI, authenticated
with the `repo` scope.


## The order, and why it is this order

1. **Local first commit**, with `.gitignore` written before the first `git add`.
2. **Create the remote**, choosing private or public.
3. **Merge settings**: squash only, delete the branch on merge.
4. **The gate**: a ruleset requiring the CI check.

The first two are ordered so the ignore file exists before anything is pushed:
retrofitting it means the thing you were keeping out is already in history, and a
secret that reached a commit has to be rotated, not deleted.

The last two are ordered so the check exists before it is required. A ruleset that
requires a context nothing reports blocks every merge forever, and the pull request
sits on "Expected: waiting for status to be reported" with no way to satisfy it.


## Ask first: private or public

This is not just a visibility flag. **On GitHub Free, rulesets and branch protection
are not available on private repositories.** Both endpoints answer:

```
403 Upgrade to GitHub Pro or make this repository public to enable this feature.
```

So the answer decides whether step 4 is possible at all:

| | Squash only | Delete branch on merge | Required CI check |
|---|---|---|---|
| Public | yes | yes | yes |
| Private, Free | yes | yes | **no**, needs Pro or above |
| Private, Pro and up | yes | yes | yes |

Check the plan before promising the gate, on any repository:

```bash
gh api repos/OWNER/REPO/rulesets --silent && echo "rulesets available" \
  || echo "not available on this repo and plan"
```

For a private repository without the gate, CI still runs on pull requests and its
result is still visible: what is missing is the enforcement. Say so out loud rather
than leaving the impression main is protected when it is not.


## 1. The first commit

```bash
mkdir myproject && cd myproject
git init -b main
```

Write `.gitignore` **now**, before the first `git add`. Paste-ready blocks per
ecosystem are in `gitignore-templates.md`. Then the rest of the first commit:

- `.gitignore`, from the templates, plus `.dockerignore` if the project ships an image
- `README.md`, even a single line saying what this is
- `LICENSE`, if the answer to private-or-public was public
- `.github/workflows/ci.yml`, so the check exists before it is required (below)

```bash
git add .gitignore README.md LICENSE .github/workflows/ci.yml
git commit -m "Initial commit"
```

Stage specific paths rather than `git add -A`, for the reason in `SKILL.md`.


## 2. The starter workflow

The job id becomes the check name the ruleset requires, so these two have to agree.
Below, the id is `ci`, and the ruleset requires the context `ci`.

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  ci:                      # <- this id is the required context
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: pytest
```

Three things about this file are load-bearing:

- **`on: pull_request` must be there.** A workflow that only runs on push never
  reports on a pull request, so a ruleset requiring it blocks every merge.
- **The context is the job's `name:` when set, otherwise the job id.** Setting
  `name: Tests` on the `ci` job changes the required context to `Tests`. Pick one and
  keep the ruleset in step with it.
- **A matrix job reports one context per combination**, named like
  `ci (3.12, ubuntu-latest)`. Requiring plain `ci` then never passes. Either require
  each combination, or keep the required job outside the matrix.

Swap the steps for whatever the project actually runs. What matters is that the job
exists, runs on pull requests, and can genuinely fail.


## 3. Create the remote

```bash
gh repo create OWNER/REPO --private --source=. --remote=origin --push
# or --public
```

`--source=.` uses the local repository, so the first commit is what lands. The
default branch on GitHub becomes whatever the local branch is called, which is why
`git init -b main` above was explicit.


## 4. Merge settings

```bash
gh api -X PATCH repos/OWNER/REPO \
  -F allow_squash_merge=true \
  -F allow_merge_commit=false \
  -F allow_rebase_merge=false \
  -F delete_branch_on_merge=true
```

`-F` sends typed values, so `false` arrives as a boolean. `-f` would send the string
`"false"`, which is truthy, and the setting would silently stay on.

**Squash only** is the setting the first practice in `SKILL.md` assumes: one commit
per pull request on main, and a branch whose commits are replaced rather than moved.
**Delete branch on merge** removes the merged branch from the remote, which is what
stops it being the accidental base for the next one.

Optional, and worth it: make the squash commit message come from the pull request
rather than the concatenated branch commits.

```bash
gh api -X PATCH repos/OWNER/REPO \
  -f squash_merge_commit_title=PR_TITLE \
  -f squash_merge_commit_message=PR_BODY
```


## 5. The ruleset

Public repositories, and private ones on Pro and above. This exact body has been
round-tripped through the API: create, read back, delete.

```bash
cat > /tmp/ruleset.json <<'JSON'
{
  "name": "main",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": false,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false,
        "allowed_merge_methods": ["squash"]
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": false,
        "do_not_enforce_on_create": true,
        "required_status_checks": [{ "context": "ci" }]
      }
    }
  ]
}
JSON

gh api -X POST repos/OWNER/REPO/rulesets --input /tmp/ruleset.json
```

What each part is doing, and what to change:

- **`~DEFAULT_BRANCH`** targets whatever the default branch is called, so the ruleset
  survives a rename and can be copied between repositories unedited.
- **`required_approving_review_count: 0`** suits a solo repository: the pull request
  is required, the approval is not. Raise it to 1 when someone else is around to
  click it, otherwise every change blocks on a review that cannot happen.
- **`allowed_merge_methods: ["squash"]`** restates the repository setting at the rule
  level. Belt and braces, and it is the one that survives someone flipping the
  repository setting back.
- **`deletion` and `non_fast_forward`** stop main being deleted or force-pushed. Not
  requested as often as the other three, cheap, and the failure they prevent is
  unrecoverable. Drop them if you disagree.
- **`strict_required_status_checks_policy: false`** does not force the branch to be
  up to date with main before merging. Setting it to `true` means every merge to main
  invalidates every open pull request until it is updated, which on a busy repository
  is constant churn for little gain.
- **`do_not_enforce_on_create: true`** lets the branch be created without a check
  having reported yet.


## Verify, and undo

```bash
gh api repos/OWNER/REPO \
  -q '{squash:.allow_squash_merge, merge:.allow_merge_commit, rebase:.allow_rebase_merge, delete:.delete_branch_on_merge}'

gh api repos/OWNER/REPO/rulesets -q '.[] | "\(.id) \(.name) \(.enforcement)"'
gh api repos/OWNER/REPO/rulesets/RULESET_ID -q '.rules'
```

Reading the ruleset back is worth doing once: the API accepts a body and stores its
own normalized version, so what you sent and what is enforced are not always the same
text.

When a ruleset has to come off for a moment, turn enforcement down rather than
deleting it, so the rules survive:

```bash
gh api -X PUT repos/OWNER/REPO/rulesets/RULESET_ID -F enforcement=disabled
gh api -X PUT repos/OWNER/REPO/rulesets/RULESET_ID -F enforcement=active
gh api -X DELETE repos/OWNER/REPO/rulesets/RULESET_ID   # only to remove it for good
```

Testing a ruleset body on a real repository is safe at `"enforcement": "disabled"`:
it is stored and readable, and it gates nothing while you check the shape.


## Bringing an existing repository up to this

Steps 4 and 5 apply unchanged to a repository that already exists. Two things to
check first, because they are the ones that bite:

```bash
gh api repos/OWNER/REPO -q .default_branch          # ~DEFAULT_BRANCH follows this
gh pr checks <number> --json name -q '.[].name'     # the real context names
```

Take the check name from a pull request that has actually run rather than from the
workflow file. What the ruleset needs is the name as reported, matrix suffixes and
all.