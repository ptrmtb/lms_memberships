# Copyright (c) 2024, PT Teknologi Eukarya Indonesia and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import add_months, getdate, nowdate


@frappe.whitelist(allow_guest=True)
def get_membership_tiers():
	"""Get all active membership tiers"""
	tiers = frappe.get_all(
		"LMS Membership Tier",
		filters={"is_active": 1},
		fields=[
			"name",
			"tier_name",
			"description",
			"price",
			"currency",
			"duration_months",
			"benefits",
			"access_all_courses",
			"is_default",
		],
		order_by="price asc",
	)

	for tier in tiers:
		if not tier.access_all_courses:
			tier.courses = frappe.get_all(
				"Membership Tier Course", filters={"parent": tier.name}, fields=["course", "course_title"]
			)
		else:
			tier.courses = []

	return tiers


@frappe.whitelist(allow_guest=True)
def get_user_membership(user=None):
	"""Get current user's active membership"""
	if not user:
		user = frappe.session.user

	if user == "Guest":
		return None

	membership = frappe.db.get_value(
		"LMS User Membership",
		{"member": user, "status": "Active"},
		["name", "membership_tier", "start_date", "end_date", "status"],
		as_dict=True,
	)

	if membership:
		membership.tier_details = frappe.db.get_value(
			"LMS Membership Tier",
			membership.membership_tier,
			["tier_name", "description", "access_all_courses"],
			as_dict=True,
		)

	return membership


@frappe.whitelist(allow_guest=True)
def check_membership_status(user=None):
	"""Check if user has active membership and return status details"""
	if not user:
		user = frappe.session.user

	if user == "Guest":
		return {
			"has_membership": False,
			"is_logged_in": False,
			"message": _("Please login to view membership status"),
		}

	membership = get_user_membership(user)

	if membership:
		days_remaining = (getdate(membership.end_date) - getdate(nowdate())).days
		return {
			"has_membership": True,
			"is_logged_in": True,
			"membership": membership,
			"days_remaining": days_remaining,
			"is_expiring_soon": days_remaining <= 30,
			"message": _("You have an active {0} membership").format(membership.tier_details.tier_name),
		}
	else:
		return {
			"has_membership": False,
			"is_logged_in": True,
			"message": _("You don't have an active membership"),
		}


@frappe.whitelist()
def has_course_access(course_name):
	"""Check if current user has access to a specific course through membership"""
	user = frappe.session.user

	if user == "Guest":
		return False

	# Check if user has active membership
	membership = frappe.db.get_value(
		"LMS User Membership", {"member": user, "status": "Active"}, ["membership_tier"], as_dict=True
	)

	if not membership:
		return False

	tier = frappe.get_doc("LMS Membership Tier", membership.membership_tier)

	# If tier has access to all courses
	if tier.access_all_courses:
		return True

	# Check if specific course is in the tier
	for course in tier.courses:
		if course.course == course_name:
			return True

	return False


@frappe.whitelist()
def get_accessible_courses():
	"""Get all courses accessible through user's membership"""
	user = frappe.session.user

	if user == "Guest":
		return []

	membership = frappe.db.get_value(
		"LMS User Membership", {"member": user, "status": "Active"}, ["membership_tier"], as_dict=True
	)

	if not membership:
		return []

	tier = frappe.get_doc("LMS Membership Tier", membership.membership_tier)

	if tier.access_all_courses:
		# Return all published courses
		courses = frappe.get_all(
			"LMS Course",
			filters={"published": 1},
			fields=["name", "title", "image", "short_introduction", "paid_course", "course_price"],
		)
	else:
		# Return only courses in the tier
		course_names = [c.course for c in tier.courses]
		if course_names:
			courses = frappe.get_all(
				"LMS Course",
				filters={"name": ["in", course_names], "published": 1},
				fields=["name", "title", "image", "short_introduction", "paid_course", "course_price"],
			)
		else:
			courses = []

	return courses


