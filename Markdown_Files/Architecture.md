# Compass Automation - Architecture

## Application Flow
1. **MVA Entry** → Vehicle validation
2. **Work Items Tab** → Detect existing PM Work Items (Open | Complete)
3. **Rules**
   - Open PM → Complete it
   - Complete PM < 30 days → Skip
   - Complete PM > 30 days OR none → Create new
4. **New PM Flow**
   - Add Work Item → Associate complaint → Drivability=Yes → Mileage → Opcode=PM Gas → Create → Complete

## Diagram
```
[MVA] → [Work Items?]
   ├─ Open PM → Complete → Done
   ├─ Complete <30 days → Skip
   └─ Else → New Work Item → Complaint → Mileage → Opcode → Complete
```

## Validation Scenarios
- Invalid MVA → Skip early
- Open PM present → Complete
- Only closed PM >30 days → Create new
- PM complaint missing → Add new complaint

## Structure
- flows/: business logic
- pages/: page objects
- utils/: helpers (logging, UI, data)
- core/: driver + navigation
- tests/: orchestration
