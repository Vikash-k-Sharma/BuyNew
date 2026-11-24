<template>
    <nav class="sticky top-0 z-50 w-full bg-[#780D32] shadow-md">
        <div class="mx-auto flex min-h-[64px] max-w-[1450px] items-center gap-3 px-4 py-2 sm:px-6 lg:gap-5">

            <!-- Logo -->
            <RouterLink to="/home" class="flex shrink-0 items-center">
                <img src="../assets/byn.png" alt="BuyNew" class="h-9 w-auto object-contain sm:h-11" />
            </RouterLink>

            <!-- Divider -->
            <div class="hidden h-9 w-px bg-white/30 sm:block"></div>

            <!-- Delivery Location -->
            <div class="hidden shrink-0 items-center gap-2 text-white sm:flex">
                <i class="fas fa-map-marker-alt text-xl"></i>
                <div class="leading-tight">
                    <p class="text-[11px] text-white/80">Deliver to</p>
                    <p class="text-sm font-semibold">
                        Bihar 801103
                        <i class="fas fa-chevron-down ml-1 text-[10px]"></i>
                    </p>
                </div>
            </div>

            <!-- Desktop Search -->
            <form @submit.prevent="searchProducts" class="hidden min-w-0 flex-1 md:flex">
                <div class="relative flex h-[42px] w-full">
                    <div class="flex w-full overflow-hidden rounded-xl bg-white shadow-sm">
                        <div class="flex items-center pl-4 text-gray-500">
                            <i class="fas fa-search"></i>
                        </div>

                        <input v-model="searchQuery" type="search" placeholder="Search for products, brands and more..."
                            autocomplete="off" @focus="showSuggestions = true" @input="showSuggestions = true"
                            @blur="hideSuggestions"
                            class="w-full min-w-0 border-none bg-white px-3 text-sm text-gray-800 outline-none focus:ring-0" />

                        <button type="submit"
                            class="shrink-0 bg-[#FFC900] px-6 text-sm font-bold text-black transition hover:bg-yellow-400">
                            Search
                        </button>
                    </div>

                    <!-- Search Suggestions -->
                    <div v-if="showSuggestions && searchQuery.trim()"
                        class="absolute left-0 right-0 top-full z-[100] mt-1 max-h-[420px] overflow-y-auto rounded-xl border border-gray-200 bg-white shadow-xl">
                        <button v-for="product in searchSuggestions" :key="product.name" type="button"
                            @click="selectSuggestion(product)"
                            class="flex w-full items-center gap-4 border-b border-gray-100 px-4 py-3 text-left hover:bg-gray-50">
                            <div class="flex h-14 w-14 shrink-0 items-center justify-center rounded-lg bg-gray-50">
                                <img v-if="product.product_image" :src="product.product_image"
                                    :alt="product.products_name" class="h-full w-full object-contain p-1" />
                                <i v-else class="fas fa-image text-gray-300"></i>
                            </div>

                            <div class="min-w-0 flex-1">
                                <p class="truncate text-sm font-semibold text-gray-800">
                                    {{ product.products_name }}
                                </p>
                                <p class="mt-1 text-xs text-gray-500">
                                    {{ product.brand || product.category || 'Product' }}
                                </p>
                                <p class="mt-1 text-sm font-bold text-[#780D32]">
                                    ₹{{ Number(product.selling_price || 0).toLocaleString('en-IN') }}
                                </p>
                            </div>
                        </button>

                        <div v-if="searchSuggestions.length === 0" class="px-4 py-5 text-center text-sm text-gray-500">
                            No matching products found.
                        </div>

                        <button type="submit"
                            class="w-full bg-gray-50 px-4 py-3 text-left text-sm font-semibold text-[#780D32] hover:bg-gray-100">
                            <i class="fas fa-search mr-2"></i>
                            Search for "{{ searchQuery }}"
                        </button>
                    </div>
                </div>
            </form>

            <!-- Right Side -->
            <div class="ml-auto flex shrink-0 items-center gap-3 text-white sm:gap-5">

                <!-- Wishlist -->
                <RouterLink to="/wishlist" aria-label="Wishlist"
                    class="flex items-center text-white transition hover:text-yellow-300">
                    <span class="relative">
                        <i class="far fa-heart text-xl sm:text-2xl"></i>
                        <span v-if="wishlistCount > 0"
                            class="absolute -right-2 -top-2 flex h-[17px] min-w-[17px] items-center justify-center rounded-full bg-[#FFC900] px-1 text-[10px] font-bold text-black">
                            {{ wishlistCount }}
                        </span>
                    </span>
                </RouterLink>

                <!-- Cart -->
                <RouterLink to="/cart" class="flex items-center gap-2 text-white transition hover:text-yellow-300">
                    <span class="relative">
                        <i class="fas fa-shopping-cart text-xl sm:text-2xl"></i>
                        <span v-if="cartCount > 0"
                            class="absolute -right-2 -top-3 flex h-[17px] min-w-[17px] items-center justify-center rounded-full bg-[#FFC900] px-1 text-[10px] font-bold text-black">
                            {{ cartCount }}
                        </span>
                    </span>
                </RouterLink>

                <!-- Divider -->
                <div class="h-9 w-px bg-white/30"></div>

                <!-- Login / Register -->
                <template v-if="!isLoggedIn">
                    <RouterLink to="/login" class="flex items-center gap-2 text-white transition hover:text-yellow-300">
                        <i class="far fa-user text-xl sm:text-2xl"></i>
                        <span class="hidden text-xs font-semibold leading-tight sm:block">
                            Login /<br /> Register
                        </span>
                    </RouterLink>
                </template>

                <!-- Profile Dropdown -->
                <template v-else>
                    <div class="relative" ref="profileMenuRef">
                        <button type="button" @click="toggleProfileDropdown"
                            class="flex items-center gap-2 text-white transition hover:text-yellow-300">
                            <!-- User Profile Image -->
                            <img v-if="userProfile?.user_image" :src="userProfile.user_image" alt="Profile"
                                class="h-9 w-9 rounded-full border-2 border-white object-cover sm:h-10 sm:w-10" />

                            <!-- Default Icon -->
                            <i v-else class="fas fa-user-circle text-2xl sm:text-3xl"></i>

                            <i class="fas fa-chevron-down text-xs"></i>
                        </button>

                        <!-- Profile Menu -->
                        <div v-if="profileDropdown"
                            class="absolute right-0 top-full z-[200] mt-4 w-[220px] overflow-hidden rounded-sm border border-gray-200 bg-white shadow-xl">
                            <!-- Username -->
                            <div class="bg-[#780D32] px-4 py-4 text-white">
                                <div class="flex items-center gap-3">
                                    <img v-if="userProfile?.user_image" :src="userProfile.user_image" alt="Profile"
                                        class="h-10 w-10 rounded-full border border-white object-cover" />
                                    <i v-else class="fas fa-user-circle text-3xl"></i>

                                    <p class="truncate text-lg font-medium">
                                        {{ fullName }}
                                    </p>
                                </div>
                            </div>

                            <!-- Profile -->
                            <RouterLink to="/profilepage" @click="profileDropdown = false"
                                class="flex items-center gap-3 border-b border-gray-100 px-5 py-4 text-sm text-gray-700 transition hover:bg-gray-100">
                                <i class="fas fa-user text-gray-500"></i>
                                Profile
                            </RouterLink>

                            <!-- Logout -->
                            <button type="button" @click="openLogoutConfirm"
                                class="flex w-full items-center gap-3 px-5 py-4 text-left text-sm text-gray-700 transition hover:bg-gray-100">
                                <i class="fas fa-power-off text-gray-500"></i>
                                Logout
                            </button>
                        </div>
                    </div>
                </template>
            </div>
        </div>

        <!-- Mobile Search -->
        <form @submit.prevent="searchProducts" class="relative z-[60] px-4 pb-3 md:hidden">
            <div class="relative">
                <div class="flex h-10 overflow-hidden rounded-lg bg-white">
                    <input v-model="searchQuery" type="search" placeholder="Search for products, brands and more..."
                        autocomplete="off" @focus="showSuggestions = true" @input="showSuggestions = true"
                        @blur="hideSuggestions"
                        class="w-full min-w-0 border-none px-3 text-sm text-gray-800 outline-none focus:ring-0" />

                    <button type="submit" class="shrink-0 bg-[#FFC900] px-5 text-sm font-bold text-black">
                        Search
                    </button>
                </div>

                <!-- Mobile Suggestions -->
                <div v-if="showSuggestions && searchQuery.trim()"
                    class="absolute left-0 right-0 top-full z-[100] mt-1 max-h-[60vh] overflow-y-auto overscroll-contain rounded-lg border border-gray-200 bg-white shadow-xl">
                    <button v-for="product in searchSuggestions" :key="product.name" type="button"
                        @click="selectSuggestion(product)"
                        class="flex w-full items-center gap-3 border-b border-gray-100 p-3 text-left">
                        <img v-if="product.product_image" :src="product.product_image"
                            :alt="product.products_name" class="h-12 w-12 shrink-0 object-contain" />

                        <div class="min-w-0">
                            <p class="truncate text-sm font-semibold text-gray-800">
                                {{ product.products_name }}
                            </p>
                            <p class="text-sm font-bold text-[#780D32]">
                                ₹{{ Number(product.selling_price || 0).toLocaleString('en-IN') }}
                            </p>
                        </div>
                    </button>

                    <p v-if="searchSuggestions.length === 0" class="p-4 text-center text-sm text-gray-500">
                        No matching products found.
                    </p>
                </div>
            </div>
        </form>
    </nav>

    <!-- Logout Confirmation Modal -->
    <div v-if="showLogoutConfirm" @click.self="closeLogoutConfirm"
        class="fixed inset-0 z-[300] flex items-center justify-center bg-black/50 px-4">
        <div class="w-full max-w-[380px] rounded-xl bg-white p-6 shadow-2xl">

            <div class="mb-4 flex justify-center">
                <div class="flex h-14 w-14 items-center justify-center rounded-full bg-red-100">
                    <i class="fas fa-sign-out-alt text-2xl text-red-600"></i>
                </div>
            </div>

            <h2 class="text-center text-xl font-bold text-gray-800">
                Logout Confirmation
            </h2>

            <p class="mt-2 text-center text-sm text-gray-500">
                Are you sure you want to logout from your account?
            </p>

            <p v-if="logoutError" role="alert" class="mt-3 text-center text-sm text-red-600">
                {{ logoutError }}
            </p>

            <div class="mt-6 flex gap-3">
                <button type="button" @click="closeLogoutConfirm" :disabled="isLoggingOut"
                    class="flex-1 rounded-lg border border-gray-300 px-4 py-3 text-sm font-semibold text-gray-700 transition hover:bg-gray-100 disabled:opacity-50">
                    No
                </button>

                <button type="button" @click="logout" :disabled="isLoggingOut"
                    class="flex-1 rounded-lg bg-[#780D32] px-4 py-3 text-sm font-semibold text-white transition hover:bg-[#600A28] disabled:cursor-not-allowed disabled:opacity-50">
                    {{ isLoggingOut ? 'Logging out...' : 'Yes, Logout' }}
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'

