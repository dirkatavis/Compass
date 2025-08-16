# AUT Structure Overview

## High-Level Flow (States)
1. **Auth** → **CompassMain** → **CompassMobileLanding** → **WWIDGate** → **MobileHome**

## Pages / Objects
- **MsAuthPage**
  - `pick_account(email)`
  - `enter_username(value)` / `enter_password(value)`
  - `confirm_stay_signed_in()`
- **CompassMainPage**
  - `go_to_compass_mobile()`
- **CompassMobileLanding**
  - `enter_wwid(wwid)`
  - `wait_for_mobile_home()`
- **MobileHome**
  - Components: `FilterBar`, `Tabs`, `WorkItemsPanel`, `ComplaintsPanel`
  - `tabs.click_work_items()`
  - `tabs.click_complaints()`
  - `filters.select_location(code)`

## Components
- **Tabs**
  - `click(name | data_tab_id)` → verifies `aria-selected="true"`
- **FilterBar**
  - `select_location(code)` with overlay wait
- **MvaSearch**
  - `type_mva(value)`
  - `wait_echo(value)`
- **ComplaintTile**
  - Fields: `state` (Open/Closed), `type`
- **WorkItemTile**
  - Fields: `state` (Open/Deferred/Completed), `type`

## Domain Models
```python
class ComplaintState(Enum):
    Open = "Open"
    Closed = "Closed"

class WorkItemState(Enum):
    Open = "Open"
    Deferred = "Deferred"
    Completed = "Completed"
```
- `Complaint { state: ComplaintState, type: str, created_at?: datetime }`
- `WorkItem { state: WorkItemState, type: str, created_at?: datetime }`

## Services
- **SessionService**
  - `ensure_logged_in(username, password)`
  - `ensure_ready(username, password, wwid)`
- **VehicleContext**
  - `set_location(code)`
  - `search_mva(mva)`
- **ComplaintService**
  - `list()` → `list[Complaint]`
  - Predicates: `has_open_of_type(type)`
- **WorkItemService**
  - `list()` → `list[WorkItem]`
  - Predicates: `has_open_of_type(type)`

## Suggested File Layout
```
pages/
  ms_auth_page.py
  compass_main_page.py
  mobile_landing_page.py
  mobile_home_page.py
components/
  tabs.py
  filter_bar.py
  mva_search.py
  complaint_tile.py
  work_item_tile.py
services/
  session_service.py
  vehicle_context.py
  complaint_service.py
  work_item_service.py
models/
  complaint.py
  work_item.py
  enums.py
```

## Example Test
```python
sess.ensure_ready(USER, PASS, WWID)
veh.set_location("GA4-A")
veh.search_mva(MVA)

if complaint_svc.has_open_of_type("PM"):
    # Action A
if workitem_svc.has_open_of_type("PM"):
    # Action B
```
