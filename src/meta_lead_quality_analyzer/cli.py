import datetime
import hashlib
import sys
import webbrowser
from pathlib import Path
from typing import List, Optional

import typer
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from meta_lead_quality_analyzer.analyzers import (
    CompletionSpeedAnalyzer,
    CRMStageMatchAnalyzer,
    CustomQuestionAnalyzer,
    DisposableEmailAnalyzer,
    PhoneValidator,
)
from meta_lead_quality_analyzer.data.loader import load_crm_deals, load_meta_leads
from meta_lead_quality_analyzer.exporters import (
    CRMDisqualificationExporter,
    MetaCAPIOfflineExporter,
)
from meta_lead_quality_analyzer.models import (
    LeadAuditResult,
    LeadQualitySummary,
    MetaLeadRow,
    QualityFinding,
    Severity,
)
from meta_lead_quality_analyzer.report import ReportGenerator
from meta_lead_quality_analyzer.storage import SQLiteStorage

app = typer.Typer(
    name="meta-lead",
    help="Meta Lead Quality Analyzer: Lead Ads & CRM Attribution Diagnostic Health Engine.",
)
console = Console()


@app.command()
def audit(
    leads: Optional[Path] = typer.Option(
        None,
        "--leads",
        "-l",
        help="Path to Meta Instant Form Leads CSV export. Uses built-in sample data if omitted.",
    ),
    crm: Optional[Path] = typer.Option(
        None,
        "--crm",
        "-c",
        help="Path to CRM Deal / Stage CSV export. Uses built-in sample data if omitted.",
    ),
    out_dir: Path = typer.Option(
        Path("reports"),
        "--out-dir",
        "--output-dir",
        "-o",
        help="Directory to save audit reports and CAPI exports.",
    ),
    open_browser: bool = typer.Option(
        False,
        "--open-browser",
        help="Automatically open the interactive HTML audit report in default browser.",
    ),
) -> None:
    """Run an end-to-end lead quality and CPQL audit against Meta Instant Leads and CRM logs."""
    console.print(
        Panel.fit(
            "[bold cyan]Meta Lead Quality Analyzer[/bold cyan]\n"
            "[dim]Cross-referencing Meta Instant Form leads with CRM revenue stages...[/dim]",
            border_style="cyan",
        )
    )

    package_data_dir = Path(__file__).parent / "data" / "sample_data"
    root_data_dir = Path(__file__).resolve().parent.parent.parent / "data" / "sample_data"
    sample_dir = package_data_dir if package_data_dir.exists() else root_data_dir

    if leads is None:
        leads = sample_dir / "meta_instant_leads.csv"
        console.print("[yellow]Notice:[/yellow] No leads file provided. Using built-in sample dataset.")

    if crm is None:
        crm = sample_dir / "crm_lead_stages.csv"
        console.print("[yellow]Notice:[/yellow] No CRM file provided. Using built-in sample dataset.")

    if not leads.exists():
        console.print(f"[bold red]Error:[/bold red] File not found: {leads}")
        sys.exit(1)

    lead_rows = load_meta_leads(leads)
    crm_rows = load_crm_deals(crm) if crm.exists() else []

    all_findings: List[QualityFinding] = []

    # Run Analyzers
    with console.status("[bold green]Evaluating lead quality indicators..."):
        email_findings = DisposableEmailAnalyzer().analyze(lead_rows)
        phone_findings = PhoneValidator().analyze(lead_rows)
        speed_findings = CompletionSpeedAnalyzer().analyze(lead_rows)
        custom_findings = CustomQuestionAnalyzer().analyze(lead_rows)

        crm_findings, total_spend, fe_cpl, qual_count, true_cpql, junk_count, junk_pct, crm_disq_count = (
            CRMStageMatchAnalyzer().analyze(lead_rows, crm_rows)
        )

        all_findings.extend(email_findings)
        all_findings.extend(phone_findings)
        all_findings.extend(speed_findings)
        all_findings.extend(custom_findings)
        all_findings.extend(crm_findings)

    # Sort findings by severity
    severity_order = {
        Severity.CRITICAL: 0,
        Severity.HIGH: 1,
        Severity.MEDIUM: 2,
        Severity.LOW: 3,
        Severity.INFO: 4,
    }
    all_findings.sort(key=lambda f: severity_order[f.severity])

    summary = LeadQualitySummary(
        total_leads_audited=len(lead_rows),
        total_ad_spend=total_spend,
        front_end_cpl=fe_cpl,
        qualified_leads_count=qual_count,
        true_cpql=true_cpql,
        junk_lead_count=junk_count,
        junk_lead_rate_pct=junk_pct,
        disposable_email_count=len(email_findings),
        invalid_phone_count=len(phone_findings),
        speed_clicker_count=len(speed_findings),
        crm_disqualified_count=crm_disq_count,
    )

    audit_timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")
    audit_hash = hashlib.md5(f"{audit_timestamp}-{len(all_findings)}".encode()).hexdigest()[:6]
    audit_id = f"{audit_timestamp}-{audit_hash}"

    audit_result = LeadAuditResult(
        audit_id=audit_id,
        created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        summary=summary,
        findings=all_findings,
    )

    # Save to SQLite and export reports
    storage = SQLiteStorage(out_dir / "lead_quality.sqlite")
    storage.save_audit(audit_result)

    reporter = ReportGenerator(output_dir=out_dir)
    report_paths = reporter.generate_all(audit_result)

    # Export CAPI Offline & CRM Disqualification lists
    capi_path = MetaCAPIOfflineExporter(out_dir).export(lead_rows, crm_rows)
    disq_path = CRMDisqualificationExporter(out_dir).export(all_findings)

    # Display KPI Table
    kpi_table = Table(title="Meta Lead Quality & Economics Summary", border_style="blue")
    kpi_table.add_column("Metric", style="bold")
    kpi_table.add_column("Value", style="cyan")

    kpi_table.add_row("Total Leads Audited", str(len(lead_rows)))
    kpi_table.add_row("Total Ad Spend", f"${total_spend:,.2f}")
    kpi_table.add_row("Front-End Cost Per Lead (CPL)", f"${fe_cpl:.2f}")
    kpi_table.add_row("True Cost Per Qualified Lead (CPQL)", f"[bold red]${true_cpql:.2f}[/bold red]")
    kpi_table.add_row("Qualified Sales Leads", f"[bold green]{qual_count}[/bold green]")
    kpi_table.add_row("Junk / Unqualified Lead Rate", f"[bold red]{junk_pct}%[/bold red]")
    kpi_table.add_row("Disposable / Spam Emails", f"{len(email_findings)}")
    kpi_table.add_row("Invalid / Fake Phone Numbers", f"{len(phone_findings)}")
    kpi_table.add_row("Sub-5s Speed Clickers / Bots", f"{len(speed_findings)}")
    console.print(kpi_table)

    # Display Findings Table
    findings_table = Table(title="Detected Lead Quality Issues", border_style="cyan")
    findings_table.add_column("Severity", style="bold")
    findings_table.add_column("Lead ID", style="dim")
    findings_table.add_column("Category")
    findings_table.add_column("Issue Title")

    for f in all_findings[:15]:
        sev_color = {
            Severity.CRITICAL: "red",
            Severity.HIGH: "yellow",
            Severity.MEDIUM: "blue",
            Severity.LOW: "white",
            Severity.INFO: "dim",
        }.get(f.severity, "white")

        findings_table.add_row(
            f"[{sev_color}]{f.severity.value}[/{sev_color}]",
            f.lead_id,
            f.category.value,
            f.title,
        )

    console.print(findings_table)

    console.print(
        Panel.fit(
            f"[bold green]Audit Complete![/bold green]\n\n"
            f"- Interactive HTML Report: [cyan]{report_paths['html']}[/cyan]\n"
            f"- Machine-readable JSON:  [dim]{report_paths['json']}[/dim]\n"
            f"- Flat CSV Findings:      [dim]{report_paths['csv']}[/dim]\n"
            f"- Meta CAPI Offline JSON: [dim]{capi_path}[/dim]\n"
            f"- CRM Disqualification:   [dim]{disq_path}[/dim]",
            border_style="green",
        )
    )

    if open_browser:
        webbrowser.open(report_paths["html"].resolve().as_uri())


