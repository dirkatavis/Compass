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
[MVA] 52823864 — Status: RENTABLE, Gap: 4200, Audit: Record Missing (CREATE & COMPLETE)
[MVA] 52823864 — Status: RENTABLE, Gap: 1200 (CDK Update Required: Data Lag)
[MVA] 52823864 — Status: PM, Gap: 5000 (CDK Update Required: Status Lag)
```

## Weekly Review
- ✅ Confirm branch hygiene (main vs feature)
- ✅ Check recent commits for scope creep
- ✅ Update History.md with milestones
- ✅ Archive noisy details into Session_Log.md

## Scripting Patterns (The "Three Pillars" Standard)

### State-Matched Interaction (Assertion-Based Clicks)
Never assume a `.click()` succeeded. The script must verify the UI transition before proceeding.
1. **Action**: `click()` the target element.
2. **Verification**: `WebDriverWait` for a specific unique element or text on the *next* screen.
3. **Remediation**: If transition fails, catch the error (or empty list), log the "Silent Failure," and retry via `JavaScript` click.
4. **Stale Handling**: Always re-locate elements inside retry loops to prevent `StaleElementReferenceException`.

### Avoiding Locator Ambiguity
To ensure the script doesn't click the "wrong" object:
- **Robust Text Locators**: Prefer `//button[descendant-or-self::*[normalize-space()='Text']]`. This specifically handles PWA buttons where the text might be nested inside a `<span>`, `<p>`, or `<i>` tag, ensuring the parent button receives the actual click.
- **Scoping**: Prefix XPaths with unique container IDs or classes if multiple buttons share text (e.g., `//div[@id='complaints-tab']//button[...]`).
- **No Fall-Backs**: Never use `A or B` locators. If logic requires a choice, use `find_elements` and an `if/else` block to log exactly which state was detected.

## Chat Guidelines
- Be concise
- Prefer code diffs over full dumps
- Freeze environment during debugging (driver/browser versions)
- Add logs before changing behavior
