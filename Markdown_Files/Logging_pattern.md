# 📘 Logging Level Quick Reference

## INFO
Use for **normal flow milestones** a tester/business cares about.  
✔ Flow entry/exit  
✔ Major success path actions  
✔ State changes  

**Examples:**  
- [FLOW] Starting login flow  
- [LOGIN] WWID submitted  
- [WORKITEM] 52823864 – starting CREATE NEW WORK ITEM  

---

## DEBUG
Use for **developer details** that are too noisy for normal runs.  
✔ Element locators, counts, raw values  
✔ Minor UI interactions  
✔ Internal checks  

**Examples:**  
- [DEBUG] [LOGIN] Typing email: user@domain.com  
- [DEBUG] [WORKITEMS] collected 3 item(s)  
- [DEBUG] [COMPLAINT] searching for existing PM complaint  

---

## WARN
Use for **recoverable issues** or expected-but-absent cases.  
✔ Timeouts that don’t stop the flow  
✔ Skips/optional dialogs  
✔ Missing but non-fatal UI  

**Examples:**  
- [WARN] [LOGIN] Stay signed in dialog not found  
- [WARN] [LOGIN] WWID field not found — may not be loaded  
- [WARN] [COMPLAINT] 52823864 – no complaint tiles found  

---

## E
