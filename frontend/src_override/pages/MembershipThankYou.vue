<template>
	<header
		class="sticky flex items-center justify-between top-0 z-10 border-b bg-surface-white px-3 py-2.5 sm:px-5"
	>
		<Breadcrumbs :items="breadcrumbs" />
	</header>

	<!-- Loading State -->
	<div v-if="loading" class="flex flex-col items-center justify-center min-h-[60vh]">
		<Spinner class="w-12 h-12 text-blue-600" />
		<p class="mt-4 text-ink-gray-6">{{ __('Loading your membership details...') }}</p>
	</div>

	<!-- Error State -->
	<div v-else-if="error" class="max-w-2xl mx-auto px-5 py-20 text-center">
		<div class="w-20 h-20 mx-auto mb-6 rounded-full bg-red-100 flex items-center justify-center">
			<AlertCircle class="w-10 h-10 text-red-500" />
		</div>
		<h1 class="text-2xl font-bold text-ink-gray-9 mb-4">{{ __('Oops! Something went wrong') }}</h1>
		<p class="text-ink-gray-6 mb-8">{{ error }}</p>
		<div class="flex justify-center gap-4">
			<Button variant="solid" @click="$router.push({ name: 'Membership' })">
				{{ __('Back to Membership') }}
			</Button>
		</div>
	</div>

	<!-- Success State -->
	<div v-else-if="membership" class="max-w-4xl mx-auto px-5 py-10">
		<!-- Success Hero -->
		<div class="text-center mb-10 p-8 rounded-2xl"
			:class="membership.status === 'Active' 
				? 'bg-gradient-to-r from-green-600 to-green-800 text-white' 
				: 'bg-gradient-to-r from-amber-500 to-orange-500 text-white'">
			<div class="w-20 h-20 mx-auto mb-6 rounded-full bg-white/20 flex items-center justify-center">
				<CheckCircle v-if="membership.status === 'Active'" class="w-10 h-10 text-white" />
				<Clock v-else class="w-10 h-10 text-white" />
			</div>
			<h1 class="text-3xl font-bold mb-3">
				<template v-if="membership.status === 'Active'">
					{{ __('Welcome to') }} {{ tier?.tier_name }}!
				</template>
				<template v-else>
					{{ __('Payment Processing') }}
				</template>
			</h1>
			<p class="text-lg text-white/90 max-w-lg mx-auto">
				<template v-if="membership.status === 'Active'">
					{{ __('Congratulations') }}, {{ userName }}! 
					{{ __('Your membership is now active. Start exploring your courses below.') }}
				</template>
				<template v-else>
					{{ __('Thank you for subscribing! Your payment is being processed. Your membership will be activated shortly.') }}
				</template>
			</p>
		</div>

		<!-- Membership Details Card -->
		<div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden mb-10">
			<div class="p-6 border-b border-gray-100">
				<div class="flex items-center justify-between flex-wrap gap-4">
					<div>
						<h2 class="text-xl font-bold text-ink-gray-9">{{ tier?.tier_name }}</h2>
						<p class="text-ink-gray-6">{{ tier?.description || __('Premium membership') }}</p>
					</div>
					<div class="flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium"
						:class="membership.status === 'Active' 
							? 'bg-green-100 text-green-700' 
							: 'bg-amber-100 text-amber-700'">
						<CheckCircle v-if="membership.status === 'Active'" class="w-4 h-4" />
						<Clock v-else class="w-4 h-4" />
						{{ membership.status === 'Active' ? __('Active') : __('Processing') }}
					</div>
				</div>
			</div>
			
			<div class="grid grid-cols-2 md:grid-cols-4 gap-6 p-6">
				<div>
					<div class="text-sm text-ink-gray-5 mb-1">{{ __('Member') }}</div>
					<div class="font-medium text-ink-gray-9">{{ userName }}</div>
				</div>
				<div>
					<div class="text-sm text-ink-gray-5 mb-1">{{ __('Membership ID') }}</div>
					<div class="font-medium text-ink-gray-9">{{ membership.name }}</div>
				</div>
				<div>
					<div class="text-sm text-ink-gray-5 mb-1">{{ __('Start Date') }}</div>
					<div class="font-medium text-ink-gray-9">{{ membership.start_date || __('Pending') }}</div>
				</div>
				<div>
					<div class="text-sm text-ink-gray-5 mb-1">{{ __('End Date') }}</div>
					<div class="font-medium text-ink-gray-9">{{ membership.end_date || __('Pending') }}</div>
				</div>
			</div>
		</div>

		<!-- Quick Actions -->
		<div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10">
			<router-link :to="{ name: 'Courses' }" 
				class="flex items-center gap-4 p-5 bg-white rounded-xl border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all">
				<div class="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center">
					<BookOpen class="w-6 h-6 text-blue-600" />
				</div>
				<div>
					<div class="font-semibold text-ink-gray-9">{{ __('Browse Courses') }}</div>
					<div class="text-sm text-ink-gray-6">{{ __('Start learning now') }}</div>
				</div>
			</router-link>
			
			<router-link :to="{ name: 'ProfileAbout' }" 
				class="flex items-center gap-4 p-5 bg-white rounded-xl border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all">
				<div class="w-12 h-12 rounded-xl bg-purple-100 flex items-center justify-center">
					<User class="w-6 h-6 text-purple-600" />
				</div>
				<div>
					<div class="font-semibold text-ink-gray-9">{{ __('My Profile') }}</div>
					<div class="text-sm text-ink-gray-6">{{ __('View your details') }}</div>
				</div>
			</router-link>
			
			<router-link :to="{ name: 'Membership' }" 
				class="flex items-center gap-4 p-5 bg-white rounded-xl border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all">
				<div class="w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center">
					<Award class="w-6 h-6 text-green-600" />
				</div>
				<div>
					<div class="font-semibold text-ink-gray-9">{{ __('Membership') }}</div>
					<div class="text-sm text-ink-gray-6">{{ __('Manage your plan') }}</div>
				</div>
			</router-link>
		</div>

		<!-- Accessible Courses -->
		<div v-if="courses.length > 0">
			<h2 class="text-2xl font-bold text-ink-gray-9 mb-6">
				{{ __('Start Learning') }}
			</h2>
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
				<router-link v-for="course in courses" :key="course.name"
					:to="{ name: 'CourseDetail', params: { courseName: course.name } }"
					class="group bg-white rounded-xl border border-gray-200 overflow-hidden hover:shadow-lg transition-all">
					<div class="aspect-video bg-gray-100 overflow-hidden">
						<img v-if="course.image" 
							:src="course.image" 
							:alt="course.title"
							class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
						<div v-else class="w-full h-full flex items-center justify-center">
							<BookOpen class="w-12 h-12 text-gray-300" />
						</div>
					</div>
					<div class="p-4">
						<div v-if="course.category" class="text-xs text-blue-600 font-medium mb-2">
							{{ course.category }}
						</div>
						<h3 class="font-semibold text-ink-gray-9 group-hover:text-blue-600 transition-colors line-clamp-2">
							{{ course.title }}
						</h3>
						<p v-if="course.short_introduction" class="text-sm text-ink-gray-6 mt-2 line-clamp-2">
							{{ course.short_introduction }}
						</p>
					</div>
				</router-link>
			</div>
			
			<div class="text-center mt-8">
				<Button variant="outline" @click="$router.push({ name: 'Courses' })">
					{{ __('View All Courses') }}
					<template #suffix>
						<ArrowRight class="w-4 h-4" />
					</template>
				</Button>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue'
