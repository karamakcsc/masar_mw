# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt
from datetime import datetime
from datetime import datetime, timedelta
import time
import threading
import json
import frappe
from frappe.model.document import Document

# class SalesAcquisition(Document):
#     def onload(self):
#         self.wf_load = self.workflow_state
#         # frappe.msgprint(str(self.wf_load))
#     def after_save(self, update_modified=False):
#         super().after_save(update_modified=update_modified)

#         # Call the history_wf function after the after_save is completed
#         history_wf(self.name)

    # def on_update(self):
    #     self.update_last_stage_update()
        # threading.Thread(target=history_wf(self.name)).start()
    # def on_change(self):
    # # def execute_history_wf(self):
    #     if self.status != self.wf_refresh :
    #         history_wf(self.name)

#     @frappe.whitelist()
#     def wf_state(self):
#         self.wf_refresh = self.status
#         self.set('wf_refresh' ,self.status )


#     def update_last_stage_update(self):
#         # frappe.msgprint("hello")
#         status =frappe.db.sql("""SELECT idx ,state from `tabWorkflow Document State` twds 
#             WHERE idx=1 GROUP BY state""",as_dict = True)[0]['state']
#         # if self.status != "Draft":
#         if self.status != self.wf_refresh or self.status == status:
#             # doc = frappe.get_doc("Sales Acquisition", self.name)
#             self.last_stage_update = str(self.modified)
#             self.db_update()
#             # self.db_set('last_stage_update', str(self.modified))
#             # self.save()
#             # frappe.msgprint("version")
            

# @frappe.whitelist()
# def update_last_stage(name):
#         result = frappe.db.sql(f"""
#               select tsa.modified
#                 from `tabSales Acquisition` tsa
#                 where name= '{name}' """, as_dict= True)
#         modified = result[0]['modified']
#         doc = frappe.get_doc("Sales Acquisition", name)
#         doc.last_stage_update = str(modified)
#         doc.db_update()
#         # frappe.msgprint("version out class")
#         return str(modified)



# @frappe.whitelist()
# def history_wf(name):
#     # frappe.msgprint("history_wf")
#     results = frappe.db.sql("""
#         SELECT name, creation, modified, modified_by, owner, docstatus, ref_doctype, docname, data
#         FROM `tabVersion` tv 
#         WHERE docname = %s
#         ORDER BY creation DESC
#         LIMIT 1;
#     """, (name), as_dict=True)
    
#     if results:
#         result = results[0]
#         if result.get('ref_doctype') in ['Sales Acquisition', 'Kanban Board']:
#             wf_name = result.get('name')
#             creation = result.get('creation')
#             modified = result.get('modified')
#             modified_by = result.get('modified_by')
#             owner = result.get('owner')
#             docstatus = result.get('docstatus')
#             docname = result.get('docname')
#             ref_doctype = result.get('ref_doctype')

#             str_data = result.get('data')
#             all_data = json.loads(str_data)

#             wf_from = None
#             wf_to = None
#             time_from = None
#             time_to = None

#             for key, value in all_data.items():
#                 if key == 'changed':
#                     for lsts in value:
#                         if lsts[0] == "status":
#                             wf_from = lsts[1]
#                             wf_to = lsts[2]
#                         elif lsts[0] == 'last_stage_update':
#                             time_from_str = lsts[1]
#                             time_to_str = lsts[2]
#                             time_from = datetime.strptime(time_from_str, "%d-%m-%Y %H:%M:%S")
#                             time_to = datetime.strptime(time_to_str, "%d-%m-%Y %H:%M:%S")

#             if time_from and time_to:
#                 duration_time = time_to - time_from
#             else:
#                 duration_time = None
#             if wf_from and wf_to :
#                 doc = frappe.new_doc('Workflow History')
#                 doc.wf_parent = wf_name
#                 doc.wf_creation = creation
#                 doc.wf_modified = modified
#                 doc.wf_modified_by = modified_by
#                 doc.owner_user = owner
#                 doc.wf_status = docstatus
#                 doc.docname = docname
#                 doc.ref_doctype = ref_doctype
#                 doc.wf_from = wf_from
#                 doc.wf_to = wf_to
#                 doc.stage_start_time =time_from 
#                 doc.stage_end_time = time_to
#                 if duration_time:
#                     duration_in_seconds = duration_time.total_seconds()
#                     doc.duration = duration_in_seconds
#                 doc.insert(ignore_permissions=True)
#                 # frappe.msgprint(f"{str(time_from)}  ,    {str(time_to)} , {str(duration_in_seconds)}")
#                 frappe.db.commit()
#             else:
#                 frappe.throw("The provided document name does not belong to 'Sales Acquisition' or 'Kanban Board'.")
#     else:
#         frappe.throw("No record found with the provided document name.")


######################################Start New Code##########

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





            


