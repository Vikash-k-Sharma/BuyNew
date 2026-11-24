<script setup>
import { ref, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'

const first_name = ref('')
const last_name = ref('')
const email = ref('')
const password = ref('')
const confirm_password = ref('')

const showPassword = ref(false)
const showConfirmPassword = ref(false)

const profileImage = ref(null)
const profileImagePreview = ref('')
const fileInput = ref(null)

const loading = ref(false)
const error = ref('')
const success = ref('')

// Select profile image
const handleImageSelect = (event) => {
    const file = event.target.files?.[0]

    error.value = ''

    if (!file) return

    const allowedTypes = [
        'image/jpeg',
        'image/png',
        'image/gif'
    ]

    if (!allowedTypes.includes(file.type)) {
        error.value = 'Please upload JPG, PNG or GIF image.'
        event.target.value = ''
        return
    }

    if (file.size > 5 * 1024 * 1024) {
        error.value = 'Image size must be less than 5 MB.'
        event.target.value = ''
        return
    }

    if (profileImagePreview.value) {
        URL.revokeObjectURL(profileImagePreview.value)
    }

    profileImage.value = file
    profileImagePreview.value = URL.createObjectURL(file)
}

// Remove profile image
const removeProfileImage = () => {
    if (profileImagePreview.value) {
        URL.revokeObjectURL(profileImagePreview.value)
    }

    profileImage.value = null
    profileImagePreview.value = ''

    if (fileInput.value) {
        fileInput.value.value = ''
    }
}

// Get CSRF token
const getCsrfToken = async () => {
    const existingToken = (
        document.querySelector('meta[name="csrf-token"]')?.content ||
        window.frappe?.csrf_token ||
        ''
    )

    if (existingToken) return existingToken

    const response = await fetch('/api/method/buy_new.api.get_csrf_token', {
        credentials: 'same-origin',
        headers: { Accept: 'application/json' }
    })
    const data = await response.json().catch(() => ({}))
    const token = data.message

    if (!response.ok || typeof token !== 'string' || !token) {
        throw new Error('Unable to start a secure upload. Please refresh the page and try again.')
    }

    window.frappe = window.frappe || {}
    window.frappe.csrf_token = token

    return token
}

const getServerError = (data) => {
    if (typeof data.message?.error === 'string') return data.message.error
    if (typeof data.message === 'string') return data.message

    try {
        const messages = JSON.parse(data._server_messages || '[]')
        const message = messages
            .map((entry) => JSON.parse(entry).message)
            .filter(Boolean)
            .at(-1)

        if (message) {
            const container = document.createElement('div')
            container.innerHTML = message
            return container.textContent?.trim() || ''
        }
    } catch {
        // Use the fallback message when Frappe returned no readable server message.
    }

    return ''
}

// Upload profile image
const uploadProfileImage = async () => {
    if (!profileImage.value) {
        throw new Error('Please upload your profile photo.')
    }

    const formData = new FormData()

    formData.append('file', profileImage.value)
    formData.append('is_private', '0')

    const csrfToken = await getCsrfToken()

    const response = await fetch(
        '/api/method/buy_new.api.upload_profile_image',
        {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                Accept: 'application/json',
                ...(csrfToken
                    ? { 'X-Frappe-CSRF-Token': csrfToken }
                    : {})
            },
            body: formData
        }
    )

    const data = await response.json().catch(() => ({}))

    if (
        !response.ok ||
        data.exc ||
        !data.message?.file_url
    ) {
        throw new Error(
            getServerError(data) ||
            'Unable to upload profile image. Please try again.'
        )
    }

    return data.message.file_url
}

// Register customer
const register = async () => {
    error.value = ''
    success.value = ''

    const cleanEmail = email.value.trim().toLowerCase()

    if (
        !first_name.value.trim() ||
        !cleanEmail ||
        !password.value ||
        !confirm_password.value ||
        !profileImage.value
    ) {
        error.value = 'Please fill all required fields and upload your profile photo.'
        return
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(cleanEmail)) {
        error.value = 'Please enter a valid email address.'
        return
    }

    if (password.value.length < 8) {
        error.value = 'Password must be at least 8 characters.'
        return
    }

    if (password.value !== confirm_password.value) {
        error.value = 'Passwords do not match.'
        return
    }

    loading.value = true

    try {
        // Upload profile photo
        const profileImageUrl = await uploadProfileImage()

        // Register customer
        const csrfToken = await getCsrfToken()

        const response = await fetch(
            '/api/method/buy_new.api.register_customer',
            {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                    Accept: 'application/json',
                    ...(csrfToken
                        ? { 'X-Frappe-CSRF-Token': csrfToken }
                        : {})
                },
                body: JSON.stringify({
                    first_name: first_name.value.trim(),
                    last_name: last_name.value.trim(),
                    email: cleanEmail,
                    password: password.value,
                    confirm_password: confirm_password.value,
                    profile_image: profileImageUrl
                })
            }
        )

        const data = await response.json()
        const result = data.message

        if (!response.ok || !result?.success) {
            throw new Error(
                result?.message ||
                data.exception ||
                'Registration failed. Please try again.'
            )
        }

        // Verify login session
        if (!result.logged_in) {
            throw new Error(
                'Account created, but automatic login was not completed.'
            )
        }

        const sessionResponse = await fetch(
            '/api/method/buy_new.api.get_session_user',
            {
                method: 'GET',
                credentials: 'same-origin',
                headers: {
                    Accept: 'application/json'
                }
            }
        )

        const sessionData = await sessionResponse.json()
        const loggedInUser = sessionData.message

        if (
            !sessionResponse.ok ||
            !loggedInUser ||
            loggedInUser === 'Guest' ||
            loggedInUser.toLowerCase() !== cleanEmail
        ) {
            throw new Error(
                'Account created, but login session could not be verified. Please try logging in.'
            )
        }

        // Update navbar
        window.dispatchEvent(
            new Event('buynew-auth-changed')
        )

        // Clear form
        first_name.value = ''
        last_name.value = ''
        email.value = ''
        password.value = ''
        confirm_password.value = ''

        removeProfileImage()

        // Show success message
        success.value = 'Account created successfully!'

        // Go to home
        window.location.assign('/home')

    } catch (err) {
        console.error('Registration Error:', err)

        error.value =
            err.message || 'Unable to connect to server.'

    } finally {
        loading.value = false
    }
}

