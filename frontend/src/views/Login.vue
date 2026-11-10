<script setup>
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'

const router = useRouter()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')

const login = async () => {
    error.value = ''

    if (!email.value.trim() || !password.value) {
        error.value = 'Please enter your email and password'
        return
    }

    loading.value = true

    try {
        const csrfToken =
            document.querySelector('meta[name="csrf-token"]')?.content || ''

        const response = await fetch('/api/method/login', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-Frappe-CSRF-Token': csrfToken
            },
            body: JSON.stringify({
                usr: email.value.trim().toLowerCase(),
                pwd: password.value
            })
        })

        const data = await response.json()

        if (!response.ok || data.message !== 'Logged In') {
            throw new Error('Invalid email or password')
        }

        await router.push('/home')

    } catch (err) {
        error.value = err.message || 'Login failed. Please try again.'
    } finally {
        loading.value = false
    }
}
</script>

<template>
    <div class="min-h-screen flex items-center justify-center bg-gray-100">

        <div class="w-full max-w-5xl overflow-hidden rounded-2xl bg-white shadow-xl grid md:grid-cols-2 h-[555px]">

            <!-- Left Side -->
            <div class="hidden md:flex flex-col justify-center items-center bg-[#82103c] p-12 text-white">
                <i class="fas fa-shopping-bag text-7xl mb-6"></i>

                <h1 class="text-4xl font-bold mb-4">
                    Welcome to BuyNew
                </h1>

                <p class="text-center text-blue-100 leading-relaxed">
                    Login to your account and enjoy shopping with BuyNew.
                </p>
            </div>

            <!-- Right Side -->
            <div class="p-8 sm:p-10">

                <div class="mb-8">
                    <h2 class="text-3xl font-bold text-gray-800">
                        Login
                    </h2>

                    <p class="mt-2 text-gray-500">
                        Enter your account details to continue.
                    </p>
                </div>

                <form @submit.prevent="login" class="space-y-6">

                    <!-- Email -->
                    <div>
                        <label class="block mb-2 text-sm font-semibold text-gray-700">
                            Email Address
                        </label>

                        <div class="relative">
                            <i class="fas fa-envelope absolute left-4 top-1/2 -translate-y-1/2 text-gray-400"></i>

                            <input v-model="email" type="email" placeholder="Enter your email" autocomplete="username"
                                class="w-full rounded-lg border border-gray-300 py-3 pl-11 pr-4 outline-none focus:border-[#82103c] focus:ring-2 focus:ring-blue-100" />
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
                                placeholder="Enter your password" autocomplete="current-password"
                                class="w-full rounded-lg border border-gray-300 py-3 pl-11 pr-12 outline-none focus:border-[#82103c] focus:ring-2 focus:ring-blue-100" />

                            <button type="button" @click="showPassword = !showPassword"
                                class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-blue-600">
                                <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                            </button>
                        </div>
                    </div>

                    <!-- Error -->
                    <div v-if="error" class="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-600">
                        {{ error }}
                    </div>

                    <!-- Forgot Password -->
                    <div class="flex justify-end">
                        <a href="/update-password" class="text-sm font-medium text-blue-600 hover:underline">
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

                <p class="mt-8 text-center text-sm text-gray-500">
                    Don't have an account?
                    <span class="font-semibold text-gray-700">
                        Contact administrator
                    </span>
                </p>

                <div class="mt-8 text-center">
                    <RouterLink to="/" class="text-sm text-[#82103c] hover:underline">
                        <i class="fas fa-arrow-left mr-1"></i>
                        Back to Home
                    </RouterLink>
                </div>

            </div>
        </div>
    </div>
</template>
