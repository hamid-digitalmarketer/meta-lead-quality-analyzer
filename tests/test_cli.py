from pathlib import Path

from typer.testing import CliRunner

from meta_lead_quality_analyzer.cli import app

runner = CliRunner()


def test_cli_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "meta-lead-quality-analyzer" in result.stdout
    assert "0.1.0" in result.stdout


def test_cli_validate_lead():
    # Test valid lead
    result_valid = runner.invoke(
        app,
        ["validate-lead", "--email", "valid@company.com", "--phone", "415-322-8901", "--duration", "25.0"],
    )
    assert result_valid.exit_code == 0
    assert "PASSED" in result_valid.stdout

    # Test spam disposable lead
    result_spam = runner.invoke(
        app,
        ["validate-lead", "--email", "trash@mailinator.com", "--phone", "5555555555", "--duration", "2.0"],
    )
    assert result_spam.exit_code == 0
    assert "QUALITY ISSUES FOUND" in result_spam.stdout


def test_cli_audit(tmp_path: Path):
    result = runner.invoke(app, ["audit", "--out-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "Meta Lead Quality & Economics Summary" in result.stdout
    assert "Audit Complete!" in result.stdout

    # Verify generated files
    assert (tmp_path / "lead_quality.sqlite").exists()
    assert (tmp_path / "meta_capi_offline_events.json").exists()
    assert (tmp_path / "crm_disqualification_list.csv").exists()
    assert len(list(tmp_path.glob("audit-*.html"))) == 1