onUnmounted(() => {
    if (profileImagePreview.value) {
        URL.revokeObjectURL(profileImagePreview.value)
    }
})
</script>

<template>
    <div class="min-h-[calc(100dvh-72px)] flex items-center justify-center bg-gray-100 px-3 py-5 sm:px-5 sm:py-8">

        <div class="w-full max-w-5xl overflow-hidden rounded-2xl bg-white shadow-xl grid grid-cols-1 md:grid-cols-2">

            <!-- Left Side -->
            <div class="hidden md:flex flex-col justify-center items-center bg-[#82103c] p-8 lg:p-12 text-white">

                <i class="fas fa-shopping-bag text-6xl lg:text-7xl mb-6"></i>

                <h1 class="text-3xl lg:text-4xl font-bold mb-4 text-center">
                    Welcome to BuyNew
                </h1>

                <p class="text-center text-pink-100 leading-relaxed text-sm lg:text-base">
                    Create your account and discover amazing products.
                    Shop your favourite products with BuyNew.
                </p>

                <div class="mt-8 text-center">
                    <i class="fas fa-user-plus text-4xl mb-3"></i>

                    <p class="text-sm text-pink-100">
                        Your shopping journey starts here.
                    </p>
                </div>

            </div>

            <!-- Right Side -->
            <div class="p-5 sm:p-8 lg:p-10 flex flex-col justify-center">

                <!-- Header -->
                <div class="mb-5 sm:mb-6">

                    <div class="flex items-center gap-3 mb-3 md:hidden">
                        <div class="w-10 h-10 rounded-xl bg-[#82103c] flex items-center justify-center text-white">
                            <i class="fas fa-shopping-bag text-lg"></i>
                        </div>

                        <span class="text-xl font-bold text-[#82103c]">
                            BuyNew
                        </span>
                    </div>

                    <h2 class="text-2xl sm:text-3xl font-bold text-gray-800">
                        Create Account
                    </h2>

                    <p class="mt-2 text-sm text-gray-500">
                        Enter your details to create a new account.
                    </p>

                </div>

                <!-- Register Form -->
                <form @submit.prevent="register" class="space-y-4">
                    <!-- Profile Photo -->
                    <div>
                        <label class="block mb-2 text-sm font-semibold text-gray-700">
                            Profile Photo *
                        </label>

                        <div class="flex items-center gap-4 rounded-lg border border-gray-200 bg-gray-50 p-4">

                            <div
                                class="h-20 w-20 shrink-0 overflow-hidden rounded-full border-2 border-[#82103c] bg-white flex items-center justify-center">

                                <img v-if="profileImagePreview" :src="profileImagePreview" alt="Profile Preview"
                                    class="h-full w-full object-cover" />

                                <i v-else class="fas fa-user text-4xl text-gray-300"></i>

                            </div>

                            <div class="min-w-0 flex-1">

                                <input ref="fileInput" type="file" accept="image/jpeg,image/png,image/gif" required
                                    :disabled="loading" @change="handleImageSelect"
                                    class="block w-full text-xs text-gray-600 file:mr-2 file:rounded-lg file:border-0 file:bg-[#82103c] file:px-3 file:py-2.5 file:text-xs file:font-semibold file:text-white hover:file:bg-[#6b0b30]" />

                                <p class="mt-2 text-xs text-gray-500">
                                    JPG, PNG or GIF. Maximum 5 MB.
                                </p>

                                <button v-if="profileImage" type="button" @click="removeProfileImage"
                                    :disabled="loading" class="mt-2 text-xs font-semibold text-red-600 hover:underline">
                                    <i class="fas fa-trash-alt mr-1"></i>
                                    Remove Photo
                                </button>

                            </div>

                        </div>
                    </div>
                    <!-- First Name and Last Name -->
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">

                        <div>
                            <label class="block mb-1.5 text-sm font-semibold text-gray-700">
                                First Name *
                            </label>

                            <div class="relative">
                                <i class="fas fa-user absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400"></i>

                                <input v-model="first_name" type="text" placeholder="Enter first name"
                                    autocomplete="given-name" maxlength="140" required :disabled="loading"
                                    class="w-full rounded-lg border border-gray-300 py-3 pl-10 pr-3 text-sm outline-none transition focus:border-[#82103c] focus:ring-2 focus:ring-pink-100" />
                            </div>
                        </div>

                        <div>
                            <label class="block mb-1.5 text-sm font-semibold text-gray-700">
                                Last Name
                            </label>

                            <div class="relative">
                                <i class="fas fa-user absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400"></i>

                                <input v-model="last_name" type="text" placeholder="Enter last name"
                                    autocomplete="family-name" maxlength="140" :disabled="loading"
                                    class="w-full rounded-lg border border-gray-300 py-3 pl-10 pr-3 text-sm outline-none transition focus:border-[#82103c] focus:ring-2 focus:ring-pink-100" />
                            </div>
                        </div>

                    </div>

                    <!-- Email -->
                    <div>
                        <label class="block mb-1.5 text-sm font-semibold text-gray-700">
                            Email Address *
                        </label>

                        <div class="relative">
                            <i class="fas fa-envelope absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400"></i>

                            <input v-model="email" type="email" placeholder="Enter your email address"
                                autocomplete="email" maxlength="254" required :disabled="loading"
                                class="w-full rounded-lg border border-gray-300 py-3 pl-10 pr-3 text-sm outline-none transition focus:border-[#82103c] focus:ring-2 focus:ring-pink-100" />
                        </div>
                    </div>

                    <!-- Password and Confirm Password -->
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">

                        <div>
                            <label class="block mb-1.5 text-sm font-semibold text-gray-700">
                                Password *
                            </label>

                            <div class="relative">
                                <i class="fas fa-lock absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400"></i>

                                <input v-model="password" :type="showPassword ? 'text' : 'password'"
                                    placeholder="Minimum 8 characters" autocomplete="new-password" minlength="8"
                                    required :disabled="loading"
                                    class="w-full rounded-lg border border-gray-300 py-3 pl-10 pr-10 text-sm outline-none transition focus:border-[#82103c] focus:ring-2 focus:ring-pink-100" />

                                <button type="button" @click="showPassword = !showPassword"
                                    :aria-label="showPassword ? 'Hide password' : 'Show password'"
                                    class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-[#82103c]">
                                    <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                                </button>
                            </div>
                        </div>

                        <div>
                            <label class="block mb-1.5 text-sm font-semibold text-gray-700">
                                Confirm Password *
                            </label>

                            <div class="relative">
                                <i class="fas fa-lock absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400"></i>

                                <input v-model="confirm_password" :type="showConfirmPassword ? 'text' : 'password'"
                                    placeholder="Confirm password" autocomplete="new-password" minlength="8" required
                                    :disabled="loading"
                                    class="w-full rounded-lg border border-gray-300 py-3 pl-10 pr-10 text-sm outline-none transition focus:border-[#82103c] focus:ring-2 focus:ring-pink-100" />

                                <button type="button" @click="showConfirmPassword = !showConfirmPassword"
                                    :aria-label="showConfirmPassword ? 'Hide password' : 'Show password'"
                                    class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-[#82103c]">
                                    <i :class="showConfirmPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                                </button>
                            </div>
                        </div>

                    </div>

                    <!-- Error Message -->
                    <div v-if="error" role="alert"
                        class="rounded-lg bg-red-50 border border-red-200 px-3 py-3 text-sm text-red-600 break-words">
                        <i class="fas fa-exclamation-circle mr-2"></i>
                        {{ error }}
                    </div>

                    <!-- Success Message -->
                    <div v-if="success" role="status"
                        class="rounded-lg bg-green-50 border border-green-200 px-3 py-3 text-sm text-green-700">
                        <i class="fas fa-check-circle mr-2"></i>
                        {{ success }}
                    </div>

                    <!-- Register Button -->
                    <button type="submit" :disabled="loading"
                        class="w-full flex items-center justify-center rounded-lg bg-[#82103c] py-3.5 font-semibold text-white transition duration-200 hover:bg-[#6b0b30] active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-60">
                        <i v-if="loading" class="fas fa-spinner fa-spin mr-2"></i>

                        <i v-else class="fas fa-user-plus mr-2"></i>

                        {{ loading ? 'Creating Account...' : 'Create Account' }}
                    </button>

                </form>

                <!-- Login Link -->
                <p class="mt-5 text-center text-sm text-gray-500">
                    Already have an account?

                    <RouterLink to="/login" class="font-semibold text-[#82103c] hover:underline ml-1">
                        Login
                    </RouterLink>
                </p>

                <!-- Back To Home -->
                <div class="mt-4 text-center">
                    <RouterLink to="/" class="text-sm text-[#82103c] hover:underline">
                        <i class="fas fa-arrow-left mr-1"></i>
                        Back to Home
                    </RouterLink>
                </div>

            </div>
        </div>
    </div>
</template>
