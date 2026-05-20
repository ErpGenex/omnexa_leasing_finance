# Copyright (c) 2026, ErpGenEx
"""IFRS 16 early termination / settlement (SAP FS-CML parity) — pure functions."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class EarlyTerminationInput:
	remaining_liability: Decimal
	rou_net_book: Decimal
	months_remaining: int
	penalty_rate: Decimal = Decimal("0.02")
	unamortized_initial_direct_costs: Decimal = Decimal("0")


@dataclass(frozen=True)
class EarlyTerminationResult:
	settlement_cash: Decimal
	penalty_amount: Decimal
	rou_derecognition: Decimal
	liability_derecognition: Decimal
	profit_loss_on_termination: Decimal
	ifrs16_controls: list[str]

	def to_dict(self) -> dict:
		return {
			"settlement_cash": str(self.settlement_cash),
			"penalty_amount": str(self.penalty_amount),
			"rou_derecognition": str(self.rou_derecognition),
			"liability_derecognition": str(self.liability_derecognition),
			"profit_loss_on_termination": str(self.profit_loss_on_termination),
			"ifrs16_controls": self.ifrs16_controls,
		}


def compute_early_termination(inp: EarlyTerminationInput) -> EarlyTerminationResult:
	"""Estimate cash settlement and P&L on lessee early termination (non-posting)."""
	liability = max(Decimal("0"), inp.remaining_liability)
	penalty = (liability * inp.penalty_rate).quantize(Decimal("0.01"))
	settlement = liability + penalty
	rou = max(Decimal("0"), inp.rou_net_book)
	pl = rou - liability - inp.unamortized_initial_direct_costs
	controls = [
		"IFRS16_EARLY_TERMINATION_REVIEW",
		"LEASE_MODIFICATION_OR_TERMINATION_DOCS",
	]
	if inp.months_remaining > 12:
		controls.append("LONG_TERM_LEASE_REMEASUREMENT")
	return EarlyTerminationResult(
		settlement_cash=settlement,
		penalty_amount=penalty,
		rou_derecognition=rou,
		liability_derecognition=liability,
		profit_loss_on_termination=pl,
		ifrs16_controls=controls,
	)
