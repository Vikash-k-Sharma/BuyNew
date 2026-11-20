<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

const loading = ref(true);
const placingOrder = ref(false);
const errorMessage = ref("");
const cartItems = ref([]);

const form = ref({
    customer_name: "",
    phone: "",
    address: "",
    city: "",
    state: "",
    pincode: "",
    payment_method: "COD",
});

const subtotal = ref(0);
const deliveryCharge = ref(0);
const grandTotal = ref(0);

const paymentMethods = [
    { value: "COD", label: "Cash on Delivery", description: "Pay when your order arrives" },
    { value: "UPI", label: "UPI", description: "Demo payment using UPI" },
    { value: "Card", label: "Credit / Debit Card", description: "Demo card payment" },
    { value: "Net Banking", label: "Net Banking", description: "Demo net banking payment" },
];

const selectedPayment = computed(() =>
    paymentMethods.find((method) => method.value === form.value.payment_method)
);

const formatPrice = (price) =>
    new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 2,
    }).format(Number(price || 0));

async function loadCheckout() {
    loading.value = true;
    errorMessage.value = "";

    try {
        const response = await fetch(
            "/api/method/buy_new.api.get_checkout_data",
            { credentials: "include" }
        );

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.exception || "Unable to load checkout");
        }

        const data = result.message || {};

        cartItems.value = data.items || [];
        subtotal.value = Number(data.subtotal || 0);
        deliveryCharge.value = Number(data.delivery_charge || 0);
        grandTotal.value = Number(data.grand_total || 0);

        if (!cartItems.value.length) {
            router.replace("/cart");
        }
    } catch (error) {
        errorMessage.value = error.message || "Something went wrong";
    } finally {
        loading.value = false;
    }
}

async function placeOrder() {
    errorMessage.value = "";

    if (!form.value.customer_name.trim()) {
        errorMessage.value = "Please enter your full name";
        return;
    }

    if (!/^[0-9]{10}$/.test(form.value.phone)) {
        errorMessage.value = "Please enter a valid 10-digit mobile number";
        return;
    }

    if (!form.value.address.trim() ||
        !form.value.city.trim() ||
        !form.value.state.trim()) {
        errorMessage.value = "Please complete your delivery address";
        return;
    }

    if (!/^[0-9]{6}$/.test(form.value.pincode)) {
        errorMessage.value = "Please enter a valid 6-digit pincode";
        return;
    }

    if (!cartItems.value.length) {
        errorMessage.value = "Your cart is empty";
        return;
    }

    placingOrder.value = true;

    try {
        const csrfToken =
            window.frappe?.csrf_token ||
            document.querySelector('meta[name="csrf-token"]')?.content ||
            "";

        const body = new URLSearchParams({
            customer_name: form.value.customer_name.trim(),
            phone: form.value.phone,
            address: form.value.address.trim(),
            city: form.value.city.trim(),
            state: form.value.state.trim(),
            pincode: form.value.pincode,
            payment_method: form.value.payment_method,
        });

        const response = await fetch(
            "/api/method/buy_new.api.place_order",
            {
                method: "POST",
                credentials: "include",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-Frappe-CSRF-Token": csrfToken,
                },
                body,
            }
        );

        const result = await response.json();

        if (!response.ok || result.exc) {
            throw new Error(
                result._server_messages
                    ? JSON.parse(result._server_messages).map((item) => {
                        try {
                            return JSON.parse(item).message;
                        } catch {
                            return item;
                        }
                    }).join(", ")
                    : result.exception || "Order could not be placed"
            );
        }

        const order = result.message;

        if (!order?.success) {
            throw new Error("Order could not be placed");
        }

        router.push({
            path: "/order-success",
            query: {
                order: order.order_id,
                payment: order.payment_status,
                method: order.payment_method,
                total: order.grand_total,
            },
        });
    } catch (error) {
        errorMessage.value = error.message || "Something went wrong";
    } finally {
        placingOrder.value = false;
    }
}

onMounted(loadCheckout);
</script>

