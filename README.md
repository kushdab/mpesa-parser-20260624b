# M-Pesa Parser 2026

A lightweight command-line utility to extract transaction data from M-Pesa PDF statements. It calculates spending summaries and can export the data to CSV for further analysis in Excel or Google Sheets.

## Features
- Parses standard M-Pesa PDF statements.
- Extracts Receipt No, Date, Details, and Amounts.
- Generates a CLI summary of income and expenses.
- Categorizes spending (Transfers, Airtime, Merchants).
- Exports to CSV.

## Installation

1. Ensure you have Python 3.8+ installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```bash
python main.py statement.pdf
```

To export to CSV:
```bash
python main.py statement.pdf --csv output.csv
```

*Note: If your PDF is encrypted, you must remove the password protection before running this tool (using tools like `qpdf` or 'Print to PDF').*