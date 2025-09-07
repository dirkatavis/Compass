Start (MVA typed)
        │
        ▼
Check for PM Work Items (get_work_items)
        │
 ┌──────┴────────────────┐
 │                       │
Yes (≥1)               No (0)
 │                       │
 ▼                       ▼
process_workitem    create_new_workitem
 │                      │
 ▼                      │
   Done                 ▼
                    Complaints 
                    detected?
                        │
                ┌─────┴────────────┐
                │                  │
                Yes                 No
                │                  │
                ▼                  ▼
        associate_existing  nav_back_home
        complaint           (arrow button)
                │
                ▼
        process_workitem
                │
                ▼
                Done
