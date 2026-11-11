<template>
    <div class="min-h-screen bg-[#faf5f7] px-3 py-5 sm:px-6">
        <div class="mx-auto max-w-7xl">

            <!-- Page Heading -->
            <h1 class="mb-5 text-xl font-bold text-[#82103c] sm:text-2xl">
                My Cart
                <span class="text-sm font-normal text-[#82103c]/70">
                    ({{ totalItems }} Items)
                </span>
            </h1>

            <!-- Loading -->
            <div v-if="loading" class="rounded-lg bg-white py-16 text-center shadow-sm">
                <i class="fas fa-spinner fa-spin text-3xl text-[#82103c]"></i>
                <p class="mt-3 text-sm text-gray-500">
                    Loading your cart...
                </p>
            </div>

            <!-- Error -->
            <div v-else-if="error" class="rounded-lg bg-white py-12 text-center shadow-sm">
                <i class="fas fa-exclamation-circle text-4xl text-red-500"></i>
                <p class="mt-3 text-sm text-red-600">{{ error }}</p>

                <button @click="getCart" class="mt-4 rounded-lg bg-[#82103c] px-6 py-2 text-white">
                    Try Again
                </button>
            </div>

            <!-- Empty Cart -->
            <div v-else-if="cart.length === 0" class="rounded-lg bg-white py-16 text-center shadow-sm">
                <i class="fas fa-shopping-cart text-5xl text-[#82103c]/30"></i>

                <h2 class="mt-4 text-xl font-semibold text-[#82103c]">
                    Your Cart is Empty!
                </h2>

                <p class="mt-2 text-sm text-[#82103c]/70">
                    Add products to your cart to see them here.
                </p>

                <RouterLink to="/products"
                    class="mt-5 inline-block rounded-lg bg-[#82103c] px-8 py-3 font-semibold text-white transition hover:bg-[#650c2f]">
                    Shop Now
                </RouterLink>
            </div>

            <!-- Cart Layout -->
            <div v-else class="grid grid-cols-1 items-start gap-5 lg:grid-cols-3">

                <!-- LEFT: Cart Products -->
                <div class="space-y-4 lg:col-span-2">

                    <div v-for="item in cart" :key="item.name"
                        class="overflow-hidden rounded-lg border border-[#82103c]/10 bg-white shadow-sm">

                        <!-- Product Details -->
                        <div class="flex flex-col gap-4 p-4 sm:flex-row">

                            <!-- Product Image -->
                            <div class="flex h-32 w-full shrink-0 items-center justify-center sm:w-32">
                                <img v-if="item.product_image" :src="item.product_image" :alt="item.product_name"
                                    class="h-full w-full object-contain" />

                                <i v-else class="fas fa-image text-5xl text-[#82103c]/30"></i>
                            </div>

                            <!-- Product Information -->
                            <div class="min-w-0 flex-1">

                                <h2 class="break-words text-base font-semibold text-[#82103c] sm:text-lg">
                                    {{ item.product_name }}
                                </h2>

                                <div class="mt-3">
                                    <span class="text-xl font-bold text-[#82103c]">
                                        ₹{{ formatPrice(item.selling_price) }}
                                    </span>
                                </div>

                                <!-- Quantity -->
                                <div class="mt-3 flex items-center gap-2">
                                    <label class="text-sm font-medium text-[#82103c]">
                                        Qty:
                                    </label>

                                    <select :value="item.quantity" :disabled="updatingItem === item.name"
                                        @change="changeQuantity(item, Number($event.target.value))"
                                        class="rounded border border-[#82103c]/30 bg-white px-3 py-1.5 text-sm text-[#82103c] outline-none focus:border-[#82103c] focus:ring-1 focus:ring-[#82103c] disabled:opacity-50">
                                        <option v-for="qty in 10" :key="qty" :value="qty">
                                            {{ qty }}
                                        </option>
                                    </select>

                                    <i v-if="updatingItem === item.name"
                                        class="fas fa-spinner fa-spin text-[#82103c]"></i>
                                </div>

                                <!-- Subtotal -->
                                <p class="mt-3 text-sm text-gray-500">
                                    Subtotal:
                                    <span class="font-bold text-[#82103c]">
                                        ₹{{ formatPrice(Number(item.selling_price) * Number(item.quantity)) }}
                                    </span>
                                </p>

                            </div>
                        </div>

                        <!-- Product Actions -->
                        <div class="grid grid-cols-2 border-t border-[#82103c]/10">

                            <button @click="saveForLater(item)"
                                class="px-2 py-4 text-xs font-semibold text-[#82103c] transition hover:bg-[#82103c]/5 sm:text-sm">
                                <i class="far fa-bookmark mr-1 sm:mr-2"></i>
                                Save for later
                            </button>

                            <button @click="removeItem(item)" :disabled="removingItem === item.name"
                                class="border-l border-[#82103c]/10 px-2 py-4 text-xs font-semibold text-[#82103c] transition hover:bg-[#82103c]/5 disabled:opacity-50 sm:text-sm">
                                <i :class="removingItem === item.name
                                    ? 'fas fa-spinner fa-spin'
                                    : 'far fa-trash-alt'" class="mr-1 sm:mr-2"></i>
                                Remove
                            </button>

                        </div>

                    </div>
                </div>

                <!-- RIGHT: Price Details -->
                <div class="space-y-4">

                    <div class="rounded-lg border border-[#82103c]/10 bg-white p-5 shadow-sm">

                        <h2 class="border-b border-[#82103c]/20 pb-4 text-base font-bold uppercase text-[#82103c]">
                            Price Details
                        </h2>

                        <div class="mt-4 space-y-4">

                            <div class="flex justify-between gap-2 text-sm">
                                <span class="text-[#82103c]/80">
                                    Price ({{ totalItems }} items)
                                </span>

                                <span class="font-semibold text-[#82103c]">
                                    ₹{{ formatPrice(totalPrice) }}
                                </span>
                            </div>

                            <div class="flex justify-between gap-2 text-sm">
                                <span class="text-[#82103c]/80">
                                    Protect Promise Fee
                                </span>

                                <span class="font-semibold text-[#82103c]">
                                    ₹{{ protectionFee }}
                                </span>
                            </div>

                            <div class="flex justify-between text-sm">
                                <span class="text-[#82103c]/80">
                                    Delivery Charges
                                </span>

                                <span class="font-semibold text-green-600">
                                    Free
                                </span>
                            </div>

                        </div>

                        <!-- Total -->
                        <div class="mt-6 flex justify-between gap-2 border-t border-dashed border-[#82103c]/30 pt-5">
                            <span class="font-semibold text-[#82103c]">
                                Total Amount
                            </span>

                            <span class="text-lg font-bold text-[#82103c]">
                                ₹{{ formatPrice(finalAmount) }}
                            </span>
                        </div>

                        <p class="mt-4 text-sm font-medium text-[#82103c]">
                            You will save on your purchase!
                        </p>

                    </div>

                    <!-- Secure Payment -->
                    <div class="flex items-center justify-center gap-3 px-3 py-3 text-center">
                        <i class="fas fa-shield-alt text-2xl text-[#82103c]"></i>

                        <p class="text-xs font-medium text-[#82103c]/80 sm:text-sm">
                            Safe and secure payments.
                            Easy returns.
                        </p>
                    </div>

                </div>
            </div>

            <!-- Bottom Order Bar -->
            <div v-if="!loading && !error && cart.length"
                class="sticky bottom-0 z-30 mt-5 flex items-center justify-between gap-3 rounded-lg border border-[#82103c]/20 bg-white p-3 shadow-lg sm:p-4">
                <div>
                    <p class="text-xs text-[#82103c]/70">
                        Total Amount
                    </p>

                    <p class="text-lg font-bold text-[#82103c] sm:text-xl">
                        ₹{{ formatPrice(finalAmount) }}
                    </p>
                </div>

                <button @click="placeOrder"
                    class="rounded-lg bg-[#82103c] px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-[#650c2f] sm:px-12">
                    Place Order
                </button>
            </div>

        </div>

        <!-- Toast -->
        <Transition enter-active-class="transition duration-300 ease-out" enter-from-class="translate-y-4 opacity-0"
            enter-to-class="translate-y-0 opacity-100" leave-active-class="transition duration-200 ease-in"
            leave-from-class="translate-y-0 opacity-100" leave-to-class="translate-y-4 opacity-0">
            <div v-if="showToast"
                class="fixed bottom-5 right-5 z-[100] rounded-xl bg-gray-900 px-5 py-4 text-sm font-medium text-white shadow-xl">
                {{ toastMessage }}
            </div>
        </Transition>

    </div>
