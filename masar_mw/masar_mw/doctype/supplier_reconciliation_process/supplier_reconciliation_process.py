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
					row.fx_gainloss_cost_center = self.default_cost_center or frappe.throw(f"Cost Center is required in row {row.idx}.")
				if not row.fx_gainloss_description:
					row.fx_gainloss_description = f"{row.party_name} - {self.fx_description}" if self.fx_description else f"Rate @ {self.default_fx_gain_loss_} - {row.remarks}"

	def create_payment(self):
		if not self.invoices:
			frappe.throw("No invoices found to create payment entry.")

		usd_to_jod = self.get_usd_to_jod()
		suppliers = self.split_invoices_by_supplier(usd_to_jod)

		for supplier, data in suppliers.items():
			payment_entry = self.build_payment_entry(supplier, data, usd_to_jod)
			payment_entry.insert(ignore_permissions=True)
			frappe.msgprint(f"Payment Entry {payment_entry.name} created successfully for supplier {supplier}.", alert=True, indicator='green')

	def get_usd_to_jod(self):
		if self.paid_from_account_currency == "USD":
			rate = frappe.get_value("Currency Exchange", {
				"from_currency": "USD",
				"to_currency": "JOD"
			}, "exchange_rate")
			if not rate:
				frappe.throw("Please add a currency exchange from USD to JOD.")
			return rate
		return 1

	def split_invoices_by_supplier(self, exchange_rate):
		suppliers = {}

		for row in self.invoices:
			if row.party not in suppliers:
				suppliers[row.party] = {
					"references": [],
					"total_paid": 0,
					"fx_gain_loss": 0,
					"return_inv_total": 0,
					"discount_total": 0,
					"fx_account": self.default_deductions_account,
					"discount_account": self.default_discount_account,
					"cost_center": row.fx_gainloss_cost_center,
					"description": row.fx_gainloss_description,
					"discount": row.discount if row.discount else 0
				}

			suppliers[row.party]["references"].append({
				"reference_doctype": row.invoice_type,
				"reference_name": row.invoice_number,
				"total_amount": row.amount,
				"outstanding_amount": row.outstanding_amount,
				"allocated_amount": row.amount_to_pay
			})

			suppliers[row.party]["total_paid"] += row.amount_to_pay
			suppliers[row.party]["fx_gain_loss"] += row.fx_gain_loss_amount

			if row.outstanding_amount < 0:
				suppliers[row.party]["return_inv_total"] += row.amount_to_pay
			discount_amount = 0
			if row.discount:
				discount_amount = flt(row.amount_to_pay * row.fx_gain_loss_perc * (row.discount / 100), 3)
			suppliers[row.party]["discount_total"] += discount_amount
		return suppliers

	def build_payment_entry(self, supplier, data, exchange_rate):
		references = data["references"]
		total_allocated = sum(ref["allocated_amount"] for ref in references)
		
		fx_loss = data.get("fx_gain_loss", 0)
		discount_amount = data.get("discount_total", 0)
		
		fx_deduction_jod = flt(fx_loss * exchange_rate, 2)
		discount_deduction_jod = flt(discount_amount * exchange_rate, 2)
		
		fx_deduction_usd = flt(fx_deduction_jod / exchange_rate, 2)
		discount_deduction_usd = flt(discount_deduction_jod / exchange_rate, 2)
		
		paid_amount = flt(total_allocated - fx_deduction_usd - discount_deduction_usd, 2)
		
		base_paid_amount = flt(paid_amount * exchange_rate, 2)

		# final_difference = base_paid_amount - (data["total_paid"] * exchange_rate - fx_deduction_jod - discount_deduction_jod)
		# if abs(final_difference) <= 0.01:
		# 	base_paid_amount -= final_difference

		pe = frappe.new_doc("Payment Entry")
		pe.payment_type = "Pay"
		pe.posting_date = self.posting_date
		pe.company = self.company
		pe.mode_of_payment = self.mode_of_payment
		pe.party_type = "Supplier"
		pe.party = supplier
		pe.paid_amount = paid_amount
		pe.received_amount = paid_amount
		pe.base_paid_amount = base_paid_amount
		pe.base_received_amount = base_paid_amount
		pe.source_exchange_rate = exchange_rate
		pe.target_exchange_rate = exchange_rate
		pe.reference_no = self.name
		pe.reference_date = self.posting_date
		pe.paid_from = self.paid_from
		pe.paid_from_account_currency = self.paid_from_account_currency
		pe.custom_supp_recon_ref = self.name

		for ref in references:
			pe.append("references", ref)

		if fx_loss > 0:
			pe.append("deductions", {
				"account": data["fx_account"],
				"cost_center": data["cost_center"],
				"amount": -fx_deduction_jod,
				"is_exchange_gain_loss": 1,
				"description": data["description"]
			})

		if discount_amount > 0:
			pe.append("deductions", {
				"account": data["discount_account"],
				"cost_center": data["cost_center"],
				"amount": -discount_deduction_jod,
				"description": f"Discount {data['discount']}%"
			})

		return pe