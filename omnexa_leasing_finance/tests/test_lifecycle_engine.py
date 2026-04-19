from decimal import Decimal

from frappe.tests.utils import FrappeTestCase

from omnexa_leasing_finance.engine import LeaseCase, evaluate_lease_case


class TestLeasingLifecycleEngine(FrappeTestCase):
	def test_evaluate_lease_case(self):
		out = evaluate_lease_case(LeaseCase(principal=Decimal("100000"), term_months=60, residual_value=Decimal("10000")))
		self.assertIn(out.recommended_stage, ("ORIGINATION", "APPROVAL", "SERVICING", "WATCHLIST"))
		self.assertGreater(out.periodic_payment, Decimal("0"))

	def test_sale_leaseback_risk(self):
		out = evaluate_lease_case(LeaseCase(principal=Decimal("300000"), term_months=96, lease_type="SALE_LEASEBACK", rate_type="FLOATING", sector_risk_band="HIGH", delinquency_days=45))
		self.assertIn("SALE_LEASEBACK_STRUCTURE", out.reason_codes)
