<template>
    <section class="w-full bg-white">

        <!-- Heading -->
        <div class="mb-3">
            <h2 class="text-xl font-bold text-[#212121]">
                Fashion
            </h2>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="py-10 text-center text-gray-500">
            Loading fashion products...
        </div>

        <!-- Error -->
        <div v-else-if="error" class="py-10 text-center text-red-600">
            {{ error }}
            <button @click="getProducts" class="ml-2 font-semibold underline">
                Try Again
            </button>
        </div>

        <!-- Empty -->
        <div v-else-if="visibleProducts.length === 0" class="py-10 text-center text-gray-500">
            No fashion products available.
        </div>

        <!-- Product Grid -->
        <div v-else class="w-full overflow-x-hidden">
            <div class="grid grid-cols-3 gap-2 md:grid-cols-4 lg:grid-cols-6 lg:gap-3">

                <article v-for="product in visibleProducts" :key="product.name"
                    class="min-w-0 cursor-pointer rounded-lg bg-white transition-transform duration-200 hover:-translate-y-1"
                    @click="openProduct(product)">

                    <!-- Product Image -->
                    <div
                        class="relative flex aspect-[0.76/1] w-full items-center justify-center overflow-hidden rounded-lg bg-[#f3f3f3]">

                        <div v-if="product.product_image && !product.imageLoaded && !product.imageFailed"
                            class="absolute inset-0 animate-pulse bg-gray-200"></div>

                        <img v-if="product.product_image && !product.imageFailed" :src="product.product_image"
                            :alt="product.products_name" loading="lazy" :class="[
                                'h-full w-full p-1.5 object-contain transition-opacity duration-200',
                                product.imageLoaded ? 'opacity-100' : 'opacity-0'
                            ]" @load="product.imageLoaded = true" @error="product.imageFailed = true" />

                        <i v-else class="fas fa-image text-3xl text-gray-300"></i>

                        <!-- Wishlist Button -->
                        <button type="button" @click.stop="toggleWishlist(product)"
                            :disabled="wishlistLoading.includes(product.name)"
                            class="absolute right-2 top-2 flex h-8 w-8 items-center justify-center rounded-full bg-white shadow-md transition hover:scale-110 disabled:opacity-50"
                            :aria-label="isWishlisted(product.name) ? 'Remove from wishlist' : 'Add to wishlist'">
                            <i :class="[
                                'fas fa-heart text-sm',
                                isWishlisted(product.name)
                                    ? 'text-[#82103c]'
                                    : 'text-gray-400'
                            ]"></i>
                        </button>

                        <!-- Rating -->
                        <div v-if="product.rating"
                            class="absolute bottom-1.5 left-1.5 flex items-center gap-1 rounded bg-white px-1.5 py-0.5 text-xs font-semibold text-black shadow-sm">
                            {{ Number(product.rating).toFixed(1) }}
                            <span class="text-green-700">★</span>
                        </div>

                    </div>

                    <!-- Product Details -->
                    <div class="min-w-0 pt-2">

                        <h3 class="truncate text-xs font-normal leading-5 text-gray-800 sm:text-sm"
                            :title="product.products_name">
                            {{ product.products_name }}
                        </h3>

                        <!-- Price -->
                        <div class="mt-1 flex min-w-0 items-baseline gap-1.5 whitespace-nowrap">

                            <span class="text-sm font-bold leading-5 text-gray-900 sm:text-base">
                                ₹{{ formatPrice(product.selling_price) }}
                            </span>

                            <span v-if="Number(product.mrp) > Number(product.selling_price)"
                                class="truncate text-[10px] text-gray-400 line-through sm:text-xs">
                                ₹{{ formatPrice(product.mrp) }}
                            </span>

                        </div>

                        <!-- Bank Offer -->
                        <p v-if="getBankOffer(product)"
                            class="mt-0.5 truncate text-[10px] font-medium leading-4 text-blue-700 sm:text-xs sm:leading-[18px]"
                            :title="getBankOffer(product)">
                            {{ getBankOffer(product) }}
                        </p>

                        <!-- Hot Deal -->
                        <p v-if="isHotDeal(product)"
                            class="mt-1 text-[10px] font-semibold leading-4 text-green-700 sm:text-xs sm:leading-[18px]">
                            Hot Deal
                        </p>

                    </div>

                </article>

            </div>
        </div>

    </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const products = ref([])
const loading = ref(true)
const error = ref('')

const wishlistProducts = ref([])
const wishlistLoading = ref([])

const csrfToken = () => {
    return window.frappe?.csrf_token ||
        document.querySelector('meta[name="csrf-token"]')?.content ||
        ''
}

