# Logging Strategy — Compass Automation Project

## 1. Purpose of Logs
- **Traceability**: every automated step should leave a breadcrumb (e.g., “clicked Next button for MVA 12345678”).
- **Diagnosability**: when something fails, logs must explain *why* (timeout, missing element, unexpected dialog).
- **Auditability**: logs should capture what the automation actually did, not just what it tried (e.g., “Work Item created” vs “Clicked create button”).

---

## 2. Log Levels and Usage
- **DEBUG** → low-level details (locators used, retries, raw exceptions).
- **INFO** → workflow events and expected outcomes (“WWID entered”, “Complaint selected”).
- **WARN** → recoverable issues (“Retrying due to stale element”).
- **ERROR** → unrecoverable conditions that end the flow.

*Team must agree early what belongs at each level to keep logs consistent and useful.*

---

## 3. Log Structure
- **Consistent prefixes**: include context like `[WORKITEM]`, `[LOGIN]`, `[COMPLAINT]`.
- **Identifiers**: always include key data (e.g., `MVA=52823864`, `login_id=E96693`).
- **Structured reason codes**: machine-readable tags for failures (`timeout_email_field`, `invalid_opcode`).

Logs should be both human-readable **and** parsable if shipped to ELK/Splunk/etc.

---

## 4. Exception Handling
- Do not allow raw Selenium exceptions to bubble up.
- Catch, log the event, and return a normalized `{status, reason}` object.
- Every log should capture:
  - the **step** (e.g., `enter_wwid`)
  - the **cause** (e.g., `TimeoutException`)
  - the **impact** (e.g., “field not found”).

---

## 5. Scope & Granularity
- **One log per action**: input, click, dialog navigation, etc.
- **Log at boundaries**: when entering or exiting major flows.
- Avoid excessive noise: don’t log every micro-poll.

---

## 6. Storage & Review
- Test runs: logs go to console and test reports.
- Optionally: write to rotating log files for later inspection.
- Define log retention policy — e.g., keep last 10 runs.

---

## 7. Documentation & Enforcement
- Document patterns (e.g., always include MVA in work item logs).
- Provide helpers (`_info`, `_dbg`, `safe_wait`) so all logs follow the same style.
- Code reviews should flag:
  - bare `print(...)`
  - missing identifiers
  - missing reason codes

---

## Example Outcomes
- **INFO**: `[WORKITEM] 52823864 — Create step started`
- **ERROR**: `[LOGIN] E96693 — timeout_email_field (10s)`
- **DEBUG**: `[DRV] locator used: //button[text()='Next']`
