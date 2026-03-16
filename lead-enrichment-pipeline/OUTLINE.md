# Lead Enrichment Pipeline — Outline

## Problem
Manual prospecting was eating 5+ hours per week with inconsistent data quality. Researching companies, finding decision makers, scoring fit, and entering data into the CRM was tedious and error-prone. Leads would sit in a spreadsheet for days before getting worked.

## Approach
- Built a 4-stage n8n pipeline:
  - Stage 1 (Discovery): Pulls company data from Apollo based on ICP criteria (industry, geography, company size)
  - Stage 2 (Enrichment): Enriches with financial data, technology stack, recent news via Firecrawl web scraping
  - Stage 3 (Contact Finding): Identifies decision makers, validates emails, scores contacts by relevance to buying committee
  - Stage 4 (Storage + RAG): Stores enriched data in Supabase with vector embeddings for semantic search across the prospect database
- Human-in-the-loop approval queue: only leads scoring above quality thresholds (Priority >= 50, ICP >= 40) enter the sales pipeline
- Rejection feedback loop: rejection reasons (Wrong Industry, Out of Territory, etc.) feed back into scoring model refinement

## Result
Batch enrichment of 50+ leads per run with zero manual data entry. Leads arrive in the CRM pre-scored, pre-enriched, with decision makers already identified. Approval queue prevents low-quality leads from cluttering the pipeline.

## Tech Stack
n8n, Apollo API, Firecrawl, Supabase (PostgreSQL + pgvector), NocoDB, HuggingFace embeddings
