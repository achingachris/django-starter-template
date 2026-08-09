---
name: git
description: Working practices for git itself and the forge around it, independent of what the repository contains. Creating a repository with the settings it should have had from day one: asking private or public first, because on GitHub Free a private repository cannot have rulesets or branch protection at all, then squash-only merges, deleting the branch on merge, and a ruleset requiring the CI check, added last because a required check nothing reports blocks every merge forever. Where a branch starts and why it decides whether a pull request merges cleanly: cut every branch from a freshly fetched default branch, because a branch cut from an already-merged branch conflicts with the squash commit that replaced it, which shows up as conflicts in files nobody touched, as sections duplicated only in the merge result, and as pull requests whose checks never start. Rebasing rather than merging the default branch back in, force-with-lease, checking mergeable state before asking for review, and paired branches across sibling repositories. What must never be committed (secrets and environment files first), that .gitignore does not untrack anything, and that a committed secret gets rotated rather than merely deleted. And working in more than one branch at once with git worktree. Use whenever creating a repository or setting one up on GitHub, deciding whether a repository is private or public, configuring merge or branch-deletion settings, requiring a status check, creating a branch, opening a pull request, resolving a conflict in a file you did not edit, reacting to a pull request whose checks never ran, picking up work right after a merge or a release, initializing a repository, writing a .gitignore or .dockerignore, staging files, creating a file that holds credentials, reacting to a secret that reached a commit, or needing a second branch checked out while the first one is mid-change.
---

# Working with git

Practices for driving git and the forge around it. Nothing here is about what a
repository contains; that belongs to the language or framework skill for the
project. What belongs here is the part that goes wrong the same way in every
repository regardless of what it holds.

This skill is meant to grow. Each practice below is self-contained. Add new ones
under `## Practices`, and when one has real detail behind it, give it a file
under `references/` and link it from here.


## Practices

### Starting a repository

**Principle.** A repository gets its settings on the day it is created, not the day
someone is annoyed enough to fix them. Every one of them is a default that decides
how the rest of these practices behave.

**Ask private or public before anything else.** It is not only a visibility flag: on
GitHub Free, rulesets and branch protection are **not available on private
repositories**, and both endpoints answer `403 Upgrade to GitHub Pro or make this
repository public to enable this feature`. Squash merges and branch deletion work
either way; the required check is what the answer decides. Never leave the impression
main is gated when the plan does not allow it.

The order matters, and it is this:

1. **First commit, `.gitignore` before the first `git add`.** Retrofitting it means
   what you were keeping out is already in history. See the practice below.
2. **Create the remote** at the visibility you were told.
3. **Squash only, and delete the branch on merge.**
4. **A ruleset requiring the CI check**, last, because the check has to exist first.

```bash
git init -b main                       # .gitignore, README, LICENSE, ci.yml, commit
gh repo create OWNER/REPO --private --source=. --remote=origin --push   # or --public

gh api -X PATCH repos/OWNER/REPO \
  -F allow_squash_merge=true -F allow_merge_commit=false \
  -F allow_rebase_merge=false -F delete_branch_on_merge=true
```

Use `-F`, not `-f`: `-f` sends the string `"false"`, which is truthy, and the setting
stays on while the command reports success.

**Squash only is what the next practice assumes.** One commit per pull request on
main, branch commits replaced rather than moved. **Delete branch on merge** is what
stops a merged branch becoming the accidental base for the next one.

**The gate goes on last, and its name has to match.** A ruleset requiring a context
nothing reports blocks every merge forever: the pull request waits on a status that
can never arrive. So the starter workflow ships in the first commit, its job id is
the context the ruleset requires, and it triggers `on: pull_request`, because a
workflow that only runs on push never reports on a pull request at all.

The full sequence, the ruleset body, the plan check, and how to bring an existing
repository up to the same settings are in `references/new-repo.md`. Read it before
creating a repository rather than reconstructing the ruleset from memory.

### Where a branch starts decides whether it merges

