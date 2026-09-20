---
name: code-review
description: What to look for in a diff, by dimension. Use when reviewing a PR against its ticket. The verdict format, where the review is posted and how the commit is marked are in your AGENTS.md - this file is only the checklist.
metadata: { "openclaw": { "emoji": "🔍" } }
---

# Code review checklist

**Your AGENTS.md owns the procedure** - which PR, how to read the diff, the exact
review-file format (`APPROVED` / `CHANGES REQUESTED`, `Reviewed SHA:`, one line per
acceptance criterion, `## Blocking` then `## Non-blocking`), posting with
`gh pr review`, and `--review-status`. Nothing here overrides it.

This file is the other half: **what to actually look for**. Use the dimensions
that apply to the change in front of you. A checklist is a prompt for attention,
not a form to fill in - do not paste it into a review.

## How to read a diff

1. **Scope first.** Does the diff do what the ticket's acceptance criteria say,
   and nothing else? Work that is out of scope is a finding, even when it is good.
2. **Then correctness**, on the paths the change actually touches.
3. **Then the rest** of the dimensions below, as the change warrants.

Every finding names `file:line` and says why it matters. Separate what blocks a
merge from what is taste, and never dress up a preference as a correctness issue.
A criterion with no test is `MISSING`, not "looks fine".

## Correctness

- Edge cases: empty, zero, negative, maximum, exactly-at-limit.
- Null/undefined access; guards or optional chaining where a value is nullable.
- Off-by-one: loop bounds, slicing, pagination offsets.
- Race conditions: concurrent access to shared state uses locks, transactions or
  atomic operations.
- Timezones stored as UTC, converted at the presentation layer.
- Encoding: string operations handle multi-byte characters; encoding is explicit.
- Numeric precision: money and large numbers use a decimal/bigint type, not floats.
- Error propagation: failures from async calls and external services are caught,
  never silently swallowed.
- State consistency: multi-step mutations are transactional, so a partial failure
  leaves a valid state.

## Security

- Injection: queries are parameterised or go through an ORM; no string
  concatenation with user input. Same for shell commands and file paths.
- Output escaping where user content is rendered.
- Authentication on every protected entry point; authorization scoped to the
  requesting user (no IDOR).
- Input validation on the server: type, length, format, range - for params,
  headers, body and uploads.
- **Secrets**: no keys, tokens or passwords in source, in tests, or in fixtures.
  This project's credentials come only from the vault through the launchers.
  A token-shaped literal in a diff is always blocking.
- Sensitive data never logged, never in error messages, never in responses.
- Uploads validated for type and size, stored outside the served root.
- New dependencies: trusted, maintained, no known CVEs, and actually needed.
- Rate limiting on public and auth endpoints.

## Testing

- New logic paths have tests; critical paths have a happy path *and* a failure case.
- A bug fix includes a test that reproduces the bug.
- Tests are deterministic: no reliance on timing, real network, or shared mutable
  state, and no order dependence.
- Assertions are on behaviour, not implementation detail.
- Only external boundaries (network, DB, filesystem) are mocked.
- The test command is the project's own, from PROJECT_CONTEXT, and it exits.
  A watch-mode target is a finding: it hangs QA.

## Maintainability

- Names reveal intent; each unit does one thing.
- Duplicated logic extracted; magic values named.
- New code follows the conventions already in this codebase, not the reviewer's
  preferred ones.
- Dead code, commented-out blocks, unused imports and obsolete flags removed.
- Errors handled at a sensible boundary and logged with context.
- Dependencies point inward: core logic does not import from UI or framework layers.

## Performance

Apply what fits; a small change rarely needs all of it.

- N+1 queries: database access in a loop is batched or joined.
- Queries filter and sort on indexed columns; list endpoints paginate.
- Expensive work is cached, or moved to a background job rather than blocking a
  request.
- Resources released: listeners, subscriptions, timers, file handles, connections.
- **Web/UI changes only**: avoidable re-renders, bundle size and tree-shaking,
  lazy loading below the fold, image sizing and formats.

## Anti-patterns in the review itself

- Approving because the diff is short, or because CI is green.
- Rewriting the author's approach when theirs is sound - that is a preference.
- A wall of nits with the one blocking defect buried in the middle.
- Reviewing a head you did not read: after any new push, the SHA changed and the
  review is void. Review the new head.
