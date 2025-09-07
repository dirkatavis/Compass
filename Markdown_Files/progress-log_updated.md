## TODO Backlog Convention

We will capture TODOs during development using the following format:

```
# TODO[category][priority]: short action-oriented description
```

**Categories:**
- refactor — restructure existing code
- perf — improve performance
- stability — reduce flakiness / improve reliability
- feature — add new functionality
- techdebt — address known technical debt
- test — add or improve automated tests
- docs — documentation updates

**Priorities:**
- p0 — do now
- p1 — do soon
- p2 — do later

**Example:**
```
# TODO[refactor][p1]: Consolidate repeated waits into helper
```

All approved TODOs will be appended here in the **TODO Backlog** section.

---

## TODO Backlog

# Automation Progress — Aug 6

## ✅ Completed
- Login flow works (email, password, stay signed in)
- WWID entered and submitted
- MVA search confirmed via `wait_for_mva_match()`
- Work Item flow:
  - Clicks 'Add Work Item'
  - Detects existing PM Work Items and skips MVA
  - Selects existing 'PM' complaint or clicks 'Add New Complaint'

## 🔜 Next Steps
- Fill out complaint form if needed
- Save new Work Item
- Refactor with config-based timeouts and helper utilities