const searchQuery = computed(() =>
    typeof route.query.search === 'string'
        ? route.query.search
        : ''
)

// Fashion Category Filter
const fashionProducts = computed(() => {
    return products.value.filter(product => {
        const category = String(product.category || '').toLowerCase().trim()
        const subcategory = String(product.subcategory || '').toLowerCase().trim()

        return (
            category.includes('fashion') ||
            category.includes('clothing') ||
            category.includes('apparel') ||
            category.includes('garment') ||
            subcategory.includes('fashion') ||
            subcategory.includes('clothing') ||
            subcategory.includes('apparel')
        )
    })
})

// Search Filter
const visibleProducts = computed(() => {
    const query = searchQuery.value.trim().toLowerCase()

    if (!query) return fashionProducts.value

    return fashionProducts.value.filter(product => {
        const values = [
            product.products_name,
            product.products_code,
            product.brand,
            product.category
        ]

        return values.some(value =>
            String(value || '').toLowerCase().includes(query)
        )
    })
})

// Format Price
const formatPrice = (price) => {
    return Number(price || 0).toLocaleString('en-IN')
}

// Bank Offer
const getBankOffer = (product) => {
    const offerPrice =
        product.bank_offer_price ||
        product.offer_price ||
        product.bank_price

    const offerLabel =
        product.bank_offer_label ||
        product.bank_name ||
        'Bank offer'

    if (offerPrice) {
        return `₹${formatPrice(offerPrice)} with ${offerLabel}`
    }

    return product.bank_offer_text || product.bank_offer || ''
}

// Hot Deal
const isHotDeal = (product) => {
    return Boolean(
        product.is_hot_deal ||
        product.hot_deal ||
        product.tag === 'Hot Deal'
    )
}

// Product Details
const openProduct = (product) => {
    router.push({
        name: 'ProductDetail',
        params: {
            id: product.name
        }
    })
}

// API Response
const readApiResponse = async (response) => {
    try {
        return await response.json()
    } catch {
        return {}
    }
}

// API Error
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
            console.error('Server message error:', err)
        }
    }

    if (typeof result?.message === 'string') {
        return result.message
    }

    return fallback
}

// Check Wishlist
const isWishlisted = (productName) => {
    return wishlistProducts.value.includes(productName)
}

// Get Wishlist
const getWishlist = async () => {
    try {
        const response = await fetch(
            '/api/method/buy_new.api.get_wishlist',
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
            return
        }

        const items = Array.isArray(result.message)
            ? result.message
            : []

        wishlistProducts.value = items.map(item => item.name)

    } catch (err) {
        console.error('Wishlist Load Error:', err)
    }
}

// Toggle Wishlist
const toggleWishlist = async (product) => {
    if (wishlistLoading.value.includes(product.name)) return

    wishlistLoading.value.push(product.name)

    const alreadyAdded = isWishlisted(product.name)

    try {
        const method = alreadyAdded
            ? 'remove_from_wishlist'
            : 'add_to_wishlist'

        const response = await fetch(
            `/api/method/buy_new.api.${method}`,
            {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Frappe-CSRF-Token': csrfToken()
                },
                body: JSON.stringify({
                    product: product.name
                })
            }
        )

        const result = await readApiResponse(response)

        if (!response.ok || result.exc || result.exception) {
            const message = getApiErrorMessage(
                result,
                'Unable to update wishlist.'
            )

            if (
                message.toLowerCase().includes('login') ||
                message.toLowerCase().includes('guest')
            ) {
                router.push('/login')
                return
            }

            throw new Error(message)
        }

        if (alreadyAdded) {
            wishlistProducts.value = wishlistProducts.value.filter(
                name => name !== product.name
            )
        } else {
            wishlistProducts.value.push(product.name)
        }

        window.dispatchEvent(new Event('buynew-wishlist-updated'))

    } catch (err) {
        console.error('Wishlist Error:', err)
        alert(err.message || 'Wishlist update failed.')
    } finally {
        wishlistLoading.value = wishlistLoading.value.filter(
            name => name !== product.name
        )
    }
}

// Fetch Products
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
                getApiErrorMessage(
                    result,
                    'Unable to load fashion products.'
                )
            )
        }

        products.value = Array.isArray(result.message)
            ? result.message.map(product => ({
                ...product,
                imageLoaded: false,
                imageFailed: false
            }))
            : []

    } catch (err) {
        console.error('Fashion Products Error:', err)
        error.value = err.message || 'Unable to load fashion products.'
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    getProducts()
    getWishlist()
})
</script>
