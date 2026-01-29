# app/report/investment_ledger_report/investment_ledger_report.py
import frappe

def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)

    return columns, data

def get_columns():
    return [
        {"label": "Ledger Entry Name", "fieldname": "ledger_entry_name", "fieldtype": "Link", "options": "Investment Ledger Entry", "width": 180},
        {"label": "Investment Name", "fieldname": "investment_name", "fieldtype": "Link", "options": "Investment", "width": 150},
        {"label": "Investment Date", "fieldname": "investment_date", "fieldtype": "Date", "width": 150},
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
        {"label": "Transaction Type", "fieldname": "transaction_type", "fieldtype": "Data", "width": 140},
        {"label": "Investment Type", "fieldname": "investment_type", "fieldtype": "Data", "width": 140},
        {"label": "Category", "fieldname": "investment_category", "fieldtype": "Data", "width": 120},
        {"label": "Broker", "fieldname": "broker", "fieldtype": "Data", "width": 120},
        {"label": "Investment Scheme", "fieldname": "investment_scheme", "fieldtype": "Link", "options": "Investment", "width": 180},
        {"label": "Units In", "fieldname": "units_in", "fieldtype": "Float", "width": 100},
        {"label": "Units Out", "fieldname": "units_out", "fieldtype": "Float", "width": 100},
        {"label": "Debit Amount", "fieldname": "debit_amount", "fieldtype": "Currency", "width": 120},
        {"label": "Credit Amount", "fieldname": "credit_amount", "fieldtype": "Currency", "width": 140},
        {"label": "Balance Units", "fieldname": "balance_units", "fieldtype": "Float", "width": 120},
        {"label": "Balance Amount", "fieldname": "balance_amount", "fieldtype": "Currency", "width": 140}
    ]

def get_data(filters):
    conditions = ""
    
    # --- FILTERS ---

    if filters.get("investment_type"):
        conditions += " AND i.investment_type = %(investment_type)s"

    if filters.get("broker"):
        conditions += " AND i.broker = %(broker)s"

    if filters.get("investment_scheme"):
        conditions += " AND i.investment_scheme = %(investment_scheme)s"

    if filters.get("investment_date"):
        conditions += " AND i.investment_date = %(investment_date)s"

    # Date Range Logic (Applies to Posting Date)
    if filters.get("from_date"):
        conditions += " AND ile.posting_date >= %(from_date)s"

    if filters.get("to_date"):
        conditions += " AND ile.posting_date <= %(to_date)s"

    sql_query = f"""
        SELECT
            ile.name AS ledger_entry_name,
            ile.investment AS investment_name,
            i.investment_date AS investment_date, 
            ile.transaction_type AS transaction_type,
            ile.units_in AS units_in,
            ile.units_out AS units_out,
            ile.debit_amount AS debit_amount,
            ile.credit_amount AS credit_amount,
            ile.balance_units AS balance_units,
            ile.balance_amount AS balance_amount,
            ile.posting_date AS posting_date,
            i.investment_type AS investment_type,
            i.investment_category AS investment_category,
            i.broker AS broker,
            i.investment_scheme AS investment_scheme
        FROM
            `tabInvestment Ledger Entry` ile
        LEFT JOIN
            `tabInvestment` i
        ON
            ile.investment = i.name
        WHERE
            i.docstatus = 1 
            {conditions}
        ORDER BY
            ile.posting_date DESC
    """

    return frappe.db.sql(sql_query, filters, as_dict=True)