## Summary

<!-- What changed and why. Ticket id if there is one (e.g. NV-007). -->

## Type

- [ ] Feature
- [ ] Fix
- [ ] Docs
- [ ] CI / CD
- [ ] Release (`development` → `production`)
- [ ] Chore / other

## Scope

- [ ] Diff matches this PR. No drive-by refactors, old migration edits, datasets, or generated files.
- [ ] Naming and layering follow this repo.
- [ ] Public API / DB contracts are unchanged, or the break is called out below.
- [ ] Dead code and one-off wrappers are gone.
- [ ] Tests cover new behavior, or none were needed (say why in Notes).

## Areas

Check what this PR actually changes:

- [ ] Frontend
- [ ] auth - Authentication Service
- [ ] users - Users Service
- [ ] food - Food Service
- [ ] nutrition - Nutrition Service
- [ ] meals - Meals Service
- [ ] Database / migrations
- [ ] CI / CD (GitHub Actions, Vercel, FastAPI Cloud)
- [ ] Docs / config examples

## Verification

Check what you actually ran. Unchecked means not done.

- [ ] Backend tests (`pytest`)
- [ ] Frontend lint / typecheck
- [ ] UI checked in the browser
- [ ] Preview or production deploy checked

## Release (only for `development` → `production`)

- [ ] Intended for production
- [ ] Env / CORS / secrets already set on Vercel and FastAPI Cloud, or this PR updates the docs/examples
- [ ] After merge, production app and API behave as expected

## Notes

<!-- Decisions, limitations, follow-ups, contract breaks, preview URLs. -->