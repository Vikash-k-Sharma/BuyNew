<template>
    <div class="min-h-screen bg-gray-50">

        <!-- Loading -->
        <div v-if="loading" class="py-20 text-center text-gray-500">
            <i class="fas fa-spinner fa-spin mr-2"></i>
            Loading product...
        </div>

        <!-- Error -->
        <div v-else-if="error" class="py-20 text-center text-red-600">
            {{ error }}
            <button @click="getProduct" class="ml-2 underline font-semibold">
                Try Again
            </button>
        </div>

        <!-- Product Details -->
        <div v-else-if="product" class="mx-auto max-w-7xl px-3 py-5 sm:px-6">

            <!-- Breadcrumb -->
            <div class="mb-5 text-xs text-gray-500 sm:text-sm">
                <RouterLink to="/home" class="hover:text-[#82103c]">
                    Home
                </RouterLink>
                /
                <RouterLink to="/products" class="hover:text-[#82103c]">
                    Products
                </RouterLink>
                /
                <span class="text-gray-800">
                    {{ product.products_name }}
                </span>
            </div>

            <div class="grid gap-6 rounded-xl bg-white p-4 shadow-sm md:grid-cols-2 md:p-6">

                <!-- Product Image -->
                <div class="flex flex-col gap-3">

                    <div class="flex h-[300px] items-center justify-center rounded-lg bg-gray-50 sm:h-[450px]">
                        <img v-if="product.product_image" :src="product.product_image" :alt="product.products_name"
                            class="h-full w-full object-contain p-4" />

                        <i v-else class="fas fa-image text-6xl text-gray-300"></i>
                    </div>

                    <div v-if="isOutOfStock(product)" role="status"
                        class="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-5 py-3 font-semibold text-red-700">
                        <i class="fas fa-circle-exclamation"></i>
                        Out of Stock
                    </div>
                    <button v-else @click="addToCart" :disabled="adding"
                        class="w-full rounded-lg bg-[#82103c] px-5 py-3 font-semibold text-white transition hover:bg-[#6b0b30] disabled:opacity-50">
                        <i :class="adding ? 'fas fa-spinner fa-spin' : 'fas fa-shopping-cart'" class="mr-2"></i>

                        {{ adding ? 'Adding...' : 'Add to Cart' }}
                    </button>

                </div>

                <!-- Product Information -->
                <div class="flex flex-col">

                    <p class="text-sm text-gray-500">
                        {{ product.brand || 'No Brand' }}
                    </p>

                    <h1 class="mt-2 text-xl font-bold text-gray-900 sm:text-2xl">
                        {{ product.products_name }}
                    </h1>

                    <p class="mt-2 text-sm text-gray-500">
                        Product Code: {{ product.products_code || product.name }}
                    </p>

                    <!-- Rating -->
                    <div v-if="product.rating" class="mt-3">
                        <span class="rounded bg-green-600 px-2 py-1 text-sm font-semibold text-white">
                            {{ product.rating }} ★
                        </span>
                    </div>

                    <!-- Price -->
                    <div class="mt-6 flex flex-wrap items-center gap-3">

                        <span class="text-3xl font-bold text-gray-900">
                            ₹{{ formatPrice(product.selling_price) }}
                        </span>

                        <span v-if="product.mrp" class="text-base text-gray-400 line-through">
                            ₹{{ formatPrice(product.mrp) }}
                        </span>

                    </div>

                    <!-- Discount -->
                    <p v-if="product.discount_percentage" class="mt-2 font-semibold text-green-600">
                        {{ product.discount_percentage }}% OFF
                    </p>

                    <!-- Stock -->
                    <p class="mt-4 text-sm font-medium" :class="isOutOfStock(product)
                        ? 'text-red-600'
                        : 'text-green-600'">
                        <i :class="isOutOfStock(product) ? 'fas fa-circle-exclamation' : 'fas fa-circle-check'"
                            class="mr-1"></i>
                        {{ isOutOfStock(product) ? 'Out of Stock' : (product.stock_status || 'Stock information unavailable') }}
                    </p>

                    <p class="mt-1 text-sm text-gray-500">
                        Available Quantity: {{ product.stock_quantity ?? 0 }}
                    </p>

                    <hr class="my-6 border-gray-200" />

                    <!-- Description -->
                    <h2 class="mb-3 text-lg font-bold text-gray-800">
                        Product Description
                    </h2>

                    <div v-if="product.description" class="product-description text-sm leading-7 text-gray-700"
                        v-html="cleanDescription(product.description)"></div>

                    <p v-else class="text-sm text-gray-500">
                        No description available.
                    </p>

                    <!-- Short Description -->
                    <div v-if="product.short_description" class="mt-5 rounded-lg bg-gray-50 p-4">
                        <h3 class="mb-2 font-semibold text-gray-800">
                            Highlights
                        </h3>

                        <p class="whitespace-pre-line text-sm leading-6 text-gray-600">
                            {{ product.short_description }}
                        </p>
                    </div>

                    <!-- Category -->
                    <div v-if="product.category" class="mt-5 text-sm text-gray-600">
                        <strong>Category:</strong>
                        {{ product.category }}
                    </div>

                </div>

            </div>

            <!-- Back Button -->
            <div class="mt-5">
                <RouterLink to="/products"
                    class="inline-flex items-center gap-2 font-semibold text-[#82103c] hover:underline">
                    <i class="fas fa-arrow-left"></i>
                    Back to Products
                </RouterLink>
            </div>

        </div>

        <!-- Toast -->
        <Transition enter-active-class="transition duration-300" enter-from-class="translate-y-4 opacity-0"
            enter-to-class="translate-y-0 opacity-100" leave-active-class="transition duration-200"
            leave-from-class="opacity-100" leave-to-class="opacity-0">
            <div v-if="showToast"
                class="fixed bottom-5 right-5 z-50 rounded-xl px-5 py-4 text-sm font-medium text-white shadow-xl"
                :class="toastType === 'success' ? 'bg-gray-900' : 'bg-red-600'">
                {{ toastMessage }}
            </div>
        </Transition>

    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import DOMPurify from 'dompurify'

