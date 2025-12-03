# Copyright (c) 2024, PT Teknologi Eukarya Indonesia and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_months, getdate, nowdate


class LMSUserMembership(Document):
	def validate(self):
		self.validate_dates()
		self.set_status()

	def validate_dates(self):
		if self.start_date and self.end_date:
			if getdate(self.start_date) > getdate(self.end_date):
				frappe.throw(_("End Date cannot be before Start Date"))

	def set_status(self):
		if self.status == "Cancelled":
			return

		today = getdate(nowdate())

		if not self.start_date:
			self.status = "Pending"
		elif getdate(self.start_date) > today:
			self.status = "Pending"
		elif self.end_date and getdate(self.end_date) < today:
			self.status = "Expired"
		else:
			self.status = "Active"

	def before_save(self):
		# Calculate end_date based on membership tier duration
		if self.start_date and self.membership_tier and not self.end_date:
			duration = frappe.db.get_value("LMS Membership Tier", self.membership_tier, "duration_months")
			if duration:
				self.end_date = add_months(self.start_date, duration)


def update_expired_memberships():
	"""Scheduled task to update expired memberships"""
	today = nowdate()

	expired_memberships = frappe.get_all(
		"LMS User Membership", filters={"status": "Active", "end_date": ["<", today]}, pluck="name"
	)

	for membership in expired_memberships:
		frappe.db.set_value("LMS User Membership", membership, "status", "Expired")

	if expired_memberships:
		frappe.db.commit()
