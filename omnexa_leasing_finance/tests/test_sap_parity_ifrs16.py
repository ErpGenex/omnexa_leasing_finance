# Copyright (c) 2026, ErpGenEx
from decimal import Decimal

from frappe.tests.utils import FrappeTestCase

from omnexa_leasing_finance.engine.early_termination import EarlyTerminationInput, compute_early_termination
from omnexa_leasing_finance.engine.lifecycle import LeaseCase, evaluate_lease_case


class TestSapParityIfrs16(FrappeTestCase):
	def test_lease_recognition_controls(self):
		result = evaluate_lease_case(
			LeaseCase(principal=Decimal("100000"), term_months=36, lease_type="FINANCE")
		)
		self.assertIn("IFRS16_RECOGNITION_CHECK", result.required_controls)

	def test_early_termination_settlement(self):
		out = compute_early_termination(
			EarlyTerminationInput(
				remaining_liability=Decimal("50000"),
				rou_net_book=Decimal("48000"),
				months_remaining=24,
				penalty_rate=Decimal("0.02"),
			)
		)
		self.assertEqual(out.penalty_amount, Decimal("1000.00"))
		self.assertEqual(out.settlement_cash, Decimal("51000.00"))
		self.assertIn("IFRS16_EARLY_TERMINATION_REVIEW", out.ifrs16_controls)
