<script setup>
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();

const orderId = route.query.order || "";
const paymentStatus = route.query.payment || "Pending";
const paymentMethod = route.query.method || "COD";
const total = Number(route.query.total || 0);

const formatPrice = (price) =>
    new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 2,
    }).format(price);
</script>

<template>
    <div class="flex min-h-screen items-center justify-center bg-gray-100 px-4 py-10">
        <div class="w-full max-w-lg rounded-2xl bg-white p-8 text-center shadow-sm">

            <div
                class="mx-auto mb-5 flex h-20 w-20 items-center justify-center rounded-full bg-green-100 text-4xl text-green-600">
                ✓
            </div>

            <h1 class="text-2xl font-bold text-gray-900">
                Order Placed Successfully!
            </h1>

            <p class="mt-2 text-gray-500">
                Thank you for shopping with BuyNew.
            </p>

            <div class="my-7 rounded-xl bg-gray-50 p-5 text-left">
                <div class="flex justify-between gap-3 py-2 text-sm">
                    <span class="text-gray-500">Order ID</span>
                    <strong class="text-gray-900">{{ orderId }}</strong>
                </div>

                <div class="flex justify-between gap-3 py-2 text-sm">
                    <span class="text-gray-500">Payment Method</span>
                    <strong class="text-gray-900">{{ paymentMethod }}</strong>
                </div>

                <div class="flex justify-between gap-3 py-2 text-sm">
                    <span class="text-gray-500">Payment Status</span>
                    <strong :class="paymentStatus === 'Pending' ? 'text-amber-600' : 'text-green-600'">
                        {{ paymentStatus }}
                    </strong>
                </div>

                <div class="mt-3 flex justify-between border-t pt-4">
                    <span class="font-semibold text-gray-700">Total Paid / Payable</span>
                    <strong class="text-lg text-[#82103c]">
                        {{ formatPrice(total) }}
                    </strong>
                </div>
            </div>

            <p class="mb-5 text-xs text-gray-500">
                Online payment status is simulated for demo purposes only.
            </p>

            <button @click="router.push('/products')"
                class="w-full rounded-lg bg-[#82103c] px-5 py-3 font-semibold text-white hover:bg-[#650d30]">
                Continue Shopping
            </button>
        </div>
    </div>
</template>
