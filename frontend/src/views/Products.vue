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
                <button @click="getProducts" class="ml-2 font-semibold underline">
                    Try Again
                </button>
            </div>

            <!-- No Products -->
            <div v-else-if="visibleProducts.length === 0" class="py-12 text-center text-gray-500">
                {{ searchQuery ? `No products found for "${searchQuery}".` : 'No products available.' }}
            </div>

            <!-- Product Grid -->
            <div v-else class="flex flex-col gap-0">

                <div v-for="product in visibleProducts" :key="product.name" class="flex w-full gap-3 border-b border-gray-200 bg-white px-2 py-5
                    lg:grid lg:grid-cols-[190px_minmax(0,1fr)_230px]
                    lg:items-start lg:gap-5 lg:px-6 lg:py-6">

                    <!-- Product Image -->
                    <div @click="openProduct(product)" class="flex h-36 w-[38%] shrink-0 cursor-pointer items-center justify-center
                        lg:h-[190px] lg:w-full lg:bg-gray-50">
                        <img v-if="product.product_image" :src="product.product_image" :alt="product.products_name"
                            loading="lazy" class="h-full w-full object-contain" />

                        <i v-else class="fas fa-image text-4xl text-gray-300"></i>
                    </div>

                    <!-- Product Details -->
                    <div class="flex min-w-0 flex-1 flex-col lg:py-1">

                        <!-- Product Name -->
                        <h2 @click="openProduct(product)"
                            class="line-clamp-2 cursor-pointer text-sm font-medium leading-5 text-gray-800 hover:text-[#82103c] sm:text-base sm:font-semibold lg:text-lg">
                            {{ product.products_name }}
                        </h2>

                        <!-- Brand -->
                        <p class="mt-1 text-xs text-gray-500 sm:text-sm">
                            {{ product.brand || 'No Brand' }}
                        </p>

                        <!-- Rating -->
                        <div v-if="product.rating" class="mt-2 flex flex-wrap items-center gap-2 text-xs">
                            <span class="rounded bg-green-600 px-2 py-1 font-semibold text-white">
                                {{ product.rating }} ★
                            </span>

                            <span class="text-gray-500">
                                Product Rating
                            </span>
                        </div>

                        <!-- Desktop Description -->
                        <div v-if="product.short_description || product.description"
                            class="product-description mt-3 hidden text-sm leading-6 text-gray-700 lg:block">
                            <!-- Short Description -->
                            <p v-if="product.short_description" class="whitespace-pre-line">
                                {{ product.short_description }}
                            </p>

                            <!-- HTML Description -->
                            <div v-else v-html="cleanDescription(product.description)"></div>
                        </div>

                        <!-- Mobile Price -->
                        <div class="mt-2 flex flex-wrap items-center gap-2 lg:hidden">

                            <span class="text-lg font-bold text-gray-900">
                                ₹{{ formatPrice(product.selling_price) }}
                            </span>

                            <span v-if="product.mrp" class="text-xs text-gray-400 line-through">
                                ₹{{ formatPrice(product.mrp) }}
                            </span>

                        </div>

                        <!-- Mobile Discount -->
                        <p v-if="product.discount_percentage"
                            class="mt-1 text-xs font-semibold text-green-600 lg:hidden">
                            {{ product.discount_percentage }}% OFF
                        </p>

                        <!-- Stock -->
                        <p class="mt-2 text-xs" :class="isOutOfStock(product)
                            ? 'font-semibold text-red-600'
                            : 'text-gray-500'">
                            {{ isOutOfStock(product) ? 'Out of Stock' : (product.stock_status || 'Stock information unavailable') }}
                        </p>

                        <!-- Mobile Add to Cart -->
                        <div v-if="isOutOfStock(product)" role="status"
                            class="mt-3 flex w-full items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2.5 text-sm font-semibold text-red-700 lg:hidden">
                            <i class="fas fa-circle-exclamation"></i>
                            Out of Stock
                        </div>
                        <button v-else type="button" @click="addToCart(product)"
                            :disabled="addingProduct === product.name"
                            class="mt-3 w-full rounded-lg bg-[#82103c] px-3 py-2.5 text-sm font-semibold text-white transition hover:bg-[#6b0b30] active:scale-95 disabled:cursor-not-allowed disabled:opacity-50 lg:hidden">
                            <i :class="addingProduct === product.name
                                ? 'fas fa-spinner fa-spin'
                                : 'fas fa-shopping-cart'" class="mr-2"></i>

                            {{ addingProduct === product.name ? 'Adding...' : 'Add to Cart' }}
                        </button>

                    </div>

                    <!-- Desktop Price Section -->
                    <div class="hidden lg:flex lg:flex-col lg:items-start lg:py-1">

                        <span class="text-2xl font-bold text-gray-900">
                            ₹{{ formatPrice(product.selling_price) }}
                        </span>

                        <span v-if="product.mrp" class="mt-1 text-sm text-gray-400 line-through">
                            ₹{{ formatPrice(product.mrp) }}
                        </span>

                        <p v-if="product.discount_percentage" class="mt-2 text-sm font-semibold text-green-600">
                            {{ product.discount_percentage }}% OFF
                        </p>

                        <p class="mt-2 text-xs" :class="isOutOfStock(product)
                            ? 'font-semibold text-red-600'
                            : 'text-gray-600'">
                            {{ isOutOfStock(product) ? 'Out of Stock' : (product.stock_status || 'Stock information unavailable') }}
                        </p>

                        <!-- Desktop Add to Cart -->
                        <div v-if="isOutOfStock(product)" role="status"
                            class="mt-4 flex w-full items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">
                            <i class="fas fa-circle-exclamation"></i>
                            Out of Stock
                        </div>
                        <button v-else type="button" @click="addToCart(product)"
                            :disabled="addingProduct === product.name"
                            class="mt-4 w-full rounded-lg bg-[#82103c] px-4 py-3 text-sm font-semibold text-white transition hover:bg-[#6b0b30] disabled:cursor-not-allowed disabled:opacity-50">
                            <i :class="addingProduct === product.name
                                ? 'fas fa-spinner fa-spin'
                                : 'fas fa-shopping-cart'" class="mr-2"></i>

                            {{ addingProduct === product.name ? 'Adding...' : 'Add to Cart' }}
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import DOMPurify from 'dompurify'

