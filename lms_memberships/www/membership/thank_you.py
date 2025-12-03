# Copyright (c) 2024, PT Teknologi Eukarya Indonesia and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import add_months, nowdate

no_cache = 1


def get_context(context):
	"""Context for thank-you page after membership subscription."""
	# Set defaults first to avoid undefined errors in template
	context.membership = None
	context.tier = None
	context.user = None
	context.courses = []
	context.error = None
	context.title = _("Membership")
	context.no_breadcrumbs = True

	try:
		if frappe.session.user == "Guest":
			context.error = _("Please login to view this page")
			frappe.local.flags.redirect_location = "/login?redirect-to=" + frappe.request.url
			raise frappe.Redirect

		membership_name = frappe.form_dict.get("membership")
		transaction_status = frappe.form_dict.get("transaction_status")

		if not membership_name:
			# Try to get the most recent membership
			membership_name = frappe.db.get_value(
				"LMS User Membership",
				{"member": frappe.session.user, "status": ["in", ["Active", "Pending"]]},
				"name",
				order_by="creation desc",
			)

		if not membership_name:
			context.error = _("No membership found. Please subscribe to a membership plan.")
			return

		# Check if membership exists
		if not frappe.db.exists("LMS User Membership", membership_name):
			context.error = _("Membership not found: {0}").format(membership_name)
			return

		membership = frappe.get_doc("LMS User Membership", membership_name)

		# Verify ownership
		if membership.member != frappe.session.user:
			context.error = _("You don't have permission to view this membership")
			return

		# Check if payment was successful via redirect parameters
		# This handles the case where Midtrans redirects back with success status
		# before the server-to-server notification arrives
		if membership.status == "Pending" and transaction_status in ["capture", "settlement"]:
			try:
				activate_membership_from_redirect(membership)
				# Reload the membership to get updated data
				membership.reload()
			except Exception as e:
				frappe.log_error(f"Failed to activate membership from redirect: {e!s}")

		context.membership = membership
		context.user = frappe.get_doc("User", frappe.session.user)

		# Get tier details
		if not frappe.db.exists("LMS Membership Tier", membership.membership_tier):
			context.error = _("Membership tier not found")
			return

		context.tier = frappe.get_doc("LMS Membership Tier", membership.membership_tier)

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

	except frappe.Redirect:
		raise
	except Exception as e:
		frappe.log_error(f"Thank you page error: {e!s}")
		context.error = _("An error occurred while loading the page. Please try again.")


def activate_membership_from_redirect(membership):
	"""Activate membership when redirected back from payment gateway with success status."""
	if membership.status != "Pending":
		return

	tier = frappe.get_doc("LMS Membership Tier", membership.membership_tier)

	today = nowdate()
	end_date = add_months(today, tier.duration_months)

	frappe.db.set_value(
		"LMS User Membership",
		membership.name,
		{
			"status": "Active",
			"start_date": today,
			"end_date": end_date,
		},
	)

	frappe.db.commit()

	# Send confirmation email
	try:
		from lms_memberships.api.membership import send_membership_confirmation

		send_membership_confirmation(membership.member, membership.name)
	except Exception as e:
		frappe.log_error(f"Failed to send membership confirmation: {e!s}")
