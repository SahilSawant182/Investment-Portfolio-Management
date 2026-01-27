import frappe
from frappe.model.document import Document
from frappe.utils import nowdate
from investment_portfolio_management.investment_portfolio_management.doctype.investment_ledger_entry.investment_ledger_entry import create_investment_ledger_entry

class Investment(Document):
    def validate(self):
        self.validate_mandatory_fields()
        
    def validate_mandatory_fields(self):
        # Fetch Investment Type settings
        if not self.investment_type:
            return
            
        inv_type = frappe.get_doc("Investment Type", self.investment_type)
        
        if inv_type.requires_broker and not self.broker:
            frappe.throw(f"Broker is required for Investment Type: {self.investment_type}")
            
        if inv_type.has_scheme and not self.investment_scheme:
            frappe.throw(f"Investment Scheme is required for Investment Type: {self.investment_type}")
            
        if inv_type.has_maturity and not self.maturity_date:
            frappe.throw(f"Maturity Date is required for Investment Type: {self.investment_type}")

    def on_submit(self):
        self.create_ledger_entry()
        self.status = "Active"
        
    def on_cancel(self):
        # reverse entry (Credit/Debit swapped).
        self.create_ledger_entry(cancel=True)
        self.status = "Cancelled"

    def create_ledger_entry(self, cancel=False):
        args = {
            "investment": self.name,
            "posting_date": self.investment_date,
            "transaction_type": "Investment",
            "remarks": self.remarks
        }
        
        if not cancel:
            args["debit_amount"] = self.amount_invested
            args["units_in"] = self.units
        else:
            # Credit the amount, Units Out
            args["credit_amount"] = self.amount_invested
            args["units_out"] = self.units
            args["remarks"] = f"Reversal of {self.name}"
            
        create_investment_ledger_entry(args)

