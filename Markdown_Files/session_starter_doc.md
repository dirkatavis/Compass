# Compass Automation - Session Starter Brief

## Project Overview
**Goal:** Automate end-to-end Preventive Maintenance (PM) Work Item workflows in Compass Mobile PWA using Python 3.13, Selenium, and pytest.

**Core Flow:** MVA entry → detect existing PM Work Items → complete open PMs OR create new PM Work Items by associating complaints, entering mileage, selecting opcodes, and finalizing.

**Current Status:** Login, MVA validation, and work item detection working. Recently fixed invalid MVA handling with early detection.

---

## Application Under Test (Compass Mobile PWA)

### Entry & Authentication
- Access: ABG Compass portal → Microsoft Auth → "Compass Mobile" PWA
- Login: username/password → "Stay signed in" → WWID entry → Mobile home

### Core PM Workflow
1. **MVA Entry** (8-digit, normalize leading zeros) → vehicle details echo
2. **Work Items Tab** → shows PM work items (Open | Complete states)
3. **Business Rules:**
   - Open PM exists → complete it
   - Complete PM < 30 days → skip (still valid)
   - Complete PM > 30 days OR no PM → create new
4. **New PM Creation:** Add Work Item → associate PM complaint → drivability=Yes → submit → mileage=Next → opcode=PM Gas → create → complete

---

## Current Working Patterns

### Flow Control
- **Simple-first approach:** start with direct locators, add resilience only when real failures appear
- **Patch-style changes:** show only lines to replace, no full file dumps
- **Structured returns:** `{"status": "ok|failed|skipped", "reason": "...", "mva": "..."}`
- **Flow exits:** each MVA iteration ends with `continue` after success/skip

### Logging Conventions
- **Tags:** `[LOGIN] [MVA] [WORKITEM] [COMPLAINT] [WARN] [ERROR]`
- **Format:** `[TAG] {mva} - action/outcome`
- **Examples:**
  ```
  [MVA] 52823864 — invalid/unknown MVA, skipping
  [WORKITEM] 52823864 - open PM Work Item found, completing it
  [COMPLAINT][ASSOCIATED] 52823864 - complaint 'PM' selected
  ```

### Locator Patterns (grab-and-go)
```xpath
// Buttons by text
//button[.//span[normalize-space()='Submit Complaint']]
//button[.//p[normalize-space()='Next']]

// Work item tiles
//div[contains(@class,'scan-record-header')][.//div[normalize-space()='PM']]

// Complaint tiles
//div[contains(@class,'fleet-operations-pwa__complaintItem__')]
```

---

## Key Architecture

### File Structure
```
flows/          # Business logic flows
  work_item_flow.py      # Main PM work item handling
  complaints_flows.py    # Complaint association/creation
  finalize_flow.py       # Work item completion
utils/          # Helpers and utilities
  ui_helpers.py          # UI interaction primitives
  mva_helpers.py         # MVA-specific functions
pages/          # Page object models
tests/          # Test orchestration
```

### Critical Functions
- `handle_pm_workitems(driver, mva)` - main entry point
- `is_mva_known(driver, mva)` - validates MVA before processing
- `associate_existing_complaint(driver, mva)` - links PM complaints
- `navigate_back_to_home(driver)` - returns to MVA input screen

---

## Recent Changes & Current State

### Fixed Issues
- **Invalid MVA Detection:** Added `is_mva_known()` check immediately after MVA input to catch invalid MVAs early and skip cleanly
- **30-Day PM Rule:** Complete PMs expire after 30 days, triggering new PM creation
- **Flow Navigation:** Proper back-arrow navigation to home screen after skips

### Active Scenarios
- ✅ **Skip Invalid MVAs:** Early detection via vehicle properties check
- ✅ **Complete Open PMs:** Find and mark complete with "Done" note
- ✅ **Skip Recent Complete PMs:** 30-day validity window
- 🚧 **Create New PMs:** Work item creation with complaint association

### Expected Log Patterns
```bash
# Valid flows
[WORKITEM] {mva} — flow completed successfully
[MVA] {mva} — invalid/unknown MVA, skipping
[WORKITEM] {mva} — navigating back home after skip

# Issues to investigate
[WORKITEM][WARN] {mva} - any warnings
[ERROR] {mva} - any errors
```

---

## Current Focus & Next Steps

**Testing Phase:** Running batches of MVAs to identify edge cases and failure modes beyond invalid MVAs and no-complaint scenarios.

**Watch For:**
- New failure patterns in complaint association
- Timing issues with UI rendering
- Unexpected dialog states
- Navigation problems

**Working Strategy:** 
1. Feed real MVAs through automation
2. When problems occur → stop, debug, fix, commit
3. Build reliability incrementally without premature optimization