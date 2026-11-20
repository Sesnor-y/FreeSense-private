# Two repositories in one folder (private notes and agents)

This working folder holds two git repositories:

- **Public code** — plain `git`, remote `Sesnor-y/FreeSense` (private until the public release, then public). Everything except the three folders below.
- **Private files** — `.claude/`, `.agents/` and `working_notes/`, tracked in `Sesnor-y/FreeSense-private` through a bare-repo overlay. The public `.gitignore` ignores all three, and `CLAUDE.md` stays public (owner decision).

The private repo's command is `git --git-dir=$HOME/.freesense-private.git --work-tree=<this folder>`; the owner's shell alias for it is `fsp`. The alias does not exist in your Bash tool, so always write the full form, with `<this folder>` the absolute path of the current project root.

## Rules

- A change under `.claude/`, `.agents/` or `working_notes/` is committed with the private command, never with plain `git`. A change anywhere else is committed with plain `git`, never with the private command.
- A **new** private file needs `add -f <path>` (the public `.gitignore` applies to the overlay too). Never `add -A`, `add .` or `commit -a` with the private command on new files: they would pull the public tree into the private repo.
- Never add `.claude/settings.local.json`, `__pycache__/` or `working_notes/repro/interactive_report/out/` (generated) to the private repo.
- The owner works on two computers (Mac primary, Linux laptop secondary). When private files change in a session, remind the owner to sync them (`fsp add -f …`, `fsp commit`, `fsp push`; `fsp pull` on the other computer) — or do it when asked. Commit or push only when the owner asks.
- Before any push, check which repository and remote the command targets. Nothing from `working_notes/`, `.claude/` or `.agents/` may ever reach `Sesnor-y/FreeSense`; `git ls-files | grep -E '^(working_notes|\.claude|\.agents)/'` must print nothing.
- **Never merge, cherry-pick or push from `Sesnor-y/FreeSense-dev`** (the archived pre-release history, cloned at `~/Documents/RATA-Flow-App` on the Mac). The histories are unrelated and the old one contains files that must not become public. Port a change by re-applying it.
- A public file (code, comment, `CHANGELOG.md`, `docs/`, `README.md`, `CLAUDE.md`) must not point readers at a file under `working_notes/`; cite a public record instead.
