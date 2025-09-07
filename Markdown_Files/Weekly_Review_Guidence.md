# Weekly Review Checklist (Compass PWA Automation)

**When:** End of week (15–20 min)

## 1) Scope & Hygiene
- [ ] Confirm current focus branch / flow (e.g., PM work item creation).
- [ ] One-small-change rule honored? (small patch → smoke → commit)
- [ ] Test vs. page-class split respected? (helpers agnostic; orchestration in tests)

## 2) Flow Accuracy (latest working path)
- [ ] No-PM creation flow exact order is preserved:
      Add Work Item → Add/Create Complaint → Drivability=Yes → PM → Submit → Mileage Next → PM Gas → Create Work Item
- [ ] OPEN PM path: open → mark complete → Done (no duplication).
- [ ] COMPLETE PM path: 30-day rule applied (expired → create new).

## 3) Helpers & Reuse
- [ ] `create_pm_workitem(driver, mva)` is the single source for creation steps.
- [ ] UI helpers remain **agnostic** (e.g., `click_button`, `get_text`).
- [ ] Context wrappers exist (e.g., `get_create_date_workitem`); avoid inline XPath in tests.

## 4) Reliability Tweaks
- [ ] Click targets are **clickable elements** (button/tile containers), not inner text.
- [ ] Minimal timing only where needed (`sleep(0.2–0.3)`, `scrollIntoView`).
- [ ] Nil-safe call sites: `res = helper(...) or {"status":"failed","reason":"helper_returned_none"}`.

## 5) Logging & Debug
- [ ] Logs use short tags: `[LOGIN] [MVA] [WORKITEM] [COMPLAINT] [WARN] [DBG]`.
- [ ] Remove stale `input(...)` pauses and noisy debug prints.
- [ ] Keep one or two high-value `[DBG] found/clicked/selected` traces for tricky steps.

## 6) Indentation & Returns
- [ ] No dimmed “dead code” in VS Code.
- [ ] Every failure branch `return {"status":"failed","reason":"…"}`.
- [ ] Success returns **only** at the end: `{"status":"created"}` (or appropriate).

## 7) Tests & Data
- [ ] MVAs CSV still valid; at least 2–3 MVAs exercised.
- [ ] Flaky spots noted with TODOs (replace `sleep` with wait when needed).

## 8) Docs & Commits
- [ ] `KEY_TAKEAWAYS.md` updated (new learnings in Markdown).
- [ ] Commits clear & scoped (message describes exact flow and key fix).