const route = useRoute()
const router = useRouter()

const product = ref(null)
const loading = ref(true)
const error = ref('')
const adding = ref(false)
const isOutOfStock = (item) =>
    Number(item?.stock_quantity) <= 0 ||
    String(item?.stock_status || '').toLowerCase().includes('out of stock')

const showToast = ref(false)
const toastMessage = ref('')
const toastType = ref('success')

let toastTimer = null

// FORMAT PRICE
const formatPrice = (price) => {
    return Number(price || 0).toLocaleString('en-IN')
}

// CLEAN DESCRIPTION
const cleanDescription = (description) => {
    return DOMPurify.sanitize(description || '', {
        USE_PROFILES: { html: true }
    })
}

// NOTIFICATION
const notify = (message, type = 'success') => {
    toastMessage.value = message
    toastType.value = type
    showToast.value = true

    clearTimeout(toastTimer)

    toastTimer = setTimeout(() => {
        showToast.value = false
    }, 3000)
}

// CSRF TOKEN
const getCsrfToken = () => {
    return (
        document.querySelector('meta[name="csrf-token"]')?.content ||
        window.frappe?.csrf_token ||
        ''
    )
}

// API RESPONSE
const readResponse = async (response) => {
    try {
        return await response.json()
    } catch {
        return {}
    }
}

// FETCH SINGLE PRODUCT
const getProduct = async () => {
    loading.value = true
    error.value = ''
    product.value = null

    try {
        const productId = route.params.id

        const response = await fetch(
            `/api/method/buy_new.api.get_product?product_name=${encodeURIComponent(productId)}`,
            {
                method: 'GET',
                credentials: 'same-origin',
                headers: {
                    Accept: 'application/json'
                }
            }
        )

        const result = await readResponse(response)

        if (!response.ok || result.exc || result.exception) {
            throw new Error(
                result._server_messages
                    ? 'Unable to load product details.'
                    : 'Product not found.'
            )
        }

        product.value = result.message

        if (!product.value) {
            throw new Error('Product not found.')
        }

    } catch (err) {
        console.error('Product Detail Error:', err)
        error.value = err.message || 'Unable to load product.'
    } finally {
        loading.value = false
    }
}

// ADD TO CART
const addToCart = async () => {
    if (!product.value || adding.value) return
    if (isOutOfStock(product.value)) {
        notify('Out of Stock', 'error')
        return
    }

    adding.value = true

    try {
        // CHECK LOGIN
        const sessionResponse = await fetch(
            '/api/method/frappe.auth.get_logged_user',
            {
                credentials: 'same-origin'
            }
        )

        const sessionData = await readResponse(sessionResponse)

        if (
            !sessionResponse.ok ||
            !sessionData.message ||
            sessionData.message === 'Guest'
        ) {
            notify('Please login first!', 'error')
            await router.push('/login')
            return
        }

        // ADD TO CART
        const response = await fetch(
            '/api/method/buy_new.api.add_to_cart',
            {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Frappe-CSRF-Token': getCsrfToken()
                },
                body: JSON.stringify({
                    product: product.value.name
                })
            }
        )

        const result = await readResponse(response)

        if (!response.ok || result.exc || result.exception) {
            throw new Error('Unable to add product to cart.')
        }

        notify('Product added to cart successfully!')

    } catch (err) {
        console.error('Add to Cart Error:', err)
        notify(err.message || 'Unable to add product!', 'error')
    } finally {
        adding.value = false
    }
}

// LOAD PRODUCT
onMounted(() => {
    getProduct()
})

// UPDATE WHEN PRODUCT ID CHANGES
watch(
    () => route.params.id,
    () => getProduct()
)

// CLEANUP
onUnmounted(() => {
    clearTimeout(toastTimer)
})
</script>

<style>
.product-description p {
    margin-bottom: 8px;
}

.product-description ul {
    list-style: disc;
    padding-left: 22px;
    margin-bottom: 10px;
}

.product-description ol {
    list-style: decimal;
    padding-left: 22px;
    margin-bottom: 10px;
}

.product-description img {
    max-width: 100%;
    height: auto;
}

.product-description strong,
.product-description b {
    font-weight: 700;
}

.product-description h1,
.product-description h2,
.product-description h3 {
    margin-bottom: 8px;
    font-weight: 700;
}
</style>
