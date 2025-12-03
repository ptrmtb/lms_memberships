/**
 * LMS Memberships - Frontend Integration
 *
 * This script handles:
 * 1. Membership banner injection on LMS pages (/lms, /lms/courses)
 * 2. Membership info on user profile (/lms/user/{username})
 * 3. PWA install prompt suppression
 */

(function () {
	"use strict";

	// Namespace for our app
	window.lms_memberships = window.lms_memberships || {};

	// ========================================
	// 1. Disable PWA Install Prompt
	// ========================================
	window.addEventListener(
		"beforeinstallprompt",
		function (e) {
			// Prevent the default browser prompt
			e.preventDefault();
			// Store it but don't show
			window.__pwaPromptEvent = e;
			return false;
		},
		true
	);

	// Hide any existing install prompt dialogs from Vue
	const hidePWAPrompt = function () {
		// Hide dialog elements that contain "Install Frappe Learning" text
		const allElements = document.querySelectorAll("*");
		allElements.forEach(function (el) {
			if (
				el.textContent &&
				el.textContent.includes("Install Frappe Learning") &&
				!el.textContent.includes("lms_memberships")
			) {
				// Find the closest dialog/modal container
				const dialog =
					el.closest('[role="dialog"]') ||
					el.closest(".fixed.bottom-") ||
					el.closest('[class*="dialog"]') ||
					el.closest('[class*="modal"]') ||
					el.closest('[class*="popover"]');
				if (dialog) {
					dialog.style.display = "none";
					dialog.style.visibility = "hidden";
					dialog.remove();
				}
			}
		});
	};

	// Run periodically to catch dynamically added prompts
	setInterval(hidePWAPrompt, 500);
	// Also run on DOM changes
	const pwaObserver = new MutationObserver(hidePWAPrompt);
	if (document.body) {
		pwaObserver.observe(document.body, { childList: true, subtree: true });
	}

	// ========================================
	// 2. Membership Status Cache
	// ========================================
	let membershipCache = null;
	let membershipCacheTime = 0;
	const CACHE_DURATION = 60000; // 1 minute

	const getMembershipStatus = async function () {
		const now = Date.now();
		if (membershipCache && now - membershipCacheTime < CACHE_DURATION) {
			return membershipCache;
		}

		// Check if frappe is available
		if (typeof frappe === "undefined" || !frappe.call) {
			return null;
		}

		try {
			const response = await new Promise((resolve, reject) => {
				frappe.call({
					method: "lms_memberships.api.membership.check_membership_status",
					async: true,
					callback: (r) => resolve(r),
					error: (e) => reject(e),
				});
			});
			membershipCache = response.message;
			membershipCacheTime = now;
			return membershipCache;
		} catch (error) {
			console.error("Failed to get membership status:", error);
			return null;
		}
	};

	// ========================================
	// 3. Membership Banner for LMS Pages
	// ========================================
	const createMemberBanner = function (membership) {
		const daysRemaining = membership.days_remaining || 0;
		const tierName = membership.membership?.tier_details?.tier_name || "Member";
		const endDate = membership.membership?.end_date || "";

		if (membership.is_expiring_soon) {
			return `
				<div class="lms-membership-banner expiring-banner" id="lms-membership-banner">
					<div class="lms-banner-content">
						<div class="lms-banner-icon">
							<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<circle cx="12" cy="12" r="10"></circle>
								<line x1="12" y1="8" x2="12" y2="12"></line>
								<line x1="12" y1="16" x2="12.01" y2="16"></line>
							</svg>
						</div>
						<div class="lms-banner-text">
							<h3>Your membership expires in ${daysRemaining} days</h3>
							<p>Renew now to continue enjoying unlimited access to all courses.</p>
						</div>
					</div>
					<div class="lms-banner-cta">
						<a href="/membership" class="lms-banner-btn">Renew Now</a>
					</div>
				</div>
			`;
		}

		return `
			<div class="lms-membership-banner member-banner" id="lms-membership-banner">
				<div class="lms-banner-content">
					<div class="lms-banner-icon">
						<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<circle cx="12" cy="8" r="7"></circle>
							<polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"></polyline>
						</svg>
					</div>
					<div class="lms-banner-text">
						<h3>Welcome back, ${tierName}! 🎉</h3>
						<p>You have full access to all courses. Membership valid until ${formatDate(endDate)}.</p>
					</div>
				</div>
			</div>
		`;
	};

	const createNonMemberBanner = function () {
		return `
			<div class="lms-membership-banner cta-banner" id="lms-membership-banner">
				<div class="lms-banner-content">
					<div class="lms-banner-icon">
						<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<path d="M12 2L2 7l10 5 10-5-10-5z"></path>
							<path d="M2 17l10 5 10-5"></path>
							<path d="M2 12l10 5 10-5"></path>
						</svg>
					</div>
					<div class="lms-banner-text">
						<h3>Unlock Unlimited Learning</h3>
						<p>Get access to all courses with our membership plans. Learn at your own pace, anytime, anywhere.</p>
					</div>
				</div>
				<div class="lms-banner-cta">
					<a href="/membership" class="lms-banner-btn">
						View Plans
						<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<line x1="5" y1="12" x2="19" y2="12"></line>
							<polyline points="12 5 19 12 12 19"></polyline>
						</svg>
					</a>
				</div>
			</div>
		`;
	};

	const createGuestBanner = function () {
		return `
			<div class="lms-membership-banner guest-banner" id="lms-membership-banner">
				<div class="lms-banner-content">
					<div class="lms-banner-icon">
						<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
							<circle cx="9" cy="7" r="4"></circle>
							<path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
							<path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
						</svg>
					</div>
					<div class="lms-banner-text">
						<h3>Join Our Learning Community</h3>
						<p>Sign up and subscribe to get unlimited access to all courses and learning materials.</p>
					</div>
				</div>
				<div class="lms-banner-cta">
					<a href="/login?redirect-to=/membership" class="lms-banner-btn">
						Get Started
						<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<line x1="5" y1="12" x2="19" y2="12"></line>
							<polyline points="12 5 19 12 12 19"></polyline>
						</svg>
					</a>
				</div>
			</div>
		`;
	};

	const injectBanner = async function () {
		// Check if we're on an LMS page
		const path = window.location.pathname;
		if (!path.startsWith("/lms")) {
			return;
		}

		// Don't inject on certain pages
		if (
			path.includes("/learn/") ||
			path.includes("/edit") ||
			path.includes("/user/")
		) {
			return;
		}

		// Only inject on home and courses pages
		const allowedPaths = ["/lms", "/lms/", "/lms/courses"];
		const isAllowed = allowedPaths.some(
			(p) => path === p || path.startsWith(p + "?")
		);
		if (!isAllowed) {
			return;
		}

		// Check if banner already exists
		if (document.getElementById("lms-membership-banner")) {
			return;
		}

		// Wait for the Vue app to render
		const container = await waitForElement(".p-5.pb-10, .w-full.px-5.pt-5");
		if (!container) {
			return;
		}

		const status = await getMembershipStatus();
		let bannerHtml = "";

		if (!status) {
			return; // API error, don't show banner
		}

		if (!status.is_logged_in) {
			bannerHtml = createGuestBanner();
		} else if (status.has_membership) {
			bannerHtml = createMemberBanner(status);
		} else {
			bannerHtml = createNonMemberBanner();
		}

		// Insert banner at the top of the container
		const bannerWrapper = document.createElement("div");
		bannerWrapper.innerHTML = bannerHtml;
		const bannerEl = bannerWrapper.firstElementChild;
		container.insertBefore(bannerEl, container.firstChild);
	};

	// ========================================
	// 4. Membership Info for Profile Pages
	// ========================================
	const createProfileMembershipCard = function (membership) {
		if (!membership || !membership.has_membership) {
			return `
				<div class="lms-profile-membership-card no-membership" id="lms-profile-membership">
					<div class="lms-card-header">
						<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<circle cx="12" cy="8" r="7"></circle>
							<polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"></polyline>
						</svg>
						<h3>Membership Status</h3>
					</div>
					<div class="lms-card-body">
						<p class="no-membership-text">No active membership</p>
						<a href="/membership" class="lms-subscribe-link">Subscribe Now →</a>
					</div>
				</div>
			`;
		}

		const tierName = membership.membership?.tier_details?.tier_name || "Member";
		const startDate = membership.membership?.start_date || "";
		const endDate = membership.membership?.end_date || "";
		const daysRemaining = membership.days_remaining || 0;

		let statusClass = "active";
		let statusText = "Active";
		if (membership.is_expiring_soon) {
			statusClass = "expiring";
			statusText = `Expiring in ${daysRemaining} days`;
		}

		return `
			<div class="lms-profile-membership-card has-membership" id="lms-profile-membership">
				<div class="lms-card-header">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<circle cx="12" cy="8" r="7"></circle>
						<polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"></polyline>
					</svg>
					<h3>Membership Status</h3>
					<span class="lms-status-badge ${statusClass}">${statusText}</span>
				</div>
				<div class="lms-card-body">
					<div class="lms-membership-details">
						<div class="lms-detail-item">
							<label>Plan</label>
							<span>${tierName}</span>
						</div>
						<div class="lms-detail-item">
							<label>Member Since</label>
							<span>${formatDate(startDate)}</span>
						</div>
						<div class="lms-detail-item">
							<label>Valid Until</label>
							<span>${formatDate(endDate)}</span>
						</div>
						<div class="lms-detail-item">
							<label>Days Remaining</label>
							<span>${daysRemaining} days</span>
						</div>
					</div>
					${
						membership.is_expiring_soon
							? `<a href="/membership" class="lms-renew-btn">Renew Membership</a>`
							: ""
					}
				</div>
			</div>
		`;
	};

	const injectProfileMembership = async function () {
		const path = window.location.pathname;

		// Check if on profile page
		if (!path.startsWith("/lms/user/")) {
			return;
		}

		// Check if already injected
		if (document.getElementById("lms-profile-membership")) {
			return;
		}

		// Wait for profile to load - look for the About section
		const aboutSection = await waitForElement(".mt-7.mb-10");
		if (!aboutSection) {
			return;
		}

		const status = await getMembershipStatus();

		// Only show on own profile (check if logged in)
		if (!status || !status.is_logged_in) {
			return;
		}

		// Check if this is the current user's profile
		// The profile URL contains the username
		const pathParts = path.split("/");
		const profileUsername = pathParts[pathParts.length - 1] || pathParts[pathParts.length - 2];

		// Get current user's username from frappe
		let currentUsername = "";
		if (typeof frappe !== "undefined" && frappe.session) {
			currentUsername = frappe.session.user_name || "";
		}

		// Only show membership card on own profile
		// If we can't determine, show anyway for logged-in users
		// (the API only returns membership for the current user anyway)

		// Create and insert the card
		const cardWrapper = document.createElement("div");
		cardWrapper.innerHTML = createProfileMembershipCard(status);
		const cardEl = cardWrapper.firstElementChild;

		// Insert before the About section
		aboutSection.parentNode.insertBefore(cardEl, aboutSection);
	};

	// ========================================
	// 6. Route Change Handler (Vue SPA)
	// ========================================
	let lastPath = window.location.pathname;
	let routeChangeTimeout = null;

	const handleRouteChange = function () {
		const currentPath = window.location.pathname;
		if (currentPath !== lastPath) {
			lastPath = currentPath;

			if (routeChangeTimeout) {
				clearTimeout(routeChangeTimeout);
			}

			routeChangeTimeout = setTimeout(() => {
				// Clear cache on navigation
				membershipCache = null;
				membershipCacheTime = 0;

				// Re-inject components
				injectBanner();
				injectProfileMembership();
			}, CONFIG.ROUTE_CHANGE_DELAY);
		}
	};

	// Override history methods to detect SPA navigation
	const originalPushState = history.pushState;
	history.pushState = function () {
		originalPushState.apply(this, arguments);
		setTimeout(handleRouteChange, 100);
	};

	const originalReplaceState = history.replaceState;
	history.replaceState = function () {
		originalReplaceState.apply(this, arguments);
		setTimeout(handleRouteChange, 100);
	};

	window.addEventListener("popstate", function () {
		setTimeout(handleRouteChange, 100);
	});

	// Backup: poll for route changes
	setInterval(handleRouteChange, CONFIG.BANNER_CHECK_INTERVAL);

	// ========================================
	// 7. Initialize
	// ========================================
	const init = function () {
		if (document.readyState === "loading") {
			document.addEventListener("DOMContentLoaded", initAfterLoad);
		} else {
			initAfterLoad();
		}
	};

	const initAfterLoad = function () {
		// Wait for Vue to mount
		setTimeout(() => {
			injectBanner();
			injectProfileMembership();
		}, 1500);
	};

	// Public API
	lms_memberships.refreshBanner = function () {
		membershipCache = null;
		membershipCacheTime = 0;
		const existing = document.getElementById("lms-membership-banner");
		if (existing) existing.remove();
		injectBanner();
	};

	lms_memberships.refreshProfileCard = function () {
		membershipCache = null;
		membershipCacheTime = 0;
		const existing = document.getElementById("lms-profile-membership");
		if (existing) existing.remove();
		injectProfileMembership();
	};

	lms_memberships.clearCache = function() {
		membershipCache = null;
		membershipCacheTime = 0;
	};

	init();
})();

