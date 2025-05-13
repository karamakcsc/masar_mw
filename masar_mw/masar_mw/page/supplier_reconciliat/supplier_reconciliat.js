frappe.pages['supplier-reconciliat'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Supplier Reconciliation',
        single_column: true
    });

    $(wrapper).find('.layout-main-section').html(`
        <div class="filter-section mb-4">
            <div class="row">
                <div class="col-md-2">
                    <div class="form-group">
                        <div class="voucher-type-filter"></div>
                    </div>
                </div>
                <div class="col-md-2">
                    <div class="form-group">
                        <div class="supplier-filter"></div>
                    </div>
                </div>
                <div class="col-md-2">
                    <div class="form-group">
                        <div class="supplier-group-filter"></div>
                    </div>
                </div>
                <div class="col-md-2">
                    <div class="form-group">
                        <div class="from-date"></div>
                    </div>
                </div>
                <div class="col-md-2">
                    <div class="form-group">
                        <div class="to-date"></div>
                    </div>
                </div>
            </div>
        </div>
        <div class="datatable-container"></div>
    `);

    createFilters();
    loadData();

    function createFilters() {
        const fromDate = frappe.ui.form.make_control({
            parent: $(wrapper).find('.from-date'),
            df: {
                // label: 'From Date',
                fieldtype: 'Date',
                fieldname: 'from_date',
                placeholder: 'From Date',
                onchange: function() {
                    loadData();
                }
            }
        });
        fromDate.refresh();

        const toDate = frappe.ui.form.make_control({
            parent: $(wrapper).find('.to-date'),
            df: {
                // label: 'To Date',
                fieldtype: 'Date',
                fieldname: 'to_date',
                placeholder: 'To Date',
                onchange: function() {
                    loadData();
                }
            }
        });
        toDate.refresh();

        const supplierFilter = frappe.ui.form.make_control({
            parent: $(wrapper).find('.supplier-filter'),
            df: {
                // label: 'Supplier',
                fieldtype: 'Link',
                fieldname: 'supplier',
                options: 'Supplier',
                placeholder: 'Supplier',
                onchange: function() {
                    loadData();
                }
            }
        });
        supplierFilter.refresh();

        const voucherTypeFilter = frappe.ui.form.make_control({
            parent: $(wrapper).find('.voucher-type-filter'),
            df: {
                // label: 'Voucher Type',
                fieldtype: 'Select',
                fieldname: 'voucher_type',
                options: '\nPurchase Invoice\nJournal Entry',
                placeholder: 'Voucher Type',
                onchange: function() {
                    loadData();
                }
            }
        });
        voucherTypeFilter.refresh();

        const supplierGroupFilter = frappe.ui.form.make_control({
            parent: $(wrapper).find('.supplier-group-filter'),
            df: {
                // label: 'Voucher Type',
                fieldtype: 'Link',
                fieldname: 'supplier_group',
                options: 'Supplier Group',
                placeholder: 'Supplier Group',
                onchange: function() {
                    loadData();
                }
            }
        });
        supplierGroupFilter.refresh();

        page.filters = {
            fromDate,
            toDate,
            supplierFilter,
            voucherTypeFilter,
            supplierGroupFilter
        };
    }

    function loadData() {
        const filters = {
            from_date: page.filters.fromDate.get_value(),
            to_date: page.filters.toDate.get_value(),
            supplier: page.filters.supplierFilter.get_value(),
            voucher_type: page.filters.voucherTypeFilter.get_value(),
            supplier_group: page.filters.supplierGroupFilter.get_value()
        };

        frappe.call({
            method: 'masar_mw.masar_mw.page.supplier_reconciliat.supplier_reconciliat.get_purchase_invoice',
            args: {
                filters: filters
            },
            callback: function(response) {
                if (!response.message) {
                    frappe.msgprint(__('No Data found'));
                    return;
                }

                const purchaseInvoices = response.message;
                const tableData = purchaseInvoices.map(pi => [
                    pi.name,
                    pi.voucher_type,
                    pi.voucher_no,
                    frappe.datetime.str_to_user(pi.posting_date),
                    pi.remarks || '',
                    pi.supplier,
                    pi.supplier_group,
                    pi.grand_total
                ]);

                $(wrapper).find('.datatable-container').empty();

                const datatable = new frappe.DataTable(
                    $(wrapper).find('.datatable-container')[0], {
                        columns: [
                            { name: 'Name', width: 200, editable: false },
                            { name: 'Voucher Type', width: 140, editable: false },
                            { name: 'Voucher No.', width: 225, editable: false },
                            { name: 'Posting Date', width: 120, editable: false, },
                            { name: 'Remarks', width: 350, editable: false },
                            { name: 'Supplier', width: 100, editable: false },
                            { name: 'Supplier Group', width: 150, editable: false },
                            { name: 'Grand Total', width: 120, editable: false, format: value => frappe.format(value, {fieldtype: 'Currency'}) },
                            { name: 'Amount to Pay  ', width: 120, editable: true, format: value => frappe.format(value, {fieldtype: 'Currency'}) },
                            { name: 'FX Gain Loss %', width: 120, editable: true },
                            { name: 'Net Payable', width: 120, editable: true },
                            { name: 'FX Gain Loss Amount', width: 120, editable: true },
                        ],
                        data: tableData,
                        dynamicRowHeight: true,
                        checkboxColumn: true,
                        inlineFilters: true
                    }
                );

                page.set_primary_action('Create Payment', () => {
                    // frappe.msgprint('Under Construction');
                    // console.log('datatable', datatable);
                    const selectedRows = document.querySelectorAll('div.dt-row--highlight');
                    const selectedRowData = []; // <-- fix: array outside the loop

                    selectedRows.forEach(row => {
                        const rowData = [];
                        
                        const cells = row.querySelectorAll('div.dt-cell');
                        
                        cells.forEach(cell => {
                            rowData.push(cell.textContent.trim());
                        });
                        
                        selectedRowData.push(rowData); // <-- collect each row's data
                    });

                    if (selectedRows.length === 0) {
                        frappe.msgprint(__('Please select at least one row.'));
                        return;
                    }

                    const selectedData = selectedRowData.map(row => ({
                        name: row[2],
                        voucher_type: row[3],
                        voucher_no: row[4],
                        posting_date: row[5],
                        remarks: row[6],
                        supplier: row[7],
                        supplier_group: row[8],
                        grand_total: row[9],
                        amount_to_pay: row[10],
                        fx_gain_loss: row[11],
                        net_payable: row[12],
                        fx_gain_loss_amount: row[13]
                    }));

                    console.log(selectedData);
                    frappe.call({
                        method: 'masar_mw.masar_mw.page.supplier_reconciliat.supplier_reconciliat.create_payment',
                        args: {
                            selected_data: selectedData
                        },
                        callback: function(response) {
                            // if (response.message) {
                            //     frappe.msgprint(__('Payment created successfully.'));
                            // } else {
                            //     frappe.msgprint(__('Failed to create payment.'));
                            // }
                        }
                    });
                    datatable.clearSelectedRows();
                    datatable.refresh();
                });
            }
        });
    }
};