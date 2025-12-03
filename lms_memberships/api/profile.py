# Copyright (c) 2024, PT Teknologi Eukarya Indonesia and contributors
# For license information, please see license.txt

"""
Profile API overrides to add membership information to user profiles.
"""

import frappe
from frappe import _
from frappe.utils import getdate, nowdate
from lms.lms.api import get_user_info as original_get_user_info


@frappe.whitelist(allow_guest=True)
def get_user_info():
	"""Override LMS get_user_info to add membership information"""
	# Call the original function to get base data
	user_info = original_get_user_info()

	if not user_info:
		return user_info

	# Add membership information
	membership = get_user_membership_info(user_info.get("name"))
	if membership:
		user_info["membership"] = membership
		user_info["has_active_membership"] = membership.get("status") == "Active"
		user_info["is_bluechip_member"] = (
			membership.get("status") == "Active" and membership.get("tier_name") == "Bluechip Member"
		)
	else:
		user_info["membership"] = None
		user_info["has_active_membership"] = False
		user_info["is_bluechip_member"] = False

	return user_info


def get_user_membership_info(user):
	"""Get membership info for a user"""
	if not user or user == "Guest":
		return None

	membership = frappe.db.get_value(
		"LMS User Membership",
		{"member": user, "status": ["in", ["Active", "Expired"]]},
		["name", "membership_tier", "start_date", "end_date", "status"],
		as_dict=True,
		order_by="creation desc",
	)

	if not membership:
		return None

	tier = frappe.db.get_value(
		"LMS Membership Tier",
		membership.membership_tier,
		["tier_name", "description", "access_all_courses"],
		as_dict=True,
	)

	if tier:
		membership.update(tier)

	# Calculate days remaining
	if membership.end_date and membership.status == "Active":
		days_remaining = (getdate(membership.end_date) - getdate(nowdate())).days
		membership["days_remaining"] = max(0, days_remaining)
		membership["is_expiring_soon"] = days_remaining <= 30
	else:
		membership["days_remaining"] = 0
		membership["is_expiring_soon"] = False

	# Format dates for display
	if membership.start_date:
		membership["start_date_formatted"] = frappe.utils.format_date(membership.start_date)
	if membership.end_date:
		membership["end_date_formatted"] = frappe.utils.format_date(membership.end_date)

	return membership


@frappe.whitelist(allow_guest=True)
def get_profile_membership(username):
	"""Get membership info for a specific user profile"""
	if not username:
		return None

	# Get user by username
	user = frappe.db.get_value("User", {"username": username}, "name")
	if not user:
		return None

	return get_user_membership_info(user)
