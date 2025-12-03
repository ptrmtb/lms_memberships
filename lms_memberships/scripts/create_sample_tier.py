"""Create initial Bluechip Member tier."""

import frappe


def create_bluechip_tier():
	"""Create the Bluechip Member tier if it doesn't exist."""
	if not frappe.db.exists("LMS Membership Tier", {"tier_name": "Bluechip Member"}):
		tier = frappe.get_doc(
			{
				"doctype": "LMS Membership Tier",
				"tier_name": "Bluechip Member",
				"description": "Bluechip Member adalah membership premium yang memberikan akses ke seluruh konten pembelajaran di platform kami. Dengan berlangganan tahunan, Anda akan mendapatkan akses penuh ke semua kursus, materi pembelajaran, dan fitur eksklusif lainnya.",
				"price": 249000,
				"currency": "IDR",
				"duration_months": 12,
				"benefits": """Akses penuh ke semua kursus premium
Update materi pembelajaran setiap bulan
Sertifikat digital untuk setiap kursus yang diselesaikan
Konsultasi langsung dengan instruktur
Akses ke komunitas eksklusif member
Diskon khusus untuk event dan workshop""",
				"access_all_courses": 1,
				"is_active": 1,
				"is_default": 1,
			}
		)
		tier.insert(ignore_permissions=True)
		frappe.db.commit()
		print(f"Created tier: {tier.name}")
		return tier.name
	else:
		print("Bluechip Member tier already exists")
		return None