const router = useRouter()
const route = useRoute()

const isLoggedIn = ref(false)
const fullName = ref('')
const userProfile = ref(null)

const searchQuery = ref('')
const allProducts = ref([])
const showSuggestions = ref(false)

const profileDropdown = ref(false)
const profileMenuRef = ref(null)

const cartCount = ref(0)
const wishlistCount = ref(0)

const showLogoutConfirm = ref(false)
const isLoggingOut = ref(false)
const logoutError = ref('')

// Refresh CSRF Token
const refreshCsrfToken = async () => {
    const response = await fetch('/home', {
        method: 'GET',
        credentials: 'same-origin',
        cache: 'no-store',
        headers: { Accept: 'text/html' }
    })

    if (!response.ok) {
        throw new Error('Unable to refresh the security token. Please try again.')
    }

    const html = await response.text()
    const token = html.match(
        /(?:window\.)?frappe\.csrf_token\s*=\s*["']([^"']+)["']/
    )?.[1]

    if (!token) {
        throw new Error('Security token is missing. Please refresh the page and try again.')
    }

    window.frappe = window.frappe || {}
    window.frappe.csrf_token = token

    return token
}

// Check Login Session
const checkLogin = async () => {
    try {
        const response = await fetch(
            '/api/method/buy_new.api.get_session_user',
            {
                credentials: 'same-origin',
                headers: { Accept: 'application/json' }
            }
        )

        const data = await response.json()

        isLoggedIn.value =
            response.ok &&
            data.message &&
            data.message !== 'Guest'

        fullName.value = isLoggedIn.value ? data.message : ''

        if (!isLoggedIn.value) {
            cartCount.value = 0
            wishlistCount.value = 0
            userProfile.value = null
        }

    } catch (error) {
        console.error('Login Check Error:', error)
        isLoggedIn.value = false
        fullName.value = ''
        userProfile.value = null
        cartCount.value = 0
    }
}

