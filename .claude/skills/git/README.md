# git

Working practices for git itself, independent of what the repository contains.

Loads on its own when a repository is being created, a branch is being created, a
pull request is being opened, a conflict shows up in a file nobody edited, a pull
request's checks never run, or work begins right after a merge or a release.

- **A repository gets its settings on day one**: ask private or public first,
  because on GitHub Free a private repository cannot have rulesets or branch
  protection at all. Then squash-only merges, delete the branch on merge, and a
  ruleset requiring the CI check, added last because a required check that
  nothing reports blocks every merge forever.
- **Where a branch starts decides whether it merges**: cut from a freshly
  fetched default branch every time, including when you just merged something
  and are sure it is current. Your working copy is standing wherever the last
  task left it.
- **A squash merge makes the merged branch poison**: squashing writes a new
  commit rather than moving yours, so a branch cut from the old one collides
  with its own already-merged work. It shows up as a phantom conflict, as a
  section duplicated only in the merge result, or as checks that never start.
- **Rebase, do not merge the default branch back in**: merging records the
  duplicate as a resolution and carries it forward. Then `--force-with-lease`,
  never bare `--force`.
- **Verify mergeability before asking for review**: `MERGEABLE CLEAN` is a fact
  you can check; `UNKNOWN` just means the forge is still computing.
- **Paired branches share a name and get pushed together**: a sibling check that
  falls back to the default branch reports fake drift.
- **Reset your position the moment something merges**: back to the default
  branch, delete the merged branch, then start the next thing.
- **A secret must never reach a commit**: `.gitignore` written in the first
  commit, `.gitignore` does not untrack anything, and a committed credential
  gets rotated rather than merely deleted.
- **Use a worktree when you need two states at once**: an urgent fix over
  half-finished work, reviewing someone's branch, or a long build running while
  you keep editing.

## Adding practices

This skill is meant to grow. Each practice is self-contained: principle first,
then the commands, then the failure it prevents. Detail that would crowd the file
goes in `references/` and gets linked from its practice.

## Files

- `SKILL.md`: the skill Claude loads.