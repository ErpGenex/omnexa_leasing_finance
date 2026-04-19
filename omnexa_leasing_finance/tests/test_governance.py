from frappe.tests.utils import FrappeTestCase

from omnexa_leasing_finance.governance import create_audit_snapshot, submit_policy_version


class TestLeasingGovernance(FrappeTestCase):
	def test_submit_policy_and_snapshot(self):
		submit_policy_version("omnexa_leasing_finance", "Lease Risk Policy", "v1", {"max_term": 120})
		s = create_audit_snapshot("omnexa_leasing_finance", "lease_eval", {"a": 1}, {"b": 2})
		self.assertIn("snapshot_hash", s)
