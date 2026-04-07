# Manual KVS Activity Sync — NocoDB → KVS via Selenium

## Overview

Teltonika Sales Automation: Manual synchronization of customer activity records from NocoDB (cloud CRM) to KVS (internal CRM system) using Selenium browser automation.

**Workflow:**
1. User talks to Claude Code about customer interactions
2. Claude Code creates Sales Activity records in NocoDB
3. User manually triggers: "Push sales activities to KVS"
4. Claude Code executes Selenium automation to create KVS tasks
5. KVS Task IDs and sync status are captured and stored in NocoDB
6. Records are marked as synced (checkbox unchecked)

## Why Manual Push Instead of Automated?

Previous implementation used n8n workflow to automatically poll NocoDB every minute and push activities. Challenges:

- **Timing issues** — Activities pushed before user confirmation
- **No control** — User couldn't decide when to sync to KVS
- **Complex debugging** — Automated polling made troubleshooting difficult
- **Operational overhead** — Required constant workflow maintenance

**Solution:** Manual on-demand push gives users explicit control while maintaining full automation for the sync itself.

## Architecture

```
Chrome Debugging Session (Persistent)
         ↑
         │ Selenium WebDriver
         │
    push_kvs_activities.py
         │
         ├─→ Query NocoDB for flagged activities
         │
         ├─→ Validate required fields
         │
         ├─→ Map to KVS task format
         │
         ├─→ Fill KVS form via Selenium
         │
         ├─→ Capture KVS Task ID
         │
         └─→ Update NocoDB (Task ID, Sync Status, errors)
```

## Files

- **MANUAL_KVS_PUSH_GUIDE.md** — Complete user guide with examples, troubleshooting, best practices
- **push_kvs_activities.py** — Python automation script (Selenium-based)

## Quick Start

### Prerequisites

```bash
# Install dependencies
pip install selenium requests

# Set up Chrome debugging session (one-time per system)
start-kvs-chrome.bat

# Login to KVS in Chrome window
```

### Usage

```bash
# Preview activities to push (dry-run)
python push_kvs_activities.py --dry-run

# Push all flagged activities to KVS
python push_kvs_activities.py

# Process only first 5 activities (for testing)
python push_kvs_activities.py --limit 5
```

### Environment

Required environment variable:
```bash
NOCODB_API_TOKEN=<your_nocodb_api_token>
```

## Workflow Steps

### 1. User Documents Interaction in Claude Code

```
"I just called Eduardo at Citimarine. He's interested in the 
RUTM20 for maritime applications and wants a demo next week."
```

Claude Code creates Sales Activity with:
- Title: "Call with Eduardo - RUTM20 interest"
- Date: [today]
- Account: Citimarine LLC
- Contact: Eduardo Ripoll
- Outcome: Positive
- Push to KVS: ✓ TRUE

### 2. User Requests Manual Push

```
"Push sales activities to KVS"
```

### 3. Claude Code Executes

```
$ python push_kvs_activities.py
✓ Connected to Chrome (port 9222)
✓ Found 3 activities to push

[1/3] Call with Eduardo - RUTM20 interest
  ✓ Synced (Task ID: 12345)

[2/3] Email follow-up to L3Harris
  ✓ Synced (Task ID: 12346)

[3/3] Demo scheduled - Connectivity Warehouse
  ✓ Synced (Task ID: 12347)

============================================================
KVS PUSH SUMMARY
============================================================
Total activities:  3
Synced:            3 ✓
Failed:            0 ✗
============================================================
```

### 4. NocoDB Updated Automatically

For each activity:
- `Push to KVS` = ✓ FALSE (unchecked)
- `KVS Task ID` = "12345" (newly created)
- `KVS Sync Status` = "Synced" (or "Error" if failed)
- `KVS Error Message` = [error details if applicable]

## NocoDB Integration

### Sales Activities Table

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| Title | Text | Yes | Activity description |
| Date | Date | Yes | When it happened |
| Account | Link | Yes | Which customer account |
| Contact | Link | No | Who you spoke with |
| Outcome | Select | Yes | Positive, Neutral, Negative, No Answer, Voicemail |
| Notes | Long Text | No | Additional context |
| **Push to KVS** | **Checkbox** | **Auto** | **TRUE = ready to sync** |
| **KVS Task ID** | **Text** | **Auto** | **Populated after sync** |
| **KVS Sync Status** | **Select** | **Auto** | **Pending, Synced, Error** |
| **KVS Error Message** | **Long Text** | **Auto** | **Error details** |

## Chrome Session Management

### Initial Setup

```bash
# Run once per system
start-kvs-chrome.bat
```

This starts Chrome with:
- Remote debugging enabled on port 9222
- Profile stored at `C:\selenium\ChromeProfile`
- Persistent session (survives sleep/wake)

### Manual Login

