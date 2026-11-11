<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const loading = ref(true)
const error = ref('')
const user = ref({
    name: '',
    full_name: '',
    email: '',
    mobile_no: '',
    user_image: ''
})

const primaryColor = '#82103c'

const getCsrfToken = () => (
    document.querySelector('meta[name="csrf-token"]')?.content ||
    window.frappe?.csrf_token ||
    ''
)

const readApiResponse = async (response) => {
    try {
        return await response.json()
    } catch {
        return {}
    }
}

const getApiErrorMessage = (result, fallback) => {
    if (result?._server_messages) {
        try {
            const messages = JSON.parse(result._server_messages)
                .map(message => JSON.parse(message).message)
                .filter(Boolean)

            if (messages.length) return messages.join(', ')
        } catch (err) {
            console.error('Server message parse error:', err)
        }
    }

    if (typeof result?.message === 'string' && result.message.trim()) {
        return result.message
    }

    if (typeof result?.message?.message === 'string') {
        return result.message.message
    }

    return fallback
}

// Fetch logged-in user
const getProfile = async () => {
    loading.value = true
    error.value = ''

    try {
        const response = await fetch(
            '/api/method/buy_new.api.get_current_user_profile',
            {
                method: 'GET',
                credentials: 'same-origin',
                headers: {
                    Accept: 'application/json'
                }
            }
        )

        const result = await readApiResponse(response)

        if (!response.ok || result.exc || result.exception) {
            const errorDetails = `${result.exc_type || ''} ${result.exception || ''} ${result.message || ''}`
            if ([401, 403].includes(response.status) || /PermissionError|Please login/i.test(errorDetails)) {
                await router.replace('/login')
                return
            }

            throw new Error(getApiErrorMessage(result, 'Unable to load profile details'))
        }

        if (!result.message || typeof result.message !== 'object') {
            throw new Error('The profile API returned no user details')
        }

        user.value = result.message

    } catch (err) {
        console.error('Profile Error:', err)
        error.value = err.message || 'Unable to load your profile. Please try again.'
    } finally {
        loading.value = false
    }
}

// Logout
const logout = async () => {
    try {
        const response = await fetch('/api/method/logout', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'X-Frappe-CSRF-Token': getCsrfToken()
            }
        })

        const result = await readApiResponse(response)

        if (!response.ok || result.exc || result.exception) {
            throw new Error(getApiErrorMessage(result, 'Logout failed'))
        }

        window.dispatchEvent(
            new Event('buynew-auth-changed')
        )

        await router.replace('/home')

    } catch (err) {
        console.error('Logout Error:', err)
        error.value = err.message || 'Unable to logout. Please try again.'
    }
}

onMounted(() => {
    getProfile()
})
</script>

