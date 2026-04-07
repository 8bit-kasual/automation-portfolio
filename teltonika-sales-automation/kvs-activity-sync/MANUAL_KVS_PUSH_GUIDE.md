# Manual KVS Push Workflow Guide

## Overview

Sales Activities created in NocoDB are no longer automatically synced to KVS. Instead, you manually trigger Claude Code to push flagged records to KVS using Selenium browser automation. This gives you control over when activities are created in KVS and ensures consistent task creation.

## Workflow Diagram

```
User (Steve)
  ↓
Talks to Claude Code about customer interactions
  ↓
Claude Code creates Sales Activity records in NocoDB
  (with "Push to KVS" checkbox = TRUE)
  ↓
User manually requests: "Push sales activities to KVS"
  ↓
Claude Code executes:
  1. Query NocoDB for all flagged Sales Activities
  2. Map each activity to KVS task format
  3. Use Selenium + create_kvs_task_final.py to create KVS tasks
  4. Capture KVS Task ID and any errors
  5. Update NocoDB records with:
     - KVS Task ID
     - KVS Sync Status ("Synced" or "Error")
     - Error message (if applicable)
     - Uncheck "Push to KVS" flag
  ↓
Activities now in KVS with full audit trail
```

## Step 1: Document Customer Interactions in Claude Code

When you have a conversation with a customer (call, email, meeting), tell Claude Code what happened:

**Example:**
```
I just called Eduardo at Citimarine. He said Matthias is interested 
in the RUTM20 for maritime applications. Wants to schedule a demo 
for next week. His email is matthias@citimarine.com.
```

**Claude Code will:**
- Create a Sales Activity record in NocoDB with your input
- Link it to the correct account and contact
- Set `Push to KVS` = TRUE (ready to sync manually)
- Document outcome, date, and any next steps

## Step 2: Request Manual Push to KVS

When you're ready to sync activities to KVS, request it directly:

**Example commands:**
```
Push all pending sales activities to KVS
Sync these activities to KVS now
Create KVS tasks from the pending activities
```

**What Claude Code will do:**
1. Query NocoDB Sales Activities table for all records with `Push to KVS = true`
2. For each record:
   - Validate required fields (Account, Date, Title, Contact if applicable)
   - Map NocoDB data to KVS task format
   - Use Selenium to open KVS Create Task form
   - Fill form fields via `create_kvs_task_final.py`
   - Submit task
   - Capture KVS Task ID from success page
3. Update each NocoDB record with:
   - `KVS Task ID` = newly created task ID
   - `KVS Sync Status` = "Synced" (success) or "Error" (failure)
   - `KVS Error Message` = detailed error if sync failed
   - `Push to KVS` = FALSE (uncheck to mark as processed)

## Step 3: Review Results

After the push completes, Claude Code will show you:

**Success Summary:**
```
✅ 3 activities synced to KVS
- Citimarine: Follow-up email (Task ID: 12345)
- L3Harris: Phone call (Task ID: 12346)
- Connectivity Warehouse: Demo scheduled (Task ID: 12347)
```

**With Errors:**
```
✅ 2 activities synced
❌ 1 activity failed:
- PRM Filtration: Email — Error: Missing required contact info
  (Action: Add contact to record, manually create task)
```

## Requirements Before Pushing

