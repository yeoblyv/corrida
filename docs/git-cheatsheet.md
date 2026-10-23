# Git cheatsheet

The git commands for how we work. The rules themselves (branches, pull
requests, code style) are in [CONTRIBUTING.md](../CONTRIBUTING.md).

## Who's who

| GitHub username | Name | Branch (`<yourname>` below) |
| --- | --- | --- |
| `@mr-hanze` | Mark Rijpstra | `mark` |
| `@mrahimof` | Marjan Rahimof | `Marjan` |
| `@Danisnicee` | Daniel Chiemezie Nwadike | `Daniel` |
| `@yeoblyv` | Yehor Oblyvantsov | `yehor` |

`<yourname>` in the commands below is your branch name from the table,
not your GitHub username. For Mark, `git push origin <yourname>` is
`git push origin mark`, not `git push origin mr-hanze`. The GitHub
username is only for logging in.

## 1. Log in (once per machine)

GitHub doesn't accept your account password for git over HTTPS. Pick one:

- Easiest: install the [GitHub CLI](https://cli.github.com/) and run
  `gh auth login`. After that `git push` and `git pull` just work.
- SSH keys: if you already use an SSH key with GitHub, clone with the
  `git@github.com:...` URL instead of `https://...`.

Do this on every new machine or VM before your first clone.

## 2. First-time setup (once per machine)

```bash
git clone https://github.com/yeoblyv/corrida.git
cd corrida
git config user.name "Your Full Name"
git config user.email "your.email@used.on.github"
```

The email has to be one that is verified on your GitHub account,
otherwise your commits aren't linked to your profile. Add `--global` if
you want the same name and email for every repo on that machine.

Your branch lives on GitHub, not on one machine. You can clone the repo
on a lab PC, your laptop or a VM and continue where you stopped.

If your branch doesn't exist yet:

```bash
git checkout -b <yourname>
git push -u origin <yourname>
```

If it already exists (new machine or VM):

```bash
git fetch origin
git checkout <yourname>
```

## 3. Every time you start working

Get the latest `main` first. Someone may have pushed since you last
looked.

```bash
git checkout main
git pull origin main
git checkout <yourname>
git merge main
```

It's easier to solve a conflict now than later inside a pull request.

## 4. While working

```bash
git status              # see what changed
git add <file>          # add the files you want, rather than `git add .`
git status              # check that nothing else got staged
git commit -m "feat: what you did"
```

Commit when a piece of work is done. The message format is in
[CONTRIBUTING.md](../CONTRIBUTING.md#commits).

## 5. Before you push

Do step 3 again if some time has passed, so your branch has the latest
`main`.

## 6. Push

```bash
git push origin <yourname>
```

The first push of a new branch needs `-u` (see step 2). After that plain
`git push` works on that machine.

## 7. Open a pull request

When your branch builds and `./scripts/lint.sh` passes:

```bash
gh pr create --base main --head <yourname> --title "feat: ..." --body "..."
```

Or push and click **Compare & pull request** on
[github.com/yeoblyv/corrida](https://github.com/yeoblyv/corrida).

## 8. Working on another machine or VM

```bash
gh auth login                          # once per machine, see step 1
git clone https://github.com/yeoblyv/corrida.git
cd corrida
git config user.name "..."
git config user.email "..."
git checkout <yourname>                # gets your existing branch
```

Always `git push` before you shut a VM down or give it back. A change
that only exists on that VM can get lost.

## 9. If something goes wrong

| Situation | Fix |
| --- | --- |
| Committed on `main` by mistake, not pushed yet | `git checkout <yourname> && git merge main` brings the commit onto your branch. Then `git checkout main && git reset --hard origin/main` removes it from `main`. If it's already pushed to `origin/main`, stop and ask, don't force-push. |
| `git add .` staged a file you didn't want | `git restore --staged <file>` |
| Merge conflict after `git merge main` | Git marks the conflict in the file with `<<<<<<<`, `=======` and `>>>>>>>`. Edit it to what it should be, remove the markers, then `git add <file>` and `git commit`. |
| "Detached HEAD" message | `git checkout <yourname>` gets you back on your branch |
| Forgot which branch you're on | `git status` (first line) or `git branch --show-current` |
| Pushed and then saw a mistake in the last commit | `git commit --amend` only if there is no pull request yet and nobody else pulled it. Otherwise make a new commit that fixes it. |

## 10. Quick reference

| Command | What it does |
| --- | --- |
| `git status` | What changed, what is staged and which branch you're on |
| `git pull origin main` | Fetch the latest `main` and merge it into your current branch |
| `git log --oneline -10` | Last 10 commits, one line each |
| `git diff` | Changes that aren't staged yet |
| `git diff --staged` | Staged changes, what the next commit will contain |
| `git checkout <branch>` | Switch branches |
| `git branch -a` | List all branches, local and remote |
| `git stash` / `git stash pop` | Put uncommitted changes aside and bring them back later |
