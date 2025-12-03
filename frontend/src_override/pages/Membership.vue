<template>
	<header
		class="sticky flex items-center justify-between top-0 z-10 border-b bg-surface-white px-3 py-2.5 sm:px-5"
	>
		<Breadcrumbs :items="breadcrumbs" />
	</header>

	<div class="max-w-6xl mx-auto px-5 py-10">
		<!-- Hero Section -->
		<div class="text-center mb-12">
			<h1 class="text-4xl font-bold text-ink-gray-9 mb-4">
				{{ __('Membership Plans') }}
			</h1>
			<p class="text-lg text-ink-gray-6 max-w-2xl mx-auto">
				{{ __('Unlock unlimited access to all courses and accelerate your learning journey with our membership plans.') }}
			</p>
		</div>

		<!-- Pending Payment Alert -->
		<div v-if="pendingMembership.data" 
			class="mb-10 p-6 rounded-2xl bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-xl">
			<div class="flex items-center justify-between flex-wrap gap-4">
				<div class="flex items-center gap-4">
					<div class="w-14 h-14 rounded-full bg-white/20 flex items-center justify-center">
						<Clock class="w-7 h-7 text-white" />
					</div>
					<div>
						<h2 class="text-xl font-bold">{{ __('Pending Payment') }}</h2>
						<p class="text-white/90">
							{{ __('You have a pending payment for') }} {{ pendingMembership.data.tier_name }}.
							{{ __('Created on') }} {{ pendingMembership.data.creation_formatted }}.
						</p>
					</div>
				</div>
				<div class="flex items-center gap-3">
					<Button 
						@click="retryPendingPayment"
						:loading="retryLoading"
						class="bg-white text-amber-600 hover:bg-amber-50">
						{{ __('Complete Payment') }}
					</Button>
					<button 
						@click="cancelPendingPayment"
						:disabled="cancelLoading"
						class="px-4 py-2 rounded-lg font-medium border-2 border-white/70 text-white bg-transparent hover:bg-white/20 transition-colors disabled:opacity-50">
						<span v-if="cancelLoading">...</span>
						<span v-else>{{ __('Cancel') }}</span>
					</button>
				</div>
			</div>
		</div>

		<!-- Current Membership Status (if member) -->
		<div v-if="user.data?.has_active_membership" 
			class="mb-10 p-6 rounded-2xl bg-gradient-to-r from-green-500 to-emerald-600 text-white shadow-xl">
			<div class="flex items-center justify-between flex-wrap gap-4">
				<div class="flex items-center gap-4">
					<div class="w-14 h-14 rounded-full bg-white/20 flex items-center justify-center">
						<Award class="w-7 h-7 text-white" />
					</div>
					<div>
						<h2 class="text-xl font-bold">{{ __('You are a') }} {{ user.data?.membership?.tier_name }}!</h2>
						<p class="text-white/90">
							{{ __('Your membership is valid until') }} {{ user.data?.membership?.end_date_formatted }}
						</p>
					</div>
				</div>
				<div class="flex items-center gap-3">
					<div class="text-right">
						<div class="text-2xl font-bold">{{ user.data?.membership?.days_remaining }}</div>
						<div class="text-sm text-white/80">{{ __('days remaining') }}</div>
					</div>
				</div>
			</div>
			<div v-if="user.data?.membership?.is_expiring_soon" 
				class="mt-4 p-3 bg-orange-500/30 rounded-lg text-sm flex items-center gap-2">
				<AlertTriangle class="w-5 h-5" />
				{{ __('Your membership expires soon. Renew now to keep your access!') }}
			</div>
		</div>

		<!-- Loading State -->
		<div v-if="tiers.loading" class="flex justify-center py-20">
			<Spinner class="w-8 h-8 text-blue-600" />
		</div>

		<!-- Membership Tiers -->
		<div v-else-if="tiers.data?.length" class="flex justify-center">
			<div class="grid grid-cols-1 gap-8" 
				:class="{
					'md:grid-cols-2 lg:grid-cols-3 max-w-5xl': tiers.data.length >= 3,
					'md:grid-cols-2 max-w-3xl': tiers.data.length === 2,
					'max-w-md': tiers.data.length === 1
				}">
			<div v-for="tier in tiers.data" :key="tier.name"
				class="relative rounded-2xl border-2 transition-all duration-300 hover:shadow-xl"
				:class="tier.is_popular 
					? 'border-blue-900 shadow-lg scale-105 bg-white' 
					: 'border-gray-200 bg-white hover:border-blue-300'">
				
				<!-- Popular Badge -->
				<div v-if="tier.is_popular" 
					class="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-blue-900 text-white text-sm font-semibold rounded-full">
					{{ __('Most Popular') }}
				</div>

				<div class="p-8">
					<!-- Tier Header -->
					<div class="text-center mb-6">
						<div class="w-16 h-16 mx-auto mb-4 rounded-2xl flex items-center justify-center"
							:class="tier.is_popular ? 'bg-blue-900' : 'bg-gray-100'">
							<Crown v-if="tier.is_popular" class="w-8 h-8 text-white" />
							<Award v-else class="w-8 h-8 text-gray-600" />
						</div>
						<h3 class="text-2xl font-bold text-ink-gray-9">{{ tier.tier_name }}</h3>
						<p class="text-ink-gray-6 mt-2 text-sm">{{ tier.description }}</p>
					</div>

					<!-- Pricing -->
					<div class="text-center mb-6">
						<div class="flex items-baseline justify-center gap-1">
							<span class="text-lg text-ink-gray-6">Rp</span>
							<span class="text-4xl font-bold text-ink-gray-9">{{ formatPrice(tier.price) }}</span>
						</div>
						<div class="text-ink-gray-5 text-sm mt-1">
							/ {{ tier.duration_months }} {{ tier.duration_months > 1 ? __('months') : __('month') }}
						</div>
						<div v-if="tier.duration_months >= 12" class="text-green-600 text-sm font-medium mt-2">
							{{ __('Save') }} {{ Math.round((1 - (tier.price / (tier.duration_months * getMonthlyPrice(tier)))) * 100) }}%
						</div>
					</div>

					<!-- Features -->
					<ul class="space-y-3 mb-8">
						<li class="flex items-start gap-3">
							<Check class="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
							<span class="text-ink-gray-7">{{ __('Access to all courses') }}</span>
						</li>
						<li class="flex items-start gap-3">
							<Check class="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
							<span class="text-ink-gray-7">{{ __('Unlimited learning materials') }}</span>
						</li>
						<li class="flex items-start gap-3">
							<Check class="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
							<span class="text-ink-gray-7">{{ __('Certificate of completion') }}</span>
						</li>
						<li v-if="tier.duration_months >= 6" class="flex items-start gap-3">
							<Check class="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
							<span class="text-ink-gray-7">{{ __('Priority support') }}</span>
						</li>
						<li v-if="tier.duration_months >= 12" class="flex items-start gap-3">
							<Check class="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
							<span class="text-ink-gray-7">{{ __('Exclusive member events') }}</span>
						</li>
					</ul>

					<!-- CTA Button -->
					<Button 
						v-if="user.data"
						@click="selectPlan(tier)"
						:loading="selectedTier === tier.name && paymentLoading"
						:variant="tier.is_popular ? 'solid' : 'outline'"
						class="w-full justify-center py-3"
						:class="tier.is_popular 
							? 'bg-blue-900 hover:bg-blue-800 text-white' 
							: 'border-blue-900 text-blue-900 hover:bg-blue-50'">
						<template v-if="user.data?.has_active_membership">
							{{ user.data?.membership?.tier_name === tier.tier_name ? __('Current Plan') : __('Switch Plan') }}
						</template>
						<template v-else>
							{{ __('Get Started') }}
						</template>
					</Button>
					<a v-else 
						:href="`/login?redirect-to=/lms/membership`"
						class="block w-full text-center py-3 rounded-lg font-medium transition-colors"
						:class="tier.is_popular 
							? 'bg-blue-900 hover:bg-blue-800 text-white' 
							: 'border-2 border-blue-900 text-blue-900 hover:bg-blue-50'">
						{{ __('Login to Subscribe') }}
					</a>
				</div>
			</div>
			</div>
		</div>

		<!-- No Plans Available -->
		<div v-else class="text-center py-20">
			<div class="w-20 h-20 mx-auto mb-6 rounded-full bg-gray-100 flex items-center justify-center">
				<Package class="w-10 h-10 text-gray-400" />
			</div>
			<h3 class="text-xl font-semibold text-ink-gray-9 mb-2">{{ __('No Plans Available') }}</h3>
			<p class="text-ink-gray-6">{{ __('Membership plans are being prepared. Please check back later.') }}</p>
		</div>

		<!-- FAQ Section -->
		<div class="mt-16">
			<h2 class="text-2xl font-bold text-ink-gray-9 text-center mb-8">
				{{ __('Frequently Asked Questions') }}
			</h2>
			<div class="max-w-3xl mx-auto space-y-4">
				<div class="border border-gray-200 rounded-xl p-5">
					<h4 class="font-semibold text-ink-gray-9 mb-2">{{ __('What happens when my membership expires?') }}</h4>
					<p class="text-ink-gray-6 text-sm">{{ __('When your membership expires, you will lose access to premium courses. You can renew anytime to regain access.') }}</p>
				</div>
				<div class="border border-gray-200 rounded-xl p-5">
					<h4 class="font-semibold text-ink-gray-9 mb-2">{{ __('Can I cancel my membership?') }}</h4>
					<p class="text-ink-gray-6 text-sm">{{ __('Memberships are non-refundable, but you can enjoy access until the end of your subscription period.') }}</p>
				</div>
				<div class="border border-gray-200 rounded-xl p-5">
					<h4 class="font-semibold text-ink-gray-9 mb-2">{{ __('How do I pay for membership?') }}</h4>
					<p class="text-ink-gray-6 text-sm">{{ __('We accept various payment methods including bank transfer, e-wallets, and credit cards through our secure payment gateway.') }}</p>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, inject, computed } from 'vue'
