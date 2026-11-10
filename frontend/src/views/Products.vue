<template>
    <div class="min-h-screen bg-gray-50">

        <div class="mx-auto max-w-7xl px-4 py-6">

            <!-- Heading -->
            <div class="mb-6">
                <h1 class="text-2xl font-bold text-gray-800">
                    Our Products
                </h1>
                <p class="mt-1 text-sm text-gray-500">
                    Explore our latest products
                </p>
            </div>

            <!-- Loading -->
            <div v-if="loading" class="py-12 text-center text-gray-500">
                Loading products...
            </div>

            <!-- Error -->
            <div v-else-if="error" class="py-12 text-center text-red-500">
                {{ error }}
            </div>

            <!-- No Products -->
            <div v-else-if="products.length === 0" class="py-12 text-center text-gray-500">
                No products available.
            </div>

            <!-- Product Grid -->
            <div v-else class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">

                <div v-for="product in products" :key="product.name"
                    class="flex min-w-0 flex-col overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-lg">

                    <!-- Product Image -->
                    <div class="flex h-36 items-center justify-center bg-gray-50 sm:h-48">

                        <img v-if="product.product_image" :src="product.product_image" :alt="product.products_name"
                            loading="lazy" class="h-full w-full object-contain p-3" />

                        <i v-else class="fas fa-image text-4xl text-gray-300"></i>

                    </div>

                    <!-- Product Details -->
                    <div class="flex flex-1 flex-col p-3">

                        <h2 class="truncate text-sm font-semibold text-gray-800 sm:text-base">
                            {{ product.products_name }}
                        </h2>

                        <p class="mt-1 text-xs text-gray-500">
                            {{ product.brand || 'No Brand' }}
                        </p>

                        <!-- Price -->
                        <div class="mt-3 flex flex-wrap items-center gap-2">

                            <span class="text-lg font-bold text-gray-900">
                                ₹{{ product.selling_price }}
                            </span>

                            <span v-if="product.mrp" class="text-xs text-gray-400 line-through">
                                ₹{{ product.mrp }}
                            </span>

                        </div>

                        <!-- Discount -->
                        <p v-if="product.discount_percentage" class="mt-1 text-xs font-semibold text-green-600">
                            {{ product.discount_percentage }}% OFF
                        </p>

                        <!-- Stock -->
                        <p class="mt-2 text-xs text-gray-500">
                            {{ product.stock_status || 'Stock information unavailable' }}
                        </p>

                        <!-- Add to Cart -->
                        <button type="button" @click="addToCart(product)"
                            class="mt-4 w-full rounded-lg bg-[#82103c] px-3 py-2.5 text-sm font-semibold text-white transition hover:bg-[#6b0b30] active:scale-95">
                            <i class="fas fa-shopping-cart mr-2"></i>
                            Add to Cart
                        </button>

                    </div>
                </div>

            </div>

        </div>

        <!-- Toast Notification -->
        <Transition enter-active-class="transition duration-300 ease-out" enter-from-class="translate-y-4 opacity-0"
            enter-to-class="translate-y-0 opacity-100" leave-active-class="transition duration-200 ease-in"
            leave-from-class="translate-y-0 opacity-100" leave-to-class="translate-y-4 opacity-0">
            <div v-if="showToast"
                class="fixed bottom-5 right-5 z-[100] flex max-w-[calc(100vw-40px)] items-center gap-3 rounded-xl px-5 py-4 text-white shadow-xl"
                :class="toastType === 'success' ? 'bg-gray-900' : 'bg-red-600'">

                <i :class="toastType === 'success'
                    ? 'fas fa-check-circle text-green-400'
                    : 'fas fa-exclamation-circle text-white'" class="text-xl"></i>

                <span class="text-sm font-medium">
                    {{ toastMessage }}
                </span>

                <button type="button" @click="showToast = false" class="ml-2 text-gray-300 hover:text-white">
                    <i class="fas fa-times"></i>
                </button>

            </div>
        </Transition>

    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Product Data
const products = ref([])

// Loading and Error
const loading = ref(true)
const error = ref('')

// Toast Notification
const showToast = ref(false)
const toastMessage = ref('')
const toastType = ref('success')

let toastTimer = null

// Show Notification
const notify = (message, type = 'success') => {
    toastMessage.value = message
    toastType.value = type
    showToast.value = true

    clearTimeout(toastTimer)

    toastTimer = setTimeout(() => {
        showToast.value = false
    }, 3000)
}

// Fetch Products from Frappe API
const getProducts = async () => {
    loading.value = true
    error.value = ''

    try {
        const response = await fetch(
            '/api/method/buy_new.api.get_products',
            {
                method: 'GET',
                credentials: 'same-origin',
                headers: {
                    Accept: 'application/json'
                }
            }
        )

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`)
        }

        const result = await response.json()

        products.value = result.message || []

        console.log('Products:', products.value)

    } catch (err) {
        console.error('Product Error:', err)
        error.value = 'Unable to load products.'
    } finally {
        loading.value = false
    }
}

// Add Product to Cart - Login Required
const addToCart = async (product) => {
    try {
        // Check Frappe Login Session
        const response = await fetch(
            '/api/method/frappe.auth.get_logged_user',
            {
                method: 'GET',
                credentials: 'same-origin'
            }
        )

        const result = await response.json()
        const user = result.message

        // User Not Logged In
        if (
            !response.ok ||
            !user ||
            user === 'Guest'
        ) {
            notify('Please login first to add products!', 'error')

            setTimeout(() => {
                router.push('/login')
            }, 1000)

            return
        }

        // Get Existing Cart
        let cart = JSON.parse(
            localStorage.getItem('buynew_cart') || '[]'
        )

        // Check Existing Product
        const existingProduct = cart.find(
            item => item.name === product.name
        )

        if (existingProduct) {
            existingProduct.quantity += 1
        } else {
            cart.push({
                ...product,
                quantity: 1
            })
        }

        // Save Cart
        localStorage.setItem(
            'buynew_cart',
            JSON.stringify(cart)
        )

        // Success Notification
        notify(`${product.products_name} added to cart!`)

        console.log('Updated Cart:', cart)

    } catch (err) {
        console.error('Cart Error:', err)

        notify('Unable to verify login. Please try again!', 'error')
    }
}

// Load Products
onMounted(() => {
    getProducts()
})

// Clear Timer
onUnmounted(() => {
    clearTimeout(toastTimer)
})
</script>