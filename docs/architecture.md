# Meta Lead Quality Analyzer - Technical Architecture

`meta-lead-quality-analyzer` provides a unified diagnostic pipeline connecting Meta Instant Forms with CRM sales stages to compute accurate Cost-Per-Qualified-Lead (CPQL) metrics and automate CAPI offline value optimization.

---

## 1. Pipeline Flow

```mermaid
flowchart TD
    subgraph Ingestion ["Data Ingestion"]
        L1["Meta Lead Ads CSV<br/>(Instant Form Submissions)"] --> LD["data/loader.py"]
        L2["CRM Deals CSV<br/>(Opportunity Stages & Values)"] --> LD
    end

    subgraph Evaluation ["Quality & Spam Analyzers"]
        LD --> A1["DisposableEmailAnalyzer<br/>(Burner Domains & Dummy Patterns)"]
        LD --> A2["PhoneValidator<br/>(Repeated/Sequential Digits, Fake Area Codes)"]
        LD --> A3["CompletionSpeedAnalyzer<br/>(Sub-5s Bot / Accidental Auto-fill)"]
        LD --> A4["CustomQuestionAnalyzer<br/>(Gibberish / Single-Char Input)"]
        LD --> A5["CRMStageMatchAnalyzer<br/>(Qualified vs Disqualified, True CPQL)"]
    end

    subgraph StorageEngine ["Persistence & Summary"]
        A1 & A2 & A3 & A4 & A5 --> RES["LeadAuditResult & LeadQualitySummary"]
        RES --> SQL["SQLite Storage<br/>(reports/lead_quality.sqlite)"]
    end

    subgraph Deliverables ["Artifacts & Platform Exporters"]
        RES --> REP1["Tailwind CSS Audit Dashboard (.html)"]
        RES --> REP2["Machine JSON & Flat CSV Summary"]
        RES --> EXP1["Meta CAPI Offline Events (.json)<br/>(QualifiedLead & Value Signals)"]
        RES --> EXP2["CRM Disqualification Exclusion (.csv)<br/>(Sales Suppression List)"]
    end
```

---

## 2. Core Economic Metric Formulas

### Front-End Cost Per Lead (CPL)
$$\text{Front-End CPL} = \frac{\sum \text{Meta Ad Spend}}{\text{Total Raw Leads}}$$

### True Cost Per Qualified Lead (CPQL)
$$\text{True CPQL} = \frac{\sum \text{Meta Ad Spend}}{\text{Total Sales-Qualified Leads}}$$

### Junk Lead Rate
$$\text{Junk Rate} = \frac{\text{Total Disqualified Leads (Spam Email, Fake Phone, Bot Speed)}}{\text{Total Leads}} \times 100\%$$
