# NocoDB CRM + Multi-System Orchestration — Outline

## Problem
My company uses an internal CRM that has no API, no automation capabilities, and a 5-minute session timeout. Meanwhile I needed pipeline tracking, automated follow-ups, contact management, and integration with tools like Notion and n8n. Salesforce was overkill and expensive. I needed a lightweight, self-hosted CRM that could actually talk to other systems.

## Approach
- Deployed NocoDB as the primary CRM layer (Active Accounts, Contacts, Deals, Sales Activities tables) — self-hosted, zero licensing cost
- Built bidirectional sync between NocoDB and the internal CRM using Selenium browser automation (no API available, so I automated the browser)
- n8n workflows handle orchestration: internal CRM pull (daily), NocoDB push (poll every minute for new activities)
- Notion integration for change request tracking with automated 3-day reminder escalations
- Deduplication engine with name normalization (strips distributor tags for matching, preserves full names in storage)
- Lead approval queue with human-in-the-loop quality gates (Priority Score >= 50, ICP Score >= 40, minimum 2 decision makers)

## Result
Fully functional CRM with automated pipeline management across 4 systems at zero licensing cost. 57/57 account sync (100% coverage). Bidirectional — changes in either system propagate automatically.

## Tech Stack
NocoDB, n8n, Python, Selenium, Notion API, PostgreSQL
