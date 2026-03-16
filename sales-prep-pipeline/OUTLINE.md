# Nightly Sales Prep Pipeline — Outline

## Problem
As a B2B sales rep managing 50+ industrial IoT accounts, I was spending 30-45 minutes every morning manually pulling CRM data, checking last contact dates, reviewing account notes, and figuring out who to call and what to say. That's 3+ hours/week of prep that doesn't generate revenue.

## Approach
- Built an n8n workflow that triggers daily, queries NocoDB for accounts due for follow-up (based on Next Planned Action Date and Priority Score)
- Python-based call prep agent enriches each account with contact context, niche-specific intelligence, and product recommendations
- Generates structured call briefs: opener, discovery questions tailored to industry vertical, objection handling, and specific close (sample offer)
- Post-call workflow updates CRM with outcome, creates sales activity record, and syncs back to internal CRM automatically within 1 minute
- Niche detection engine classifies accounts (Automotive, Food & Bev, Manufacturing, MSP/Integrator) and tailors questions + product recs

## Result
Morning prep dropped from 45 minutes to ~5 minutes. Call quality improved — every call now has personalized discovery questions and product recommendations based on the prospect's industry vertical.

## Tech Stack
n8n, Python, NocoDB API, Claude AI (LLM), Selenium