@app.command()
def validate_lead(
    email: str = typer.Option(..., "--email", "-e", help="Lead email to validate"),
    phone: str = typer.Option(..., "--phone", "-p", help="Lead telephone number to validate"),
    duration: float = typer.Option(10.0, "--duration", "-d", help="Form completion duration in seconds"),
) -> None:
    """Validate a single lead's contact info and completion duration."""
    dummy_lead = MetaLeadRow(
        lead_id="test_lead",
        created_time=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        campaign_name="Manual Test",
        ad_name="Manual Test Ad",
        form_name="Manual Test Form",
        full_name="Test Subject",
        email=email,
        phone_number=phone,
        completion_time_sec=duration,
    )

    findings = []
    findings.extend(DisposableEmailAnalyzer().analyze([dummy_lead]))
    findings.extend(PhoneValidator().analyze([dummy_lead]))
    findings.extend(CompletionSpeedAnalyzer().analyze([dummy_lead]))

    if not findings:
        console.print("[bold green]PASSED:[/bold green] Contact info passed all spam and disposable checks.")
    else:
        console.print(f"[bold red]QUALITY ISSUES FOUND ({len(findings)}):[/bold red]")
        for f in findings:
            console.print(f"  - [{f.severity.value}] {f.title}")
            console.print(f"    Detail: {f.metric_detail}")
            console.print(f"    Action: {f.recommended_action}\n")


@app.command()
def serve(
    db_path: Path = typer.Option(
        Path("reports/lead_quality.sqlite"),
        "--db-path",
        help="Path to SQLite audit database.",
    ),
    port: int = typer.Option(8000, "--port", "-p", help="Port to run web server on."),
    host: str = typer.Option("127.0.0.1", "--host", help="Host interface."),
) -> None:
    """Launch local web server to browse the latest lead quality audit report."""
    server_app = FastAPI(title="Meta Lead Quality Analyzer Web Viewer")

    @server_app.get("/", response_class=HTMLResponse)
    def index() -> str:
        storage = SQLiteStorage(db_path)
        audit = storage.get_latest_audit()
        if not audit:
            raise HTTPException(
                status_code=404,
                detail="No audit found in database. Run 'meta-lead audit' first.",
            )
        template_dir = Path(__file__).parent / "templates"
        from jinja2 import Environment, FileSystemLoader
        env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)
        return env.get_template("report.html").render(audit=audit)

    console.print(f"[bold green]Starting viewer on http://{host}:{port}...[/bold green]")
    uvicorn.run(server_app, host=host, port=port)


@app.command()
def version() -> None:
    """Display current version of Meta Lead Quality Analyzer."""
    console.print("[bold cyan]meta-lead-quality-analyzer[/bold cyan] version [bold white]0.1.0[/bold white]")


if __name__ == "__main__":
    app()
