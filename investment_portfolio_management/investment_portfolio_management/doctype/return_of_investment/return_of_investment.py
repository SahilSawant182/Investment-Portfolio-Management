import frappe
from frappe.model.document import Document
from investment_portfolio_management.investment_portfolio_management.doctype.investment_ledger_entry.investment_ledger_entry import create_investment_ledger_entry

class ReturnofInvestment(Document):
    def on_submit(self):
        self.create_ledger_entry()
        
    def on_cancel(self):
        self.create_ledger_entry(cancel=True)

    def create_ledger_entry(self, cancel=False):
        args = {
            "investment": self.investment,
            "posting_date": self.return_date,
            "transaction_type": "Return",
            "remarks": self.remarks or f"Return: {self.return_type}"
        }
        
        amount = self.amount
        units = self.units_affected or 0.0
        
        if not cancel:
            if units > 0:
                args["debit_amount"] = amount
                args["units_in"] = units
        else:
            if units > 0:
                args["credit_amount"] = amount
                args["units_out"] = units
                
        create_investment_ledger_entry(args)
