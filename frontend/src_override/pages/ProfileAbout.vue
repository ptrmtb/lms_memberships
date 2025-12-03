<template>
	<!-- Membership Card - Show for own profile or public view -->
	<div class="mb-8">
		<h2 class="mb-3 text-lg font-semibold text-ink-gray-9">
			{{ isOwnProfile ? __('My Membership') : __('Membership') }}
		</h2>
		
		<!-- Loading State -->
		<div v-if="membership.loading" class="rounded-xl border border-gray-200 p-6">
			<div class="flex items-center justify-center">
				<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-900"></div>
			</div>
		</div>

		<!-- Active Membership Card -->
		<div v-else-if="membership.data?.has_active_membership" 
			class="rounded-xl overflow-hidden bg-gradient-to-r from-blue-900 to-blue-700 text-white">
			<div class="p-6">
				<div class="flex items-center justify-between flex-wrap gap-4">
					<div class="flex items-center gap-4">
						<div class="w-14 h-14 rounded-full bg-white/20 flex items-center justify-center">
							<Award class="w-7 h-7 text-white" />
						</div>
						<div>
							<p class="text-sm text-white/70">{{ __('Current Plan') }}</p>
							<h3 class="text-2xl font-bold">{{ membership.data.tier_name }}</h3>
						</div>
					</div>
					<div class="text-right">
						<p class="text-sm text-white/70">{{ __('Valid Until') }}</p>
						<p class="text-xl font-semibold">{{ membership.data.end_date_formatted }}</p>
					</div>
				</div>

				<!-- Member Since -->
				<div class="mt-4 pt-4 border-t border-white/20">
					<div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
						<div>
							<p class="text-xs text-white/60">{{ __('Member Since') }}</p>
							<p class="text-sm font-medium">{{ membership.data.start_date_formatted }}</p>
						</div>
						<div>
							<p class="text-xs text-white/60">{{ __('Days Remaining') }}</p>
							<p class="text-sm font-medium">{{ membership.data.days_remaining }}</p>
						</div>
						<div>
							<p class="text-xs text-white/60">{{ __('Plan Duration') }}</p>
							<p class="text-sm font-medium">{{ membership.data.total_days }} {{ __('days') }}</p>
						</div>
						<div>
							<p class="text-xs text-white/60">{{ __('Status') }}</p>
							<p class="text-sm font-medium flex items-center justify-center gap-1">
								<span class="w-2 h-2 rounded-full bg-green-400"></span>
								{{ __('Active') }}
							</p>
						</div>
					</div>
				</div>

				<!-- Expiring Soon Warning (only for own profile) -->
				<div v-if="isOwnProfile && membership.data.is_expiring_soon" 
					class="mt-4 p-3 bg-orange-500/20 rounded-lg flex items-center justify-between flex-wrap gap-3">
					<div class="flex items-center gap-2">
						<AlertTriangle class="w-5 h-5 text-orange-300" />
						<span class="text-sm">
							{{ __('Expires in') }} {{ membership.data.days_remaining }} {{ __('days') }}
						</span>
					</div>
					<router-link to="/membership" 
						class="px-4 py-2 bg-white text-blue-900 rounded-lg font-medium text-sm hover:bg-blue-50 transition-colors">
						{{ __('Renew Now') }}
					</router-link>
				</div>

				<!-- Progress Bar -->
				<div class="mt-6">
					<div class="flex justify-between text-xs text-white/70 mb-2">
						<span>{{ membership.data.start_date_formatted }}</span>
						<span>{{ membership.data.end_date_formatted }}</span>
					</div>
					<div class="h-2 bg-white/20 rounded-full overflow-hidden">
						<div class="h-full bg-white/80 rounded-full transition-all duration-500"
							:style="{ width: `${Math.min(100, 100 - (membership.data.days_remaining / membership.data.total_days * 100))}%` }">
						</div>
					</div>
					<p class="text-center text-xs text-white/70 mt-2">
						{{ membership.data.days_remaining }} {{ __('days remaining') }}
					</p>
				</div>

				<!-- Manage Subscription Button (only for own profile) -->
				<div v-if="isOwnProfile" class="mt-6 flex justify-center">
					<router-link to="/membership" 
						class="inline-flex items-center gap-2 px-6 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg font-medium text-sm transition-colors border border-white/20">
						<Settings class="w-4 h-4" />
						{{ __('Manage Subscription') }}
					</router-link>
				</div>
			</div>
		</div>

		<!-- No Membership Card (for own profile) -->
		<div v-else-if="isOwnProfile" class="rounded-xl border-2 border-dashed border-gray-300 p-6">
			<div class="text-center">
				<div class="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-100 flex items-center justify-center">
					<Users class="w-8 h-8 text-gray-400" />
				</div>
				<h3 class="text-lg font-semibold text-gray-700 mb-2">
					{{ __('No Active Membership') }}
				</h3>
				<p class="text-sm text-gray-500 mb-4">
					{{ __('Subscribe to get unlimited access to all courses.') }}
				</p>
				<router-link to="/membership" 
					class="inline-flex items-center gap-2 px-6 py-3 bg-blue-900 text-white rounded-lg font-medium hover:bg-blue-800 transition-colors">
					{{ __('View Membership Plans') }}
					<ArrowRight class="w-4 h-4" />
				</router-link>
			</div>
		</div>

		<!-- No Membership (viewing other user's profile) -->
		<div v-else class="rounded-xl border border-gray-200 p-6">
			<div class="flex items-center gap-3 text-gray-500">
				<Users class="w-5 h-5" />
				<span class="text-sm">{{ __('This user does not have an active membership') }}</span>
			</div>
		</div>
	</div>

	<div class="mt-7 mb-10">
		<h2 class="mb-3 text-lg font-semibold text-ink-gray-9">
			{{ __('About') }}
		</h2>
		<div
			v-if="profile.data.bio"
			v-html="
				DOMPurify.sanitize(decodeEntities(profile.data.bio), {
					ALLOWED_TAGS: [
						'b',
						'i',
						'em',
						'strong',
						'a',
						'p',
						'br',
						'ul',
						'ol',
						'li',
						'img',
					],
					ALLOWED_ATTR: ['href', 'target', 'rel', 'src'],
				})
			"
			class="ProseMirror prose prose-table:table-fixed prose-td:p-2 prose-th:p-2 prose-td:border prose-th:border prose-td:border-outline-gray-2 prose-th:border-outline-gray-2 prose-td:relative prose-th:relative prose-th:bg-surface-gray-2 prose-sm max-w-none !whitespace-normal"
		></div>
		<div v-else class="text-ink-gray-7 text-sm italic">
			{{ __('No introduction') }}
		</div>
	</div>
	<div class="mt-7 mb-10" v-if="badges.data?.length">
		<h2 class="mb-3 text-lg font-semibold text-ink-gray-9">
			{{ __('Achievements') }}
		</h2>
		<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
			<div v-for="badge in badges.data">
				<Popover trigger="hover" :leaveDelay="Number(0.01)">
					<template #target>
						<div class="relative">
							<img
								:src="badge.badge_image"
								:alt="badge.badge"
								class="h-[80px]"
							/>
							<div
								v-if="badge.count > 1"
								class="flex items-end bg-surface-gray-2 p-2 text-xs font-semibold rounded-full absolute right-0 bottom-0"
							>
								<span>
									<X class="w-3 h-3" />
								</span>
								{{ badge.count }}
							</div>
						</div>
					</template>
					<template #body-main>
						<div class="w-[250px] text-base">
							<img
								:src="badge.badge_image"
								:alt="badge.badge"
								class="bg-surface-gray-2 rounded-t-md h-[200px] mx-auto"
							/>
							<div class="p-5">
								<div class="text-2xl font-semibold mb-2">
									{{ badge.badge }}
								</div>
								<div class="leading-5 mb-4">
									{{ badge.badge_description }}
								</div>
								<div class="flex flex-col mb-4">
									<span class="text-xs text-ink-gray-7 font-medium mb-1">
										{{ __('Issued on') }}:
									</span>
									{{ dayjs(badge.issued_on).format('DD MMM YYYY') }}
								</div>
								<div class="flex flex-col">
									<span class="text-xs text-ink-gray-7 font-medium mb-1">
										{{ __('Share on') }}:
									</span>
									<div class="flex items-center space-x-2">
										<Button
											variant="outline"
											size="sm"
											@click="shareOnSocial(badge, 'LinkedIn')"
										>
											<template #prefix>
												<LinkedinIcon class="h-3 w-3 text-ink-gray-7" />
											</template>
											<span class="text-xs">
												{{ __('LinkedIn') }}
											</span>
										</Button>
										<Button
											variant="outline"
											size="sm"
											@click="shareOnSocial(badge, 'Twitter')"
										>
											<template #prefix>
												<Twitter class="h-3 w-3 text-ink-gray-7" />
											</template>
											<span class="text-xs">
												{{ __('Twitter') }}
											</span>
										</Button>
									</div>
								</div>
							</div>
						</div>
					</template>
				</Popover>
			</div>
		</div>
	</div>
</template>
<script setup>
import { inject, computed, watch } from 'vue'
import { createResource, Popover, Button } from 'frappe-ui'
import { X, LinkedinIcon, Twitter, Award, AlertTriangle, Users, ArrowRight, Settings } from 'lucide-vue-next'
import { sessionStore } from '@/stores/session'
import { decodeEntities } from '@/utils'
import DOMPurify from 'dompurify'

const dayjs = inject('$dayjs')
const user = inject('$user')
const { branding } = sessionStore()

const props = defineProps({
	profile: {
		type: Object,
		required: true,
	},
})

// Check if viewing own profile
const isOwnProfile = computed(() => {
	return user.data?.name === props.profile.data?.name
})

// Fetch membership status for the profile being viewed
const membership = createResource({
	url: 'lms_memberships.api.membership.get_user_membership_status',
	params: {
		user_email: props.profile.data?.name
	},
	auto: true,
})

// Reload membership data when profile changes
watch(() => props.profile.data?.name, (newVal) => {
	if (newVal) {
		membership.update({
			params: { user_email: newVal }
		})
		membership.reload()
	}
})

const badges = createResource({
	url: 'frappe.client.get_list',
	params: {
		doctype: 'LMS Badge Assignment',
		fields: ['name', 'badge', 'badge_image', 'badge_description', 'issued_on'],
		filters: {
			member: props.profile.data.name,
		},
	},
	auto: true,
	transform(data) {
		let finalBadges = []
		let groupedBadges = Object.groupBy(data, ({ badge }) => badge)
		for (let badge in groupedBadges) {
			let badgeData = groupedBadges[badge][0]
			badgeData.count = groupedBadges[badge].length
			finalBadges.push(badgeData)
		}
		return finalBadges
	},
})

const shareOnSocial = (badge, medium) => {
	let shareUrl
	const url = encodeURIComponent(
		`${window.location.origin}/lms/badges/${badge.badge}/${props.profile.data?.email}`
	)
	const summary = `I am happy to announce that I earned the ${
		badge.badge
	} badge on ${dayjs(badge.issued_on).format('DD MMM YYYY')} at ${
		branding.data?.app_name
	}.`

	if (medium == 'LinkedIn')
		shareUrl = `https://www.linkedin.com/shareArticle?mini=true&url=${url}&text=${summary}`
	else if (medium == 'Twitter')
		shareUrl = `https://twitter.com/intent/tweet?text=${summary}&url=${url}`

	window.open(shareUrl, '_blank')
}
</script>
