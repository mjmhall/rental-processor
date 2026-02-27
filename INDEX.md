# Rental Statement Processor

## Project Overview
Automated pipeline that extracts rental income/expenditure transactions
from PDF statements received via Gmail and writes them to Google Sheets.

## Tech Stack
- Python 3.13
- pytest for testing
- SQLite for local state

## Conventions
- Keep INDEX.md files updated at each directory level
- Write scratch notes to notes/
- Log issues to issues/
- All errors must be logged with full context, never swallowed silently
- Use structured JSON for all intermediate data formats

## Testing
- Run all scenarios: `pytest scenarios/`
- Run training scenarios: `pytest scenarios/training/`
- Run holdout scenarios: `pytest scenarios/holdout/`

## Project Structure
- seeds/       — spec documents
- scenarios/   — test scenarios (training + holdout)
- src/         — application code
- notes/       — agent scratch notes
- issues/      — tracked problems
- docs/        — generated documentation
