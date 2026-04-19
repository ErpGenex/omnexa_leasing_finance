from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class LeaseCase:
	principal: Decimal
	term_months: int
	lease_type: str = "FINANCE"
	discount_rate: Decimal = Decimal("0.08")
	residual_value: Decimal = Decimal("0")
	rate_type: str = "FIXED"
	sector_risk_band: str = "MEDIUM"
	delinquency_days: int = 0


@dataclass(frozen=True)
class LifecycleResult:
	risk_score: Decimal
	pricing_spread: Decimal
	recommended_stage: str
	ifrs9_stage: str
	eir: Decimal
	npv: Decimal
	irr: Decimal
	rou_asset: Decimal
	lease_liability: Decimal
	periodic_payment: Decimal
	reason_codes: list[str]
	required_controls: list[str]

	def to_dict(self) -> dict:
		return {"risk_score": str(self.risk_score), "pricing_spread": str(self.pricing_spread), "recommended_stage": self.recommended_stage, "ifrs9_stage": self.ifrs9_stage, "eir": str(self.eir), "npv": str(self.npv), "irr": str(self.irr), "rou_asset": str(self.rou_asset), "lease_liability": str(self.lease_liability), "periodic_payment": str(self.periodic_payment), "reason_codes": self.reason_codes, "required_controls": self.required_controls}


def evaluate_lease_case(c: LeaseCase) -> LifecycleResult:
	risk = Decimal("0.04")
	reasons, controls = [], ["IFRS16_RECOGNITION_CHECK", "ASSET_TITLE_CHECK", "INSURANCE_VALIDATION"]
	if c.lease_type == "OPERATING": risk += Decimal("0.01"); reasons.append("OPERATING_LEASE_PROFILE")
	if c.lease_type == "SALE_LEASEBACK": risk += Decimal("0.02"); reasons.append("SALE_LEASEBACK_STRUCTURE")
	if c.rate_type == "FLOATING": risk += Decimal("0.02"); reasons.append("FLOATING_RATE_EXPOSURE")
	if c.sector_risk_band == "HIGH": risk += Decimal("0.05"); reasons.append("HIGH_SECTOR_RISK")
	if c.delinquency_days > 30: risk += Decimal("0.06"); reasons.append("DELINQUENCY_SIGNAL"); controls.append("EARLY_WARNING_ESCALATION")
	pay = _periodic_payment(c.principal, c.discount_rate, c.term_months, c.residual_value)
	cashflows = [-c.principal] + [pay for _ in range(max(0, c.term_months - 1))] + [pay + c.residual_value]
	npv = _npv(c.discount_rate / Decimal("12"), cashflows)
	irr = _irr(cashflows)
	eir = irr * Decimal("12")
	liability = _npv(c.discount_rate / Decimal("12"), [pay for _ in range(c.term_months)])
	stage, ifrs9 = "ORIGINATION", "STAGE_1"
	if risk >= Decimal("0.18"): stage, ifrs9 = "WATCHLIST", "STAGE_3"
	elif risk >= Decimal("0.10"): stage, ifrs9 = "SERVICING", "STAGE_2"
	elif c.term_months > 120: stage = "APPROVAL"
	if not reasons: reasons.append("BASE_POLICY")
	return LifecycleResult(risk, Decimal("0.02") + risk, stage, ifrs9, eir, npv, irr, c.principal, liability, pay, reasons, sorted(set(controls)))


def _periodic_payment(principal: Decimal, annual_rate: Decimal, term_months: int, residual: Decimal) -> Decimal:
	if term_months <= 0: return Decimal("0")
	r = annual_rate / Decimal("12")
	if r <= 0: return (principal - residual) / Decimal(term_months)
	disc = (Decimal("1") + r) ** term_months
	balance = principal - (residual / disc)
	return balance * r * disc / (disc - Decimal("1"))


def _npv(rate: Decimal, cashflows: list[Decimal]) -> Decimal:
	return sum(Decimal(cf) / ((Decimal("1") + rate) ** i) for i, cf in enumerate(cashflows))


def _irr(cashflows: list[Decimal]) -> Decimal:
	rate = Decimal("0.01")
	for _ in range(40):
		f, df = Decimal("0"), Decimal("0")
		for i, cf in enumerate(cashflows):
			f += Decimal(cf) / ((Decimal("1") + rate) ** i)
			if i: df -= i * Decimal(cf) / ((Decimal("1") + rate) ** (i + 1))
		if abs(f) < Decimal("0.0000001") or df == 0: break
		rate -= f / df
	return rate