import { Breadcrumbs, Button, Spinner, createResource, call } from 'frappe-ui'
import { Award, Crown, Check, AlertTriangle, Package, Clock } from 'lucide-vue-next'

const user = inject('$user')
const selectedTier = ref(null)
const paymentLoading = ref(false)
const retryLoading = ref(false)
const cancelLoading = ref(false)

const breadcrumbs = computed(() => [
	{ label: __('Home'), route: { name: 'Home' } },
	{ label: __('Membership'), route: { name: 'Membership' } },
])

const tiers = createResource({
	url: 'lms_memberships.api.membership.get_membership_tiers',
	auto: true,
	transform(data) {
		// Mark the middle tier as popular if there are 3 tiers
		if (data.length === 3) {
			data[1].is_popular = true
		} else if (data.length > 0) {
			// Otherwise mark the first tier as popular
			data[0].is_popular = true
		}
		return data
	}
})

const pendingMembership = createResource({
	url: 'lms_memberships.api.membership.get_pending_membership',
	auto: true,
})

const retryPendingPayment = async () => {
	if (!pendingMembership.data) return
	
	retryLoading.value = true
	try {
		const result = await call('lms_memberships.api.membership.retry_pending_payment', {
			membership_name: pendingMembership.data.name
		})
		
		if (result?.payment_url) {
			window.location.href = result.payment_url
		}
	} catch (error) {
		console.error('Retry payment error:', error)
		frappe.msgprint({
			title: __('Error'),
			indicator: 'red',
			message: error.messages?.[0] || __('Failed to retry payment. Please try again.')
		})
	} finally {
		retryLoading.value = false
	}
}

