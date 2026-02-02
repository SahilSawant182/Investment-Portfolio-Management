import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import nowdate, add_days

class TestInvestmentLogic(FrappeTestCase):
    def setUp(self):
        # Create Masters if needed
        pass
        
    def test_excess_exit_validation(self):
        # 1. Create Investment
        inv = frappe.get_doc({
            "doctype": "Investment",
            "investment_category": "Test Category",
            "investment_type": "Test Equity Type",
            "investment_company": "Test AMC",
            "investment_scheme": "Test Scheme",
            "broker": "Test Broker",
            "investment_date": nowdate(),
            "amount_invested": 10000,
            "units": 100,
            "price_per_unit": 100,
            "remarks": "Initial Investment"
        })
        inv.insert()
        inv.submit()
        
        # 2. Try to Exit 150 units (Excess)
        exit_doc = frappe.get_doc({
            "doctype": "Exit Investment",
            "investment": inv.name,
            "exit_date": add_days(nowdate(), 1),
            "exit_type": "Partial",
            "units_sold": 150,
            "exit_price": 150,
            "charges": 0
        })
        
        # Expect Error
        self.assertRaises(frappe.ValidationError, exit_doc.save)
        
        # 3. Valid Exit (50 units)
        exit_doc.units_sold = 50
        exit_doc.save()
        exit_doc.submit()
        
        # Check Ledger
        entry = frappe.db.get_value("Investment Ledger Entry", 
            {"investment": inv.name, "transaction_type": "Exit", "credit_amount": 7500}, 
            ["balance_units", "document_date", "is_cancelled", "pnl"], as_dict=1)
            
        self.assertEqual(entry.balance_units, 50)
        self.assertEqual(entry.is_cancelled, 0)
        self.assertEqual(entry.pnl, 2500) # 7500 - 5000 (Cost)
        
        # 4. Cancel Exit
        exit_doc.cancel()
        
        # Check Ledger for Cancelled status on the SAME entry
        cancel_entry = frappe.db.get_value("Investment Ledger Entry", 
            {"investment": inv.name, "voucher_no": exit_doc.name}, 
            ["is_cancelled", "balance_units", "company"], as_dict=1)
            
        self.assertEqual(cancel_entry.is_cancelled, 1)
        self.assertEqual(cancel_entry.balance_units, 100)
        self.assertEqual(cancel_entry.company, inv.company) # Verify Company logic
        
        # Check Exit Status
        exit_doc.reload()
        self.assertEqual(exit_doc.status, "Cancelled")
        
        # Check Balance restored
        final_balance = frappe.db.get_value("Investment Ledger Entry", 
            {"investment": inv.name}, 
            "balance_units", order_by="creation desc")
            
        self.assertEqual(final_balance, 100)
