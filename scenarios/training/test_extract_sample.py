import json
import subprocess
from pathlib import Path

SAMPLE_PDF = "samples/CCL240085 - Landlord Statement Flat 3, 6 Montpellier Spa Road 33.pdf"

def test_extract_runs_without_error():
    """Given a valid PDF, when the extractor runs, then it exits successfully."""
    result = subprocess.run(
        ["python", "src/extract.py", SAMPLE_PDF],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"Extractor failed: {result.stderr}"

def test_output_file_created():
    """Given a valid PDF, when the extractor runs, then a JSON output file is created."""
    output = Path(SAMPLE_PDF).with_suffix(".json")
    assert output.exists(), f"Expected output file {output} not found"

def load_output():
    output = Path(SAMPLE_PDF).with_suffix(".json")
    return json.loads(output.read_text())

def test_property_name():
    data = load_output()
    assert data["property_name"] == "Flat 3, 6 Montpellier Spa Road", \
        f"Expected 'Flat 3, 6 Montpellier Spa Road', got '{data['property_name']}'"

def test_opening_balance():
    data = load_output()
    assert data["opening_balance"] == 2974.32, \
        f"Expected 2974.32, got {data['opening_balance']}"

def test_closing_balance():
    data = load_output()
    assert data["closing_balance"] == 574.32, \
        f"Expected 574.32, got {data['closing_balance']}"

def test_transaction_count():
    data = load_output()
    assert len(data["transactions"]) == 1, \
        f"Expected 1 transaction, got {len(data['transactions'])}"

def test_transaction_details():
    data = load_output()
    txn = data["transactions"][0]
    assert txn["date"] == "2026-02-06", f"Expected date '2026-02-06', got '{txn['date']}'"
    assert txn["description"] == "Invoice from Top Choice: Roof leak", \
        f"Unexpected description: '{txn['description']}'"
    assert txn["net"] == 2000.00, f"Expected net 2000.00, got {txn['net']}"
    assert txn["vat"] == 400.00, f"Expected VAT 400.00, got {txn['vat']}"
    assert txn["gross"] == 2400.00, f"Expected gross 2400.00, got {txn['gross']}"
    assert txn["category"] == "Expenditure", f"Expected 'Expenditure', got '{txn['category']}'"

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

