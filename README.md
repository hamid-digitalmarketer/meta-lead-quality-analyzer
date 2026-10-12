# Meta Lead Quality Analyzer 🎯📋

[![CI](https://github.com/hamid-digitalmarketer/meta-lead-quality-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/hamid-digitalmarketer/meta-lead-quality-analyzer/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)
[![Hire Me: Lead Gen Audits](https://img.shields.io/badge/Hire%20Me-Lead%20Gen%20Audits%20%26%20CAPI-2ea44f?style=flat-square&logo=googlechrome&logoColor=white)](https://abouthamid.web.app/)
[![Connect on LinkedIn](https://img.shields.io/badge/LinkedIn-Muhammad%20Hamid-0077b5?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/muhammad-hamid-digital-marketing/)
[![Direct Email](https://img.shields.io/badge/Email-mhamidlad%40gmail.com-red?style=flat-square&logo=gmail&logoColor=white)](mailto:mhamidlad@gmail.com)

> **Diagnostic and quality audit engine for Meta Lead Ads (Instant Forms) and CRM pipelines.**  
> Detects disposable burner emails, fake telephone numbers, sub-5-second speed-clickers, and computes true **Cost-Per-Qualified-Lead (CPQL)** vs vanity front-end **Cost-Per-Lead (CPL)**. Generates automated **Meta Conversions API (CAPI) offline event payloads** for value optimization and custom audience exclusion lists.

---

![Meta Lead Quality Analyzer Audit Preview](docs/report_preview.png)

---

## ⚡ The Problem: Cheap Meta Leads That Never Close

Meta Lead Ads (Instant Forms) deliver extraordinary lead volume at low apparent front-end Cost-Per-Lead ($15–$30 CPL). However, sales and revenue teams frequently encounter severe drop-off:

1. **Auto-Fill Mis-clicks & Speed Bots**: Meta pre-populates lead forms with user profile data. Users scrolling Instagram Reels tap the ad, accidentally confirm the pre-filled form, and submit in $<5$ seconds without reading the offer.
2. **Burner Disposable Emails**: Users seeking downloadable PDFs or price sheets use throwaway temporary inboxes (`@mailinator.com`, `@tempmail.com`, `@guerrillamail.com`).
3. **Fictional Phone Numbers**: Users bypass mandatory phone fields with repeated digits (`5555555555`, `1234567890`) or reserved dummy prefixes.
4. **The CPL vs. CPQL Illusion**: While marketing celebrates a $25.00 CPL, sales only qualifies 1 in 8 leads, making the true Cost-Per-Qualified-Lead (CPQL) $200.00+. Meta's algorithm continues optimizing for cheap, low-intent volume because down-funnel sales qualification signals are never fed back.

**Meta Lead Quality Analyzer** audits your lead flow, calculates real acquisition economics, and automates closed-loop feedback to train Meta's algorithms on qualified pipeline.

---

## 🚀 Key Features

- 🔍 **5 Specialized Quality Analyzers**:
  - `DisposableEmailAnalyzer`: Flags temporary inboxes, throwaway domain providers, and dummy addresses.
  - `PhoneValidator`: Detects repeated digit spam, sequential keyboard inputs, and invalid formats.
  - `CompletionSpeedAnalyzer`: Flags sub-5-second submissions indicating auto-fill mis-clicks or bot scrapers.
  - `CustomQuestionAnalyzer`: Evaluates user answers to custom qualification questions for gibberish (`asdf`, `none`, `test`).
  - `CRMStageMatchAnalyzer`: Cross-references leads against CRM deal stages (`Qualified`, `Disqualified_Bad_Info`, `Won`), calculating true CPQL and junk lead percentage.
- 🔄 **Meta CAPI Offline Event Exporter**:
  - Generates ready-to-upload JSON payloads with SHA-256 normalized user matching (`QualifiedLead`, `WonDeal`) to feed back into Meta Advantage+ value optimization.
- 📋 **CRM Disqualification & Suppression List**:
  - Exports flagged leads to CSV for bulk CRM cleanup and Meta Custom Audience negative targeting.
- 📊 **Executive & Engineering Reports**:
  - **Interactive Tailwind CSS Dashboard**: Visual cards showing CPL vs True CPQL divergence, lead quality score, and filterable finding cards.
  - **JSON & Flat CSV Exports**: Machine-readable logs for data pipelines.
  - **SQLite Database Persistence**: Full audit history stored in `reports/lead_quality.sqlite`.
- 🔒 **100% Privacy & Local Execution**: Runs locally without transmitting sensitive CRM customer data externally.

---

## 📦 Installation

```bash
git clone https://github.com/hamid-digitalmarketer/meta-lead-quality-analyzer.git
cd meta-lead-quality-analyzer

# Install package in editable mode with development tools
pip install -e ".[dev]"
```

---

## 🛠️ Quick Start

### 1. Run Audit with Built-in Datasets
Test the diagnostic engine immediately using realistic synthetic multi-campaign datasets:

```bash
meta-lead audit
```

To automatically launch the interactive HTML report in your browser:
```bash
meta-lead audit --open-browser
```

### 2. Audit Your Own Meta Leads & CRM Data
Pass your Meta Lead Ads export CSV and CRM deal stages export CSV:

```bash
meta-lead audit \
  --leads path/to/meta_instant_leads.csv \
  --crm path/to/crm_lead_stages.csv \
  --out-dir ./reports \
  --open-browser
```

### 3. Quick Single Lead Verification
Validate contact information and form completion duration:

```bash
meta-lead validate-lead --email "user@tempmail.com" --phone "5555555555" --duration 2.5
```

### 4. Serve the Web Dashboard Locally
```bash
meta-lead serve --port 8000
```
Browse your latest audit at `http://localhost:8000`.

---

## 💻 Programmatic Python API

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

# Load CSV data
leads = load_meta_leads("data/sample_data/meta_instant_leads.csv")
crm = load_crm_deals("data/sample_data/crm_lead_stages.csv")

# Run quality checks
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

## 📁 Repository Structure

```
meta-lead-quality-analyzer/
├── .github/
│   ├── ISSUE_TEMPLATE/        # Bug report and feature request templates
│   ├── workflows/ci.yml       # GitHub Actions CI matrix (Python 3.11, 3.12)
│   └── pull_request_template.md
├── data/
│   ├── loader.py              # Ingestion utilities
│   └── sample_data/           # Synthetic real-world test datasets
│       ├── meta_instant_leads.csv
│       └── crm_lead_stages.csv
├── docs/
│   ├── architecture.md        # Technical pipeline architecture
│   ├── lead_quality_guide.md  # Failure taxonomy & remediation
│   ├── usage.md               # CLI & API guide
│   └── report_preview.png     # Dashboard screenshot
├── reports/                   # Audit outputs (.html, .json, .csv, .sqlite)
├── src/meta_lead_quality_analyzer/
│   ├── analyzers/             # 5 Quality diagnostic engines
│   │   ├── disposable_email.py
│   │   ├── phone_validator.py
│   │   ├── completion_speed.py
│   │   ├── custom_question_analyzer.py
│   │   └── crm_stage_match.py
│   ├── exporters/             # CAPI offline and CRM suppression exporters
│   │   ├── meta_capi_offline.py
│   │   └── crm_disqualification_list.py
│   ├── templates/             # Jinja2 Tailwind CSS report template
│   │   └── report.html
│   ├── cli.py                 # Typer command-line interface
│   ├── models.py              # Pydantic data schemas
│   ├── report.py              # Multi-format report generator
│   └── storage.py             # SQLite persistence engine
├── tests/                     # 11 Unit and integration tests
│   ├── test_analyzers.py
│   ├── test_cli.py
│   ├── test_exporters.py
│   └── test_report.py
├── CONTRIBUTING.md            # Contributor guidelines
├── LICENSE                    # MIT License
└── pyproject.toml             # Packaging and dependency configuration
```

---

## 🧪 Testing & Quality Assurance

```bash
# Run unit tests
pytest -v

# Run linter
ruff check .

# Run static type checker
mypy src
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.

---

## 💼 Done-For-You Lead Quality Audits & Meta CAPI CRM Pipelines

> **Stop burning ad budget on tire-kickers and fake leads.** If your sales team is rejecting 50%+ of Meta form submissions, your ad campaigns are actively training Meta's algorithm to find more low-intent users.

With **7+ years as a Digital Marketing Head** scaling lead generation for BPOs, healthcare institutions, and professional services across the US, UK, and international markets, I help revenue teams align Meta Ads directly with closed-won sales revenue.

### 🎯 Available Services & Engagement Tiers

| Service Tier | Best For | What's Included | Typical Impact |
|---|---|---|---|
| **🔍 Meta Lead Fraud & Quality Audit** | Brands spending \$10k–\$100k/mo on Lead Gen | Forensic analysis of form completion speeds, burner domains, fake phone patterns, and true Cost-Per-Qualified-Lead (CPQL) by ad set | Identifies which campaigns produce sales vs vanity numbers; cuts wasted CPL spend |
| **⚙️ Turnkey CAPI Offline CRM Feedback Engine** | High-volume lead generators | Automated 2-way pipeline between your CRM (HubSpot/Salesforce/GoHighLevel) and Meta Conversions API for qualified lead & closed-won events | Trains Meta's delivery algorithm on real buyers; decreases CPQL by **30%–55%** |
| **👑 Performance Lead Gen & Growth Retainer** | Scaling B2B & service brands | Full-funnel campaign architecture, multi-step qualification forms, landing page CRO, and sales team feedback loops | Consistent, high-intent SQL volume with positive sales pipeline ROI |

---

### 🚀 Ready to Fix Your Lead Quality?

Connect with **Muhammad Hamid** to schedule an audit or discuss custom implementation:

- 🌐 **Portfolio & Case Studies**: [abouthamid.web.app](https://abouthamid.web.app/)
- 💼 **LinkedIn Profile**: [linkedin.com/in/muhammad-hamid-digital-marketing](https://www.linkedin.com/in/muhammad-hamid-digital-marketing/)
- 📩 **Direct Business Email**: [`mhamidlad@gmail.com`](mailto:mhamidlad@gmail.com)
- 📅 **Book a 1-on-1 Strategy Session**: [Schedule Discovery Call](https://abouthamid.web.app/)

<p align="center">
  <a href="https://abouthamid.web.app/"><img src="https://img.shields.io/badge/Book%20Lead%20Gen%20Audit-abouthamid.web.app-2ea44f?style=for-the-badge&logo=googlechrome&logoColor=white" alt="Book Audit"></a>
  <a href="https://www.linkedin.com/in/muhammad-hamid-digital-marketing/"><img src="https://img.shields.io/badge/LinkedIn-Muhammad%20Hamid-0077b5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"></a>
  <a href="mailto:mhamidlad@gmail.com"><img src="https://img.shields.io/badge/Email-mhamidlad%40gmail.com-red?style=for-the-badge&logo=gmail&logoColor=white" alt="Email"></a>
</p>

---

## 👤 Author & Open Source Community

Created and maintained by **Muhammad Hamid** ([@hamid-digitalmarketer](https://github.com/hamid-digitalmarketer)).  
Submit an [issue](https://github.com/hamid-digitalmarketer/meta-lead-quality-analyzer/issues) or pull request to contribute!

