frappe.ui.form.on("Payment Entry", {
    refresh: function (frm) {
        if (frm.doc.references && frm.doc.references.length > 0) {
            get_remarks(frm);
            get_reference_no(frm);
        }
    },
    validate: function (frm) {
        if (frm.doc.references && frm.doc.references.length > 0) {
            get_remarks(frm);
            get_reference_no(frm);
        }
    },
});



function get_remarks(frm) {
    if (frm.doc.payment_type == "Receive" && frm.doc.references && frm.doc.references.length > 0) {
        frm.doc.references.forEach(function (ref) {
            if (ref.reference_doctype === "Sales Invoice") {
                frappe.call({
                    method: "frappe.client.get_value",
                    args: {
                        doctype: "Sales Invoice",
                        fieldname: "remarks",
                        filters: { name: ref.reference_name }
                    },
                    callback: function (data) {
                        if (data.message && data.message.remarks) {
                            frappe.model.set_value(ref.doctype, ref.name, "custom_remarks", data.message.remarks);
                            frm.refresh_field("references");
                        }
                    }
                })
            }
        });
    }
}

function get_reference_no(frm) {
    if (frm.doc.payment_type == "Receive" && frm.doc.references && frm.doc.references.length > 0) {
        frm.doc.references.forEach(function (ref) {
            if (ref.reference_doctype === "Sales Invoice") {
                frappe.call({
                    method: "frappe.client.get_value",
                    args: {
                        doctype: "Sales Invoice",
                        fieldname: "custom_ref_no",
                        filters: { name: ref.reference_name }
                    },
                    callback: function (data) {
                        if (data.message && data.message.custom_ref_no) {
                            frappe.model.set_value(ref.doctype, ref.name, "custom_reference_number", data.message.custom_ref_no);
                            frm.refresh_field("references");
                        }
                    }
                })
            }
        });
    }
}