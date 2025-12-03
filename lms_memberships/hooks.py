app_name = "lms_memberships"
app_title = "LMS Memberships"
app_publisher = "PT Teknologi Eukarya Indonesia"
app_description = "Enable membership subscription system for Frappe LMS platform"
app_email = "putra@eukarya.id"
app_license = "mit"

# Apps
# ------------------

required_apps = ["lms", "payments"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "lms_memberships",
# 		"logo": "/assets/lms_memberships/logo.png",
# 		"title": "LMS Memberships",
# 		"route": "/lms_memberships",
# 		"has_permission": "lms_memberships.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/lms_memberships/css/lms_memberships.css"
# app_include_js = "/assets/lms_memberships/js/lms_memberships.js"

# include js, css files in header of web template
web_include_css = "/assets/lms_memberships/css/membership.css"
web_include_js = "/assets/lms_memberships/js/membership.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "lms_memberships/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "lms_memberships/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
jinja = {
	"methods": [
		"lms_memberships.api.membership.get_user_membership",
		"lms_memberships.api.membership.check_membership_status",
		"lms_memberships.api.membership.has_course_access",
	],
}

# Installation
# ------------

# before_install = "lms_memberships.install.before_install"
# after_install = "lms_memberships.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "lms_memberships.uninstall.before_uninstall"
# after_uninstall = "lms_memberships.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "lms_memberships.utils.before_app_install"
# after_app_install = "lms_memberships.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "lms_memberships.utils.before_app_uninstall"
# after_app_uninstall = "lms_memberships.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "lms_memberships.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": [
		"lms_memberships.lms_memberships.doctype.lms_user_membership.lms_user_membership.update_expired_memberships"
	],
}

# Testing
# -------

# before_tests = "lms_memberships.install.before_tests"

# Overriding Methods
# ------------------------------

override_whitelisted_methods = {"lms.lms.api.get_user_info": "lms_memberships.api.profile.get_user_info"}

# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "lms_memberships.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["lms_memberships.utils.before_request"]
# after_request = ["lms_memberships.utils.after_request"]

# Job Events
# ----------
# before_job = ["lms_memberships.utils.before_job"]
# after_job = ["lms_memberships.utils.after_job"]

# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "LMS User Membership",
		"filter_by": "member",
		"redact_fields": [],
		"partial": 1,
	},
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"lms_memberships.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Fixtures - export standard data
fixtures = [{"doctype": "LMS Membership Tier", "filters": [["is_active", "=", 1]]}]
