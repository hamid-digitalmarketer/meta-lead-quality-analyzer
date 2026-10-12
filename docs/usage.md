# CLI & Python API Usage Guide

`meta-lead-quality-analyzer` provides a command-line interface, local web viewer, and programmatic Python API for auditing Meta Lead Gen campaigns.

---

## Command Line Interface (CLI)

### Installation
```bash
git clone https://github.com/hamid-digitalmarketer/meta-lead-quality-analyzer.git
cd meta-lead-quality-analyzer
pip install -e ".[dev]"
```

### 1. Run Complete Quality & CPQL Audit
Audit your exported Meta Lead Ads CSV and CRM deal stages CSV:

```bash
meta-lead audit \
  --leads path/to/meta_instant_leads.csv \
  --crm path/to/crm_lead_stages.csv \
  --out-dir ./reports \
  --open-browser
```

To run with built-in realistic sample data:
```bash
meta-lead audit
```

### 2. Quick Lead Contact Validation
Verify a single lead's contact details and submission speed:

```bash
meta-lead validate-lead \
  --email "user@tempmail.com" \
  --phone "5555555555" \
  --duration 2.5
```

### 3. Launch Local Audit Web Viewer
Browse previous audit reports interactively:

```bash
meta-lead serve --port 8000 --host 127.0.0.1
```
Open `http://localhost:8000` in your web browser.

---

## Python Programmatic API

```python
from pathlib import Path
from meta_lead_quality_analyzer.data.loader import load_crm_deals, load_meta_leads
from meta_lead_quality_analyzer.analyzers import (
    DisposableEmailAnalyzer,
    PhoneValidator,
    CompletionSpeedAnalyzer,
    CRMStageMatchAnalyzer,
)
from meta_lead_quality_analyzer.report import ReportGenerator

# 1. Load lead and CRM data
leads = load_meta_leads("data/sample_data/meta_instant_leads.csv")
crm = load_crm_deals("data/sample_data/crm_lead_stages.csv")

# 2. Run diagnostic analyzers
findings = []
findings.extend(DisposableEmailAnalyzer().analyze(leads))
findings.extend(PhoneValidator().analyze(leads))
findings.extend(CompletionSpeedAnalyzer().analyze(leads))

crm_findings, total_spend, fe_cpl, qual_count, true_cpql, junk_count, junk_pct, crm_disq = (
    CRMStageMatchAnalyzer().analyze(leads, crm)
)
findings.extend(crm_findings)

print(f"Front-End CPL: ${fe_cpl:.2f} | True CPQL: ${true_cpql:.2f} | Junk Rate: {junk_pct}%")
```

---

## Generated Artifacts

- **`reports/audit-<timestamp>-<hash>.html`**: Self-contained Tailwind CSS dashboard.
- **`reports/audit-<timestamp>-<hash>.json`**: Machine-readable JSON summary.
- **`reports/audit-<timestamp>-<hash>.csv`**: Flat CSV export of all findings.
- **`reports/meta_capi_offline_events.json`**: Formatted Meta Conversions API offline conversion payload (`QualifiedLead` and `Purchase` events).
- **`reports/crm_disqualification_list.csv`**: Unviable contact list for CRM suppression.