@frappe.whitelist()
def get_pending_membership():
	"""Get user's pending membership if any"""
	if frappe.session.user == "Guest":
		return None

	pending = frappe.get_all(
		"LMS User Membership",
		filters={"member": frappe.session.user, "status": "Pending"},
		fields=["name", "membership_tier", "creation", "amount_paid", "currency"],
		order_by="creation desc",
		limit=1,
	)

	if not pending:
		return None

	pending = pending[0]

	# Get tier details
	tier = frappe.db.get_value(
		"LMS Membership Tier",
		pending.membership_tier,
		["tier_name", "description", "duration_months"],
		as_dict=True,
	)

	if tier:
		pending.update(tier)

	pending["creation_formatted"] = frappe.utils.format_datetime(pending.creation, "d MMM yyyy, h:mm a")

	return pending


@frappe.whitelist()
def create_membership_payment(tier_name, address=None):
	"""Create payment for membership subscription"""
	if frappe.session.user == "Guest":
		frappe.throw(_("Please login to subscribe to a membership"))

	tier = frappe.get_doc("LMS Membership Tier", tier_name)

	if not tier.is_active:
		frappe.throw(_("This membership tier is not available"))

	# Check if user already has active membership
	existing = frappe.db.exists("LMS User Membership", {"member": frappe.session.user, "status": "Active"})

	if existing:
		frappe.throw(
			_("You already have an active membership. Please wait for it to expire or cancel it first.")
		)

	# Check for existing pending membership for the same tier - reuse it
	existing_pending = frappe.db.get_value(
		"LMS User Membership",
		{"member": frappe.session.user, "status": "Pending", "membership_tier": tier_name},
		"name",
	)

	if existing_pending:
		# Reuse existing pending membership - retry payment
		return retry_pending_payment(existing_pending)

	# Cancel any other pending memberships for different tiers
	other_pending = frappe.get_all(
		"LMS User Membership",
		filters={"member": frappe.session.user, "status": "Pending", "membership_tier": ["!=", tier_name]},
		pluck="name",
	)

	for pending_name in other_pending:
		frappe.db.set_value("LMS User Membership", pending_name, "status", "Cancelled")

	# Create pending membership
	membership = frappe.new_doc("LMS User Membership")
	membership.update(
		{
			"member": frappe.session.user,
			"membership_tier": tier_name,
			"status": "Pending",
			"amount_paid": tier.price,
			"currency": tier.currency,
		}
	)
	membership.insert(ignore_permissions=True)

	# Get payment gateway from LMS Settings
	payment_gateway = frappe.db.get_single_value("LMS Settings", "payment_gateway")

	if not payment_gateway:
		frappe.throw(_("Payment gateway is not configured. Please contact administrator."))

	# Prepare payment details
	from lms.lms.payments import get_controller

	controller = get_controller(payment_gateway)

	user = frappe.get_doc("User", frappe.session.user)

	redirect_url = f"/lms/membership/thank-you?membership={membership.name}"

	# Generate order_id
	order_id = f"MEMBERSHIP-{membership.name}-{int(frappe.utils.now_datetime().timestamp())}"
	membership.order_id = order_id
	membership.save(ignore_permissions=True)

	payment_details = {
		"amount": int(tier.price),
		"title": f"Membership: {tier.tier_name}",
		"description": f"{user.full_name}'s subscription to {tier.tier_name}",
		"reference_doctype": "LMS User Membership",
		"reference_docname": membership.name,
		"payer_email": frappe.session.user,
		"payer_name": user.full_name,
		"currency": tier.currency,
		"payment_gateway": payment_gateway,
		"redirect_to": redirect_url,
		"payment": membership.name,
	}

	try:
		url = controller.get_payment_url(**payment_details)
		return {"payment_url": url, "membership": membership.name}
	except Exception as e:
		frappe.log_error(f"Membership Payment Error: {e!s}")
		# Clean up pending membership on error
		frappe.delete_doc("LMS User Membership", membership.name, ignore_permissions=True)
		frappe.throw(_("Failed to create payment. Please try again."))


