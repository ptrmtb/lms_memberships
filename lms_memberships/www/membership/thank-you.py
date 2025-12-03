# Copyright (c) 2024, PT Teknologi Eukarya Indonesia and contributors
# For license information, please see license.txt

import frappe
from frappe import _

no_cache = 1


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.throw(_("Please login to view this page"), frappe.PermissionError)

	membership_name = frappe.form_dict.get("membership")

	if not membership_name:
		# Try to get the most recent membership
		membership_name = frappe.db.get_value(
			"LMS User Membership",
			{"member": frappe.session.user, "status": ["in", ["Active", "Pending"]]},
			"name",
			order_by="creation desc",
		)

	if not membership_name:
		frappe.throw(_("No membership found"), frappe.DoesNotExistError)

	membership = frappe.get_doc("LMS User Membership", membership_name)

	# Verify ownership
	if membership.member != frappe.session.user:
		frappe.throw(_("You don't have permission to view this page"), frappe.PermissionError)

	context.membership = membership
	context.tier = frappe.get_doc("LMS Membership Tier", membership.membership_tier)
	context.user = frappe.get_doc("User", frappe.session.user)

	# Get accessible courses
	if context.tier.access_all_courses:
		context.courses = frappe.get_all(
			"LMS Course",
			filters={"published": 1},
			fields=["name", "title", "image", "short_introduction", "category"],
			order_by="creation desc",
			limit=12,
		)
	else:
		course_names = [c.course for c in context.tier.courses]
		if course_names:
			context.courses = frappe.get_all(
				"LMS Course",
				filters={"name": ["in", course_names], "published": 1},
				fields=["name", "title", "image", "short_introduction", "category"],
			)
		else:
			context.courses = []

	context.title = _("Welcome to Your Membership!")
	context.no_breadcrumbs = True
