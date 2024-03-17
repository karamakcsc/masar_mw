// // Copyright (c) 2024, KCSC and contributors
// // For license information, please see license.txt


frappe.ui.form.on("Sales Acquisition", {
    refresh: function(frm) {
        frappe.call({
            doc: frm.doc,
            method: 'wf_state',
        });
    }
});