@frappe.whitelist(allow_guest=True)
def membership_payment_callback():
	"""Handle Midtrans payment notification for memberships"""
	data = frappe.request.get_json()
	frappe.log_error(message=f"Membership Payment Notification: {data}", title="Membership Payment Debug")

	if not data:
		return "No data"

	order_id = data.get("order_id")
	transaction_status = data.get("transaction_status")
	fraud_status = data.get("fraud_status")

	if transaction_status == "capture":
		if fraud_status == "accept":
			activate_membership(order_id)
	elif transaction_status == "settlement":
		activate_membership(order_id)

	return "OK"


def activate_membership(order_id):
	"""Activate a membership after successful payment"""
	membership = frappe.db.get_value(
		"LMS User Membership",
		{"order_id": order_id},
		["name", "membership_tier", "status", "member"],
		as_dict=True,
	)

	if membership and membership.status == "Pending":
		tier = frappe.get_doc("LMS Membership Tier", membership.membership_tier)

		today = nowdate()
		end_date = add_months(today, tier.duration_months)

		frappe.db.set_value(
			"LMS User Membership",
			membership.name,
			{"status": "Active", "start_date": today, "end_date": end_date, "payment_reference": order_id},
		)

		frappe.db.commit()

		# Send confirmation email
		try:
			send_membership_confirmation(membership.member, membership.name)
		except Exception as e:
			frappe.log_error(f"Failed to send membership confirmation: {e!s}")


def send_membership_confirmation(user, membership_name):
	"""Send membership confirmation email"""
	membership = frappe.get_doc("LMS User Membership", membership_name)
	tier = frappe.get_doc("LMS Membership Tier", membership.membership_tier)
	user_doc = frappe.get_doc("User", user)

	frappe.sendmail(
		recipients=[user],
		subject=_("Welcome to {0} Membership!").format(tier.tier_name),
		message=_("""
			<p>Dear {0},</p>
			<p>Thank you for subscribing to {1}!</p>
			<p>Your membership is now active and will be valid until {2}.</p>
			<p>You now have access to all the courses included in your membership plan.</p>
			<p>Start learning now: <a href="{3}/lms/courses">Browse Courses</a></p>
			<p>Best regards,<br>The Team</p>
		""").format(
			user_doc.full_name,
			tier.tier_name,
			frappe.utils.format_date(membership.end_date),
			frappe.utils.get_url(),
		),
	)


@frappe.whitelist()
def renew_membership():
	"""Renew expired or expiring membership"""
	user = frappe.session.user

	if user == "Guest":
		frappe.throw(_("Please login to renew your membership"))

	# Find the most recent membership
	membership = frappe.get_all(
		"LMS User Membership",
		filters={"member": user, "status": ["in", ["Active", "Expired"]]},
		fields=["name", "membership_tier", "status", "end_date"],
		order_by="creation desc",
		limit=1,
	)

	if not membership:
		frappe.throw(_("No membership found to renew"))

	membership = membership[0]

	# Create new payment for renewal
	return create_membership_payment(membership.membership_tier)


@frappe.whitelist()
def retry_pending_payment(membership_name):
	"""Retry payment for a pending membership"""
	user = frappe.session.user

	if user == "Guest":
		frappe.throw(_("Please login to continue payment"))

	membership = frappe.get_doc("LMS User Membership", membership_name)

	# Verify ownership
	if membership.member != user:
		frappe.throw(_("You don't have permission to access this membership"))

	# Verify status is pending
	if membership.status != "Pending":
		return {"message": _("This membership is no longer pending. Status: {0}").format(membership.status)}

	tier = frappe.get_doc("LMS Membership Tier", membership.membership_tier)

	if not tier.is_active:
		frappe.throw(_("This membership tier is no longer available"))

	# Get payment gateway from LMS Settings
	payment_gateway = frappe.db.get_single_value("LMS Settings", "payment_gateway")

	if not payment_gateway:
		frappe.throw(_("Payment gateway is not configured. Please contact administrator."))

	# Prepare payment details
	from lms.lms.payments import get_controller

	controller = get_controller(payment_gateway)

	user_doc = frappe.get_doc("User", user)

	redirect_url = f"/lms/membership/thank-you?membership={membership.name}"

	# Generate new order_id for retry
	order_id = f"MEMBERSHIP-{membership.name}-{int(frappe.utils.now_datetime().timestamp())}"
	membership.order_id = order_id
	membership.save(ignore_permissions=True)

	payment_details = {
		"amount": int(tier.price),
		"title": f"Membership: {tier.tier_name}",
		"description": f"{user_doc.full_name}'s subscription to {tier.tier_name}",
		"reference_doctype": "LMS User Membership",
		"reference_docname": membership.name,
		"payer_email": user,
		"payer_name": user_doc.full_name,
		"currency": tier.currency,
		"payment_gateway": payment_gateway,
		"redirect_to": redirect_url,
		"payment": membership.name,
	}

	try:
		url = controller.get_payment_url(**payment_details)
		return {"payment_url": url, "membership": membership.name}
	except Exception as e:
		frappe.log_error(f"Membership Payment Retry Error: {e!s}")
		frappe.throw(_("Failed to create payment. Please try again."))


