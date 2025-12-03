<template>
	<!-- Member Banner - Greeting -->
	<div v-if="user.data?.has_active_membership" 
		class="rounded-xl p-4 bg-gradient-to-r from-green-600 to-green-800 text-white shadow-lg">
		<div class="flex items-center justify-between flex-wrap gap-4">
			<div class="flex items-center gap-4">
				<div class="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center">
					<Award class="w-6 h-6 text-white" />
				</div>
				<div>
					<h3 class="text-lg font-semibold">
						{{ __('Welcome back') }}, {{ user.data?.membership?.tier_name || __('Member') }}! 🎉
					</h3>
					<p class="text-sm text-white/90">
						{{ __('You have full access to all courses. Valid until') }} {{ user.data?.membership?.end_date_formatted }}.
					</p>
				</div>
			</div>
			<div v-if="user.data?.membership?.is_expiring_soon">
				<router-link to="/membership" 
					class="inline-flex items-center gap-2 px-4 py-2 bg-white text-green-700 rounded-lg font-medium text-sm hover:bg-green-50 transition-colors">
					{{ __('Renew Membership') }}
					<ArrowRight class="w-4 h-4" />
				</router-link>
			</div>
		</div>
		<div v-if="user.data?.membership?.is_expiring_soon" 
			class="mt-3 p-2 bg-orange-500/20 rounded-lg text-sm">
			⚠️ {{ __('Your membership expires in') }} {{ user.data?.membership?.days_remaining }} {{ __('days') }}. {{ __('Renew now to keep your access!') }}
		</div>
	</div>

	<!-- Non-Member Banner - CTA -->
	<div v-else-if="user.data && !user.data?.has_active_membership" 
		class="rounded-xl p-4 bg-gradient-to-r from-blue-900 to-blue-700 text-white shadow-lg">
		<div class="flex items-center justify-between flex-wrap gap-4">
			<div class="flex items-center gap-4">
				<div class="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center">
					<Sparkles class="w-6 h-6 text-white" />
				</div>
				<div>
					<h3 class="text-lg font-semibold">{{ __('Unlock Unlimited Learning') }}</h3>
					<p class="text-sm text-white/90">
						{{ __('Get access to all courses with our membership plans. Learn at your own pace.') }}
					</p>
				</div>
			</div>
			<router-link to="/membership" 
				class="inline-flex items-center gap-2 px-4 py-2 bg-white text-blue-900 rounded-lg font-medium text-sm hover:bg-blue-50 transition-colors">
				{{ __('View Plans') }}
				<ArrowRight class="w-4 h-4" />
			</router-link>
		</div>
	</div>

	<!-- Guest Banner - Sign Up CTA -->
	<div v-else-if="!user.data" 
		class="rounded-xl p-4 bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow-lg">
		<div class="flex items-center justify-between flex-wrap gap-4">
			<div class="flex items-center gap-4">
				<div class="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center">
					<Users class="w-6 h-6 text-white" />
				</div>
				<div>
					<h3 class="text-lg font-semibold">{{ __('Join Our Learning Community') }}</h3>
					<p class="text-sm text-white/90">
						{{ __('Sign up and subscribe to get unlimited access to all courses.') }}
					</p>
				</div>
			</div>
			<a href="/login?redirect-to=/lms/membership" 
				class="inline-flex items-center gap-2 px-4 py-2 bg-white text-blue-700 rounded-lg font-medium text-sm hover:bg-blue-50 transition-colors">
				{{ __('Get Started') }}
				<ArrowRight class="w-4 h-4" />
			</a>
		</div>
	</div>
</template>

<script setup>
import { inject } from 'vue'
import { Award, Sparkles, Users, ArrowRight } from 'lucide-vue-next'

const user = inject('$user')
</script>