**Principle.** Most merge conflicts are not disagreements about code. They are a
branch that started in the wrong place, and the fix is upstream of the conflict.

Before `git checkout -b`, get the default branch and update it:

```bash
git checkout main && git pull        # or: git fetch origin
git switch -c my-change origin/main  # one step, no checkout of main needed
```

Do this even when you just merged something and "know" main is current. Knowing is
the failure mode: your working copy is standing wherever the last task left it,
which after a merge or a release is the branch that was merged, not main.

**Why the previous branch is poison.** Most repositories squash on merge. Squashing
does not move your branch's commits onto main; it writes a **new** commit that
happens to contain the same lines. Your old local branch still has the original
commit, and git has no idea the two are related.

Cut a new branch from that old branch and every later comparison sees two
independent changes to the same lines. That surfaces in three ways, and only the
first looks like what it is:

| Symptom | What is actually happening |
|---|---|
| Conflict in a file you never touched, usually a changelog or a version bump | Both sides added to the same region; git cannot know they are the same edit |
| A section appears twice, and neither the branch nor main shows it twice | The duplicate exists only in the merge result, which is what CI and the merge button use |
| The pull request sits with no checks at all | The forge cannot compute a merge ref for a conflicted pull request, so `pull_request` workflows never fire |

That last one is worth internalizing. **"No checks reported" is a merge-state
symptom, not a CI outage.** Check the pull request's mergeable state before you go
looking at workflow files or the status page.

The duplicate-section case is the dangerous one, because both sides look correct
when you diff them by hand. If a cross-repository check compares files that are
byte-identical in both checkouts and still reports drift, suspect the merge ref,
not the files.

### Fix a bad base by rebasing, not by merging main back in

**Principle.** Merging main into the branch does resolve the conflict, and it
records that resolution as a merge commit that carries the duplicate forward.
Rebase instead, so the branch contains only your work, replayed on current main.

```bash
git fetch origin
git switch -c my-change-rebased origin/main
git cherry-pick <sha-of-real-work> <sha-of-followup>   # skip the stale merge/release commit
# or, when the branch is a clean run of commits on a known bad base:
git rebase --onto origin/main <old-base-sha> my-change

git push --force-with-lease origin my-change
```

Use `--force-with-lease`, never bare `--force`: it refuses if someone else pushed
in the meantime. Force-pushing your own unmerged pull request branch is normal and
expected. Force-pushing a shared or default branch is not.

After the rebase, confirm the thing that was wrong is now right. If the conflict
was a changelog, check that the released section appears exactly once.

### Verify mergeability before asking anyone to look

**Principle.** Being mergeable is a fact you can check, not a hope.

```bash
gh pr view <number> --json mergeable,mergeStateStatus -q '"\(.mergeable) \(.mergeStateStatus)"'
```

`MERGEABLE CLEAN` is what you want. `CONFLICTING DIRTY` means fix it before asking
for review. `UNKNOWN UNKNOWN` means the forge is still computing the merge; wait a
few seconds and ask again rather than reading it as a problem.

### Paired branches across sibling repositories

**Principle.** When a change spans two repositories that check each other, use the
**same branch name in both** and **push both before either one's CI runs**.

A cross-repository check typically clones the sibling's same-named branch and falls
back to its default branch when that branch does not exist yet. The fallback
compares your new work against the sibling's old state and reports it as drift,
which reads exactly like a real conflict.

If you own that check, make it log which ref it compared and warn on the fallback.
A check that says "compared against branch X" turns a confusing failure into an
obvious one.

### Reset your position the moment something merges

**Principle.** The local branch behind a merged pull request is history. Go back to
the default branch before starting anything else, and delete the merged branch so
it cannot become the accidental base for the next one.

```bash
git checkout main && git pull
git branch -d my-change
```

Make this the first thing you do after a merge, not the last thing before the next
branch. The gap between those two moments is where a bad base comes from.

### What never belongs in version control