@frappe.whitelist()
def cancel_pending_membership(membership_name):
	"""Cancel a pending membership to allow subscribing to a different tier"""
	user = frappe.session.user

	if user == "Guest":
		frappe.throw(_("Please login to cancel membership"))

	membership = frappe.get_doc("LMS User Membership", membership_name)

	# Verify ownership
	if membership.member != user:
		frappe.throw(_("You don't have permission to access this membership"))

	# Only allow cancelling pending memberships
	if membership.status != "Pending":
		frappe.throw(_("Only pending memberships can be cancelled"))

	membership.status = "Cancelled"
	membership.save(ignore_permissions=True)

	return {"message": _("Membership cancelled successfully")}


@frappe.whitelist(allow_guest=True)
def get_membership_stats():
	"""Get membership statistics for dashboard"""
	stats = {}

	stats["total_members"] = frappe.db.count("LMS User Membership", {"status": "Active"})

	stats["total_revenue"] = frappe.db.sql("""
		SELECT COALESCE(SUM(amount_paid), 0) as total
		FROM `tabLMS User Membership`
		WHERE status IN ('Active', 'Expired')
	""")[0][0]

	stats["new_this_month"] = frappe.db.count(
		"LMS User Membership",
		{"status": "Active", "start_date": [">=", frappe.utils.add_months(nowdate(), -1)]},
	)

	stats["expiring_soon"] = frappe.db.count(
		"LMS User Membership",
		{"status": "Active", "end_date": ["between", [nowdate(), frappe.utils.add_days(nowdate(), 30)]]},
	)

	return stats


@frappe.whitelist(allow_guest=True)
def get_user_membership_status(user_email=None):
	"""Get membership status for a specific user or current user

	Args:
		user_email: Email of the user to check. If not provided, uses current logged-in user.

	Returns:
		dict: Membership status with details
	"""
	# Determine which user to check
	if user_email:
		user = user_email
	else:
		user = frappe.session.user

	if user == "Guest":
		return {
			"has_active_membership": False,
			"is_logged_in": False,
			"message": _("Please login to view membership status"),
		}

	# Get active membership
	membership = frappe.db.get_value(
		"LMS User Membership",
		{"member": user, "status": "Active"},
		["name", "membership_tier", "start_date", "end_date", "status", "amount_paid", "currency"],
		as_dict=True,
	)

	if membership:
		tier = frappe.db.get_value(
			"LMS Membership Tier",
			membership.membership_tier,
			["tier_name", "description", "access_all_courses", "duration_months"],
			as_dict=True,
		)

		today = getdate(nowdate())
		start_date = getdate(membership.start_date)
		end_date = getdate(membership.end_date)
		days_remaining = (end_date - today).days
		total_days = (end_date - start_date).days

		return {
			"has_active_membership": True,
			"is_logged_in": frappe.session.user != "Guest",
			"membership_name": membership.name,
			"tier_name": tier.tier_name if tier else membership.membership_tier,
			"tier_description": tier.description if tier else "",
			"access_all_courses": tier.access_all_courses if tier else False,
			"duration_months": tier.duration_months if tier else 0,
			"start_date": str(membership.start_date),
			"end_date": str(membership.end_date),
			"start_date_formatted": frappe.utils.format_date(membership.start_date, "d MMM yyyy"),
			"end_date_formatted": frappe.utils.format_date(membership.end_date, "d MMM yyyy"),
			"days_remaining": max(0, days_remaining),
			"total_days": max(1, total_days),  # Avoid division by zero
			"is_expiring_soon": 0 < days_remaining <= 30,
			"is_expired": days_remaining <= 0,
			"amount_paid": membership.amount_paid,
			"currency": membership.currency,
			"message": _("Active {0} membership").format(tier.tier_name if tier else ""),
		}
	else:
		return {
			"has_active_membership": False,
			"is_logged_in": frappe.session.user != "Guest",
			"message": _("No active membership"),
		}