const router = useRouter()
const route = useRoute()

// PRODUCT DATA
const products = ref([])
const isOutOfStock = (product) =>
    Number(product?.stock_quantity) <= 0 ||
    String(product?.stock_status || '').toLowerCase().includes('out of stock')

const searchQuery = computed(() =>
    typeof route.query.search === 'string' ? route.query.search : ''
)
const visibleProducts = computed(() => {
    const query = searchQuery.value.trim().toLowerCase()

    if (!query) return products.value

    return products.value.filter(product => {
        const searchableValues = [
            product.products_name,
            product.products_code,
            product.brand
        ]

        return searchableValues.some(value =>
            String(value || '').toLowerCase().includes(query)
        )
    })
})

// LOADING
const loading = ref(true)
const error = ref('')

// CART
const addingProduct = ref('')

// TOAST
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
        USE_PROFILES: {
            html: true
        }
    })
}

// OPEN PRODUCT DETAIL
const openProduct = (product) => {
    router.push({
        name: 'ProductDetail',
        params: {
            id: product.name
        }
    })
}

// SHOW NOTIFICATION
const notify = (message, type = 'success') => {
    toastMessage.value = message
    toastType.value = type
    showToast.value = true

    clearTimeout(toastTimer)

    toastTimer = setTimeout(() => {
        showToast.value = false
    }, 3000)
}

// GET CSRF TOKEN
const getCsrfToken = () => {
    return (
        document.querySelector('meta[name="csrf-token"]')?.content ||
        window.frappe?.csrf_token ||
        ''
    )
}

// READ API RESPONSE
const readApiResponse = async (response) => {
    try {
        return await response.json()
    } catch {
        return {}
    }
}

// API ERROR MESSAGE
const getApiErrorMessage = (result, fallback) => {
    if (result?._server_messages) {
        try {
            const messages = JSON.parse(result._server_messages)
                .map(message => JSON.parse(message).message)
                .filter(Boolean)

            if (messages.length) {
                return messages.join(', ')
            }
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

// FETCH PRODUCTS
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

        const result = await readApiResponse(response)

        if (!response.ok || result.exc || result.exception) {
            throw new Error(
                getApiErrorMessage(result, 'Unable to load products.')
            )
        }

        products.value = Array.isArray(result.message)
            ? result.message
            : []

        console.log('Products:', products.value)

    } catch (err) {
        console.error('Product Error:', err)
        error.value = err.message || 'Unable to load products.'
    } finally {
        loading.value = false
    }
}

// ADD PRODUCT TO DATABASE CART
const addToCart = async (product) => {
    if (isOutOfStock(product)) {
        notify('Out of Stock', 'error')
        return
    }

    if (addingProduct.value) return

    addingProduct.value = product.name

    try {
        // CHECK LOGIN
        const sessionResponse = await fetch(
            '/api/method/frappe.auth.get_logged_user',
            {
                credentials: 'same-origin'
            }
        )

        const sessionData = await readApiResponse(sessionResponse)

        if (
            !sessionResponse.ok ||
            !sessionData.message ||
            sessionData.message === 'Guest'
        ) {
            notify('Please login first!', 'error')
            await router.push('/login')
            return
        }

        // ADD TO CART API
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
                    product: product.name
                })
            }
        )

        const result = await readApiResponse(response)

        if (!response.ok || result.exc || result.exception) {
            console.error('ADD TO CART FAILED:', {
                status: response.status,
                response: result
            })

            throw new Error(
                getApiErrorMessage(result, 'Unable to add product')
            )
        }

        notify(`${product.products_name} added to cart!`)

        console.log('Cart Added Successfully:', result)

    } catch (err) {
        console.error('Cart Error:', err)
        notify(err.message || 'Unable to add product!', 'error')
    } finally {
        addingProduct.value = ''
    }
}

// LOAD PRODUCTS
onMounted(() => {
    getProducts()
})

// CLEAR TIMER
onUnmounted(() => {
    clearTimeout(toastTimer)
})
</script>

<style>
.product-description p {
    margin-bottom: 6px;
}

.product-description ul {
    list-style: disc;
    padding-left: 20px;
    margin-bottom: 8px;
}

.product-description ol {
    list-style: decimal;
    padding-left: 20px;
    margin-bottom: 8px;
}

.product-description img {
    max-width: 100%;
    height: auto;
}

.product-description strong,
.product-description b {
    font-weight: 700;
}

.product-description a {
    color: #82103c;
    text-decoration: underline;
}

.product-description h1,
.product-description h2,
.product-description h3 {
    font-weight: 700;
    margin-bottom: 8px;
}
</style>
