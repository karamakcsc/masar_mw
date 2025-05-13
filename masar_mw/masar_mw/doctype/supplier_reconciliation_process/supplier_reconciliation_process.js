frappe.ui.form.on("Supplier Reconciliation Process", {
    refresh: function(frm) {
        getData(frm);
    },
});

function getData(frm) {
    if (frm.doc.docstatus == 0) {
        frm.add_custom_button(__('Get Unreconciled Entries'), function() {
            frappe.call({
                doc: frm.doc,
                method: 'get_data',
                callback: function(r) {
                    if (r.message) {
                        let invoices_sql = r.message;
                        let inv_dialog = new frappe.ui.Dialog({
                            title: __('Select Invoices'),
                            fields: [
                                {
                                    fieldtype: 'Table',
                                    fieldname: 'invoices',
                                    label: __('Invoices'),
                                    cannot_add_rows: true,
                                    cannot_delete_rows: true, 
                                    fields: [
                                        { fieldtype: 'Data', fieldname: 'v_type', label: __('Voucher Type'), read_only: 1, in_list_view: 1, columns: 1 },
                                        { fieldtype: 'Data', fieldname: 'v_no', label: __('Voucher No'), read_only: 1, in_list_view: 1, columns: 2 },
                                        { fieldtype: 'Data', fieldname: 'invoice_date', label: __('Invoice Date'), read_only: 1, in_list_view: 1, columns: 1 },
                                        { fieldtype: 'Data', fieldname: 'party_type', label: __('Party Type'), read_only: 1, in_list_view: 0 },
                                        { fieldtype: 'Data', fieldname: 'party', label: __('Party'), read_only: 1, in_list_view: 0, columns: 1 },
                                        { fieldtype: 'Data', fieldname: 'party_name', label: __('Party Name'), read_only: 1, in_list_view: 1, columns: 1 },
                                        { fieldtype: 'Currency', fieldname: 'invoice_amount', label: __('Invoice Amount'), read_only: 1, in_list_view: 0 },
                                        { fieldtype: 'Currency', fieldname: 'outstanding_amount', label: __('Outstanding Amount'), read_only: 1, in_list_view: 1, columns: 1 },
                                        { fieldtype: 'Data', fieldname: 'currency', label: __('Currency'), read_only: 1, in_list_view: 0 },
                                        { fieldtype: 'Data', fieldname: 'remarks', label: __('Remarks'), read_only: 1, in_list_view: 1, columns: 4 }
                                    ],
                                    data: invoices_sql.map(i => ({
                                        v_type: i.voucher_type,
                                        v_no: i.voucher_no,
                                        invoice_date: i.posting_date,
                                        party_type: i.party_type,
                                        party: i.party,
                                        party_name: i.party_name,
                                        invoice_amount: i.invoice_amount_in_account_currency,
                                        outstanding_amount: i.outstanding_in_account_currency,
                                        currency: i.currency,
                                        remarks: i.remarks
                                    }))
                                }
                            ],
                            primary_action_label: __('Submit'),
                            primary_action(values) {
                                inv_dialog.hide();
                                let selected_rows = inv_dialog.fields_dict.invoices.grid.get_selected_children();
                                let existing_invoice_numbers = frm.doc.invoices.map(r => r.invoice_number);                                
                                selected_rows.forEach(function(row) {
                                    if (!existing_invoice_numbers.includes(row.v_no)) {
                                        let child = frm.add_child("invoices");
                                        frappe.model.set_value(child.doctype, child.name, "invoice_type",row.v_type)
                                        .then(() =>frappe.model.set_value(child.doctype, child.name, "invoice_number", row.v_no))
                                        .then(() =>frappe.model.set_value(child.doctype, child.name, "invoice_date", row.invoice_date))
                                        .then(() =>frappe.model.set_value(child.doctype, child.name, "party_type", row.party_type))
                                        .then(() =>frappe.model.set_value(child.doctype, child.name, "party", row.party))
                                        .then(() =>frappe.model.set_value(child.doctype, child.name, "party_name", row.party_name))
                                        .then(() =>frappe.model.set_value(child.doctype, child.name, "amount", row.invoice_amount))
                                        .then(() =>frappe.model.set_value(child.doctype, child.name, "outstanding_amount", row.outstanding_amount))
                                        .then(() =>frappe.model.set_value(child.doctype, child.name, "amount_to_pay", row.outstanding_amount))
                                        .then(() =>frappe.model.set_value(child.doctype, child.name, "currency", row.currency))
                                        .then(() =>frappe.model.set_value(child.doctype, child.name, "remarks", row.remarks))
                                        .then(() => resolve());
                                    }
                                });
                                frm.refresh_field('invoices');
                            }
                        });
                        inv_dialog.show();
                        inv_dialog.$wrapper.on('shown.bs.modal', function () {
                            const $dialog = inv_dialog.$wrapper.find('.modal-dialog');
                            const $content = inv_dialog.$wrapper.find('.modal-content');

                            $dialog.css({
                                'width': '98vw',
                                'max-width': '98vw',
                                'margin': '1rem auto',
                            });

                            $content.css({
                                'height': '90vh',
                                'overflow-y': 'auto',
                                'border-radius': '8px',
                            });
                        });
                    }
                }
            });
        });
    }
}