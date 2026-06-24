import argparse
import pdfplumber
import csv
import os
import sys
from collections import defaultdict

def clean_currency(val):
    """Cleans currency string and converts to float."""
    if not val or not isinstance(val, str) or val.strip() in ["", "-"]:
        return 0.0
    try:
        return float(val.replace(',', '').replace(' ', '').strip())
    except ValueError:
        return 0.0

def parse_mpesa_pdf(pdf_path):
    """Extracts transaction data from M-Pesa PDF statement tables."""
    transactions = []
    print(f"[*] Reading {pdf_path}...")
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if not table:
                    continue
                
                for row in table:
                    # Skip headers or short rows
                    if not row or "Receipt No" in str(row[0]) or "Completion Time" in str(row[1]):
                        continue
                    
                    # M-Pesa Format: Receipt No, Completion Time, Details, Status, Paid In, Paid Out, Balance
                    if len(row) >= 6:
                        transactions.append({
                            'receipt': row[0],
                            'date': row[1],
                            'details': row[2].replace('\n', ' ') if row[2] else "",
                            'status': row[3],
                            'paid_in': clean_currency(row[4]),
                            'paid_out': clean_currency(row[5])
                        })
    except Exception as e:
        print(f"[!] Failed to parse PDF: {e}")
        sys.exit(1)
    
    return transactions

def generate_summary(transactions, output_csv):
    """Calculates totals and exports to CSV if requested."""
    total_in = 0.0
    total_out = 0.0
    categories = defaultdict(float)

    if output_csv:
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['receipt', 'date', 'details', 'status', 'paid_in', 'paid_out'])
            writer.writeheader()
            writer.writerows(transactions)

    for tx in transactions:
        total_in += tx['paid_in']
        total_out += tx['paid_out']
        
        # Simple categorization based on details
        detail_lower = tx['details'].lower()
        if 'pay bill' in detail_lower or 'buy goods' in detail_lower:
            categories['Payments/Merchants'] += tx['paid_out']
        elif 'sent to' in detail_lower or 'm-shwari' in detail_lower:
            categories['Transfers'] += tx['paid_out']
        elif 'airtime' in detail_lower:
            categories['Airtime'] += tx['paid_out']
        elif 'received' in detail_lower:
            categories['Income'] += tx['paid_in']

    print("\n" + "="*40)
    print(" M-PESA SPENDING REPORT")
    print("="*40)
    print(f"Total Transactions: {len(transactions)}")
    print(f"Total Money In:    KES {total_in:,.2f}")
    print(f"Total Money Out:   KES {total_out:,.2f}")
    print(f"Net Balance Delta: KES {(total_in - total_out):,.2f}")
    print("-"*40)
    print("TOP SPENDING CATEGORIES:")
    for cat, val in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        if val > 0:
            print(f" - {cat:<20}: KES {val:,.2f}")
    print("="*40)
    if output_csv:
        print(f"[+] Detailed report saved to: {output_csv}")

def main():
    parser = argparse.ArgumentParser(description="M-Pesa PDF Statement Parser")
    parser.add_argument("pdf", help="Path to the M-Pesa PDF statement file")
    parser.add_argument("--csv", help="Optional: Path to export CSV data", default=None)
    
    args = parser.parse_args()

    if not os.path.exists(args.pdf):
        print(f"Error: File {args.pdf} not found.")
        return

    data = parse_mpesa_pdf(args.pdf)
    if not data:
        print("No transactions found. Ensure the PDF is a valid M-Pesa statement.")
        return

    generate_summary(data, args.csv)

if __name__ == "__main__":
    main()