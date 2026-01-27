import frappe
from frappe.model.document import Document
from frappe.utils import flt
from investment_portfolio_management.investment_portfolio_management.doctype.investment_ledger_entry.investment_ledger_entry import create_investment_ledger_entry

class ExitInvestment(Document):
    def validate(self):
        self.calculate_financials()
        
    def calculate_financials(self):
        self.exit_amount = flt(self.units_sold) * flt(self.exit_price)
        self.net_amount = self.exit_amount - flt(self.charges)
        
        # Calculate P&L
        if self.investment:
            inv_doc = frappe.get_doc("Investment", self.investment)
            buy_price = flt(inv_doc.price_per_unit)
            
            # Cost of sold units
            cost_of_sold = flt(self.units_sold) * buy_price
            
            # P&L = Net Amount - Cost
            self.pnl = self.net_amount - cost_of_sold

    def on_submit(self):
        self.create_ledger_entry()
        self.update_investment_status()

    def on_cancel(self):
        self.create_ledger_entry(cancel=True)
        self.update_investment_status()

    def create_ledger_entry(self, cancel=False):
        args = {
            "investment": self.investment,
            "posting_date": self.exit_date,
            "transaction_type": "Exit",
            "remarks": self.remarks or f"Exit: {self.exit_type}"
        }
        
        inv_doc = frappe.get_doc("Investment", self.investment)
        buy_price = flt(inv_doc.price_per_unit)
        cost_of_sold = flt(self.units_sold) * buy_price
        
        if not cancel:
            args["credit_amount"] = cost_of_sold
            args["units_out"] = self.units_sold
        else:
            args["debit_amount"] = cost_of_sold
            args["units_in"] = self.units_sold
            
        create_investment_ledger_entry(args)

    def update_investment_status(self):
        last_entry = frappe.db.get_value("Investment Ledger Entry", 
            {"investment": self.investment}, 
            ["balance_units"], 
            order_by="posting_date desc, creation desc", 
            as_dict=1
        )
        
        bal_units = flt(last_entry.balance_units) if last_entry else 0.0
        
        status = "Active"
        if bal_units <= 0:
            status = "Closed"
            
        frappe.db.set_value("Investment", self.investment, "status", status)
