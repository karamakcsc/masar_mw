// frappe.pages['workflow-summary'].on_page_load = function (wrapper) {
// 	var page = frappe.ui.make_app_page({
// 		parent: wrapper,
// 		title: 'Workflow Summary',
// 		single_column: true
// 	});
// }

frappe.pages['workflow-summary'].on_page_load = function (wrapper) {
	new MyPage(wrapper);
}

// MyPage = Class.extend({
// 	init: function (wrapper) {
// 		this.page = frappe.ui.make_app_page({
// 			parent: wrapper,
// 			title: 'Workflow Summary',
// 			single_column: true
// 		});
// 		this.make();
// 	},
// 	make: function () {
// 		var draft_count = 0;
// 		var io_discussion_count = 0;
// 		var d_acquisition_count = 0;
// 		var uo_approved_count = 0;
// 		var up_approved_count = 0;
// 		var approved_count = 0;

// 		frappe.call({
// 						method: "masar_mw.masar_mw.page.workflow_summary.workflow_summary.get_count",
// 						//method: "masar_mw.masar_mw.masar_mw.page.workflow_summary.workflow_summary.get_count",
// 						callback: function (r) {
// 							console.log("r", r.message);
// 							$.each(r.message, function (i, d) {
// 								total_emp_contr += parseFloat(d.total_employee_contr.toFixed(3));
// 								total_bank_contr += parseFloat(d.total_bank_contr.toFixed(3));
// 								total_contr += parseFloat(d.total_contr.toFixed(3));
// 								total_emp_contr_pl += parseFloat(d.total_employee_pl.toFixed(3));
// 								total_bank_contr_pl += parseFloat(d.total_bank_pl.toFixed(3));
// 								total_contr_pl += parseFloat(d.total_pl.toFixed(3));
// 								total_rights += parseFloat(d.total_right.toFixed(3));
// 								chart_emps.push(d["employee_name"])
// 								chart_emp_contr.push(d["total_employee_contr"])
// 								chart_bank_contr.push(d["total_bank_contr"])
// 							});
// 	}
// });
// }})

MyPage = Class.extend({
	init: function (wrapper) {
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'Workflow Summary',
			single_column: true
		});
		this.make();
	},
	make: function () {
		var draft_count = 0;
		var io_discussion_count = 0;
		var d_acquisition_count = 0;
		var uo_approved_count = 0;
		var up_approved_count = 0;
		var approved_count = 0;
		var docname_count = 0;
		let me = $(this);
		frappe.call({
			method: "masar_mw.masar_mw.page.workflow_summary.workflow_summary.get_count",
			callback: function (r) {
				$.each(r.message, function (i, d) {
					draft_count = parseFloat(d.draft_count.toFixed());
					io_discussion_count = parseFloat(d.io_discussion_count.toFixed());
					d_acquisition_count = parseFloat(d.d_acquisition_count.toFixed(3));
					docname_count = parseFloat(d.docname_count.toFixed(3));
					uo_approved_count = parseFloat(d.uo_approved_count.toFixed(3));
					up_approved_count = parseFloat(d.up_approved_count.toFixed(3));
					approved_count = parseFloat(d.approved_count.toFixed(3));
				});
				$("#draft_count")[0].innerText = draft_count.toFixed(3)
				$("#io_discussion_count")[0].innerText = io_discussion_count.toFixed(3)
				$("#d_acquisition_count")[0].innerText = d_acquisition_count.toFixed(3)
				$("#docname_count")[0].innerText = docname_count.toFixed(3)
				$("#uo_approved_count")[0].innerText = uo_approved_count.toFixed(3)
				$("#up_approved_count")[0].innerText = up_approved_count.toFixed(3)
				$("#approved_count")[0].innerText = approved_count.toFixed(3)


				
				bar_chart()

			}
		});
		$(document).ready(function () {
			frappe.call({
				method: "masar_mw.masar_mw.page.workflow_summary.workflow_summary.get_average",
				callback: function (r) {
					var from = []; 
					var avg = [];
					$.each(r.message, function (i, d) {
						from.push(d.wf_from); 
						avg.push(parseFloat(d.avg_duration.toFixed(3)));
					});
			
					var chart = new frappe.Chart("#chart_bar", { 
						data: {
							labels: from,
							datasets: [
								{
									name: "Workflow Average",
									values: avg
								}
							]
						},
						type: 'bar',
						height: 250, 
						colors: ['blue'], 
						axisOptions: {
							xAxisMode: 'tick',
							xIsSeries: 1
						}
					});
			
					$("#wf_from")[0].innerText = from[0];
					$("#avg_duration")[0].innerText = avg[0];
				}
            });
        });
		
		let bar_chart = function () { // equals to -> function page_chart(){

			const data = {
				labels: ['Draft', 'Initiation of Discussion', 'Discussion (Acquisition)', 'Under Operator Approval' , 'Under SP Approval'],
				datasets: [
					// {
					// 	name: 'Dataset 1',
					// 	values: [10, 20, 30]
					// },
					{
						name: 'History Average',
						values: [15, 25, 35,10,50]
					}
				]
			};


			const chart = new frappe.Chart("#chart", {  // or a DOM element,
				// new Chart() in case of ES6 module with above usage
				title: "Workflow History Chart",
				data: data,
				type: 'bar', // 'axis-mixed' or 'bar', 'line', 'scatter', 'pie', 'percentage'
				height: 250,
				colors: ['#7cd6fd', '#743ee2'],
				// tooltipOptions: {
				// 		//formatTooltipX: (d) => (d).toUpperCase(),
				// 		formatTooltipY: (d) => d
				// }


			})

		}



		$(frappe.render_template(frappe.saving_funds.body, this)).appendTo(this.page.main)
		bar_chart()

	}
})