</template>


<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'

const router = useRouter()

// Cart Data
const cart = ref([])

// Loading and Error
const loading = ref(true)
const error = ref('')

// API Loading
const updatingItem = ref('')
const removingItem = ref('')

// Toast
const showToast = ref(false)
const toastMessage = ref('')
let toastTimer = null

// Protection Fee
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
            total +
            Number(item.selling_price || 0) *
            Number(item.quantity || 0),
        0
    )
})

// Final Amount
const finalAmount = computed(() => {
    return totalPrice.value +
        (cart.value.length ? protectionFee : 0)
})

// CSRF Token
const getCsrfToken = () => {
    return (
        document.querySelector('meta[name="csrf-token"]')?.content ||
        window.frappe?.csrf_token ||
        ''
    )
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

const redirectGuestIfNeeded = async (response, result) => {
    const errorDetails = `${result?.exc_type || ''} ${result?.exception || ''} ${result?.message || ''}`
    const isGuest = [401, 403].includes(response.status) ||
        /PermissionError|Please login/i.test(errorDetails)

    if (isGuest) {
        await router.replace('/login')
    }

    return isGuest
}

// Toast Notification
const notify = (message) => {
    toastMessage.value = message
    showToast.value = true

    clearTimeout(toastTimer)

    toastTimer = setTimeout(() => {
        showToast.value = false
    }, 3000)
}

// =====================================
// GET CART FROM DATABASE
// =====================================

const getCart = async () => {
    loading.value = true
    error.value = ''

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

        const result = await readApiResponse(response)

        if (!response.ok || result.exc) {
            if (await redirectGuestIfNeeded(response, result)) return
            throw new Error(getApiErrorMessage(result, 'Unable to load your cart'))
        }

        cart.value = Array.isArray(result.message) ? result.message : []

    } catch (err) {
        console.error('Get Cart Error:', err)
        error.value = err.message || 'Unable to load your cart.'

    } finally {
        loading.value = false
    }
}

