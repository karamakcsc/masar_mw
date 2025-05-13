frappe.ui.form.on('Purchase Invoice', {
	refresh(frm) {
		frm.fields_dict['items'].grid.get_field('expense_account').get_query = function(doc, cdt, cdn) {
            return {
                filters: [
                    ["is_group", "=", 0],
                    ["company", "=", frm.doc.company]
                ]
            };
        };
        frm.fields_dict['items'].grid.get_field('deferred_expense_account').get_query = function(doc, cdt, cdn) {
            return {
                filters: [
                    ["is_group", "=", 0],
                    ["company", "=", frm.doc.company]
                ]
            };
        };
	}
})