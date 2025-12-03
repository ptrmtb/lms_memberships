import frappe


def get_context(context):
	"""Context for membership page"""
	context.no_cache = 1
	context.show_sidebar = False
	context.title = "Membership Plans"

	# Add meta info
	context.metatags = {
		"title": "Membership Plans - BlueChip",
		"description": "Unlock unlimited access to all courses with our membership plans.",
	}
