# Compass Automation - Practices

## Logging Strategy
- **Levels**: DEBUG (verbose), INFO (normal), WARN (unexpected but handled), ERROR (failures)
- **Tags**: [LOGIN], [MVA], [WORKITEM], [COMPLAINT], [WARN], [ERROR]
- **Format**: [TAG] {mva} - action/outcome

### Examples
```
[MVA] 52823864 — invalid MVA, skipping
[WORKITEM] 52823864 — open PM found, completing
[COMPLAINT][ASSOCIATED] 52823864 — complaint 'PM' selected
```

## Weekly Review
- ✅ Confirm branch hygiene (main vs feature)
- ✅ Check recent commits for scope creep
- ✅ Update History.md with milestones
- ✅ Archive noisy details into Session_Log.md

## Chat Guidelines
- Be concise
- Prefer code diffs over full dumps
- Freeze environment during debugging (driver/browser versions)
- Add logs before changing behavior
