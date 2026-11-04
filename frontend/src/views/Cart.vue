<template>
    <div class="min-h-screen bg-gray-100 px-3 py-5 sm:px-6">

        <div class="mx-auto max-w-7xl">

            <!-- Page Heading -->
            <h1 class="mb-5 text-xl font-bold text-gray-800 sm:text-2xl">
                My Shopping Cart
                <span class="text-sm font-normal text-gray-500">
                    ({{ totalItems }} Items)
                </span>
            </h1>

            <!-- Empty Cart -->
            <div v-if="cart.length === 0" class="rounded-lg bg-white py-16 text-center shadow-sm">
                <i class="fas fa-shopping-cart text-5xl text-gray-300"></i>

                <h2 class="mt-4 text-xl font-semibold text-gray-700">
                    Your Cart is Empty!
                </h2>

                <p class="mt-2 text-sm text-gray-500">
                    Add products to your cart to see them here.
                </p>

                <RouterLink to="/products"
                    class="mt-5 inline-block rounded bg-yellow-400 px-8 py-3 font-semibold text-gray-900 hover:bg-yellow-500">
                    Shop Now
                </RouterLink>
            </div>


            <!-- Cart Layout -->
            <div v-else class="grid grid-cols-1 items-start gap-5 lg:grid-cols-3">

                <!-- LEFT: Cart Products -->
                <div class="space-y-4 lg:col-span-2">

                    <div v-for="item in cart" :key="item.name" class="overflow-hidden rounded-lg bg-white shadow-sm">

                        <!-- Product Details -->
                        <div class="flex flex-col gap-4 p-4 sm:flex-row">

                            <!-- Product Image -->
                            <div class="flex h-32 w-full shrink-0 items-center justify-center sm:w-32">

                                <img v-if="item.product_image" :src="item.product_image" :alt="item.products_name"
                                    class="h-full w-full object-contain" />

                                <i v-else class="fas fa-image text-5xl text-gray-300"></i>

                            </div>


                            <!-- Product Information -->
                            <div class="min-w-0 flex-1">

                                <h2 class="text-base font-medium text-gray-900 sm:text-lg">
                                    {{ item.products_name }}
                                </h2>

                                <p class="mt-1 text-sm text-gray-500">
                                    {{ item.short_description || item.brand || '' }}
                                </p>

                                <!-- Rating -->
                                <div class="mt-2 flex items-center gap-2 text-sm">
                                    <span class="text-green-600">
                                        <i class="fas fa-star"></i>
                                        <i class="fas fa-star"></i>
                                        <i class="fas fa-star"></i>
                                        <i class="fas fa-star"></i>
                                        <i class="fas fa-star-half-alt"></i>
                                    </span>

                                    <span class="text-xs text-green-700">
                                        4.2
                                    </span>
                                </div>

                                <!-- Price -->
                                <div class="mt-3 flex flex-wrap items-center gap-2">

                                    <span class="text-xl font-bold text-gray-900">
                                        ₹{{ formatPrice(item.selling_price) }}
                                    </span>

                                    <span v-if="item.mrp" class="text-sm text-gray-400 line-through">
                                        ₹{{ formatPrice(item.mrp) }}
                                    </span>

                                    <span v-if="item.discount_percentage" class="text-sm font-semibold text-green-600">
                                        {{ item.discount_percentage }}% off
                                    </span>

                                </div>

                                <!-- Quantity -->
                                <div class="mt-3 flex items-center gap-2">

                                    <label class="text-sm text-gray-600">
                                        Qty:
                                    </label>

                                    <select :value="item.quantity"
                                        @change="changeQuantity(item, Number($event.target.value))"
                                        class="rounded border border-gray-300 bg-white px-3 py-1.5 text-sm outline-none focus:border-blue-500">
                                        <option v-for="qty in 10" :key="qty" :value="qty">
                                            {{ qty }}
                                        </option>
                                    </select>

                                </div>

                                <!-- Delivery -->
                                <p class="mt-3 text-sm text-gray-700">
                                    Delivery by
                                    <span class="font-semibold text-green-600">
                                        available soon
                                    </span>
                                </p>

                            </div>

                        </div>


                        <!-- Product Actions -->
                        <div class="grid grid-cols-3 border-t border-gray-200">

                            <button
                                class="px-2 py-4 text-xs font-semibold text-gray-600 transition hover:text-blue-600 sm:text-sm">
                                <i class="far fa-bookmark mr-1 sm:mr-2"></i>
                                Save for later
                            </button>

                            <button
                                class="border-x border-gray-200 px-2 py-4 text-xs font-semibold text-gray-600 transition hover:text-red-600 sm:text-sm">
                                <i class="far fa-trash-alt mr-1 sm:mr-2"></i>
                                Remove
                            </button>

                            <button @click="buyThisNow(item)"
                                class="px-2 py-4 text-xs font-semibold text-gray-600 transition hover:text-blue-600 sm:text-sm">
                                <i class="fas fa-bolt mr-1 sm:mr-2"></i>
                                Buy this now
                            </button>

                        </div>

                    </div>

                </div>


                <!-- RIGHT: Price Details -->
                <div class="space-y-4">

                    <div class="rounded-lg bg-white p-5 shadow-sm">

                        <h2 class="border-b border-gray-200 pb-4 text-base font-bold uppercase text-gray-500">
                            Price Details
                        </h2>

                        <div class="mt-4 space-y-4">

                            <!-- Product Price -->
                            <div class="flex justify-between text-sm">
                                <span class="text-gray-700">
                                    Price ({{ totalItems }} items)
                                </span>

                                <span class="font-medium text-gray-900">
                                    ₹{{ formatPrice(totalPrice) }}
                                </span>
                            </div>

                            <!-- Protection Fee -->
                            <div class="flex justify-between text-sm">
                                <span class="text-gray-700">
                                    Protect Promise Fee
                                </span>

                                <span class="font-medium text-gray-900">
                                    ₹{{ protectionFee }}
                                </span>
                            </div>

                            <!-- Delivery -->
                            <div class="flex justify-between text-sm">
                                <span class="text-gray-700">
                                    Delivery Charges
                                </span>

                                <span class="font-semibold text-green-600">
                                    Free
                                </span>
                            </div>

                        </div>

                        <!-- Total -->
                        <div class="mt-6 flex justify-between border-t border-dashed border-gray-300 pt-5">

                            <span class="font-semibold text-gray-900">
                                Total Amount
                            </span>

                            <span class="text-lg font-bold text-gray-900">
                                ₹{{ formatPrice(finalAmount) }}
                            </span>

                        </div>

                        <p class="mt-4 text-sm font-medium text-green-600">
                            You will save on your purchase!
                        </p>

                    </div>


                    <!-- Secure Payment -->
                    <div class="flex items-center justify-center gap-3 px-3 py-3 text-center">

                        <i class="fas fa-shield-alt text-2xl text-gray-500"></i>

                        <p class="text-xs font-medium text-gray-500 sm:text-sm">
                            Safe and secure payments.
                            Easy returns.
                        </p>

                    </div>

                </div>

            </div>


            <!-- Bottom Order Bar -->
            <div v-if="cart.length"
                class="sticky bottom-0 z-30 mt-5 flex items-center justify-between gap-3 rounded-lg border border-gray-200 bg-white p-3 shadow-lg sm:p-4">

                <div>
                    <p class="text-xs text-gray-500">
                        Total Amount
                    </p>

                    <p class="text-lg font-bold text-gray-900 sm:text-xl">
                        ₹{{ formatPrice(finalAmount) }}
                    </p>
                </div>

                <button @click="placeOrder"
                    class="rounded-lg bg-yellow-400 px-5 py-3 text-sm font-semibold text-gray-900 shadow-sm transition hover:bg-yellow-500 sm:px-12">
                    Place Order
                </button>

            </div>

        </div>

    </div>
