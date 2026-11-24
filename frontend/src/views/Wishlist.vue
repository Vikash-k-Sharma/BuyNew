<template>
    <div class="min-h-screen bg-gray-50 px-4 py-6">

        <div class="mx-auto max-w-7xl">

            <!-- Heading -->
            <div class="mb-6 flex items-center gap-3">
                <i class="fas fa-heart text-2xl text-[#82103c]"></i>
                <h1 class="text-2xl font-bold text-gray-900">
                    My Wishlist
                </h1>
                <span class="rounded-full bg-[#82103c]/10 px-3 py-1 text-sm font-semibold text-[#82103c]">
                    {{ products.length }}
                </span>
            </div>

            <!-- Loading -->
            <div v-if="loading" class="py-20 text-center text-gray-500">
                <i class="fas fa-spinner fa-spin text-3xl"></i>
                <p class="mt-3">Loading wishlist...</p>
            </div>

            <!-- Error -->
            <div v-else-if="error" class="rounded-lg bg-white py-16 text-center">
                <i class="fas fa-exclamation-circle text-4xl text-red-500"></i>
                <p class="mt-3 text-gray-700">{{ error }}</p>
                <button @click="getWishlist" class="mt-4 rounded-lg bg-[#82103c] px-5 py-2 text-white">
                    Try Again
                </button>
            </div>

            <!-- Empty Wishlist -->
            <div v-else-if="products.length === 0" class="rounded-lg bg-white px-4 py-16 text-center shadow-sm">
                <i class="far fa-heart text-6xl text-gray-300"></i>

                <h2 class="mt-5 text-xl font-bold text-gray-800">
                    Your Wishlist is Empty
                </h2>

                <p class="mt-2 text-sm text-gray-500">
                    You haven't added any products to your wishlist yet.
                </p>

                <button @click="router.push('/home')"
                    class="mt-6 rounded-lg bg-[#82103c] px-6 py-3 font-semibold text-white transition hover:bg-[#650d30]">
                    Continue Shopping
                </button>
            </div>

            <!-- Wishlist Products -->
            <div v-else class="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">

                <article v-for="product in products" :key="product.wishlist_id"
                    class="overflow-hidden rounded-lg bg-white shadow-sm transition hover:shadow-md">

                    <!-- Product Image -->
                    <div class="relative flex aspect-[0.85/1] cursor-pointer items-center justify-center overflow-hidden bg-gray-100 p-3"
                        @click="openProduct(product)">
                        <img v-if="product.product_image" :src="product.product_image" :alt="product.products_name"
                            class="h-full w-full object-contain" loading="lazy" />

                        <i v-else class="fas fa-image text-4xl text-gray-300"></i>

                        <!-- Remove Button -->
                        <button @click.stop="removeFromWishlist(product)" :disabled="removing.includes(product.name)"
                            class="absolute right-2 top-2 flex h-9 w-9 items-center justify-center rounded-full bg-white shadow-md transition hover:scale-110 disabled:opacity-50"
                            aria-label="Remove from wishlist">
                            <i :class="[
                                'fas fa-heart',
                                removing.includes(product.name)
                                    ? 'text-gray-300'
                                    : 'text-[#82103c]'
                            ]"></i>
                        </button>
                    </div>

                    <!-- Product Details -->
                    <div class="p-3">

                        <h3 class="cursor-pointer truncate text-sm font-medium text-gray-800"
                            :title="product.products_name" @click="openProduct(product)">
                            {{ product.products_name }}
                        </h3>

                        <p class="mt-2 text-base font-bold text-gray-900">
                            ₹{{ formatPrice(product.selling_price) }}
                        </p>

                        <p v-if="Number(product.mrp) > Number(product.selling_price)"
                            class="mt-1 text-xs text-gray-400 line-through">
                            ₹{{ formatPrice(product.mrp) }}
                        </p>

                        <button @click="openProduct(product)"
                            class="mt-3 w-full rounded-md border border-[#82103c] py-2 text-xs font-semibold text-[#82103c] transition hover:bg-[#82103c] hover:text-white">
                            View Product
                        </button>

                    </div>

                </article>

            </div>

        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const products = ref([])
const loading = ref(true)
const error = ref('')
const removing = ref([])

const csrfToken = () => {
    return window.frappe?.csrf_token ||
        document.querySelector('meta[name="csrf-token"]')?.content ||
        ''
}

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
            console.error(err)
        }
    }

    return typeof result?.message === 'string'
        ? result.message
        : fallback
}

// Format Price
const formatPrice = (price) => {
    return Number(price || 0).toLocaleString('en-IN')
}

// Open Product
const openProduct = (product) => {
    router.push({
        name: 'ProductDetail',
        params: {
            id: product.name
        }
    })
}

// Get Wishlist
const getWishlist = async () => {
    loading.value = true
    error.value = ''

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
            throw new Error(
                getApiErrorMessage(result, 'Unable to load wishlist.')
            )
        }

        products.value = Array.isArray(result.message)
            ? result.message
            : []

    } catch (err) {
        console.error('Wishlist Error:', err)
        error.value = err.message || 'Unable to load wishlist.'
    } finally {
        loading.value = false
    }
}

// Remove Wishlist Product
const removeFromWishlist = async (product) => {
    if (removing.value.includes(product.name)) return

    removing.value.push(product.name)

    try {
        const response = await fetch(
            '/api/method/buy_new.api.remove_from_wishlist',
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
            throw new Error(
                getApiErrorMessage(result, 'Unable to remove product.')
            )
        }

        products.value = products.value.filter(
            item => item.name !== product.name
        )
        window.dispatchEvent(new Event('buynew-wishlist-updated'))

    } catch (err) {
        console.error('Remove Wishlist Error:', err)
        alert(err.message || 'Unable to remove product.')
    } finally {
        removing.value = removing.value.filter(
            name => name !== product.name
        )
    }
}

onMounted(() => {
    getWishlist()
})
</script>
