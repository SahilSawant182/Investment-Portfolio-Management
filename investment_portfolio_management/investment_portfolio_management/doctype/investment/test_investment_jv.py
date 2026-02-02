import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import nowdate, add_days, flt

class TestInvestmentJournalEntry(FrappeTestCase):
    def setUp(self):
        # Create Masters
        self.create_company_accounts()
        self.create_masters()

    def create_company_accounts(self):
        if frappe.db.exists("Company", "_Test Company"):
            company = frappe.get_doc("Company", "_Test Company")
        else:
            company = frappe.get_doc({
                "doctype": "Company",
                "company_name": "_Test Company",
                "default_currency": "INR",
                "country": "India"
            }).insert()
            
        # Ensure Parent Accounts exist
        if not frappe.db.exists("Account", "Direct Income - _TC"):
            frappe.get_doc({
                "doctype": "Account",
                "account_name": "Direct Income",
                "parent_account": "",
                "company": "_Test Company",
                "account_type": "Income",
                "is_group": 1,
                "root_type": "Income"
            }).insert()

        if not frappe.db.exists("Account", "Direct Expenses - _TC"):
            frappe.get_doc({
                "doctype": "Account",
                "account_name": "Direct Expenses",
                "parent_account": "",
                "company": "_Test Company",
                "account_type": "Expense",
                "is_group": 1,
                "root_type": "Expense"
            }).insert()

        if not frappe.db.exists("Account", "Current Assets - _TC"):
            frappe.get_doc({
                "doctype": "Account",
                "account_name": "Current Assets",
                "parent_account": "",
                "company": "_Test Company",
                "account_type": "Asset",
                "is_group": 1,
                "root_type": "Asset"
            }).insert()
        
        income_acc_name = "Test Income - _TC"
        if not frappe.db.exists("Account", income_acc_name):
            income_acc = frappe.get_doc({
                "doctype": "Account",
                "account_name": "Test Income",
                "parent_account": "Direct Income - _TC",
                "company": "_Test Company",
                "account_type": "Income"
            }).insert()
            company.default_income_account = income_acc.name

        if not frappe.db.exists("Account", "Test Expense - _TC"):
            expense_acc = frappe.get_doc({
                "doctype": "Account",
                "account_name": "Test Expense",
                "parent_account": "Direct Expenses - _TC",
                "company": "_Test Company",
                "account_type": "Expense"
            }).insert()
            company.default_expense_account = expense_acc.name
            
        company.save()
        
        # Setup Investment Account Settings
        # Check if settings exist for this company, if not create a new doc (since it's not Single)
        existing_setting = frappe.db.get_value("Default Account", 
            {"company": "_Test Company", "parenttype": "Investment Account Settings"}, 
            "parent"
        )
        
        if not existing_setting:
            frappe.get_doc({
                "doctype": "Investment Account Settings",
                "account_setting": [
                    {
                        "company": "_Test Company",
                        "deafult_income_account": income_acc_name
                    }
                ]
            }).insert()

    def create_masters(self):
        if not frappe.db.exists("Investment Category", "Test Category"):
            frappe.get_doc({
                "doctype": "Investment Category",
                "category_name": "Test Category",
                "risk_profile": "Medium"
            }).insert()
            
        if not frappe.db.exists("Investment Type", "Test Equity Type"):
            frappe.get_doc({
                "doctype": "Investment Type",
                "investment_type": "Test Equity Type",
                "asset_class": "Equity",
                "requires_broker": 1,
                "has_scheme": 1,
                "has_maturity": 0
            }).insert()
            
        if not frappe.db.exists("Investment Company", "Test AMC"):
            frappe.get_doc({
                "doctype": "Investment Company",
                "company_name": "Test AMC",
                "company_type": "Listed"
            }).insert()
            
        if not frappe.db.exists("Broker", "Test Broker"):
            frappe.get_doc({
                "doctype": "Broker",
                "broker_name": "Test Broker",
                "broker_type": "Stock Broker"
            }).insert()
            
        if not frappe.db.exists("Investment Scheme", "Test Scheme"):
            frappe.get_doc({
                "doctype": "Investment Scheme",
                "scheme_name": "Test Scheme",
                "investment_company": "Test AMC",
                "investment_type": "Test Equity Type"
            }).insert()

    def test_journal_entry_creation(self):
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
            "remarks": "Initial Investment",
            "company": "_Test Company",
            "investment_account": "Investment Assets - _TC", # Assuming standard test accounts exist
            "bank_account": "Cash - _TC"
        })
        
        # Ensure Accounts exist (Standard Frappe Test Data usually has these, but safe check)
        if not frappe.db.exists("Account", "Investment Assets - _TC"):
             frappe.get_doc({
                "doctype": "Account",
                "account_name": "Investment Assets",
                "parent_account": "Current Assets - _TC",
                "company": "_Test Company"
            }).insert()
            
        if not frappe.db.exists("Account", "Cash - _TC"):
             frappe.get_doc({
                "doctype": "Account",
                "account_name": "Cash",
                "parent_account": "Current Assets - _TC",
                "company": "_Test Company",
                "account_type": "Cash"
            }).insert()

        inv.insert()
        inv.submit()
        
        # 2. Return (Cash) -> Check JV
        ret = frappe.get_doc({
            "doctype": "Return of Investment",
            "investment": inv.name,
            "return_date": nowdate(),
            "return_type": "Dividend",
            "amount": 500,
            "units_affected": 0,
            "company": "_Test Company"
        })
        ret.insert()
        ret.submit()
        
        # Verify JV for Return
        jv_name = frappe.db.get_value("Journal Entry", {"remark": f"Return Entry for {ret.name}"}, "name")
        self.assertTrue(jv_name)
        
        jv = frappe.get_doc("Journal Entry", jv_name)
        self.assertEqual(jv.docstatus, 1) # Submitted
        
        # Debit Cash (Asset Up), Credit Income
        self.assertEqual(jv.accounts[0].account, "Test Income - _TC")
        self.assertEqual(jv.accounts[0].credit_in_account_currency, 500)
        self.assertEqual(jv.accounts[1].account, "Cash - _TC")
        self.assertEqual(jv.accounts[1].debit_in_account_currency, 500)


        # 3. Exit (Partial Gain) -> Check JV
        # Sell 50 units @ 150 (Cost 100) -> 50 * 150 = 7500. Cost = 50 * 100 = 5000. Gain = 2500.
        exit_doc = frappe.get_doc({
            "doctype": "Exit Investment",
            "investment": inv.name,
            "exit_date": add_days(nowdate(), 1),
            "exit_type": "Partial",
            "units_sold": 50,
            "exit_price": 150,
            "charges": 0,
            "company": "_Test Company"
        })
        exit_doc.insert()
        exit_doc.submit()
        
        # Verify JV for Exit
        jv_exit_name = frappe.db.get_value("Journal Entry", {"remark": f"Exit Entry for {exit_doc.name}"}, "name")
        self.assertTrue(jv_exit_name)
        
        jv_exit = frappe.get_doc("Journal Entry", jv_exit_name)
        
        # Expected:
        # Credit Investment (Cost): 5000
        # Debit Bank (Net Receive): 7500
        # Credit Income (Gain): 2500
        
        # Check specific amounts by account
        acc_map = {d.account: d for d in jv_exit.accounts}
        
        self.assertEqual(flt(acc_map["Investment Assets - _TC"].credit_in_account_currency), 5000)
        self.assertEqual(flt(acc_map["Cash - _TC"].debit_in_account_currency), 7500)
        self.assertEqual(flt(acc_map["Test Income - _TC"].credit_in_account_currency), 2500)