@frappe.whitelist()
def get_membership_thank_you_data(membership_name, transaction_status=None):
	"""Get membership data for thank-you page and optionally activate from redirect"""
	user = frappe.session.user

	if user == "Guest":
		return {"error": _("Please login to view this page")}

	if not membership_name:
		return {"error": _("No membership specified")}

	if not frappe.db.exists("LMS User Membership", membership_name):
		return {"error": _("Membership not found")}

	membership = frappe.get_doc("LMS User Membership", membership_name)

	# Verify ownership
	if membership.member != user:
		return {"error": _("You don't have permission to view this membership")}

	# Activate membership if payment was successful via redirect
	if membership.status == "Pending" and transaction_status in ["capture", "settlement"]:
		try:
			_activate_membership_from_redirect(membership)
			membership.reload()
		except Exception as e:
			frappe.log_error(f"Failed to activate membership from redirect: {e!s}")

	# Get tier details
	tier = None
	if frappe.db.exists("LMS Membership Tier", membership.membership_tier):
		tier = frappe.get_doc("LMS Membership Tier", membership.membership_tier)

	# Get accessible courses
	courses = []
	if tier:
		if tier.access_all_courses:
			courses = frappe.get_all(
				"LMS Course",
				filters={"published": 1},
				fields=["name", "title", "image", "short_introduction", "category"],
				order_by="creation desc",
				limit=12,
			)
		else:
			course_names = [c.course for c in tier.courses]
			if course_names:
				courses = frappe.get_all(
					"LMS Course",
					filters={"name": ["in", course_names], "published": 1},
					fields=["name", "title", "image", "short_introduction", "category"],
				)

	return {
		"membership": {
			"name": membership.name,
			"status": membership.status,
			"start_date": frappe.utils.format_date(membership.start_date) if membership.start_date else None,
			"end_date": frappe.utils.format_date(membership.end_date) if membership.end_date else None,
			"member": membership.member,
		},
		"tier": {
			"name": tier.name,
			"tier_name": tier.tier_name,
			"description": tier.description,
			"price": tier.price,
			"duration_months": tier.duration_months,
		}
		if tier
		else None,
		"courses": courses,
	}


def _activate_membership_from_redirect(membership):
	"""Internal function to activate membership when redirected from payment gateway"""
	if membership.status != "Pending":
		return

	tier = frappe.get_doc("LMS Membership Tier", membership.membership_tier)

	today = frappe.utils.nowdate()
	end_date = frappe.utils.add_months(today, tier.duration_months)

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
		send_membership_confirmation(membership.member, membership.name)
	except Exception as e:
		frappe.log_error(f"Failed to send membership confirmation: {e!s}")


@frappe.whitelist()
def get_recent_membership_with_details():
	"""Get the current user's most recent active or pending membership with full details"""
	user = frappe.session.user

	if user == "Guest":
		return None

	membership_name = frappe.db.get_value(
		"LMS User Membership",
		{"member": user, "status": ["in", ["Active", "Pending"]]},
		"name",
		order_by="creation desc",
	)

	if not membership_name:
		return None

	# Reuse the thank you data function
	return get_membership_thank_you_data(membership_name)