// Get Current User Profile
const getUserProfile = async () => {
    if (!isLoggedIn.value) {
        userProfile.value = null
        return
    }

    try {
        const response = await fetch(
            '/api/method/buy_new.api.get_current_user_profile',
            {
                method: 'GET',
                credentials: 'same-origin',
                headers: { Accept: 'application/json' }
            }
        )

        const result = await response.json()

        if (!response.ok || result.exc || !result.message) {
            throw new Error('Unable to fetch profile')
        }

        userProfile.value = result.message
        fullName.value = result.message.full_name || result.message.name || fullName.value

    } catch (error) {
        console.error('Profile Error:', error)
        userProfile.value = null
    }
}

// Fetch Products
const getSearchProducts = async () => {
    try {
        const response = await fetch(
            '/api/method/buy_new.api.get_products',
            {
                method: 'GET',
                credentials: 'same-origin',
                headers: { Accept: 'application/json' }
            }
        )

        const result = await response.json()

        if (!response.ok || result.exc) {
            throw new Error('Unable to fetch search products')
        }

        allProducts.value = result.message || []

    } catch (error) {
        console.error('Search Products Error:', error)
    }
}

// Filter Suggestions
const searchSuggestions = computed(() => {
    const query = searchQuery.value.trim().toLowerCase()

    if (!query) return []

    return allProducts.value
        .filter(product => {
            const searchableText = [
                product.products_name,
                product.products_code,
                product.brand,
                product.category,
                product.short_description
            ].map(value => String(value || '').toLowerCase())

            return searchableText.some(value =>
                value.includes(query)
            )
        })
        .sort((a, b) => {
            const nameA = String(a.products_name || '').toLowerCase()
            const nameB = String(b.products_name || '').toLowerCase()

            const startsA = nameA.startsWith(query) ? 0 : 1
            const startsB = nameB.startsWith(query) ? 0 : 1

            return startsA - startsB
        })
        .slice(0, 7)
})

