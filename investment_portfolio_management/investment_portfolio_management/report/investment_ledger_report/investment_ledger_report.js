// app/report/investment_ledger_report/investment_ledger_report.js

frappe.query_reports["Investment Ledger Report"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "reqd": 0
        },
        {
            "fieldname": "to_date", 
            "label": "To Date",
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 0
        },
        {
            "fieldname": "investment_date",
            "label": "Investment Date",
            "fieldtype": "Date",
            "default": "",
            //"reqd": 0
        },
        {
            "fieldname": "investment_type",
            "label": "Investment Type",
            "fieldtype": "Link",
            "options": "Investment Type",
            "default": ""
        },
        {
            "fieldname": "broker",    
            "label": "Broker",  
            "fieldtype": "Link",
            "options": "Broker",
            "default": ""
        },
        {
            "fieldname": "investment_scheme",
            "label": "Investment Scheme",
            "fieldtype": "Link",
            "options": "Investment Scheme",
            "default": ""
        }
    ],

    onload: function(report) {
    const today = frappe.datetime.get_today();
    const last_month = frappe.datetime.add_months(today, -1);

    report.set_filter_value("from_date", last_month);
    report.set_filter_value("to_date", today);
    report.set_filter_value("investment_date", "");
    report.set_filter_value("investment_type", "");
    report.set_filter_value("broker", "");
    report.set_filter_value("investment_scheme", ""); 

    report.refresh();

    // FORCE HANDLE BACKSPACE CLEAR FOR DATE FILTER
    setTimeout(() => {
        const investment_date_filter = report.get_filter("investment_date");

        if (investment_date_filter && investment_date_filter.$input) {
            investment_date_filter.$input.on("blur", function () {
                const val = investment_date_filter.get_value();

                // If user cleared the date and clicked outside
                if (!val) {
                    frappe.query_report.refresh();
                }
            });
        }
    }, 500);
}
};