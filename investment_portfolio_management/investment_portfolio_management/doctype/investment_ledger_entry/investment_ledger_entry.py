import frappe
from frappe.model.document import Document

class InvestmentLedgerEntry(Document):
    def validate(self):
        """
        Validate that this is not being modified manually if already submitted/created?
        Actually this doc is not submittable, but 'read only'.
        """
        pass

def create_investment_ledger_entry(args):
    """
    args: {
        "investment": "INV-2024-001",
        "posting_date": "2024-01-01",
        "transaction_type": "Investment" | "Return" | "Exit",
        "amount": 10000, # Positive for Investment, Negative for Exit? Or use Debit/Credit
        "units": 100, # Positive for In, Negative for Out
        "remarks": "...",
        "broker": "...",
        "company": "..."    
    }
    """
    
    # Validate required args
    if not args.get("investment"):
        frappe.throw("Investment reference is required for Ledger Entry")

    doc = frappe.new_doc("Investment Ledger Entry")
    doc.investment = args.get("investment")
    doc.posting_date = args.get("posting_date")
    doc.transaction_type = args.get("transaction_type")
    doc.remarks = args.get("remarks")
    
    # Handle amounts and units
    # For Ledger: 
    # Investment: Debit Amount (Asset increases), Units In
    # Exit: Credit Amount (Asset decreases), Units Out
    # Return: Depends. Dividends might not affect asset value effectively? 
    # User said: "Debit Amount", "Credit Amount".
    
    # Convention: 
    # Debit = Increase in Asset (Investment)
    # Credit = Decrease in Asset (Exit)
    
    amount = flt(args.get("amount"))
    units = flt(args.get("units"))
    
    if args.get("transaction_type") == "Investment":
        doc.debit_amount = amount
        doc.units_in = units
    elif args.get("transaction_type") == "Exit":
        doc.credit_amount = amount
        doc.units_out = units
    elif args.get("transaction_type") == "Return":
        # Returns (Dividends) are income, but user wants them linked.
       
        pass

    # Better approach: Caller specifies Debit/Credit directly or we infer?
    # Let's stick to what we know.
    
    if args.get("debit_amount"):
        doc.debit_amount = args.get("debit_amount")
    if args.get("credit_amount"):
        doc.credit_amount = args.get("credit_amount")
        
    if args.get("units_in"):
        doc.units_in = args.get("units_in")
    if args.get("units_out"):
        doc.units_out = args.get("units_out")
        
    # Calculate Balance
    # Get last entry for this investment
    last_entry = frappe.db.get_value("Investment Ledger Entry", 
        {"investment": doc.investment}, 
        ["balance_amount", "balance_units"], 
        order_by="posting_date desc, creation desc", 
        as_dict=1
    )
    
    prev_bal_amt = flt(last_entry.balance_amount) if last_entry else 0.0
    prev_bal_units = flt(last_entry.balance_units) if last_entry else 0.0
    
    doc.balance_amount = prev_bal_amt + flt(doc.debit_amount) - flt(doc.credit_amount)
    doc.balance_units = prev_bal_units + flt(doc.units_in) - flt(doc.units_out)
    
    doc.insert(ignore_permissions=True)
    return doc

def flt(val):
    if not val: return 0.0
    return float(val)
