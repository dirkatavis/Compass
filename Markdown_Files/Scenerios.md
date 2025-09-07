# Compass Automation — Scenario Validation

Status: ✅ = validated in test run, 🚧 = in progress, ❌ = broken/not working

---

## Work Item Scenarios

- [🚧] **Close Open PM Work Item**  
  *Flow:* detect existing Open WI → click title bar → detail dialog → Mark Complete → add note → Complete WI.  
  *Validated:* not yet.  

- [🚧] **Create New PM Work Item**  
  *Flow:* no PM WI found → Add/Create New Complaint → Drivability → Next → Opcode → Create Work Item.  
  *Validated:* not yet.  

  - [🚧] **Add an existing Complaint to a new PM Work Item**  
  *Flow:* no PM WI found → Add/Create New Complaint → Drivability → Next → Opcode → Create Work Item.  
  *Validated:* not yet.  



- [✅] **Skip Recent Complete PM Work Item**  
  *Flow:* detect Complete WI within 30 days → log skip → no new WI created.  
  *Validated:* works end-to-end.  

---

## Complaint Handling Scenarios

- [🚧] **Associate Existing Complaint**  
  *Flow:* detect complaint tile (PM or PM Hard Hold - PM) → select tile → Next.  
  *Validated:* not yet.  

- [🚧] **Create New Complaint**  
  *Flow:* no suitable complaint → click Add/Create New Complaint → Drivability Yes → Next.  
  *Validated:* not yet.  
