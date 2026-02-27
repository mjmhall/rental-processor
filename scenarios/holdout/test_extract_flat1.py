import json
import subprocess
from pathlib import Path

SAMPLE_PDF = "samples/CCL240085 - Landlord Statement Flat 1, 6 Montpellier Spa Road 37.pdf"

def test_extract_runs_without_error():
    result = subprocess.run(
        ["python", "src/extract.py", SAMPLE_PDF],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"Extractor failed: {result.stderr}"

def test_output_file_created():
    output = Path(SAMPLE_PDF).with_suffix(".json")
    assert output.exists(), f"Expected output file {output} not found"

def load_output():
    output = Path(SAMPLE_PDF).with_suffix(".json")
    return json.loads(output.read_text())

def test_property_name():
    data = load_output()
    assert data["property_name"] == "Flat 1, 6 Montpellier Spa Road", \
        f"Expected 'Flat 1, 6 Montpellier Spa Road', got '{data['property_name']}'"

def test_opening_balance():
    data = load_output()
    assert data["opening_balance"] == 3262.20, \
        f"Expected 3262.20, got {data['opening_balance']}"

def test_closing_balance():
    data = load_output()
    assert data["closing_balance"] == 3961.40, \
        f"Expected 3961.40, got {data['closing_balance']}"

def test_transaction_count():
    data = load_output()
    assert len(data["transactions"]) == 3, \
        f"Expected 3 transactions, got {len(data['transactions'])}"

def test_income_transaction():
    data = load_output()
    income = [t for t in data["transactions"] if t["category"] == "Income"]
    assert len(income) == 1, f"Expected 1 income transaction, got {len(income)}"
    assert income[0]["gross"] == 800.00, f"Expected gross 800.00, got {income[0]['gross']}"

def test_expenditure_transactions():
    data = load_output()
    expenses = [t for t in data["transactions"] if t["category"] == "Expenditure"]
    assert len(expenses) == 2, f"Expected 2 expenditure transactions, got {len(expenses)}"

def test_no_invoice_detail_rows():
    """Invoice detail rows must not be extracted — they duplicate expenditure amounts."""
    data = load_output()
    for t in data["transactions"]:
        assert "CCL49915" not in t["description"], \
            f"Invoice detail row found: {t['description']}"
        assert "CCL49916" not in t["description"], \
            f"Invoice detail row found: {t['description']}"

def test_reconciliation():
    """Opening balance + income - expenditure must equal closing balance."""
    data = load_output()
    balance = data["opening_balance"]
    for t in data["transactions"]:
        if t["category"] == "Income":
            balance += t["gross"]
        elif t["category"] == "Expenditure":
            balance -= t["gross"]
    assert abs(balance - data["closing_balance"]) < 0.01, \
        f"Reconciliation failed: calculated {balance}, but closing balance is {data['closing_balance']}"
