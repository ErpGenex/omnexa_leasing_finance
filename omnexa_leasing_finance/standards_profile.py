from __future__ import annotations


def get_standards_profile() -> dict:
	return {
		"standards": ["IFRS 16", "IFRS 9", "ICC Best Practices", "ISO 20022", "SOX"],
		"activity_controls": ["ROU_AND_LIABILITY_RECOGNITION", "LEASE_MODIFICATION_REMEASUREMENT", "ASSET_INSURANCE_TRACKING", "RESIDUAL_VALUE_MONITORING", "MULTI_CURRENCY_VALUATION"],
	}
