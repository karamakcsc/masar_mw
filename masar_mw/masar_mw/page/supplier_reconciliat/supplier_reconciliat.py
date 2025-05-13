import frappe

@frappe.whitelist()
def get_purchase_invoice(filters=None):
    conditions = " 1=1 "
    if filters:
        filters = frappe.parse_json(filters)
        if filters.get("supplier"):
            conditions += f" AND tpi.supplier = '{filters.get('supplier')}'"
        if filters.get("voucher_type"):
            conditions += f" AND tge.voucher_type = '{filters.get('voucher_type')}'"
        if filters.get("supplier_group"):
            conditions += f" AND ts.supplier_group = '{filters.get('supplier_group')}'"
        _from , to = filters.get("from_date"), filters.get("to_date")
        if _from and to:
            conditions += f" AND tge.posting_date BETWEEN '{_from}' AND '{to}'"

    sql = frappe.db.sql(f"""
        SELECT 
            tge.name,
            tge.voucher_type,
            tge.voucher_no,
            tge.posting_date,
            tpi.remarks,
            tpi.supplier,
            ts.supplier_group,
            tpi.grand_total
        FROM `tabGL Entry` tge 
        LEFT JOIN `tabPurchase Invoice` tpi ON tge.voucher_no = tpi.name 
        LEFT JOIN tabSupplier ts ON tpi.supplier = ts.name
        WHERE 
            {conditions}
            AND tge.party_type = 'Supplier' 
            AND tge.docstatus = 1 
            AND tge.credit > 0 
            AND tpi.is_paid = 0
        ORDER BY tpi.supplier, tge.posting_date
    """, as_dict=True)
    
    
    return sql



@frappe.whitelist()
def create_payment(selected_data):
    frappe.msgprint(str(selected_data))
    if selected_data:
        for row in selected_data:
            if row.get("supplier") and row.get("voucher_no"):
                party = row.get("supplier")
                voucher_no = row.get("voucher_no")
                grand_total = row.get("grand_total")
                due_date = row.get("posting_date")
                allocated = row.get("allocated")
                paid_amount = row.get("amount_to_pay")
                
                new_payment = frappe.new_doc("Payment Entry")
    