import { useRoute } from 'vue-router'
import { Breadcrumbs, Button, Spinner, call } from 'frappe-ui'
import { 
	CheckCircle, Clock, AlertCircle, BookOpen, User, Award, ArrowRight 
} from 'lucide-vue-next'

const route = useRoute()
const user = inject('$user')

const loading = ref(true)
const error = ref(null)
const membership = ref(null)
const tier = ref(null)
const courses = ref([])

const breadcrumbs = computed(() => [
	{ label: __('Home'), route: { name: 'Home' } },
	{ label: __('Membership'), route: { name: 'Membership' } },
	{ label: __('Thank You'), route: { name: 'MembershipThankYou' } },
])

const userName = computed(() => {
	if (user.data?.first_name) {
		return user.data.first_name
	}
	return user.data?.full_name || user.data?.name || __('Member')
})

const loadMembershipDetails = async () => {
	loading.value = true
	error.value = null
	
	try {
		const membershipName = route.query.membership
		const transactionStatus = route.query.transaction_status
		
		if (!membershipName) {
			// Try to get the most recent membership
			const result = await call('lms_memberships.api.membership.get_recent_membership_with_details')
			if (!result) {
				error.value = __('No membership found. Please subscribe to a membership plan.')
				return
			}
			membership.value = result.membership
			tier.value = result.tier
			courses.value = result.courses || []
			return
		}
		
		// Get membership details with optional activation
		const result = await call('lms_memberships.api.membership.get_membership_thank_you_data', {
			membership_name: membershipName,
			transaction_status: transactionStatus
		})
		
		if (result.error) {
			error.value = result.error
			return
		}
		
		membership.value = result.membership
		tier.value = result.tier
		courses.value = result.courses || []
		
	} catch (err) {
		console.error('Error loading membership:', err)
		error.value = err.messages?.[0] || __('Failed to load membership details. Please try again.')
	} finally {
		loading.value = false
	}
}

onMounted(() => {
	loadMembershipDetails()
})
</script>

<style scoped>
.line-clamp-2 {
	display: -webkit-box;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
	overflow: hidden;
}
</style>
