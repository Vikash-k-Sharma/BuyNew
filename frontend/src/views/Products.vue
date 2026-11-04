<template>
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
        <div v-else class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">

            <div v-for="product in products" :key="product.name"
                class="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-lg">

                <!-- Product Image -->
                <div class="flex h-36 items-center justify-center bg-gray-50 sm:h-48">
                    <img v-if="product.product_image" :src="product.product_image" :alt="product.products_name"
                        class="h-full w-full object-contain p-3" />

                    <i v-else class="fas fa-image text-4xl text-gray-300"></i>
                </div>

                <!-- Product Details -->
                <div class="p-3">

                    <h2 class="truncate text-sm font-semibold text-gray-800 sm:text-base">
                        {{ product.products_name }}
                    </h2>

                    <p class="mt-1 text-xs text-gray-500">
                        {{ product.brand || 'No Brand' }}
                    </p>

                    <div class="mt-3 flex flex-wrap items-center gap-2">

                        <span class="text-lg font-bold text-gray-900">
                            ₹{{ product.selling_price }}
                        </span>

                        <span v-if="product.mrp" class="text-xs text-gray-400 line-through">
                            ₹{{ product.mrp }}
                        </span>

                    </div>

                    <p v-if="product.discount_percentage" class="mt-1 text-xs font-semibold text-green-600">
                        {{ product.discount_percentage }}% OFF
                    </p>

                    <p class="mt-2 text-xs text-gray-500">
                        {{ product.stock_status || 'Stock information unavailable' }}
                    </p>

                    <!-- Add to Cart -->
                    <button type="button" @click="addToCart(product)"
                        class="mt-4 w-full rounded-lg bg-blue-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-blue-700">
                        <i class="fas fa-shopping-cart mr-2"></i>
                        Add to Cart
                    </button>

                </div>
            </div>

        </div>

    </div>
</template>


<script setup>
import { ref, onMounted } from 'vue'

// Product Data
const products = ref([])

// Loading State
const loading = ref(true)

// Error State
const error = ref('')

// Fetch Products from Frappe API
const getProducts = async () => {

    try {

        const response = await fetch(
            '/api/method/buy_new.api.get_products',
            {
                method: 'GET',
                credentials: 'same-origin',
                headers: {
                    'Accept': 'application/json'
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


// Add Product to Cart
const addToCart = (product) => {

    // Get Existing Cart
    let cart = JSON.parse(
        localStorage.getItem('buynew_cart') || '[]'
    )

    // Check Existing Product
    const existingProduct = cart.find(
        item => item.name === product.name
    )

    if (existingProduct) {

        // Increase Quantity
        existingProduct.quantity += 1

    } else {

        // Add New Product
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

    // Success Message
    alert(`${product.products_name} added to cart!`)

    console.log('Updated Cart:', cart)

}


// Fetch Products When Page Loads
onMounted(() => {

    getProducts()

})

</script>