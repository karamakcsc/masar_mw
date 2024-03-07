import frappe

@frappe.whitelist()
def get_count():
    return frappe.db.sql(f"""SELECT 
    COALESCE(tsa.status, 'Draft') AS status,
    COUNT(CASE WHEN tsa.status = 'Draft' THEN 1 END) AS draft_count,
    COUNT(CASE WHEN tsa.status = 'Initiation of Discussion' THEN 1 END) AS io_discussion_count,
    COUNT(CASE WHEN tsa.status = 'Discussion (Acquisition)' THEN 1 END) AS d_acquisition_count,
    COUNT(tsa.name)  AS docname_count,
    COUNT(CASE WHEN tsa.status = 'Under Operator Approval' THEN 1 END) AS uo_approved_count,
    COUNT(CASE WHEN tsa.status = 'Under SP Approval' THEN 1 END) AS up_approved_count,
    COUNT(CASE WHEN tsa.status = 'Approved' THEN 1 END) AS approved_count
    
FROM `tabSales Acquisition` tsa
WHERE tsa.status IN ('Draft', 'Initiation of Discussion', 'Discussion (Acquisition)', 'Under Operator Approval', 'Under SP Approval', 'Approved')
GROUP BY tsa.status AND tsa.name;""", as_dict =True)
    
@frappe.whitelist()
def get_chart():
    return frappe.db.sql(f"""SELECT 
    twh.wf_from,
    twh.`action`,
    twh.wf_to,
    SUM(twh.duration) AS total_duration
FROM `tabWorkflow History` twh
GROUP BY  twh.wf_to
ORDER BY   twh.stage_start_time  ASC """, as_dict =True)



@frappe.whitelist()
def get_average():
    average =  frappe.db.sql(f"""SELECT 
    twh.wf_from,
    AVG (twh.duration) AS avg_duration
    FROM `tabWorkflow History` twh
    GROUP BY  twh.wf_to
    ORDER BY   twh.stage_start_time  ASC 
    """, as_dict =True)
    return average