
frappe.pages['workflow-summary'].on_page_load = function (wrapper) {
	new MyPage(wrapper);
}
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
		let card_data = function(){
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

				}
			});
		}
		let duration_chart = function() {
			frappe.call({
				method: 'masar_mw.masar_mw.page.workflow_summary.workflow_summary.duration_chart_data',
				callback: function(r) {
					let wf_from = r.message.wf_from;
					let duration = r.message.durations_hours_rounded;
					const data = {
						labels: wf_from,
						datasets: [
							{
								name: 'Duration Hours',
								values: duration
							}
						]
					};
					const chart = new frappe.Chart("#duration_chart", {  
								title: "Workflow History Chart",
								data: data,
								type: 'bar',
								height: 300,
								// colors: ['green'],
							})
				
				}
			});
		}

		let duration_avg_chart = function() {
			frappe.call({
				method: 'masar_mw.masar_mw.page.workflow_summary.workflow_summary.get_duration_average',
				callback: function(r) {
					let wf_from = r.message.wf_from;
					let duration_avg = r.message.duration_avg_hours_rounded;
					const data = {
						labels: wf_from,
						datasets: [
							{
								name: 'History Average',
								values: duration_avg
							}
						]
					};
					const chart = new frappe.Chart("#duration_avg_chart", {  
								title: "Stages Percentage",
								data: data,
								type: 'percentage',
								height: 300,
								// colors: ['#7cd6fd', '#743ee2'],
							})
				
				}
			});
		}
		let status_percentage_chart = function() {
			frappe.call({
				method: 'masar_mw.masar_mw.page.workflow_summary.workflow_summary.status_percentage_data',
				callback: function(r) {
					let status = r.message.status;
					let percentages = r.message.percentages;
					const data = {
						labels: status,
						datasets: [
							{
								name: 'Status Percentage',
								values: percentages
							}
						]
					};
					const chart = new frappe.Chart("#status_per_chart", {  
								title: " ",
								data: data,
								type: 'pie',
								height: 400,
								width:200,
								// colors: ['#7cd6fd', '#743ee2'],
							})
				
				}
			});
		}
		$(frappe.render_template(frappe.saving_funds.body, this)).appendTo(this.page.main)
		card_data();
		duration_chart();
		duration_avg_chart();
		status_percentage_chart();
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
body += '		</div>'
body += '	</div>' 
body += '<div id="duration_chart"></div>'
body += '<div id="line-chart"></div>'
body += '<div id="duration_avg_chart"></div>'
body += '<div id="line-chart"></div>'
body += '<div id="status_per_chart"></div>'
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