// =====================================
// UPDATE QUANTITY IN DATABASE
// =====================================

const changeQuantity = async (item, quantity) => {
    if (quantity < 1 || quantity > 10) return

    const previousQuantity = item.quantity
    updatingItem.value = item.name

    try {
        const response = await fetch(
            '/api/method/buy_new.api.update_cart_quantity',
            {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Frappe-CSRF-Token': getCsrfToken()
                },
                body: JSON.stringify({
                    cart_item: item.name,
                    quantity: quantity
                })
            }
        )

        const result = await readApiResponse(response)

        if (!response.ok || result.exc) {
            if (await redirectGuestIfNeeded(response, result)) return
            throw new Error(getApiErrorMessage(result, 'Unable to update quantity'))
        }

        item.quantity = quantity
        notify('Cart quantity updated')

    } catch (err) {
        console.error('Quantity Error:', err)
        item.quantity = previousQuantity
        notify(err.message || 'Unable to update quantity')

    } finally {
        updatingItem.value = ''
    }
}

// =====================================
// REMOVE PRODUCT FROM DATABASE CART
// =====================================

const removeItem = async (item) => {
    removingItem.value = item.name

    try {
        const response = await fetch(
            '/api/method/buy_new.api.remove_from_cart',
            {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Frappe-CSRF-Token': getCsrfToken()
                },
                body: JSON.stringify({
                    cart_item: item.name
                })
            }
        )

        const result = await readApiResponse(response)

        if (!response.ok || result.exc) {
            if (await redirectGuestIfNeeded(response, result)) return
            throw new Error(getApiErrorMessage(result, 'Unable to remove product'))
        }

        cart.value = cart.value.filter(
            product => product.name !== item.name
        )

        notify('Product removed from cart')

    } catch (err) {
        console.error('Remove Cart Error:', err)
        notify(err.message || 'Unable to remove product')

    } finally {
        removingItem.value = ''
    }
}

// =====================================
// SAVE FOR LATER
// =====================================

const saveForLater = async (item) => {
    try {
        const saved = JSON.parse(
            localStorage.getItem('buynew_saved_items') || '[]'
        )

        if (!saved.some(product => product.product === item.product)) {
            saved.push(item)
        }

        localStorage.setItem(
            'buynew_saved_items',
            JSON.stringify(saved)
        )

        await removeItem(item)

    } catch (err) {
        console.error('Save For Later Error:', err)
        notify('Unable to save product')
    }
}

// =====================================
// BUY THIS NOW
// =====================================

const buyThisNow = (item) => {
    router.push('/checkout')
}

// =====================================
// PLACE ORDER
// =====================================

const placeOrder = () => {
    router.push('/checkout')
}

// =====================================
// LOAD CART
// =====================================

onMounted(() => {
    getCart()
})

// Cleanup
onUnmounted(() => {
    clearTimeout(toastTimer)
})
</script>
