<template>
    <div class="min-h-screen bg-gray-50">
        <div class="mx-auto max-w-7xl px-4 py-6">

            <!-- Mobile Products -->
            <section class="mb-8">
                <Mobile />
            </section>

            <!-- Fashion Products -->
            <section class="mb-8">
                <Fashion />
            </section>

        </div>
    </div>
</template>

<script setup>
import Mobile from '../components/Mobile.vue'
import Fashion from '../components/Fashion.vue'
</script>
