// Copyright (c) 2024, KCSC and contributors
// For license information, please see license.txt

frappe.query_reports["Workflow History"] = {
    "filters": [
        {
            "fieldname": "docname",
            "label": __("Document Name"),
            "fieldtype": "Link",
            "options": "Sales Acquisition",
            "width": 100,
            "reqd": 0
        },
        {
            "fieldname": "operator_name",
            "label": __("Operator Name"),
            "fieldtype": "Link",
            "options": "Operator",
            "width": 100,
            "reqd": 0
        },
        {
            "fieldname": "customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer",
            "width": 150,
            "reqd": 0
        },
        {
            "fieldname": "from",
            "label": __("From Date"),
            "fieldtype": "Date",
            "width": 80,
            "reqd": 1,
            "default": frappe.datetime.year_start()
        },
        {
            "fieldname": "to",
            "label": __("To Date"),
            "fieldtype": "Date",
            "width": 80,
            "reqd": 1,
            "default": frappe.datetime.year_end()
        },
        {
            "fieldname": "operator_country",
            "label": __("Operator Country"),
            "fieldtype": "Link",
            "options": "Country",
            "width": 100,
            "reqd": 0
        },
        {
            "fieldname": "wf_from",
            "label": __("Workflow From"),
            "fieldtype": "Select",
            "options": "\nDraft\nInitiation of Discussion\nDiscussion (Acquisition)\nUnder Operator Approval\nUnder SP Approval\nApproved",
            "width": 100,
            "reqd": 0
        },
        {
            "fieldname": "action",
            "label": __("Action Type"),
            "fieldtype": "Select",
            "options": "\nReview\nApprove\nFinal Approval\nFeedback\nReject",
            "width": 100,
            "reqd": 0
        },
        {
            "fieldname": "wf_to",
            "label": __("Workflow To"),
            "fieldtype": "Select",
            "options": "\nDraft\nInitiation of Discussion\nDiscussion (Acquisition)\nUnder Operator Approval\nUnder SP Approval\nApproved\nUnspecified",
            "width": 100,
            "reqd": 0
        },
        {
            "fieldname": "role",
            "label": __("User Role"),
            "fieldtype": "Link",
            "options": "Role",
            "width": 100,
            "reqd": 0,
			"get_query": function() {
                return {
                    filters: {
                        'disabled': 0
                    }
                }
            }
        },
        {
            "fieldname": "wf_modified_by",
            "label": __("Modified By"),
            "fieldtype": "Link",
            "options": "User",
            "width": 100,
            "reqd": 0,
            "get_query": function() {
                return {
                    filters: {
                        'enabled': 1
                    }
                }
            }
        }
    ]
};
