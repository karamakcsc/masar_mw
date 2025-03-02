frappe.ui.form.on('Purchase Invoice', {
	refresh(frm) {
		frm.fields_dict['items'].grid.get_field('expense_account').get_query = function(doc, cdt, cdn) {
            return {
                filters: [
                    // ["account_type", "=", ""],
                    ["is_group", "=", 0]
                ]
            };
        };
        frm.fields_dict['items'].grid.get_field('deferred_expense_account').get_query = function(doc, cdt, cdn) {
            return {
                filters: [
                    // ["account_type", "=", ""],
                    ["is_group", "=", 0]
                ]
            };
        };
	}
})