### System Requirements
- Chrome browser running with debug session: Run `start-kvs-chrome.bat` if not already running
- Logged into KVS (Chrome window at `localhost:9222`)
- Session must be alive (test by visiting https://kvs.teltonika.lt in that Chrome window)

### Data Requirements in NocoDB Sales Activities
- **Title** (required) — what the activity was about
- **Date** (required) — when it happened
- **Account** (required) — which account it relates to
- **Outcome** (required) — Positive, Neutral, Negative, No Answer, or Voicemail
- **Contact** (optional but recommended) — who you spoke with
- **Notes** (optional) — additional context

### Before Requesting Push
- [ ] Check that Chrome browser is running: `start-kvs-chrome.bat`
- [ ] Log in to KVS in that Chrome window
- [ ] Verify NocoDB Sales Activities with `Push to KVS = true` have required fields
- [ ] No ongoing KVS data entry (the script will create tasks while browser is in use)

## NocoDB Sales Activities Table Reference

**Table ID:** `ml5o8449sn55xxc`

**Key Fields:**

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| Title | Text | Yes | Activity description ("Email to Eduardo", "Call with Matthias") |
| Date | Date | Yes | When the activity occurred |
| Account | Link | Yes | Which account (from Active Accounts) |
| Contact | Link | No | Which contact person (from Contacts) |
| Outcome | Select | Yes | Positive, Neutral, Negative, No Answer, Voicemail |
| Notes | Long Text | No | Additional context for KVS task |
| Push to KVS | Checkbox | Auto | TRUE = ready to sync, FALSE = already synced |
| KVS Task ID | Text | Auto | ID of created KVS task (populated after sync) |
| KVS Sync Status | Select | Auto | Pending, Synced, or Error |
| KVS Error Message | Long Text | Auto | Error details if sync failed |
| Company Name | Lookup | Auto | Account name (lookup from Account link) |

## Common Scenarios

### Scenario 1: Simple Email Follow-up
```
Activity: "Follow-up email to Eduardo regarding Matthias introduction"
Date: 2026-04-07
Account: Citimarine LLC
Contact: [Eduardo Ripoll]
Outcome: Neutral
Notes: Checking if introduction email made it through (long Teltonika address may have been flagged)
Push to KVS: TRUE
```

→ Claude Code will create a KVS task titled "Follow-up email to Eduardo regarding Matthias introduction" with full activity details.

### Scenario 2: Phone Call with Decision Maker
```
Activity: "Call with Jorge - RUTM20 demo scheduled"
Date: 2026-04-05
Account: Citimarine LLC
Contact: [Jorge Martinez]
Outcome: Positive
Notes: Jorge agreed to demo RUTM20 for yacht application. Scheduled for April 12 at 2 PM. Send technical specs before call.
Push to KVS: TRUE
```

→ Claude Code creates KVS task. Next Planned Action: "Send technical specs and confirm demo time" is captured in Notes.

### Scenario 3: Failed Push (Missing Contact)
```
Activity: "Company research - Initial prospect outreach planning"
Date: 2026-04-07
Account: New Manufacturing Company
Contact: [Empty]  ← Problem
Outcome: Neutral
Notes: Researched company. Need to find decision maker before outreach.
Push to KVS: TRUE
```

→ Claude Code detects missing contact field. Sync fails with: "Missing required contact info"
→ Solution: Add a contact record, update NocoDB, request push again.

## Troubleshooting

### Chrome Not Running
**Error:** "Could not connect to Chrome debugging session"

**Fix:**
1. Run `start-kvs-chrome.bat`
2. Wait 5 seconds for Chrome to launch
3. Verify Chrome window opens (should have a small debug indicator)
4. Manually log in to KVS if needed
5. Request push again

### Not Logged Into KVS
**Error:** "KVS login required" or "Redirected to login page"

**Fix:**
1. Go to the Chrome window (minimize/maximize if hidden)
2. Visit https://kvs.teltonika.lt
3. Log in with your credentials
4. Return to Claude Code
5. Request push again

### Missing Required Fields
**Error:** "Missing required contact info" or "Account field is empty"

**Fix:**
1. Open NocoDB Sales Activities table
2. Find the flagged activity with error
3. Add missing field (Contact, Account, etc.)
4. Request push again

### Task Already Exists in KVS
**Error:** "Duplicate task detected" (if you push twice)

**Fix:**
- Manually delete the duplicate in KVS
- Claude Code won't auto-sync again (flag is unchecked after first sync)
- No harm done — just clean up KVS if needed

## Integration with Existing Systems

### KVS ↔ NocoDB Sync Flow (Complete)

```
KVS                          NocoDB                      Claude Code
  │                             │                              │
  │   [Daily 8 AM]              │                              │
  ├─ Indirect Sales Tasks ──────→ Deals table                  │
  │  (automated n8n)            │                              │
  │                             │                              │
  │                        Sales Activities                     │
  │                             │ (Push to KVS=true)           │
  │                             │                              │
  │                             │←─ Manual request ────────────┤
  │                             │  "Push to KVS"               │
  │←────────────────────────────┤                              │
  │  Task created by            │←─ create_kvs_task_final.py ─┤
  │  Claude Code                │                              │
  │  (Selenium + browser)       │                              │
  │                             │ ← KVS Task ID + Status ──────┤
  │                             │  (auto-update)               │
```

### No Impact on Existing Workflows
- **KVS → NocoDB** (Deals): Still automated daily at 8 AM via n8n
- **Social Media**: Unchanged
- **Lead Approval Queue**: Unchanged
- **All other n8n workflows**: Unchanged

Only **NocoDB → KVS (Sales Activities)** changed from automated polling to manual push.

## Best Practices

1. **Push regularly** — Don't let activities queue up for days. Push daily or after important calls.

2. **Review outcomes** — Make sure Outcome field accurately reflects call/email result (Positive/Neutral/Negative).

3. **Add context** — Use Notes field to capture next steps and action items for future follow-up.

4. **Check success** — Review the push summary to catch any failed syncs. Fix missing data and retry failed activities.

5. **Keep Chrome running** — Once `start-kvs-chrome.bat` is running, leave it running. You can minimize the window.

6. **Session timeout** — If Chrome closes or you restart the computer, run `start-kvs-chrome.bat` again and log in.

## Support & Documentation

- **Chrome Debugging Setup:** See `CLAUDE.md` → "KVS (Teltonika Internal CRM)"
- **create_kvs_task_final.py Issues:** See `memory/feedback_kvs_task_automation.md`
- **NocoDB Field Reference:** See `NocoDB` section in `CLAUDE.md`

---

**Last Updated:** 2026-04-07  
**Workflow Status:** Manual push (on-demand, not automated)
