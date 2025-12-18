import frappe
from lms.lms.doctype.lms_enrollment.lms_enrollment import LMSEnrollment

from lms_memberships.api.membership import has_course_access


class CustomLMSEnrollment(LMSEnrollment):
	def validate_course_enrollment_eligibility(self):
		if has_course_access(self.course):
			return  # Skip payment check if they have membership access
		super().validate_course_enrollment_eligibility()
