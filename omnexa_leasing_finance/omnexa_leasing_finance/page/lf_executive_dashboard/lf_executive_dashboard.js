frappe.pages["lf-executive-dashboard"].on_page_load = function (wrapper) {
	function boot() {
		if (window.omnexa_finance && omnexa_finance.bootPortalPage) {
			omnexa_finance.bootPortalPage(wrapper, "lf-executive-dashboard");
			return;
		}
		frappe.require("/assets/omnexa_core/js/finance_portal_page_boot.js", function () {
			omnexa_finance.bootPortalPage(wrapper, "lf-executive-dashboard");
		});
	}
	boot();
};
