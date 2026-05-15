# Copilot Instructions

This repository is a GitHub Action. Follow these conventions when proposing changes.

## Versioning & releases

Use SemVer with a `v` prefix for all tags and releases.

### Tagging

- **Immutable release tags**: `vMAJOR.MINOR.PATCH` (e.g. `v1.10.0`, `v1.11.0`, `v2.0.0`). Always 3 parts, always `v`-prefixed. Never reuse or move these.
- **Moving major tag**: `vMAJOR` (e.g. `v1`) must always point to the latest release within that major version. Force-push it on every new release:
  ```
  git tag -f v1 v1.10.0
  git push origin v1 --force
  ```
- **Bump MAJOR only on breaking changes** — renaming or removing an input, changing required behavior, or anything that would break an existing consumer's workflow. Otherwise bump MINOR (new feature) or PATCH (fix).
- Do **not** create two-part tags like `v1.1` or bare-number tags like `2`. They are not valid SemVer.

### GitHub Releases

- Create a GitHub Release for **every** immutable tag (`v1.10.0`), not for the moving major tag (`v1`).
- Release `name` must match the tag name exactly (e.g. tag `v1.10.0` → release title `v1.10.0`).
- Mark the newest release as **Latest**.
- Use auto-generated release notes from PRs (Releases → Draft new release → Generate release notes), or write a short summary plus a usage snippet.

### Consumer guidance

Users should reference the action as either:
- `@v1` — auto-updates within the v1 major (recommended for most users)
- `@v1.10.0` — fully pinned (recommended for security-sensitive workflows)

## Commit messages

Use the Conventional Commits format:

- First line: `type(scope): short summary` in the present tense.
- Valid types: `feat`, `fix`, `test`, `docs`, `refactor`, `chore`, `style`, `perf`.
- Example: `feat(action): support custom gallery URL`
- Keep the first line under 72 characters.
- Leave the second line blank.
- From the third line, add a more detailed description explaining the reason for the change. Use bullet points for multiple points.
