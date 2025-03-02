frappe.ui.form.on('Sales Invoice', {
	refresh(frm) {
		frm.fields_dict['items'].grid.get_field('income_account').get_query = function(doc, cdt, cdn) {
            return {
                filters: [
                    ["is_group", "=", 0]
                ]
            };
        };
        frm.fields_dict['items'].grid.get_field('expense_account').get_query = function(doc, cdt, cdn) {
            return {
                filters: [
                    ["is_group", "=", 0]
                ]
            };
        };
        frm.fields_dict['items'].grid.get_field('deferred_revenue_account').get_query = function(doc, cdt, cdn) {
            return {
                filters: [
                    ["is_group", "=", 0]
                ]
            };
        };
	}
})