// Search Products
const searchProducts = () => {
    const query = searchQuery.value.trim()

    showSuggestions.value = false

    router.push({
        path: '/products',
        query: query ? { search: query } : {}
    })
}

// Select Suggestion
const selectSuggestion = (product) => {
    clearTimeout(blurTimer)
    searchQuery.value = product.products_name || ''
    searchProducts()
}

// Hide Suggestions
let blurTimer = null

const hideSuggestions = () => {
    clearTimeout(blurTimer)

    blurTimer = setTimeout(() => {
        showSuggestions.value = false
    }, 180)
}

// Get Cart Count
const getCartCount = async () => {
    if (!isLoggedIn.value) {
        cartCount.value = 0
        return
    }

    try {
        const response = await fetch(
            '/api/method/buy_new.api.get_cart',
            {
                method: 'GET',
                credentials: 'same-origin',
                headers: {
                    Accept: 'application/json'
                }
            }
        )

        const data = await response.json()

        if (!response.ok || data.exc) {
            throw new Error('Unable to fetch cart')
        }

        const cartItems = data.message || []

        cartCount.value = cartItems.reduce(
            (total, item) => total + Number(item.quantity || 0),
            0
        )

    } catch (error) {
        console.error('Cart Count Error:', error)
    }
}

// Profile Dropdown
const toggleProfileDropdown = () => {
    profileDropdown.value = !profileDropdown.value
}

