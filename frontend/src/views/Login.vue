<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')

// LOGIN USER

const login = async () => {
    error.value = ''

    if (!username.value.trim() || !password.value) {
        error.value = 'Please enter your username or email and password'
        return
    }

    loading.value = true

    try {
        const csrfToken =
            document.querySelector('meta[name="csrf-token"]')?.content ||
            window.frappe?.csrf_token ||
            ''

        const response = await fetch('/api/method/login', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                ...(csrfToken
                    ? { 'X-Frappe-CSRF-Token': csrfToken }
                    : {})
            },
            body: JSON.stringify({
                usr: username.value.trim(),
                pwd: password.value
            })
        })

        const data = await response.json()

        const loginMessage =
            typeof data.message === 'string'
                ? data.message
                : data.message?.message

        // CHECK LOGIN RESPONSE

        const loginSuccess = [
            'Logged In',
            'No App'
        ].includes(loginMessage)

        if (!response.ok || !loginSuccess) {
            throw new Error(
                data.exception
                    ? 'Invalid username/email or password'
                    : loginMessage || 'Login failed. Please try again.'
            )
        }

        // UPDATE NAVBAR

        window.dispatchEvent(
            new Event('buynew-auth-changed')
        )

        // CLEAR PASSWORD

        password.value = ''

        window.location.assign('/home')

    } catch (err) {
        console.error('Login Error:', err)

        error.value =
            err.message || 'Login failed. Please try again.'

    } finally {
        loading.value = false
    }
}
</script>

<template>
    <div class="h-[calc(100vh-72px)] min-h-[480px] flex items-center justify-center bg-gray-100 p-3">

        <div
            class="w-full max-w-5xl h-full max-h-[550px] overflow-hidden rounded-2xl bg-white shadow-xl grid md:grid-cols-2">

            <!-- Left Side -->

            <div class="hidden md:flex flex-col justify-center items-center bg-[#82103c] p-8 text-white">

                <i class="fas fa-shopping-bag text-6xl mb-5"></i>

                <h1 class="text-3xl font-bold mb-4 text-center">
                    Welcome to BuyNew
                </h1>

                <p class="text-center text-pink-100 leading-relaxed text-sm">
                    Login to your account and enjoy shopping with BuyNew.
                    Discover amazing products at great prices.
                </p>

                <div class="mt-8 text-center">
                    <i class="fas fa-user-circle text-4xl mb-2"></i>

                    <p class="text-sm text-pink-100">
                        Your shopping journey starts here.
                    </p>
                </div>

            </div>

            <!-- Right Side -->

            <div class="p-6 sm:p-10 flex flex-col justify-center">

                <div class="mb-7">

                    <h2 class="text-3xl font-bold text-gray-800">
                        Login
                    </h2>

                    <p class="mt-2 text-gray-500 text-sm">
                        Enter your account details to continue.
                    </p>

                </div>

                <form @submit.prevent="login" class="space-y-5">

                    <!-- Email or Username -->

                    <div>

                        <label class="block mb-2 text-sm font-semibold text-gray-700">
                            Email Address or Username
                        </label>

                        <div class="relative">

                            <i class="fas fa-user absolute left-4 top-1/2 -translate-y-1/2 text-gray-400"></i>

                            <input v-model="username" type="text" placeholder="Enter your email or username"
                                autocomplete="username" required
                                class="w-full rounded-lg border border-gray-300 py-3 pl-11 pr-4 outline-none focus:border-[#82103c] focus:ring-2 focus:ring-pink-100" />

                        </div>

                    </div>

                    <!-- Password -->

                    <div>

                        <label class="block mb-2 text-sm font-semibold text-gray-700">
                            Password
                        </label>

                        <div class="relative">

                            <i class="fas fa-lock absolute left-4 top-1/2 -translate-y-1/2 text-gray-400"></i>

                            <input v-model="password" :type="showPassword ? 'text' : 'password'"
                                placeholder="Enter your password" autocomplete="current-password" required
                                class="w-full rounded-lg border border-gray-300 py-3 pl-11 pr-12 outline-none focus:border-[#82103c] focus:ring-2 focus:ring-pink-100" />

                            <button type="button" @click="showPassword = !showPassword"
                                class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-[#82103c]">
                                <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                            </button>

                        </div>

                    </div>

                    <!-- Error -->

                    <div v-if="error" class="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-600">
                        <i class="fas fa-exclamation-circle mr-2"></i>
                        {{ error }}
                    </div>

                    <!-- Forgot Password -->

                    <div class="flex justify-end">

                        <a href="/update-password" class="text-sm font-medium text-[#82103c] hover:underline">
                            Forgot Password?
                        </a>

                    </div>

                    <!-- Login Button -->

                    <button type="submit" :disabled="loading"
                        class="w-full rounded-lg bg-[#82103c] py-3 font-semibold text-white transition hover:bg-[#6b0b30] disabled:cursor-not-allowed disabled:opacity-60">

                        <i v-if="loading" class="fas fa-spinner fa-spin mr-2"></i>

                        {{ loading ? 'Logging in...' : 'Login' }}

                    </button>

                </form>

                <!-- Register Link -->

                <p class="mt-7 text-center text-sm text-gray-500">

                    Don't have an account?

                    <RouterLink to="/register" class="font-semibold text-[#82103c] hover:underline ml-1">
                        Register
                    </RouterLink>

                </p>

                <!-- Back To Home -->

                <div class="mt-5 text-center">

                    <RouterLink to="/" class="text-sm text-[#82103c] hover:underline">
                        <i class="fas fa-arrow-left mr-1"></i>
                        Back to Home
                    </RouterLink>

                </div>

            </div>

        </div>

    </div>
</template>
