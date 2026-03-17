# Steve Rachocki — Automation & Data Portfolio

I build systems that replace manual business workflows with reliable, self-hosted automation. My background is in B2B sales for industrial IoT — I got tired of spending hours on CRM updates, morning prep, and lead research, so I built the tools to automate all of it.

These projects are production systems I built and use daily, not tutorials or demos.

---

## Featured Projects

### [Nightly Sales Prep Pipeline](./sales-prep-pipeline/)
**Problem:** 30-45 minutes every morning manually prepping for sales calls.
**Solution:** n8n workflow + Python CLI agent that pulls CRM data, detects industry niche, and generates structured call briefs with tailored discovery questions and product recommendations.
**Result:** Morning prep dropped to ~5 minutes. Every call has a personalized brief.

### [Multi-System CRM Orchestration](./nocodb-crm-orchestration/)
**Problem:** Internal CRM has no API, no automation, and a 5-minute session timeout.
**Solution:** Self-hosted NocoDB as the working CRM with bidirectional Selenium-based sync, n8n orchestration, and Notion integration for change tracking.
**Result:** 57/57 account sync (100% coverage), zero licensing cost, changes propagate within 1 minute.

### [Lead Enrichment Pipeline](./lead-enrichment-pipeline/)
**Problem:** 5+ hours/week on manual prospecting with inconsistent data quality.
**Solution:** Six-workflow n8n pipeline — Apollo discovery, Firecrawl enrichment, dual ICP/Intent scoring, Hunter.io email verification, and human-in-the-loop approval queue.
**Result:** 50+ leads per batch, zero manual data entry, ~2 minutes of daily review.

---

## Tech Stack

| Category | Tools |
| -------- | ----- |
| Workflow Automation | n8n, API integrations, webhook orchestration |
| Data & CRM | NocoDB, PostgreSQL, Supabase (pgvector), SQL |
| AI/ML | Claude, Gemini, RAG systems, vector embeddings, MCP |
| Web Scraping | Selenium, BeautifulSoup, Firecrawl |
| Infrastructure | Docker, Tailscale, self-hosted Linux environments |
| Languages | Python, SQL, JavaScript |

---

## About Me

B2B sales professional turned automation builder. I work in industrial IoT networking (cellular routers, gateways, access points) and manage a 57-account territory across the Southeast US. Every project in this portfolio started as a real problem I needed to solve for my own workflow — not a side project or tutorial exercise.

I'm particularly interested in the intersection of sales operations and automation: CRM integration, lead qualification, call preparation, and pipeline management. The systems I build are designed to be maintained by one person, run on self-hosted infrastructure, and deliver measurable time savings.

Based in Fort Worth, TX.

## Contact

- GitHub: [8bit-kasual](https://github.com/8bit-kasual)
- Email: RachockiS@outlook.com
- LinkedIn: *(coming soon)*