Once Chrome starts, manually log into KVS:
1. Chrome window opens at `localhost:9222`
2. Visit https://kvs.teltonika.lt
3. Enter credentials
4. Session persists indefinitely

### After System Restart

1. Run `start-kvs-chrome.bat` again
2. Log in to KVS manually
3. Continue using push script

## Error Handling

### Missing Required Fields

**Error:** "Missing Title"

**Fix:** Update NocoDB record with Title field, then request push again.

### Chrome Not Running

**Error:** "Could not connect to Chrome debugging session"

**Fix:** Run `start-kvs-chrome.bat` and ensure Chrome window is open.

### Not Logged Into KVS

**Error:** "KVS login required"

**Fix:** Go to Chrome window, visit KVS, log in, then retry push.

### KVS Form Submission Timeout

**Error:** "Form submission timeout"

**Fix:** Check KVS availability, retry in a few seconds.

## API Configuration

### NocoDB

```python
NOCODB_API_URL = "http://localhost:8080/api/v2"
NOCODB_BASE_ID = "pu3kkly0sn9mdz1"
NOCODB_SALES_ACTIVITIES_TABLE_ID = "ml5o8449sn55xxc"
NOCODB_ACTIVE_ACCOUNTS_TABLE_ID = "mkn8keuazv469tf"
NOCODB_API_TOKEN = os.getenv("NOCODB_API_TOKEN")
```

### KVS

```python
KVS_CREATE_TASK_URL = "https://kvs.teltonika.lt/Tasks/Create/0?ReturnUrl=%2fTasks"
CHROME_DEBUG_PORT = 9222
```

## Integration with Existing Systems

### Unaffected Workflows

- **KVS → NocoDB (Deals)** — Still automated daily at 8 AM via n8n
- **Social Media automation** — Unchanged
- **Lead approval queue** — Unchanged
- **All other n8n workflows** — Unchanged

### Changed Workflows

- **NocoDB → KVS (Sales Activities)** — Changed from automated polling to manual push

## Best Practices

1. **Push regularly** — Don't queue activities for days; push daily or after important calls

2. **Validate data** — Ensure all required fields are filled before requesting push

3. **Review outcomes** — Set Outcome field accurately (Positive/Neutral/Negative)

4. **Check results** — Review push summary for failed activities and fix data

5. **Keep Chrome running** — Once started, leave Chrome running (minimize if needed)

6. **Add context** — Use Notes field for next steps and action items

## System Dependencies

- Python 3.8+
- Selenium WebDriver for Chrome
- requests library
- NocoDB API access
- Chrome browser (for Selenium)
- KVS access via https://kvs.teltonika.lt

## Troubleshooting

See **MANUAL_KVS_PUSH_GUIDE.md** for comprehensive troubleshooting guide with common issues, solutions, and examples.

## Implementation Details

### Script Logic

1. **Query NocoDB** — Fetch all Sales Activities with `Push to KVS = true`
2. **Validate** — Check that required fields (Title, Date, Account, Outcome) are present
3. **Connect** — Open Selenium WebDriver connection to Chrome (remote debugging)
4. **Navigate** — Go to KVS task creation form
5. **Map Data** — Convert NocoDB fields to KVS task format:
   - Title → Task title
   - Date → Task date
   - Account → Task context
   - Contact → Additional context
   - Outcome → Task notes
6. **Fill Form** — Use Selenium to populate KVS form fields
7. **Submit** — Click submit button
8. **Extract ID** — Parse KVS Task ID from response
9. **Update** — PATCH NocoDB record with:
   - KVS Task ID
   - Sync Status ("Synced" or "Error")
   - Error message (if applicable)
   - Push to KVS = FALSE
10. **Report** — Display summary with success/failure counts

### Validation Rules

- **Title** — Required, non-empty string
- **Date** — Required, valid date format (YYYY-MM-DD)
- **Account** — Required, linked to Active Accounts table
- **Outcome** — Required, one of: Positive, Neutral, Negative, No Answer, Voicemail

Activities failing validation are logged with specific error messages for user action.

## Performance

- **Per-activity time:** ~2-3 seconds (form fill + submission)
- **Batch of 5:** ~12-15 seconds total
- **Batch of 20:** ~50-60 seconds total

Script includes 1-second throttling between activities to prevent rate limiting.

## Future Enhancements

- [ ] Batch validation (pre-check all records before any KVS operations)
- [ ] Parallel processing (concurrent Selenium instances for faster sync)
- [ ] Webhook trigger (auto-push when activity meets certain criteria)
- [ ] Scheduled push (daily at specific time)
- [ ] Enhanced error recovery (retry failed activities automatically)
- [ ] Activity templates (preset task formats for common interactions)

## Author

**Created:** 2026-04-07  
**Purpose:** Replace automated n8n polling with manual on-demand KVS sync  
**Status:** Production-ready