<template>
    <div class="min-h-screen bg-gray-50 px-3 py-6 sm:px-6 sm:py-10">

        <div class="mx-auto max-w-5xl">

            <!-- Page Heading -->
            <div class="mb-7">
                <h1 class="text-2xl font-bold text-gray-900 sm:text-3xl">
                    My Profile
                </h1>
                <p class="mt-2 text-sm text-gray-500">
                    Manage your BuyNew account information
                </p>
            </div>

            <!-- Loading -->
            <div v-if="loading" class="rounded-2xl bg-white p-12 text-center shadow-sm">
                <i class="fas fa-spinner fa-spin text-3xl" :style="{ color: primaryColor }"></i>
                <p class="mt-3 text-sm text-gray-500">
                    Loading profile...
                </p>
            </div>

            <!-- Error -->
            <div v-else-if="error" class="rounded-xl border border-red-200 bg-white p-8 text-center">
                <i class="fas fa-exclamation-circle text-3xl text-red-500"></i>

                <p class="mt-3 text-sm text-red-600">
                    {{ error }}
                </p>

                <button @click="getProfile" class="mt-4 rounded-lg px-5 py-2 text-sm font-semibold text-white"
                    :style="{ backgroundColor: primaryColor }">
                    Try Again
                </button>
            </div>

            <!-- Profile Content -->
            <div v-else class="grid gap-6 md:grid-cols-3">

                <!-- Profile Card -->
                <div class="overflow-hidden rounded-2xl bg-white shadow-sm md:col-span-1">

                    <!-- Cover -->
                    <div class="h-32" :style="{
                        background: `linear-gradient(135deg, ${primaryColor}, #a83260)`
                    }"></div>

                    <div class="-mt-14 px-5 pb-7 text-center">

                        <!-- Profile Image -->
                        <div
                            class="mx-auto flex h-28 w-28 items-center justify-center overflow-hidden rounded-full border-4 border-white bg-gray-100 shadow-md">
                            <img v-if="user.user_image" :src="user.user_image" alt="Profile"
                                class="h-full w-full object-cover" />

                            <i v-else class="fas fa-user text-4xl" :style="{ color: primaryColor }"></i>
                        </div>

                        <h2 class="mt-4 text-xl font-bold text-gray-900">
                            {{ user.full_name || user.name }}
                        </h2>

                        <p class="mt-1 break-all text-sm text-gray-500">
                            {{ user.email || user.name }}
                        </p>

                        <span class="mt-4 inline-flex items-center gap-2 rounded-full px-4 py-2 text-xs font-semibold"
                            :style="{
                                backgroundColor: '#f8edf1',
                                color: primaryColor
                            }">
                            <i class="fas fa-check-circle"></i>
                            Active Account
                        </span>

                    </div>
                </div>

                <!-- Account Information -->
                <div class="rounded-2xl bg-white p-5 shadow-sm sm:p-7 md:col-span-2">

                    <div class="mb-6 flex items-center justify-between">
                        <h2 class="text-lg font-bold text-gray-900">
                            Personal Information
                        </h2>

                        <i class="fas fa-user-circle text-2xl" :style="{ color: primaryColor }"></i>
                    </div>

                    <div class="space-y-5">

                        <!-- Full Name -->
                        <div>
                            <label class="mb-2 block text-xs font-semibold uppercase tracking-wide text-gray-400">
                                Full Name
                            </label>

                            <div class="flex items-center gap-3 rounded-xl border border-gray-100 bg-gray-50 p-4">
                                <i class="fas fa-user w-5" :style="{ color: primaryColor }"></i>

                                <span class="break-all text-sm font-medium text-gray-800">
                                    {{ user.full_name || 'Not available' }}
                                </span>
                            </div>
                        </div>

                        <!-- Email -->
                        <div>
                            <label class="mb-2 block text-xs font-semibold uppercase tracking-wide text-gray-400">
                                Email Address
                            </label>

                            <div class="flex items-center gap-3 rounded-xl border border-gray-100 bg-gray-50 p-4">
                                <i class="fas fa-envelope w-5" :style="{ color: primaryColor }"></i>

                                <span class="break-all text-sm font-medium text-gray-800">
                                    {{ user.email || user.name }}
                                </span>
                            </div>
                        </div>

                        <!-- Mobile -->
                        <div>
                            <label class="mb-2 block text-xs font-semibold uppercase tracking-wide text-gray-400">
                                Mobile Number
                            </label>

                            <div class="flex items-center gap-3 rounded-xl border border-gray-100 bg-gray-50 p-4">
                                <i class="fas fa-phone w-5" :style="{ color: primaryColor }"></i>

                                <span class="text-sm font-medium text-gray-800">
                                    {{ user.mobile_no || 'Not available' }}
                                </span>
                            </div>
                        </div>

                    </div>

                    <!-- Logout -->
                    <div class="mt-8 border-t border-gray-100 pt-6">

                        <button @click="logout"
                            class="flex w-full items-center justify-center gap-2 rounded-xl px-5 py-3 font-semibold text-white transition hover:opacity-90 sm:w-auto"
                            :style="{ backgroundColor: primaryColor }">
                            <i class="fas fa-sign-out-alt"></i>
                            Logout
                        </button>

                    </div>

                </div>

            </div>

        </div>
    </div>
</template>
