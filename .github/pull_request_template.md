## Ticket

NV-___: <ticket title>

## Self-review

- [ ] Diff matches the ticket scope. No drive-by changes, unrelated refactors, old migration edits, datasets, rules, or generated files.
- [ ] Naming, structure, and layering follow repository conventions.
- [ ] Existing API/data contracts are unchanged unless intentionally modified by this ticket.
- [ ] Dead code, unused imports, duplicate logic, and unnecessary abstractions are removed.
- [ ] Tests cover the changed behavior and existing tests pass.
- [ ] UI changes were verified in the browser, or the limitation is documented below.
- [ ] Database changes include the required migration; historical migrations were not modified unnecessarily.

## Services touched

Check only what this PR changes:

- [ ] **auth**
- [ ] **users**
- [ ] **food**
- [ ] **nutrition**
- [ ] **meals**
- [ ] **frontend**

## Verification

- Backend: `________`
- Frontend: `________`
- Database / migration: `________`
- Manual / browser: `________`

## Notes

<!--
Mention important implementation decisions, known limitations,
deferred work, or anything reviewers should specifically check.
-->