// Close Profile Dropdown
const handleOutsideClick = (event) => {
    if (
        profileMenuRef.value &&
        !profileMenuRef.value.contains(event.target)
    ) {
        profileDropdown.value = false
    }
}

// Open Logout Confirmation
const openLogoutConfirm = () => {
    profileDropdown.value = false
    logoutError.value = ''
    showLogoutConfirm.value = true
}

// Close Logout Confirmation
const closeLogoutConfirm = () => {
    if (isLoggingOut.value) return

    showLogoutConfirm.value = false
}

// Logout
const logout = async () => {
    if (isLoggingOut.value) return

    isLoggingOut.value = true
    logoutError.value = ''

    try {
        const csrfToken = await refreshCsrfToken()

        const response = await fetch('/api/method/logout', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                Accept: 'application/json',
                'X-Frappe-CSRF-Token': csrfToken
            }
        })

        const result = await response.json().catch(() => ({}))

        if (!response.ok || result.exc || result.exception) {
            const serverMessage =
                result.message?.message ||
                result.message ||
                result.exception ||
                'Logout failed. Please try again.'

            throw new Error(serverMessage)
        }

        isLoggedIn.value = false
        fullName.value = ''
        userProfile.value = null
        cartCount.value = 0
        profileDropdown.value = false
        showLogoutConfirm.value = false
        logoutError.value = ''

        window.dispatchEvent(
            new Event('buynew-auth-changed')
        )

        await router.push('/login')

    } catch (error) {
        console.error('Logout Error:', error)
        logoutError.value = error.message || 'Unable to logout. Please try again.'

    } finally {
        isLoggingOut.value = false
    }
}

// Sync Search With URL
watch(
    () => route.query.search,
    value => {
        searchQuery.value =
            typeof value === 'string' ? value : ''

        showSuggestions.value = false
    },
    { immediate: true }
)

// Update Cart When Route Changes
watch(
    () => route.fullPath,
    () => {
        getCartCount()
    }
)

// Update Navbar After Login
const handleAuthChange = async () => {
    await checkLogin()
    await getUserProfile()
    await getCartCount()
    await updateWishlistCount()
}

// Update Cart
const handleCartUpdate = () => {
    getCartCount()
}

const handleProfileUpdate = () => {
    getUserProfile()
}

const updateWishlistCount = async () => {
    if (!isLoggedIn.value) {
        wishlistCount.value = 0
        return
    }

    try {
        const response = await fetch(
            '/api/method/buy_new.api.get_wishlist',
            {
                method: 'GET',
                credentials: 'same-origin',
                headers: { Accept: 'application/json' }
            }
        )
        const result = await response.json()

        if (!response.ok || result.exc || result.exception) {
            throw new Error('Unable to fetch wishlist count')
        }

        wishlistCount.value = Array.isArray(result.message)
            ? result.message.length
            : 0
    } catch (error) {
        console.error('Wishlist Count Error:', error)
    }
}

onMounted(async () => {
    await checkLogin()
    await getUserProfile()

    getSearchProducts()
    getCartCount()
    updateWishlistCount()

    window.addEventListener(
        'buynew-auth-changed',
        handleAuthChange
    )

    window.addEventListener(
        'buynew-cart-updated',
        handleCartUpdate
    )

    window.addEventListener(
        'buynew-profile-updated',
        handleProfileUpdate
    )

    window.addEventListener(
        'buynew-wishlist-updated',
        updateWishlistCount
    )

    window.addEventListener(
        'storage',
        updateWishlistCount
    )

    document.addEventListener(
        'click',
        handleOutsideClick
    )
})

onUnmounted(() => {
    window.removeEventListener(
        'buynew-auth-changed',
        handleAuthChange
    )

    window.removeEventListener(
        'buynew-cart-updated',
        handleCartUpdate
    )

    window.removeEventListener(
        'buynew-profile-updated',
        handleProfileUpdate
    )

    window.removeEventListener(
        'buynew-wishlist-updated',
        updateWishlistCount
    )

    window.removeEventListener(
        'storage',
        updateWishlistCount
    )

    document.removeEventListener(
        'click',
        handleOutsideClick
    )

    clearTimeout(blurTimer)
})
</script>
