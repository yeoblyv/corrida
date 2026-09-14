# Git cheatsheet — day-to-day commands

This is the "how." For the actual rules (branch model, PR requirements,
code style, definition of done) see [CONTRIBUTING.md](../CONTRIBUTING.md)
— this page just walks through the commands.

## Who's who

| GitHub username | Name | Branch to use (`<yourname>` below) |
| --- | --- | --- |
| `@mr-hanze` | Mark Rijpstra | `mark` |
| `@mrahimof` | Marjan Rahimof | `marjan` |
| `@Danisnicee` | Daniel Chiemezie Nwadike | `daniel` |
| *(repo owner)* | Yehor Oblyvantsov | `yehor` |

Every `<yourname>` placeholder below is the branch name in the right
column — your first name, lowercase — **not** your GitHub username. For
Mark, `git push origin <yourname>` is literally `git push origin mark`,
never `git push origin mr-hanze`. GitHub usernames only matter for
logging in (`gh auth login`, or as collaborators on the repo settings
page) — they never appear in branch names, commit messages, or commands.

## 1. Authentication (once per machine)

GitHub no longer accepts your account password over HTTPS. Pick one:

- **Easiest:** install [GitHub CLI](https://cli.github.com/) and run
  `gh auth login` — follow the prompts (browser login). `git push`/`pull`
  then just work.
- **SSH keys:** if you already use SSH keys with GitHub, clone with the
  `git@github.com:...` URL instead of `https://...`.

Do this on every new machine or VM before your first clone.

## 2. First-time setup (once per machine)

Nothing about your branch or commits is tied to one machine — clone the
same repo on a lab PC, your laptop, or a fresh VM, and you're back to
exactly where you left off. This is deliberate: work in a VM, push, then
pull the same branch on a different machine and keep going, no manual
file copying, no USB sticks, no "I left it on the lab PC" problem.

```bash
git clone https://github.com/yeoblyv/corrida.git
cd corrida
git config user.name "Your Full Name"
git config user.email "your.email@used.on.github"
```

Use `git config` (no `--global`) if this identity is specific to this
repo; add `--global` if it's the only thing you use git for on that
machine. The email must match one verified on your own GitHub account,
or your commits won't be linked to your profile.

**First time ever, create your branch:**

```bash
git checkout -b <yourname>
git push -u origin <yourname>
```

**Branch already exists (you're setting up a new machine/VM):**

```bash
git fetch origin
git checkout <yourname>
```

## 3. Every time you sit down to work

Pull before you touch anything — someone (including you, on another
machine) may have pushed since you last looked.

```bash
git checkout main
git pull origin main
git checkout <yourname>
git merge main
```

`git merge main` brings `main`'s latest into your branch *now*, while
you have nothing to lose — resolving a conflict here is much easier than
discovering it later inside a pull request.

## 4. While working

```bash
git status              # see what changed
git add <file>           # stage specific files — avoid `git add .`/`-A`
git status               # check nothing unexpected got staged
git commit -m "feat(scope): what you did"
```

Commit at the end of each finished chunk of work, not once a day at
random — see [CONTRIBUTING.md §3](../CONTRIBUTING.md#3-commits) for the
message format.

## 5. Before you push

Repeat step 3 — pull `main` and merge it into your branch again if any
time has passed since you last did it. Pushing straight into a stale
branch is how avoidable conflicts happen.

## 6. Push

```bash
git push origin <yourname>
```

First push from a brand-new branch needs `-u` (see §2); after that,
plain `git push` remembers where to go, on that machine.

## 7. Open a pull request

Once your branch builds and lints clean (`./scripts/lint.sh`):

```bash
gh pr create --base main --head <yourname> --title "feat: ..." --body "..."
```

or push, then click **Compare & pull request** on
[github.com/yeoblyv/corrida](https://github.com/yeoblyv/corrida).

## 8. Working across multiple machines/VMs

Your branch lives on GitHub, not on any one machine. Standard loop on a
new VM:

```bash
gh auth login                          # once per machine, see §1
git clone https://github.com/yeoblyv/corrida.git
cd corrida
git config user.name "..."
git config user.email "..."
git checkout <yourname>                # pulls your existing branch
```

Finished a session on that VM? Always `git push` before you shut it
down or hand it back — an uncommitted or unpushed change that only
exists on a VM you don't control is a change that can vanish.

## 9. If something goes wrong

| Situation | Fix |
| --- | --- |
| Committed straight on `main` by mistake, not pushed yet | `git checkout <yourname> && git merge main` (brings the commit onto your branch), then `git checkout main && git reset --hard origin/main` (drops it from `main`). If it's already pushed to `origin/main`, stop and ask - don't force-push over shared history. |
| `git add .` staged a file you didn't mean to | `git restore --staged <file>` |
| Merge conflict after `git merge main` | Git marks the conflicting lines with `<<<<<<<`/`=======`/`>>>>>>>` in the file; edit to the correct result, remove the markers, then `git add <file>` and `git commit`. |
| "Detached HEAD" message | `git checkout <yourname>` to get back on your branch |
| Forgot which branch you're on | `git status` (first line) or `git branch --show-current` |
| Pushed, then noticed a mistake in the last commit | `git commit --amend` **only if you haven't opened a PR yet and nobody else pulled it**; otherwise a new commit that fixes it is safer |

## 10. Quick reference

| Command | What it does |
| --- | --- |
| `git status` | What's changed, staged, and which branch you're on |
| `git pull origin main` | Fetch and merge `main`'s latest into your current branch |
| `git log --oneline -10` | Last 10 commits, one line each |
| `git diff` | Unstaged changes |
| `git diff --staged` | Staged changes, about to be committed |
| `git checkout <branch>` | Switch branches |
| `git branch -a` | List all branches, local and remote |
| `git stash` / `git stash pop` | Shelve uncommitted changes temporarily, bring them back later |
