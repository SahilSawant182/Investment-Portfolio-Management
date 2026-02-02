// Copyright (c) 2026, Quantbit Technologies Pvt.Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Return of Investment", {
    refresh(frm) {
        // Filter Investment field to only show Submitted docs
        frm.set_query('investment', function () {
            return {
                filters: {
                    docstatus: 1
                }
            };
        });

        frm.set_query("bank_account", function () {
            return {
                filters: {
                    "company": frm.doc.company,
                    "is_group": 0,
                    "disabled": 0
                }
            };
        });
        frm.set_query("investment_account", function () {
            return {
                filters: {
                    "company": frm.doc.company,
                    "is_group": 0,
                    "disabled": 0
                }
            };
        });
    },

    investment: function (frm) {
        if (frm.doc.investment) {
            frappe.db.get_doc('Investment', frm.doc.investment)
                .then(doc => {
                    frm.set_value('broker', doc.broker);
                });

            // Fetch balance units from Ledger?
            // "units affected should automatically fetched from that investment"
            // The user might mean total units or balance units. Let's fetch Balance Units from last ledger entry.
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Investment Ledger Entry",
                    filters: {
                        investment: frm.doc.investment
                    },
                    fields: ["balance_units"],
                    order_by: "posting_date desc, creation desc",
                    limit_page_length: 1
                },
                callback: function (r) {
                    if (r.message && r.message.length > 0) {
                        frm.set_value('units_affected', r.message[0].balance_units);
                    }
                }
            });
        }
    }
});
