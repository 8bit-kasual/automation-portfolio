# POS Splitter Bot

**Category:** RPA — Channel Sales Operations
**Platform:** UiPath Studio (attended robot)
**Status:** v1 live — May 2026 EOM

---

## Problem

Every month, our distributor sends a flat Point-of-Sale export: every invoice line item for every account, with no rep assignment. Someone on the Southeast VAR team had to manually open it, look up each end-client against a side spreadsheet to figure out which rep owns them, fill in the blanks, filter five times, and save five separate workbooks. The process took an hour or more and had a consistent failure mode: client names landing in the wrong rep's stack.

## Solution

An attended UiPath robot that handles the full split in a couple of minutes:

1. **Pick up** the newest `.xlsx` from `01_Input/`
2. **Read** the POS report and the `RepMapping.xlsx` lookup table
3. **Assign** reps — adds an `Assigned Rep` column, walks every row, matches the end-client name (whitespace-trimmed) against the mapping table
4. **Split** — for each of the five reps, filter down to their rows
5. **Write** a consistently-named workbook per rep: `POS_<Rep>_<Month>.xlsx`
6. **Log** a line count per rep to the monthly run log
7. **Archive** the source file out of the input folder

## How to Run

1. Drop the distributor export (one `.xlsx`) into `01_Input/`
2. Verify `02_Mapping/RepMapping.xlsx` reflects any new clients
3. Open the project in UiPath Studio and run (or run the published package)
4. Collect per-rep workbooks from `03_Output/`

Keep the mapping file current. When a new end-client appears in the POS export, add them with their rep before the next run. Paste names directly from the POS file to avoid typos — the lookup trims whitespace but won't fix character-level differences.

## Project Layout

```
POS_Splitter_Bot/
├── 01_Input/       # drop distributor POS export here
├── 02_Mapping/     # RepMapping.xlsx — client → rep lookup
├── 03_Output/      # one workbook per rep
├── 04_Archive/     # processed source files
├── 05_Logs/        # RunLog_<Month>.txt
└── Main.xaml       # the workflow
```

## Result

- ~1 hour/month of manual EOM work eliminated
- Data-routing errors eliminated (client-in-wrong-rep's-stack)
- Primary user: Karim, Region VAR Manager

## Spec

| Field | Value |
| --- | --- |
| Tool | UiPath Studio (attended robot) |
| Language | VB.NET, Option Strict on |
| Trigger | Manual run, once per month at EOM |
| Input | One distributor POS `.xlsx` + `RepMapping.xlsx` |
| Output | 5 per-rep workbooks, run log, archived source |
| Owner / Runtime | Karim (Region VAR Manager) |
| Author | Steven Rachocki |

## Roadmap

| Version | Feature | Status |
| --- | --- | --- |
| v1.0 | Mapping-file lookup and per-rep split | Shipped |
| v2.1 | CRM / SQL-driven rep lookup — pull rep from KVS so mapping file no longer needs hand-maintaining | Planned |
| v2.2 | Outlook drafts — generate a ready-to-send email per rep with their workbook attached | Planned |
| v2.3 | Auto-run on file arrival — folder or Outlook trigger kicks off the run when the distributor file lands | Planned |
| v2.4 | Power BI rollup dashboard — region-level view for management | Planned |
