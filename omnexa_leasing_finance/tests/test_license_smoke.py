from frappe.tests.utils import FrappeTestCase

from omnexa_leasing_finance import hooks, license_gate


class TestLeasingFinanceLicenseSmoke(FrappeTestCase):
	def test_license_gate_is_wired(self):
		self.assertEqual(hooks.before_request, ["omnexa_leasing_finance.license_gate.before_request"])
		self.assertEqual(license_gate._APP, "omnexa_leasing_finance")