const cancelPendingPayment = async () => {
	if (!pendingMembership.data) return
	
	cancelLoading.value = true
	try {
		await call('lms_memberships.api.membership.cancel_pending_membership', {
			membership_name: pendingMembership.data.name
		})
		
		// Refresh pending membership data
		pendingMembership.reload()
		
		frappe.msgprint({
			title: __('Success'),
			indicator: 'green',
			message: __('Pending membership cancelled. You can now subscribe to a different plan.')
		})
	} catch (error) {
		console.error('Cancel error:', error)
		frappe.msgprint({
			title: __('Error'),
			indicator: 'red',
			message: error.messages?.[0] || __('Failed to cancel. Please try again.')
		})
	} finally {
		cancelLoading.value = false
	}
}

const formatPrice = (price) => {
	return new Intl.NumberFormat('id-ID').format(price)
}

const getMonthlyPrice = (tier) => {
	// Calculate equivalent monthly price for comparison
	// Use the 1-month tier price as base
	const baseTier = tiers.data?.find(t => t.duration_months === 1)
	if (baseTier) {
		return baseTier.price
	}
	return tier.price / tier.duration_months
}

const selectPlan = async (tier) => {
	if (!user.data) {
		window.location.href = `/login?redirect-to=/lms/membership`
		return
	}

	// If already on this plan, do nothing
	if (user.data?.membership?.tier_name === tier.tier_name && user.data?.has_active_membership) {
		return
	}

	selectedTier.value = tier.name
	paymentLoading.value = true

	try {
		const result = await call('lms_memberships.api.membership.create_membership_payment', {
			tier_name: tier.name
		})
		
		if (result?.payment_url) {
			window.location.href = result.payment_url
		} else if (result?.error) {
			frappe.msgprint({
				title: __('Error'),
				indicator: 'red',
				message: result.error
			})
		} else {
			console.log('Unexpected result:', result)
			frappe.msgprint({
				title: __('Error'),
				indicator: 'red',
				message: __('Unexpected response from server. Please try again.')
			})
		}
	} catch (error) {
		console.error('Payment error:', error)
		frappe.msgprint({
			title: __('Error'),
			indicator: 'red',
			message: error.messages?.[0] || __('Failed to initiate payment. Please try again.')
		})
	} finally {
		paymentLoading.value = false
		selectedTier.value = null
	}
}
</script>
