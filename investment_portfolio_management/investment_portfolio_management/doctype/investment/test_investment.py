# import frappe
# import unittest
# from frappe.tests.utils import FrappeTestCase
# from frappe.utils import nowdate, add_days

# class TestInvestmentPortfolio(FrappeTestCase):
#     def setUp(self):
#         # Create Masters
#         if not frappe.db.exists("Investment Category", "Test Category"):
#             frappe.get_doc({
#                 "doctype": "Investment Category",
#                 "category_name": "Test Category",
#                 "risk_profile": "Medium"
#             }).insert()
            
#         if not frappe.db.exists("Investment Type", "Test Equity Type"):
#             frappe.get_doc({
#                 "doctype": "Investment Type",
#                 "investment_type": "Test Equity Type",
#                 "asset_class": "Equity",
#                 "requires_broker": 1,
#                 "has_scheme": 1,
#                 "has_maturity": 0
#             }).insert()
            
#         if not frappe.db.exists("Investment Company", "Test AMC"):
#             frappe.get_doc({
#                 "doctype": "Investment Company",
#                 "company_name": "Test AMC",
#                 "company_type": "Listed"
#             }).insert()
            
#         if not frappe.db.exists("Broker", "Test Broker"):
#             frappe.get_doc({
#                 "doctype": "Broker",
#                 "broker_name": "Test Broker",
#                 "broker_type": "Stock Broker"
#             }).insert()
            
#         if not frappe.db.exists("Investment Scheme", "Test Scheme"):
#             frappe.get_doc({
#                 "doctype": "Investment Scheme",
#                 "scheme_name": "Test Scheme",
#                 "investment_company": "Test AMC",
#                 "investment_type": "Test Equity Type"
#             }).insert()

#     def test_investment_flow(self):
#         # 1. Create Investment
#         inv = frappe.get_doc({
#             "doctype": "Investment",
#             "investment_category": "Test Category",
#             "investment_type": "Test Equity Type",
#             "investment_company": "Test AMC",
#             "investment_scheme": "Test Scheme",
#             "broker": "Test Broker",
#             "investment_date": nowdate(),
#             "amount_invested": 10000,
#             "units": 100,
#             "price_per_unit": 100,
#             "remarks": "Initial Investment"
#         })
#         inv.insert()
#         inv.submit()
        
#         # Check Ledger
#         entry = frappe.db.get_value("Investment Ledger Entry", 
#             {"investment": inv.name, "transaction_type": "Investment"}, 
#             ["debit_amount", "units_in", "balance_amount"], as_dict=1)
            
#         self.assertEqual(entry.debit_amount, 10000)
#         self.assertEqual(entry.units_in, 100)
#         self.assertEqual(entry.balance_amount, 10000)
        
#         # 2. Return (Dividend Reinvestment)
#         # CHANGED: "Investment Return" -> "Return of Investment"
#         ret = frappe.get_doc({
#             "doctype": "Return of Investment",
#             "investment": inv.name,
#             "return_date": nowdate(),
#             "return_type": "Dividend",
#             "amount": 500,
#             "units_affected": 5
#         })
#         ret.insert()
#         ret.submit()
        
#         # Check Ledger for Return
#         ret_entry = frappe.db.get_value("Investment Ledger Entry", 
#             {"investment": inv.name, "transaction_type": "Return"}, 
#             ["debit_amount", "units_in", "balance_amount", "balance_units"], as_dict=1)
            
#         self.assertEqual(ret_entry.debit_amount, 500)
#         self.assertEqual(ret_entry.units_in, 5)
#         self.assertEqual(ret_entry.balance_amount, 10500) # 10000 + 500
#         self.assertEqual(ret_entry.balance_units, 105) # 100 + 5
        
#         # 3. Exit (Partial)
#         # CHANGED: "Investment Exit" -> "Exit Investment"
#         # Sell 50 units @ 150 
#         exit_doc = frappe.get_doc({
#             "doctype": "Exit Investment",
#             "investment": inv.name,
#             "exit_date": add_days(nowdate(), 1),
#             "exit_type": "Partial",
#             "units_sold": 50,
#             "exit_price": 150,
#             "charges": 0
#         })
#         exit_doc.insert()
#         exit_doc.submit()
        
#         self.assertEqual(exit_doc.pnl, 2500)
        
#         # Check Ledger for Exit
#         exit_entry = frappe.db.get_value("Investment Ledger Entry", 
#             {"investment": inv.name, "transaction_type": "Exit"}, 
#             ["credit_amount", "units_out", "balance_amount"], as_dict=1)
            
#         self.assertEqual(exit_entry.credit_amount, 5000) # Cost of sold
#         self.assertEqual(exit_entry.units_out, 50)
#         self.assertEqual(exit_entry.balance_amount, 5500) # 10500 - 5000
        
#         # Check Investment Status
#         inv.reload()
#         self.assertEqual(inv.status, "Active")
        
#         # 4. Full Exit (Remaining 55 units)
#         exit_full = frappe.get_doc({
#             "doctype": "Exit Investment",
#             "investment": inv.name,
#             "exit_date": add_days(nowdate(), 2),
#             "exit_type": "Full",
#             "units_sold": 55,
#             "exit_price": 200,
#             "charges": 0
#         })
#         exit_full.insert()
#         exit_full.submit()
        
#         # Check Ledger
#         exit_full_entry = frappe.db.get_value("Investment Ledger Entry", 
#             {"investment": inv.name, "transaction_type": "Exit", "posting_date": add_days(nowdate(), 2)}, 
#             ["credit_amount", "balance_amount", "balance_units"], as_dict=1)
            
#         self.assertEqual(exit_full_entry.credit_amount, 5500)
#         self.assertEqual(exit_full_entry.balance_amount, 0)
#         self.assertEqual(exit_full_entry.balance_units, 0)
        
#         # Check Status
#         inv.reload()
#         self.assertEqual(inv.status, "Closed")
