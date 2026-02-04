# Compass Automation - Architecture

## Application Flow: Data Integrity Auditor
1. **MVA Entry** → Vehicle validation
2. **Gate 1 (Validation)**
   - Status == `RENTABLE` AND Buffer $\geq$ 4,000 → **Proceed**
   - Else → **Log "CDK Update Required"** and **Skip**
3. **Gate 2 (Audit)**
   - Search for PM Work Item (Recent/Current interval)
   - No Record Found → **Create & Complete** (Document Paperwork Gap)
   - Open Record Found → **Complete** (Sync status)
   - Closed Record Found → **Verified** (Do nothing)

## Diagram
```
[MVA] → [Status==RENTABLE & Buffer>=4k?]
   ├─ NO → Log "CDK Update Required" → Skip
   └─ YES → [Audit Work Items]
         ├─ None → Create & Complete → Done
         ├─ Open → Complete → Done
         └─ Closed → Done (Verified)
```

## Validation Scenarios
- **Data Lag**: RENTABLE but Buffer < 4,000 → Log Exception & Skip
- **Status Lag**: PM/PMHH but Buffer is fine → Log Exception & Skip
- **Paperwork Gap**: RENTABLE, Buffer $\geq$ 4,000, but no record → Create + Complete
- **Verified Success**: RENTABLE, Buffer $\geq$ 4,000, and closed record exists → Do nothing
- **Invalid MVA** → Skip early
- **PM complaint missing** → Add new complaint (during Create flow)

## Structure
- flows/: business logic
- pages/: page objects
- utils/: helpers (logging, UI, data)
- core/: driver + navigation
- tests/: orchestration
