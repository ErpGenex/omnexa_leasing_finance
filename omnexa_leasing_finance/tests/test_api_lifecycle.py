from frappe.tests.utils import FrappeTestCase

from omnexa_core.tests.test_helpers import suppress_workflow_attach_print

suppress_workflow_attach_print()

from omnexa_leasing_finance.api import apply_contract_modification, generate_lease_schedule, post_ifrs16_entries, record_lease_payment, register_lease_asset, run_residual_risk_snapshot, upsert_lease_contract


class TestLeasingLifecycleApi(FrappeTestCase):
	def test_end_to_end_leasing_flow(self):
		contract = upsert_lease_contract(customer_name="Lease Customer", lease_type="FINANCE", principal="200000", term_months=24, discount_rate="0.09", residual_value="20000")
		contract_id = contract["contract_id"]
		self.assertTrue(contract_id)
		asset = register_lease_asset(contract_id, "AST-001", "EQUIPMENT", "200000", "20000", "INS-123")
		self.assertTrue(asset["asset_id"])
		sch = generate_lease_schedule(contract_id)
		self.assertEqual(sch["schedule_rows"], 24)
		entries = post_ifrs16_entries(contract_id)
		self.assertGreaterEqual(len(entries["posted_entries"]), 3)
		pay = record_lease_payment(contract_id, "5000")
		self.assertTrue(pay["payment_id"])
		risk = run_residual_risk_snapshot(contract_id, "0.22", 10)
		self.assertTrue(risk["risk_snapshot_id"])
		mod = apply_contract_modification(contract_id, "TERM_CHANGE", '{"term_months": 36}', "1500")
		self.assertTrue(mod["modification_log_id"])
