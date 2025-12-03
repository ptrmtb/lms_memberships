# Copyright (c) 2024, PT Teknologi Eukarya Indonesia and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LMSMembershipTier(Document):
	def validate(self):
		if self.is_default:
			# Ensure only one default tier
			existing_default = frappe.db.get_value(
				"LMS Membership Tier", {"is_default": 1, "name": ["!=", self.name]}, "name"
			)
			if existing_default:
				frappe.db.set_value("LMS Membership Tier", existing_default, "is_default", 0)
