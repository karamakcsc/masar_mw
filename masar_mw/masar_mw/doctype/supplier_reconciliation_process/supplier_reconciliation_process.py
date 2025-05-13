# Copyright (c) 2025, KCSC and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, fmt_money, get_link_to_form, getdate, nowdate, today

class SupplierReconciliationProcess(Document):
	def validate(self):
		self.calculate_amounts()
	def on_submit(self):
		self.create_payment()

	@frappe.whitelist()
	def get_data(self):
		temp_vo_table = frappe.db.sql("""
			-- Step 1: Create temp_vo
			CREATE TEMPORARY TABLE temp_vo (
				account VARCHAR(100),
				voucher_type VARCHAR(100),
				voucher_no VARCHAR(100),
				party_type VARCHAR(100),
				party VARCHAR(100),
				posting_date DATE,
				due_date DATE,
				currency VARCHAR(10),
				amount DECIMAL(18, 4),
				amount_in_account_currency DECIMAL(18, 4),
				remarks TEXT
			);
		""")
  
		temp_vo_data = frappe.db.sql(f"""
			-- Step 2: Populate temp_vo
			INSERT INTO temp_vo
			SELECT
				account,
				voucher_type,
				voucher_no,
				party_type,
				party,
				posting_date,
				due_date,
				account_currency AS currency,
				SUM(amount) AS amount,
				SUM(amount_in_account_currency) AS amount_in_account_currency,
				MAX(remarks) AS remarks
			FROM 
				`tabPayment Ledger Entry`
			WHERE 
				delinked = 0 
				AND company = '{self.company}' 
				AND account_type = 'Payable' 
				AND party_type = 'Supplier' 
			GROUP BY 
				voucher_type,
				voucher_no,
				party_type,
				party,
				account,
				account_currency;
		""")
  
		temp_vo_index = frappe.db.sql("""
            -- Step 3: Create index on temp_vo
			CREATE INDEX idx_temp_vo_join ON temp_vo (
				account,
				voucher_type,
				voucher_no,
				party_type,
				party
			);
		""")
  
		temp_vo_indx = frappe.db.sql("""
			CREATE INDEX idx_temp_vo_amount ON temp_vo (amount_in_account_currency);
		""")
  
		temp_ot_table = frappe.db.sql("""
            -- Step 4: Create temp_ot
			CREATE TEMPORARY TABLE temp_ot (
				account VARCHAR(100),
				voucher_type VARCHAR(100),
				voucher_no VARCHAR(100),
				party_type VARCHAR(100),
				party VARCHAR(100),
				posting_date DATE,
				due_date DATE,
				currency VARCHAR(10),
				amount DECIMAL(18, 4),
				amount_in_account_currency DECIMAL(18, 4),
				remarks TEXT
			);
		""")
  
		temp_ot_data = frappe.db.sql(f"""
            -- Step 5: Populate temp_ot
			INSERT INTO temp_ot
			SELECT 
				account,
				against_voucher_type AS voucher_type,
				against_voucher_no AS voucher_no,
				party_type,
				party,
				posting_date,
				due_date,
				account_currency AS currency,
				SUM(amount) AS amount,
				SUM(amount_in_account_currency) AS amount_in_account_currency,
				MAX(remarks) AS remarks
			FROM 
				`tabPayment Ledger Entry`
			WHERE 
				delinked = 0 
				AND company = '{self.company}' 
				AND account_type = 'Payable' 
				AND party_type = 'Supplier' 
			GROUP BY 
				against_voucher_type,
				against_voucher_no,
				party_type,
				party,
				account,
				account_currency;
		""")
  
		temp_ot_index = frappe.db.sql("""
            -- Step 6: Create index on temp_ot
			CREATE INDEX idx_temp_ot_join ON temp_ot (
				account,
				voucher_type,
				voucher_no,
				party_type,
				party
			);
		""")
  
		temp_ot_indx = frappe.db.sql("""
			CREATE INDEX idx_temp_ot_amount ON temp_ot (amount_in_account_currency);
		""")
  
		data = frappe.db.sql(f"""
            -- Step 7: Final query using temporary tables
			SELECT 
				vo.account,
				vo.voucher_type,
				vo.voucher_no,
				vo.party_type,
				vo.party,
				ts.supplier_name AS party_name,
				vo.posting_date,
				vo.amount AS invoice_amount,
				vo.amount_in_account_currency AS invoice_amount_in_account_currency,
				ot.amount AS outstanding,
				ot.amount_in_account_currency AS outstanding_in_account_currency,
				vo.amount - IFNULL(ot.amount, 0) AS paid_amount,
				vo.amount_in_account_currency - IFNULL(ot.amount_in_account_currency, 0) AS paid_amount_in_account_currency,
				vo.due_date,
				vo.currency,
				vo.remarks
			FROM 
				temp_vo vo
			LEFT JOIN 
				temp_ot ot 
				ON vo.account = ot.account 
				AND vo.voucher_type = ot.voucher_type 
				AND vo.voucher_no = ot.voucher_no 
				AND vo.party_type = ot.party_type 
				AND vo.party = ot.party
			LEFT JOIN 
				tabSupplier ts ON ts.name = vo.party
			HAVING 
				outstanding_in_account_currency <> 0;
		""", as_dict=True)
  
		drop_temp_tables = frappe.db.sql("""
			DROP TEMPORARY TABLE IF EXISTS temp_vo;
		""")
  
		drop_temp_table = frappe.db.sql("""
			DROP TEMPORARY TABLE IF EXISTS temp_ot;
  		""")

		return data

	def calculate_amounts(self):
		if self.invoices:
			for row in self.invoices:
				# if row.amount_to_pay > row.outstanding_amount:
				# 	frappe.throw(f"Amount to pay can't be more than outstanding amount in row {row.idx}.")
				if not row.amount_to_pay:
					frappe.throw(f"Amount to pay is required in row {row.idx}.")
				if not row.fx_gain_loss_perc and not self.default_fx_gain_loss_:
					frappe.throw(f"FX Gain/Loss Percentage is required in row {row.idx}.")
				if not row.fx_gain_loss_perc and self.default_fx_gain_loss_:
					row.fx_gain_loss_perc = self.default_fx_gain_loss_
				if row.amount_to_pay and row.fx_gain_loss_perc:
					row.net_payable = abs(row.amount_to_pay) * row.fx_gain_loss_perc
					row.fx_gain_loss_amount = abs(row.amount_to_pay) - row.net_payable
				if not row.fx_gainloss_cost_center:
					row.fx_gainloss_cost_center = self.default_cost_center
				if not row.fx_gainloss_description:
					row.fx_gainloss_description = row.party_name + " - " + self.fx_description + " - " + row.remarks
					
	def create_payment(self):
		if self.invoices:
			suppliers = {}
			usd_jod = frappe.get_value("Currency Exchange", {
				"from_currency": "USD",
				"to_currency": "JOD"
			}, "exchange_rate") if self.paid_from_account_currency == "USD" else 1

			if not usd_jod:
				frappe.throw("Please add a currency exchange from USD to JOD.")

			# jod_usd = frappe.get_value("Currency Exchange", {
			# 	"from_currency": "JOD",
			# 	"to_currency": "USD"
			# }, "exchange_rate")
   
			for supp in self.invoices:
				if supp.party not in suppliers:
					suppliers[supp.party] = {
						"references": [],
						"total_paid": 0,
						"total_fx_gain_loss": 0,
						"cost_center": supp.fx_gainloss_cost_center,
						"description": supp.fx_gainloss_description,
						"return_inv": 0
					}
				
				suppliers[supp.party]["references"].append({
					"reference_doctype": supp.invoice_type,
					"reference_name": supp.invoice_number,
					"total_amount": supp.amount,
					"outstanding_amount": supp.outstanding_amount,
					"allocated_amount": supp.amount_to_pay
				})
				
				suppliers[supp.party]["total_paid"] += supp.amount_to_pay
				suppliers[supp.party]["total_fx_gain_loss"] += supp.fx_gain_loss_amount
				if supp.outstanding_amount < 0:
					suppliers[supp.party]["return_inv"] += supp.amount_to_pay

			
			for supplier, data in suppliers.items():
				total_paid = flt(data["total_paid"], 3)
				total_fx_gain_loss = flt(data["total_fx_gain_loss"], 3)
				if data["return_inv"]:
					total_paid_with_fx = flt(abs(total_paid), 3)
				else:
					total_paid_with_fx = flt(total_paid + total_fx_gain_loss * -1, 3)

				new_payment = frappe.new_doc("Payment Entry")
				new_payment.payment_type = "Pay"
				new_payment.posting_date = self.posting_date
				new_payment.company = self.company
				new_payment.mode_of_payment = "Wire Transfer"
				new_payment.party_type = "Supplier"
				new_payment.party = supplier
				new_payment.paid_amount = total_paid_with_fx
				new_payment.source_exchange_rate = usd_jod
				new_payment.reference_no = self.name
				new_payment.reference_date = self.posting_date
				new_payment.received_amount = total_paid_with_fx
				new_payment.paid_from = self.paid_from
				new_payment.paid_from_account_currency = self.paid_from_account_currency
				new_payment.custom_supp_recon_ref = self.name
				
				for ref in data["references"]:
					new_payment.append("references", ref)
				
				if not data["return_inv"]:
					if data["total_fx_gain_loss"] > 0:
						new_payment.append("deductions", {
							"account": "690000003 - FX gain / loss - MWJ",
							"cost_center": data["cost_center"],
							"amount": flt((data["total_fx_gain_loss"] * usd_jod) * -1, 3),
							"description": data["description"]
						})
     
				new_payment.save(ignore_permissions=True)
				# new_payment.submit()
				frappe.msgprint(f"Payment Entry {new_payment.name} created successfully for supplier {supplier}.", alert=True, indicator='green')
		else:
			frappe.throw("No invoices found to create payment entry.")