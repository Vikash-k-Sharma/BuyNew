<template>
    <div class="mx-auto w-full max-w-7xl overflow-hidden py-3">

        <!-- Advertisement Slider -->
        <div v-if="ads.length" class="w-full overflow-hidden">

            <div class="ad-track flex">

                <!-- Single Div for All Images -->
                <div v-for="(ad, index) in loopAds" :key="ad.name + '-' + index" class="ad-slide shrink-0 px-2">
                    <img :src="ad.ad_img" :alt="ad.name"
                        class="h-32 w-full rounded-xl object-cover sm:h-40 md:h-48 lg:h-56" />
                </div>

            </div>

        </div>

        <!-- Loading -->
        <div v-else-if="loading" class="py-10 text-center text-gray-500">
            Loading advertisements...
        </div>

        <!-- No Ads -->
        <div v-else class="py-10 text-center text-gray-500">
            No advertisements available.
        </div>

    </div>
</template>


<script setup>
import { ref, computed, onMounted } from 'vue'


// Advertisement Data
const ads = ref([])


// Loading State
const loading = ref(true)


// Duplicate Images for Infinite Loop
const loopAds = computed(() => [
    ...ads.value,
    ...ads.value
])


// Fetch Ads from Frappe Python API
const getAds = async () => {

    try {

        const response = await fetch(
            '/api/method/buy_new.api.get_ads',
            {
                method: 'GET',
                credentials: 'same-origin',
                headers: {
                    'Accept': 'application/json'
                }
            }
        )


        // Check API Response
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`)
        }


        // Get JSON Data
        const result = await response.json()


        // Store Advertisement Images
        ads.value = (result.message || []).filter(
            ad => ad.ad_img
        )



    } catch (error) {

        console.error('Advertisement Error:', error)

    } finally {

        loading.value = false

    }

}


// Fetch API When Component Loads
onMounted(() => {
    getAds()
})

</script>


<style scoped>
/* Main Slider */
.ad-track {
    width: max-content;
    animation: slide-ad 25s linear infinite;
}


/* Desktop: Two Images */
.ad-slide {
    width: calc((min(69vw, 80rem) - 2rem) / 2);
    box-sizing: border-box;
}


/* Right to Left Infinite Animation */
@keyframes slide-ad {

    from {
        transform: translateX(0);
    }

    to {
        transform: translateX(-50%);
    }

}


/* Tablet: Two Images */
@media (max-width: 1023px) {

    .ad-slide {
        width: calc((89vw - 2rem) / 2);
    }

}


/* Mobile: One Image */
@media (max-width: 767px) {

    .ad-slide {
        width: 89vw;
        padding-left: 8px;
        padding-right: 8px;
    }

}


/* Small Mobile */
@media (max-width: 380px) {

    .ad-slide img {
        height: 120px;
        border-radius: 8px;
    }

}


/* Pause on Hover */
.ad-track:hover {
    animation-play-state: paused;
}


/* Reduce Motion */
@media (prefers-reduced-motion: reduce) {

    .ad-track {
        animation: none;
    }

}
</style>