let body = '<script src="https://unpkg.com/frappe-charts@latest"></script>'
body += '<div class="widget-group ">'
body += '			<div class="widget-group-head">'
body += '				<div class="widget-group-control"></div>'
body += '			</div>'
body += '			<div class="widget-group-body grid-col-3">'

body += '				<div class="widget widget-shadow number-widget-box" data-widget-name="draft_count">'
body += '					<div class="widget-head">'
body += '					<div class="widget-label">'
body += '						<div class="widget-title">'
body += '							<div class="number-label">Draft</div>'
body += '						</div>'
body += '						<div class="widget-subtitle"></div>'
body += '					</div>'
body += '				</div>'
body += '				<div class="widget-body">'
body += '					<div class="widget-content">'
body += '						<div class="number" style="color:undefined" id="draft_count"> {draft_count} </div>'
body += '					</div>'
body += '				</div>'
body += '				<div class="widget-footer"></div>'
body += '			</div>'

body += '				<div class="widget widget-shadow number-widget-box" data-widget-name="io_discussion_count">'
body += '					<div class="widget-head">'
body += '					<div class="widget-label">'
body += '						<div class="widget-title">'
body += '							<div class="number-label">Initiation of Discussion</div>'
body += '						</div>'
body += '						<div class="widget-subtitle"></div>'
body += '					</div>'
body += '				</div>'
body += '				<div class="widget-body">'
body += '					<div class="widget-content">'
body += '						<div class="number" style="color:undefined" id="io_discussion_count"> {io_discussion_count} </div>'
body += '					</div>'
body += '				</div>'
body += '				<div class="widget-footer"></div>'
body += '			</div>'

body += '				<div class="widget widget-shadow number-widget-box" data-widget-name="d_acquisition_count">'
body += '					<div class="widget-head">'
body += '					<div class="widget-label">'
body += '						<div class="widget-title">'
body += '							<div class="number-label">Discussion (Acquisition)</div>'
body += '						</div>'
body += '						<div class="widget-subtitle"></div>'
body += '					</div>'
body += '				</div>'
body += '				<div class="widget-body">'
body += '					<div class="widget-content">'
body += '						<div class="number" style="color:undefined" id="d_acquisition_count"> {d_acquisition_count} </div>'
body += '					</div>'
body += '				</div>'
body += '				<div class="widget-footer"></div>'
body += '			</div>'

