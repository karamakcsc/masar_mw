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
def duration_chart_data():
    results =  frappe.db.sql(f"""
     SELECT 
    twh.wf_from,
    SUM(twh.duration) AS total_duration
FROM `tabWorkflow History` twh
WHERE twh.duration IS NOT NULL
GROUP BY twh.wf_from 
ORDER BY CASE 
    WHEN twh.wf_from = 'Draft' THEN 1
    WHEN twh.wf_from = 'Initiation of Discussion' THEN 2
    WHEN twh.wf_from = 'Discussion (Acquisition)' THEN 3
    WHEN twh.wf_from = 'Under Operator Approval' THEN 4
    WHEN twh.wf_from = 'Under SP Approval' THEN 5
    ELSE 6
END;
    """, as_dict =True)
    wf_from = list()
    durations_seconds= list()
    for result in results:
        wf_from.append(result.get('wf_from'))
        durations_seconds.append(float(result.get('total_duration')))
    durations_hours = [duration / 3600 for duration in durations_seconds]
    durations_hours_rounded = [round(duration, 3) for duration in durations_hours]
    return {
        'wf_from' : wf_from , 
        'durations_hours_rounded': durations_hours_rounded
    }
    



@frappe.whitelist()
def get_duration_average():
    results =  frappe.db.sql(f"""
    SELECT 
        twh.wf_from,
        AVG (twh.duration) AS avg_duration
        FROM `tabWorkflow History` twh
        GROUP BY  twh.wf_from
    ORDER BY CASE 
        WHEN twh.wf_from = 'Draft' THEN 1
        WHEN twh.wf_from = 'Initiation of Discussion' THEN 2
        WHEN twh.wf_from = 'Discussion (Acquisition)' THEN 3
        WHEN twh.wf_from = 'Under Operator Approval' THEN 4
        WHEN twh.wf_from = 'Under SP Approval' THEN 5
        ELSE 6
    END;
    """, as_dict =True)
    wf_from = list()
    duration_avg = list()
    for result in results:
        # if result.get('wf_from') is None:
        wf_from.append(result.get('wf_from'))
        if result.get('avg_duration'):
            duration_avg.append(result.get('avg_duration'))
        else:
            duration_avg.append(0.0) 
    duration_avg_hours = [ duration / 3600 for duration in  duration_avg ]
    duration_avg_hours_rounded = [round(duration, 3) for duration in duration_avg_hours]
    return {
        'wf_from' : wf_from, 
        'duration_avg_hours_rounded' : duration_avg_hours_rounded
    }

@frappe.whitelist()
def status_percentage_data():
    result = frappe.db.sql("""
        SELECT 
            COALESCE(tsa.status, 'Draft') AS status,
            COUNT(CASE WHEN tsa.status = 'Draft' THEN 1 END) AS draft_count,
            COUNT(CASE WHEN tsa.status = 'Initiation of Discussion' THEN 1 END) AS io_discussion_count,
            COUNT(CASE WHEN tsa.status = 'Discussion (Acquisition)' THEN 1 END) AS d_acquisition_count,
            COUNT(CASE WHEN tsa.status = 'Under Operator Approval' THEN 1 END) AS uo_approved_count,
            COUNT(CASE WHEN tsa.status = 'Under SP Approval' THEN 1 END) AS up_approved_count,
            COUNT(CASE WHEN tsa.status = 'Approved' THEN 1 END) AS approved_count,
            COUNT(tsa.name)  AS docname_count
        FROM 
            `tabSales Acquisition` tsa
        WHERE 
            tsa.status IN ('Draft', 'Initiation of Discussion', 'Discussion (Acquisition)', 'Under Operator Approval', 'Under SP Approval', 'Approved')
        GROUP BY 
            tsa.status AND tsa.name
    """, as_dict = True)
    status_percentage = list()
    draft_percentage = float(result[0]['draft_count']) / float(result[0]['docname_count'])
    descussion_percentage = float( result[0]['io_discussion_count']) / float(result[0]['docname_count'])
    acquisition_percentage =  float(result[0]['d_acquisition_count']) / float(result[0]['docname_count'])
    uo_approved_percentage  =  float(result[0]['uo_approved_count']) / float(result[0]['docname_count'])
    up_approved_percentage  =  float(result[0]['up_approved_count']) / float(result[0]['docname_count'])
    approved_percentage  =  float(result[0]['approved_count']) / float(result[0]['docname_count'])
    status_percentage.append(round(draft_percentage ,3))
    status_percentage.append(round(descussion_percentage,3))
    status_percentage.append(round(acquisition_percentage ,3))
    status_percentage.append(round(uo_approved_percentage,3))
    status_percentage.append(round(up_approved_percentage ,3))
    status_percentage.append(round(approved_percentage,3))

    return {
        'status' : ['Draft', 'Initiation of Discussion', 'Discussion (Acquisition)', 'Under Operator Approval', 'Under SP Approval', 'Approved'], 
        'percentages' : status_percentage
    }