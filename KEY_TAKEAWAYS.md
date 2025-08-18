# KEY TAKEAWAYS — E2E UI TESTS (Compass)

_Last updated: {{fill when you modify}}_

## How we work together
- **Simple-first**: start with the most direct locator & action; add resilience only if a real failure appears.
- **Patch-style answers**: when changing code, show **only the lines to replace** (no line numbers in the paste unless you ask).
- **Consistency**: prefer helpers like `click_button(...)` and only drop to raw `WebDriverWait` when the helper can’t express a case.
- **Minimal logging**: short, event–focused tags — `[LOGIN]`, `[MVA]`, `[TAB]`, `[WORKITEM]`, `[COMPLAINT]`, `[WARN]`, `[ERROR]`.

## Current happy-path flow (short)
1. Login → verify Compass home.
2. Enter **MVA** (handle leading zeros) → confirm echo on vehicle details.
3. Open **Work Items** tab.
4. If **no OPEN PM** → click **Add Work Item** and create one.
5. **Add Complaint** → `Is vehicle drivable?` → **Yes**.
6. Complaint type → **PM**.
7. **Submit Complaint** → **Next**.
8. Select op code → **PM Gas** → **Create Work Item**.
9. In the list, click the **record header** for the opened PM.
10. Click **Mark Complete**.
11. Dialog → textarea: type `Done` → **Complete Work Item**.

## Locator snippets (grab-and-go)
- Buttons by text (robust):  
  ```xpath
  //button[.//span[normalize-space()='Submit Complaint'] or normalize-space()='Submit Complaint']
  //button[.//p[normalize-space()='Next']]
  //button[.//span[normalize-space()='Create Work Item']]
  //button[.//div[normalize-space()='Mark Complete']]
  ```
- Op code tile (PM Gas):  
  ```xpath
  //*[contains(@class,'opCodeText')][normalize-space()='PM Gas']
  ```
- Work item record header (PM row):  
  ```xpath
  //div[contains(@class,'scan-record')]
      [ .//div[contains(@class,'scan-record-header-title')][normalize-space()='PM'] ]
  ```
- Dialog textarea + submit:  
  ```xpath
  //div[contains(@class,'dialog-container')]//textarea
  //div[contains(@class,'dialog-container')]//button[.//span[normalize-space()='Complete Work Item']]
  ```

## Wait & click pattern (simple-first)
```python
el = WebDriverWait(driver, 8).until(
    EC.element_to_be_clickable((By.XPATH, XPATH))
)
driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
el.click()
```
Fallbacks (only if needed): `JS click`, `presence_of_element_located` → small sleep → click.

## Common pitfalls we already hit (and fixes)
- **MVA echo mismatch** due to leading zeros → compare last 8 or normalize with `zfill`.  
- **“Not found” yet visible** → element inside a scrolling container → `scrollIntoView({block:'center'})` before `click()`.
- **Empty Work Items** but UI shows tiles → broaden tile selector (`.bp6-card` + text heuristics).  
- **Overengineering** → resist adding retries/abstractions until a real flake shows up.

## Logging conventions
Examples:
```
[LOGIN] Auth confirmed — session ready.
[MVA] start → 52823864
[TAB] Work Items tab clicked and verified as active
[WORKITEM] No OPEN PM — creating one
[COMPLAINT] Op code 'PM Gas' selected
[COMPLAINT][WARN] Mark Complete not found (TimeoutException); continuing
```
Keep messages short; prefer one log per meaningful user action.

## Hygiene & performance
- Use a **fresh thread** for big changes; keep a link to this doc in the first message.
- Keep test data small (CSV of MVAs) and deterministic.
- Turn **debug logs on** only for investigation; default to concise logs.
- Avoid massive code pastes; prefer patch-style snippets.

## Quick checklist before running
- Desktop (not mobile emulation); correct env/creds loaded.
- CSV path valid; first MVA known-good.
- Driver ready; no stale session in background.


## General information
- Use DIFF MODE + ≤20 LOC rule; no whole-file dumps.
- Paste only the exact call site we’re touching (few lines), not whole classes.
- Keep a mini step tracker so we don’t wander.