</template>


<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Cart Data
const cart = ref(
    JSON.parse(localStorage.getItem('buynew_cart') || '[]')
)

// Protection Fee (example amount)
const protectionFee = 299


// Format Price
const formatPrice = (price) => {
    return Number(price || 0).toLocaleString('en-IN')
}


// Total Items
const totalItems = computed(() => {
    return cart.value.reduce(
        (total, item) => total + Number(item.quantity || 0),
        0
    )
})


// Total Product Price
const totalPrice = computed(() => {
    return cart.value.reduce(
        (total, item) =>
            total + Number(item.selling_price || 0) * Number(item.quantity || 0),
        0
    )
})


// Final Amount
const finalAmount = computed(() => {
    return totalPrice.value + protectionFee
})


// Save Cart
const saveCart = () => {
    localStorage.setItem(
        'buynew_cart',
        JSON.stringify(cart.value)
    )
}


// Change Quantity
const changeQuantity = (item, quantity) => {

    item.quantity = quantity

    saveCart()

}


// Remove Product
const removeItem = (name) => {

    cart.value = cart.value.filter(
        item => item.name !== name
    )

    saveCart()

}


// Save For Later
const saveForLater = (item) => {

    const saved = JSON.parse(
        localStorage.getItem('buynew_saved_items') || '[]'
    )

    if (!saved.some(product => product.name === item.name)) {
        saved.push(item)
    }

    localStorage.setItem(
        'buynew_saved_items',
        JSON.stringify(saved)
    )

    removeItem(item.name)

}


// Buy This Now
const buyThisNow = (item) => {

    cart.value = [item]

    saveCart()

    router.push('/checkout')

}


// Place Order
const placeOrder = () => {

    router.push('/checkout')

}

</script>
