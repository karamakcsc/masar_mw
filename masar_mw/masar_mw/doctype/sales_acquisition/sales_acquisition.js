// // Copyright (c) 2024, KCSC and contributors
// // For license information, please see license.txt

// frappe.ui.form.on("Sales Acquisition", {
//     before_save: function(frm) {
//         if (frm.doc.workflow_state === "Draft") {
//             frm.set_value("doc_ref", frm.doc.item_name + "-" + frm.doc.operator_name);
//         }
//     },
//     after_save: function(frm) {
//         // After saving the form
    
//         // Call the 'update_last_stage' method of the 'sales_acquisition' doctype
//         frappe.call({
//             method: "masar_mw.masar_mw.doctype.sales_acquisition.sales_acquisition.update_last_stage",
//             args: {
//                 name: frm.doc.name // Pass the name of the current document
//             },
//             callback: function(r) { // Upon receiving a response
//                 if (r.message) { // If response is not empty
//                     // Set the value of 'last_stage_update' field with the response
//                     frm.set_value('last_stage_update', r.message).then(() => {
//                         // Refresh the 'last_stage_update' field
//                         frm.refresh_field('last_stage_update');
//                     });
    
//                     // Call the 'history_wf' method of the 'sales_acquisition' doctype
//                     // frappe.call({
//                     //     method: "masar_mw.masar_mw.doctype.sales_acquisition.sales_acquisition.history_wf",
//                     //     args: {
//                     //         name: frm.doc.name // Pass the name of the current document
//                     //     },
//                     //     callback: function(response) {
//                     //         // Do something with the response if needed
//                     //         // Currently, the callback function is empty
//                     //     }
//                     // });
//                 }
//             }
//         });
//     },
    

    
//     refresh: function(frm) {
//         frm.refresh_field('last_stage_update');
//     }
// });



// frappe.ui.form.on("Sales Acquisition" , {
//     refresh:function(frm){
//         frappe.call({
// 			doc: frm.doc,
// 			method: 'wf_state',
// 		})
//     }
// })
/////////////////////////////////Start New Code //////////////////////////
// frappe.ui.form.on("Sales Acquisition", {
//     before_save: function(frm) {
//         if (frm.doc.workflow_state === "Draft") {
//             frm.set_value("doc_ref", `${frm.doc.item_name}-${frm.doc.operator_name}`);
//         }
//     },
//     after_workflow_action: function(frm) {
//         frappe.msgprint("after_workflow_action");
//         // frappe.call({
//         //     doc: frm.doc,
//         //     method: 'update_last_stage_update',
//         //     callback: function(r) {
//         //         frm.reload_doc();
//         //     }
//         // });
//         // frappe.call({
//         //     doc: frm.doc,
//         //     method: 'wf_state',
//         // });
//     },
//     after_save: function(frm) {
//         frappe.msgprint("after_save");
//         // frappe.call({
//         //     doc: frm.doc,
//         //     method: 'create_wf_history',
//         //     callback: function(r) {
//         //         if (r.message) {
//         //             frm.set_value('last_stage_update', r.message.last_stage_update).then(() => {
//         //                 frm.refresh_field('last_stage_update');
//         //             });
//         //             frm.set_value('workflow_history_ref', r.message.workflow_history_ref).then(() => {
//         //                 frm.refresh_field('workflow_history_ref');
//         //             });
//         //         }
//         //     }
//         // }).then(()=> {
//         //     frm.reload_doc();
//         // });
// }

// });
frappe.ui.form.on("Sales Acquisition", {
    refresh: function(frm) {
        frappe.call({
            doc: frm.doc,
            method: 'wf_state',
        });
    }
});