body += '				<div class="widget widget-shadow number-widget-box" data-widget-name="docname_count">'
body += '					<div class="widget-head">'
body += '					<div class="widget-label">'
body += '						<div class="widget-title">'
body += '							<div class="number-label">Total Document</div>'
body += '						</div>'
body += '						<div class="widget-subtitle"></div>'
body += '					</div>'
body += '				</div>'
body += '				<div class="widget-body">'
body += '					<div class="widget-content">'
body += '						<div class="number text-danger" style="color:undefined" id="docname_count"> {docname_count} </div>'
body += '					</div>'
body += '				</div>'
body += '				<div class="widget-footer"></div>'
body += '			</div>'


body += '				<div class="widget widget-shadow number-widget-box" data-widget-name="uo_approved_count">'
body += '					<div class="widget-head">'
body += '					<div class="widget-label">'
body += '						<div class="widget-title">'
body += '							<div class="number-label">Under Operator Approval</div>'
body += '						</div>'
body += '						<div class="widget-subtitle"></div>'
body += '					</div>'
body += '				</div>'
body += '				<div class="widget-body">'
body += '					<div class="widget-content">'
body += '						<div class="number" style="color:undefined" id="uo_approved_count"> {uo_approved_count} </div>'
body += '					</div>'
body += '				</div>'
body += '				<div class="widget-footer"></div>'
body += '			</div>'



body += '				<div class="widget widget-shadow number-widget-box" data-widget-name="up_approved_count">'
body += '					<div class="widget-head">'
body += '					<div class="widget-label">'
body += '						<div class="widget-title">'
body += '							<div class="number-label">Under SP Approval</div>'
body += '						</div>'
body += '						<div class="widget-subtitle"></div>'
body += '					</div>'
body += '				</div>'
body += '				<div class="widget-body">'
body += '					<div class="widget-content">'
body += '						<div class="number" style="color:undefined" id="up_approved_count"> {up_approved_count} </div>'
body += '					</div>'
body += '				</div>'
body += '				<div class="widget-footer"></div>'
body += '			</div>'

body += '				<div class="widget widget-shadow number-widget-box" data-widget-name="approved_count">'
body += '					<div class="widget-head">'
body += '					<div class="widget-label">'
body += '						<div class="widget-title">'
body += '							<div class="number-label">Approved</div>'
body += '						</div>'
body += '						<div class="widget-subtitle"></div>'
body += '					</div>'
body += '				</div>'
body += '				<div class="widget-body">'
body += '					<div class="widget-content">'
body += '						<div class="number" style="color:undefined" id="approved_count"> {approved_count} </div>'
body += '					</div>'
body += '				</div>'
body += '				<div class="widget-footer"></div>'
body += '			</div>'

// body += '				<div class="widget widget-shadow number-widget-box" data-widget-name="total contr pl">'
// body += '					<div class="widget-head">'
// body += '					<div class="widget-label">'
// body += '						<div class="widget-title">'
// body += '							<div class="number-label">Total P&L Contributions</div>'
// body += '						</div>'
// body += '						<div class="widget-subtitle"></div>'
// body += '					</div>'
// body += '				</div>'
// body += '				<div class="widget-body">'
// body += '					<div class="widget-content">'
// body += '						<div class="number" style="color:undefined" id="total_contr_pl"> 0</div>'
// body += '					</div>'
// body += '				</div>'
// body += '				<div class="widget-footer"></div>'
// body += '			</div>'


body += '		</div>'
body += '	</div>'
//////////////// START mahmoud
body += '	<div id="chart_bar"></div>'
body += '	<div>'
body += '		<p><span id="wf_from"></span></p> '
body += '		<p><span id="avg_duration"></span></p>'
body += '	</div>'
/////////// END 
body += '<div id="chart"></div>'
body += '<div id="line-chart"></div>'

frappe.saving_funds = {
	body: body
}


frappe.dom.set_style(`
:root {
  --charts-label-color: #f4f5f6;
  --charts-axis-line-color: #f4f5f6;
  --charts-tooltip-title: var(--charts-label-color);
  --charts-tooltip-label: var(--charts-label-color);
  --charts-tooltip-value: yellow;
  --charts-tooltip-bg: #f4f5f6;
  --charts-dataset-circle-stroke: #f4f5f6;
  --charts-legend-label: #959da5;
  --charts-legend-value: var(--charts-label-color);
}

.graph-svg-tip{background:#959da5;}


.graph-svg-tip.comparison li .tooltip-legend {
  width: 12px;
  margin-right: 8px;
}
`);