**Principle.** The default is not "ignore what is noisy." The default is **a secret
must never reach a commit**, and everything else is housekeeping. A push is public
the moment it lands, and deleting a file in a later commit does not remove it from
history, so the cost of a mistake is not "fix the file", it is "rotate the
credential".

Write `.gitignore` **in the same commit that creates the repository**, before the
first `git add`. Retrofitting it means the thing you were trying to keep out is
already in history. When the project ships a container image, `.dockerignore` needs
the same entries: a `COPY . .` without one bakes `.env` into a readable layer.

**`.gitignore` does not untrack anything.** It governs *untracked* files. A file
git already tracks stays tracked, and its changes keep showing up, whatever the
ignore file says:

```bash
git rm --cached path/to/file      # stop tracking, keep the file on disk
```

That removal is itself a commit, and the file stays in every commit before it.

**When a secret has already been committed**, order matters and the first step is
the only one that is not optional:

1. **Rotate the credential.** Revoke it at the provider, issue a new one. Assume it
   is compromised the moment it is pushed: repositories are scraped continuously,
   forks and clones exist outside your control, and unreachable objects stay
   fetchable by SHA.
2. **Remove it from the working tree** and commit, so the current checkout is clean.
3. **Rewrite history only if it is worth it.** `git filter-repo` or BFG can purge
   the blob, but every later SHA changes and collaborators must re-clone. It is
   tidiness, not remediation.

Never let step 3 stand in for step 1. History rewriting cannot un-leak a secret; it
only makes the leak harder to see.

**Stage specific paths.** `git add -A` and `git add .` are how a stray `.env` from a
half-finished experiment gets swept in. Read `git status` first, and if something
unexpected is listed, find out what it is before staging it.

The always-ignore and never-ignore lists, plus diagnostics for "why is this file
ignored", are in `references/gitignore.md`. Paste-ready blocks per ecosystem are in
`references/gitignore-templates.md`.

### Use a worktree when you need two states at the same time

**Principle.** Stashing and branch-switching mutate the one working copy you have.
When you genuinely need two states at once, a second worktree is cheaper and safer
than juggling one: same repository, same history, separate directory, separate
checked-out branch.

```bash
git worktree add ../myrepo-review origin/main       # existing ref, detached
git worktree add -b hotfix ../myrepo-hotfix origin/main   # new branch off fresh main
git worktree list
git worktree remove ../myrepo-hotfix                # not rm -rf
git worktree prune                                  # after a manual delete
```

Reach for one when:

- **An urgent fix interrupts half-finished work.** The interrupted branch keeps its
  dirty tree; the fix gets a clean checkout cut from fresh main, which is also the
  right base (see the first practice).
- **You need to review or run someone else's branch** while yours stays as it is.
- **Something long is running.** A build, a test suite, or an agent working through
  a task can hold one worktree while you keep editing in another.
- **You are comparing two versions.** Before-and-after benchmarks, or a bisect, with
  both trees on disk at once.

What to know before you rely on it:

- **The same branch cannot be checked out in two worktrees.** Git refuses. Use a
  different branch, or a detached checkout of the ref.
- **Untracked and ignored files do not come along.** A new worktree has no
  `node_modules/`, no `.venv/`, no `.env`, and a cold build cache. For a heavy
  toolchain that setup cost can exceed the switching cost you were avoiding.
- **Remove them with `git worktree remove`.** Deleting the directory by hand leaves
  metadata behind until `git worktree prune`.
- Put worktrees **outside** the repository directory, so editors, linters and search
  do not index the same code twice.

## Reference files

- `references/new-repo.md`: creating a repository end to end: the first commit, the
  visibility question and what it decides, the merge settings, the starter workflow,
  the ruleset body, and how to verify or undo each one.
- `references/gitignore.md`: the always-ignore and never-ignore lists, and
  diagnostics for why a file is or is not ignored.
- `references/gitignore-templates.md`: paste-ready blocks: universal baseline,
  Python and Django, Node and frontend, plus the matching `.dockerignore`.
