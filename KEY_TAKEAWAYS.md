# KEY TAKEAWAYS — E2E UI TESTS (Compass)

_Last updated: {{fill when you modify}}_

## Project Goals

The goal of this project is to automate the end-to-end workflow for **Preventive Maintenance (PM) Work Items** in the Compass Mobile PWA. The automation ensures that when an MVA (vehicle number) is entered, the system checks existing Work Items and applies consistent business rules: reuse an **OPEN PM** if available, validate whether a **COMPLETE PM** is still valid within ~90 days, or otherwise create a new PM. The test flow mirrors the real user experience — entering MVAs, navigating Work Items, handling complaints, selecting op codes, and completing work — to validate that the system behaves reliably under various conditions.

Beyond validation, the automation provides a reusable framework for future Compass PWA testing. By encapsulating UI logic into page classes and centralizing helpers, the project reduces duplication and supports incremental robustness (start with simple locators/actions, hard sleeps, then evolve toward resilient waits). The ultimate aim is to build a maintainable, testable baseline for Compass Mobile that accelerates regression testing, improves confidence in releases, and enables faster iteration on business logic changes.


## Application Under Test (Compass Mobile PWA)

### Entry & Login
- Access via ABG Compass portal → Microsoft Auth (username/password, “Stay signed in”).
- Landing page: Compass → click **Compass Mobile** to enter the PWA.
- Login flow ends at **Compass Mobile home**.

### Core Workflow (Preventive Maintenance)
1. **Enter MVA** (8-digit vehicle number, normalize leading zeros).  
   - Vehicle details echoed back in vehicle pane.  
2. **Work Items Tab**  
   - Shows all Work Items for the MVA.  
   - Attributes: **Type** (e.g., PM, Tire Repair, PMSCRT), **State** (Open | Complete).  
3. **Work Item Rules**  
   - If **OPEN PM** exists → open, process, mark complete.  
   - If only **COMPLETE PM** exists → check date; if older than ~90 days, create new PM.  
   - If **no PM** → create new PM Work Item.  
4. **Add Work Item → Complaint Flow**  
   - “Is vehicle drivable?” → select **Yes**.  
   - Complaint type → click **PM** (tile auto-forwards).  
   - Complaint submit → click **Submit Complaint**.  
5. **Mileage Screen**  
   - Click **Next** (no input required).  
6. **Opcode Selection**  
   - Select **PM Gas**.  
   - Click **Create Work Item**.  
7. **Work Item Processing**  
   - Open PM record header.  
   - Click **Mark Complete**.  
   - Dialog → textarea: type `Done`.  
   - Click **Complete Work Item**.  
   - Flow ends, returning to MVA input.  

### Complaint & Work Item States
- **Complaints**: Open | Closed.  
- **Work Items**: Open | Complete.  
- Valid PM = Open, or Complete within last ~90 days.  

### UI Structure (Automation-Relevant)
- Screens are dialog-based (overlay style).  
- Buttons wrapped in `<span>` or `<p>` → locators use `normalize-space(text())`.  
- Complaint tiles auto-forward user.  
- Work Item list uses `scan-record` headers (clickable).  
- Dialog containers hold inputs + action buttons.


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

# KEY TAKEAWAYS — E2E UI TESTS (Compass)

_Last updated: 2025-08-18_

## How we work together
- **Simple-first**: start with the most direct locator & action; add resilience only if a real failure appears.
- **Patch-style answers**: when changing code, show **only the lines to replace** (no line numbers in the paste unless you ask).
- **Consistency**: prefer helpers like `click_button(...)` and only drop to raw `WebDriverWait` when the helper can’t express a case.
- **Minimal logging**: short, event–focused tags — `[LOGIN]`, `[MVA]`, `[TAB]`, `[WORKITEM]`, `[COMPLAINT]`, `[WARN]`, `[ERROR]`.

...

## Hygiene & performance
- Use a **fresh thread** for big changes; keep a link to this doc in the first message.
- Keep test data small (CSV of MVAs) and deterministic.
- Turn **debug logs on** only for investigation; default to concise logs.
- Avoid massive code pastes; prefer patch-style snippets.

## Flow exit rules
- If we **successfully finish a flow** (e.g., open/close Work Item, complete Complaint, etc.), end that loop iteration with `continue` to move cleanly to the next MVA.
- Place the `continue` **outside the if/else block** when the outcome is “done either way.”
- Only branch inside if/else when the handling diverges (e.g., warn vs. success logs).

## General information
- Use DIFF MODE + ≤20 LOC rule; no whole-file dumps.
- Paste only the exact call site we’re touching (few lines), not whole classes.
- Keep a mini step tracker so we don’t wander.


## No-PM Work Item Flow

- **Flow order locked:** Add Work Item → Add New Complaint → Drivability = Yes → PM → Submit Complaint → Mileage Next → PM Gas → Create Work Item.
- **Single source of truth:** Keep creation steps only in `create_pm_workitem(driver, mva)`; the test just calls it. No inline duplicates.
- **Success/fail pattern:**  
  `if not click_button(...): print("[WARN] …"); return {"status":"failed","reason":"…"} else: print("[OK] …")`  
  Only return success at the very end: `{"status":"created"}`.
- **Click correctness:** Target the **clickable element** (e.g., `//button[.//h1='Yes']`, tile **container** for PM Gas), not inner text nodes.
- **Simple timing aids:** tiny `sleep(0.2–0.3)` only where rendering lags; scroll to center before click.
- **Debug that matters:** add brief `[DBG] found/clicked/selected` prints at key steps; pause with `input(...)` only for temporary inspection.
- **Indentation = control flow:** dimmed code in VS Code usually meant an **unreachable success path** (fix indent so step 8 returns on success).
- **Nil-safe call site:** `res = create_pm_workitem(...) or {"status":"failed","reason":"helper_returned_none"}` to avoid `NoneType.get` crashes.
- **Commit hygiene:** Use messages that describe the **exact flow** fixed and the **return-path** correction.
