# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt
from datetime import datetime
from datetime import datetime, timedelta
import time
import threading
import json
import frappe
from frappe.model.document import Document


class SalesAcquisition(Document):
    @frappe.whitelist()
    def wf_state(self):
        self.wf_refresh = self.status
        self.set('wf_refresh', self.status)
    def validate(self):
        if self.is_saved == 0 :
            self.naming()


    def naming(self):
         self.db_set('doc_ref', f"{self.item_name} {self.operator_name}")

    def on_update(self):
        
        if self.is_saved == 0 :
            status = frappe.db.sql("""SELECT state FROM `tabWorkflow Document State` 
                                WHERE idx=1 GROUP BY state""", as_dict=True)
            if (self.status != self.wf_refresh or self.status != status):
                self.create_wf_history()
        elif self.is_saved == 1 :
            if (self.status != self.wf_refresh):
                self.update_last_stage_update()
        self.wf_refresh = str(self.status)
        self.db_set('wf_refresh', str(self.status))

    @frappe.whitelist()
    def create_wf_history(self):
        wfh = frappe.new_doc('Workflow History')

        wfh.update({
            'wf_creation': self.creation,
            'wf_modified': self.modified,
            'wf_modified_by': self.modified_by,
            'owner_user': self.owner,
            'wf_status': self.docstatus,
            'docname': self.name,
            'ref_doctype': self.doctype,
            'wf_from': self.status,
            'stage_start_time': self.created_time
        })
        wfh.insert(ignore_permissions=True)
        self.db_set('last_stage_update', (self.modified))
        self.db_set('workflow_history_ref', str(wfh.name))
        self.db_set('is_saved' , 1 )
        self.db_update()
        frappe.db.commit()
        return {
            'last_stage_update':str(self.modified),
            'workflow_history_ref' : str(wfh.name), 
        }
    @frappe.whitelist()
    def update_last_stage_update(self):
        old_doc = frappe.get_doc('Workflow History', self.workflow_history_ref)
        time_from = old_doc.stage_start_time
        time_to = datetime.strptime(str(self.modified), "%Y-%m-%d %H:%M:%S.%f")
        duration_time = time_to - time_from
        duration_in_seconds = duration_time.total_seconds()
        action = frappe.db.sql("""
        SELECT twt.`action` 
        FROM `tabWorkflow Transition` twt 
        WHERE twt.state =%s AND twt.next_state =%s
        """ , (old_doc.wf_from,self.status) , as_dict= True)
        if  action:
            action = action[0]['action']
        old_doc.update({
            'stage_end_time': str(self.modified),
            'wf_to': self.status,
            'wf_status': self.docstatus,
            'duration': duration_in_seconds,
            'action':action 
        })
        old_doc.save()
        frappe.db.commit()
        state =frappe.db.sql("""SELECT state  FROM `tabWorkflow Document State` 
            WHERE doc_status = 1     
            """,as_dict = True)[0]['state']
        if self.status != state:
            new_doc = frappe.new_doc('Workflow History')
            new_doc.update({
                'wf_creation': self.creation,
                'wf_modified': self.modified,
                'wf_modified_by': self.modified_by,
                'owner_user': self.owner,
                'wf_status': self.docstatus,
                'docname': self.name,
                'ref_doctype': self.doctype,
                'wf_from': self.status,
                'stage_start_time': self.last_stage_update
            })
            new_doc.insert(ignore_permissions=True)
            frappe.db.commit()
            self.db_set('workflow_history_ref', str(new_doc.name))
            

        self.last_stage_update = (self.modified)
        self.db_set('last_stage_update', (self.modified))
        self.db_update()





            


