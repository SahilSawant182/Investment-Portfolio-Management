frappe.ui.form.on('Investment', {
    refresh: function (frm) {
        frm.trigger('toggle_fields');
    },

    investment_type: function (frm) {
        if (!frm.doc.investment_type) return;

        frappe.db.get_doc('Investment Type', frm.doc.investment_type)
            .then(doc => {
                frm.inv_type_settings = doc; // Store for later
                frm.trigger('toggle_fields');
            });
    },

    toggle_fields: function (frm) {
        if (!frm.doc.investment_type) return;

        // If in cache use, else fetch
        if (frm.inv_type_settings) {
            apply_settings(frm, frm.inv_type_settings);
        } else {
            frappe.db.get_doc('Investment Type', frm.doc.investment_type)
                .then(doc => {
                    frm.inv_type_settings = doc;
                    apply_settings(frm, doc);
                });
        }
    }
});

function apply_settings(frm, settings) {
    // has_scheme -> investment_scheme
    frm.toggle_display('investment_scheme', settings.has_scheme);
    frm.toggle_reqd('investment_scheme', settings.has_scheme);

    // requires_broker -> broker
    frm.toggle_display('broker', settings.requires_broker);
    frm.toggle_reqd('broker', settings.requires_broker);

    // has_maturity -> maturity_date
    frm.toggle_display('maturity_date', settings.has_maturity);
    frm.toggle_reqd('maturity_date', settings.has_maturity);
}
