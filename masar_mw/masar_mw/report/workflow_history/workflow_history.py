# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

# import frappe


from __future__ import unicode_literals
from frappe import _
import frappe


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    # chart = get_chart_data(data , filters)
    return columns, data #, None , chart

def get_data(filters):
    _from, to = filters.get('from'), filters.get('to')  # date range
    # Conditions
    conditions = " AND 1=1 "
    if filters.get('docname'):
        conditions += f" AND tsa.name = '{filters.get('docname')}' "
    if filters.get('operator_name'):
        conditions += f" AND tsa.operator_name LIKE '%{filters.get('operator_name')}' "
    if filters.get('customer'):
        conditions += f" AND tsa.customer LIKE '%{filters.get('customer')}' "
    if filters.get('operator_country'):
        conditions += f" AND tsa.operator_country = '{filters.get('operator_country')}' "
    if filters.get('wf_from'):
        conditions += f" AND twh.wf_from LIKE '%{filters.get('wf_from')}' "
    if filters.get('wf_to'):
        conditions += f" AND twh.wf_to = '{filters.get('wf_to')}' "
    if filters.get('action'):
        conditions += f" AND twh.`action` = '{filters.get('action')}' "
    if filters.get('role'):
        conditions += f" AND twt.allowed = '{filters.get('role')}' "

    # SQL Query
    data = frappe.db.sql(f"""
          SELECT 
            tsa.name AS `Document Name`,
            tsa.posting_date AS `Posting Date`,
            twt.allowed AS `User Role`,
            tsa.item_name AS `Item Name`,
            tsa.operator_name AS `Operator Name`,
            tsa.customer AS `Customer Name`,
            tsa.operator_country AS `Operator Country`,
            twh.wf_from AS `From Stage`,
            IFNULL(twh.`action`, 'Unspecified') AS `Action Type`,
            IFNULL(twh.wf_to, 'Unspecified') AS `To Stage`,
            IFNULL(wf_modified_by, 'Unspecified') AS `Modified By`,
            twh.stage_start_time AS `Stage Start Time`,
            IFNULL(CAST(twh.stage_end_time AS DATETIME), NOW()) AS `Stage End Time`,
            ABS(IFNULL(twh.duration, TIMESTAMPDIFF(SECOND, IFNULL(twh.stage_start_time, NOW()), IFNULL(twh.stage_end_time, NOW())))) AS `Duration`

            
        FROM 
            `tabWorkflow History` twh
        INNER JOIN 
            `tabSales Acquisition` tsa ON twh.docname = tsa.name 
        INNER JOIN 
        	`tabWorkflow Transition` twt ON twh.wf_from = twt.state AND twh.wf_to = twt.next_state    
    	WHERE 
            (tsa.posting_date BETWEEN '{_from}' AND '{to}'){conditions}	
        ORDER BY
            twh.creation;""")

    return data

def get_columns():
    return [
        "Document Name:Link/Sales Acquisition:200",
		"Posting Date:Date:200",
        "User Role:Data:300",
        "Item Name:Data:200",
        "Operator Name:Data:200",
        "Customr Name:Data:200",
        "Operator Country:Data:200",
        "From Stage:Data:200",
        "Action Type:Data:200",
        "To Stage:Data:200",
        "Modified By:300",
        "Stage Start Time:Datetime:200",
        "Stage End Time:Datetime:200",
        "Durations:Duration:200"
    ]