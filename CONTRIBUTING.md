# Contributing — `main` is PR-only

Every change to `main` lands through a pull request that CI has gated — **nobody pushes to `main`
directly** (not humans, not agents). This keeps concurrent agent sessions from racing each other
onto `main` and stops a broken skill suite from merging.

## How it's enforced (not GitHub branch protection)

This is a **user-owned private repo on GitHub's free plan**, where branch protection and rulesets
are unavailable (they require GitHub Pro, or a public repo). So enforcement is a committed
**pre-push hook** — run once per checkout:

```sh
sh scripts/setup-hooks.sh     # sets core.hooksPath=.githooks → blocks direct pushes to main
```

After that, `git push` to `main` is refused locally; go through a PR instead. **Every checkout /
agent session must run it** — the hook can't protect a checkout that hasn't opted in.

## The workflow

```sh
git switch -c feat/your-change
# …make the change (a skill, a field kit, a workflow)…
# run the same gates CI runs:
for t in skills/*/tests workflows/*/tests tests; do [ -d "$t" ] && python3 -m unittest discover -s "$t" -p 'test_*.py'; done
python3 skills/field-kit-generator/scripts/field_kit_generator.py lint field-kits/
git push -u origin feat/your-change
gh pr create --fill
gh pr merge --squash          # after CI (unit-tests + field-kit-lint) is green; self-merge OK
```

CI (`.github/workflows/tests.yml`) runs **`unit-tests`** + **`field-kit-lint`** on PRs that touch
`skills/**`, `field-kits/**`, or the workflow itself. Keep PRs small; title with a Conventional
Commit (`feat:`, `fix:`, `chore:`, `docs:`).