<template>
    <div class="min-h-screen bg-gray-100 py-8">
        <div class="mx-auto max-w-7xl px-4">

            <!-- Header -->
            <div class="mb-7">
                <h1 class="text-2xl font-bold text-gray-900">Checkout</h1>
                <p class="mt-1 text-sm text-gray-500">
                    Complete your delivery and payment details
                </p>
            </div>

            <!-- Loading -->
            <div v-if="loading" class="py-20 text-center text-gray-500">
                Loading checkout...
            </div>

            <div v-else-if="cartItems.length" class="grid gap-6 lg:grid-cols-3">

                <!-- Left Side -->
                <div class="space-y-6 lg:col-span-2">

                    <!-- Delivery Address -->
                    <section class="rounded-xl bg-white p-5 shadow-sm sm:p-6">
                        <div class="mb-5 flex items-center gap-3">
                            <span
                                class="flex h-9 w-9 items-center justify-center rounded-full bg-pink-50 font-bold text-[#82103c]">
                                1
                            </span>
                            <div>
                                <h2 class="font-bold text-gray-900">Delivery Address</h2>
                                <p class="text-xs text-gray-500">Where should we deliver?</p>
                            </div>
                        </div>

                        <div class="grid gap-4 sm:grid-cols-2">
                            <div class="sm:col-span-2">
                                <label class="mb-1 block text-sm font-medium text-gray-700">
                                    Full Name *
                                </label>
                                <input v-model="form.customer_name" type="text" placeholder="Enter your full name"
                                    class="w-full rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-[#82103c] focus:ring-1 focus:ring-[#82103c]" />
                            </div>

                            <div class="sm:col-span-2">
                                <label class="mb-1 block text-sm font-medium text-gray-700">
                                    Mobile Number *
                                </label>
                                <input v-model="form.phone" type="tel" maxlength="10"
                                    placeholder="10 digit mobile number"
                                    class="w-full rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-[#82103c] focus:ring-1 focus:ring-[#82103c]" />
                            </div>

                            <div class="sm:col-span-2">
                                <label class="mb-1 block text-sm font-medium text-gray-700">
                                    Full Address *
                                </label>
                                <textarea v-model="form.address" rows="3"
                                    placeholder="House number, street, area, landmark..."
                                    class="w-full rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-[#82103c] focus:ring-1 focus:ring-[#82103c]"></textarea>
                            </div>

                            <div>
                                <label class="mb-1 block text-sm font-medium text-gray-700">
                                    City *
                                </label>
                                <input v-model="form.city" type="text" placeholder="City"
                                    class="w-full rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-[#82103c]" />
                            </div>

                            <div>
                                <label class="mb-1 block text-sm font-medium text-gray-700">
                                    State *
                                </label>
                                <input v-model="form.state" type="text" placeholder="State"
                                    class="w-full rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-[#82103c]" />
                            </div>

                            <div class="sm:col-span-2">
                                <label class="mb-1 block text-sm font-medium text-gray-700">
                                    Pincode *
                                </label>
                                <input v-model="form.pincode" type="text" maxlength="6" placeholder="6 digit pincode"
                                    class="w-full rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-[#82103c]" />
                            </div>
                        </div>
                    </section>

                    <!-- Payment Method -->
                    <section class="rounded-xl bg-white p-5 shadow-sm sm:p-6">
                        <div class="mb-5 flex items-center gap-3">
                            <span
                                class="flex h-9 w-9 items-center justify-center rounded-full bg-pink-50 font-bold text-[#82103c]">
                                2
                            </span>
                            <div>
                                <h2 class="font-bold text-gray-900">Payment Method</h2>
                                <p class="text-xs text-gray-500">Choose how you want to pay</p>
                            </div>
                        </div>

                        <div class="space-y-3">
                            <label v-for="method in paymentMethods" :key="method.value"
                                class="flex cursor-pointer items-center gap-3 rounded-lg border p-4 transition" :class="form.payment_method === method.value
                                    ? 'border-[#82103c] bg-pink-50'
                                    : 'border-gray-200 hover:border-gray-400'">
                                <input v-model="form.payment_method" type="radio" :value="method.value"
                                    class="h-4 w-4 accent-[#82103c]" />

                                <div class="min-w-0 flex-1">
                                    <p class="font-semibold text-gray-800">
                                        {{ method.label }}
                                    </p>
                                    <p class="text-xs text-gray-500">
                                        {{ method.description }}
                                    </p>
                                </div>

                                <span v-if="method.value !== 'COD'"
                                    class="rounded bg-amber-100 px-2 py-1 text-xs font-medium text-amber-700">
                                    Demo
                                </span>
                            </label>
                        </div>

                        <div class="mt-4 rounded-lg bg-amber-50 p-3 text-sm text-amber-800">
                            <strong>Demo mode:</strong>
                            Online payments are simulated. No real money will be charged.
                        </div>
                    </section>
                </div>

                <!-- Right Side -->
                <aside class="h-fit rounded-xl bg-white p-5 shadow-sm lg:sticky lg:top-5">
                    <h2 class="mb-5 text-lg font-bold text-gray-900">
                        Order Summary
                    </h2>

                    <div class="mb-5 space-y-4">
                        <div v-for="item in cartItems" :key="item.cart_item" class="flex gap-3">
                            <img :src="item.product_image || '/assets/buy_new/images/no-image.png'"
                                :alt="item.product_name"
                                class="h-16 w-16 rounded-lg border border-gray-100 object-contain" />

                            <div class="min-w-0 flex-1">
                                <p class="line-clamp-2 text-sm font-medium text-gray-800">
                                    {{ item.product_name }}
                                </p>
                                <p class="mt-1 text-xs text-gray-500">
                                    Qty: {{ item.quantity }}
                                </p>
                                <p class="mt-1 font-semibold text-[#82103c]">
                                    {{ formatPrice(item.amount) }}
                                </p>
                            </div>
                        </div>
                    </div>

                    <div class="space-y-3 border-t border-gray-100 pt-4 text-sm">
                        <div class="flex justify-between text-gray-600">
                            <span>Subtotal</span>
                            <span>{{ formatPrice(subtotal) }}</span>
                        </div>

                        <div class="flex justify-between text-gray-600">
                            <span>Delivery Charge</span>
                            <span>
                                {{ deliveryCharge === 0 ? "FREE" : formatPrice(deliveryCharge) }}
                            </span>
                        </div>

                        <div
                            class="flex justify-between border-t border-gray-100 pt-3 text-base font-bold text-gray-900">
                            <span>Total Amount</span>
                            <span>{{ formatPrice(grandTotal) }}</span>
                        </div>
                    </div>

                    <div class="mt-4 rounded-lg bg-gray-50 p-3 text-xs text-gray-600">
                        Selected: <strong>{{ selectedPayment?.label }}</strong>
                        <p v-if="form.payment_method === 'COD'" class="mt-1">
                            Pay when your order is delivered.
                        </p>
                        <p v-else class="mt-1">
                            This is a demo payment. No real transaction will happen.
                        </p>
                    </div>

                    <p v-if="errorMessage" class="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">
                        {{ errorMessage }}
                    </p>

                    <button @click="placeOrder" :disabled="placingOrder || loading"
                        class="mt-5 w-full rounded-lg bg-[#82103c] px-5 py-3.5 font-semibold text-white transition hover:bg-[#650d30] disabled:cursor-not-allowed disabled:opacity-60">
                        {{ placingOrder ? "Placing Order..." : "Place Order" }}
                    </button>

                    <p class="mt-3 text-center text-xs text-gray-400">
                        Your order details are securely submitted to BuyNew.
                    </p>
                </aside>
            </div>

            <div v-else class="rounded-xl bg-white p-10 text-center shadow-sm">
                <h2 class="text-xl font-bold text-gray-800">Your cart is empty</h2>
                <p class="mt-2 text-gray-500">Add products before checkout.</p>
                <button @click="router.push('/products')"
                    class="mt-5 rounded-lg bg-[#82103c] px-6 py-3 font-semibold text-white">
                    Continue Shopping
                </button>
            </div>
        </div>
    </div>
</template>
