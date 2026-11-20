<template>
    <section class="mx-auto w-full max-w-[1450px] px-3 py-3 sm:px-5">

        <div class="buynew-ads-layout">

            <!-- Main Banner -->
            <div class="buynew-main-banner">

                <div v-if="(loading && !currentMainAd) || (currentMainAd && mainImageLoadedUrl !== currentMainAd.ad_img)"
                    class="buynew-image-skeleton" role="status" aria-label="Loading advertisement image"></div>

                <Transition name="ad-fade">
                    <img v-if="currentMainAd?.ad_img" :key="currentMainAd.ad_img" :src="currentMainAd.ad_img"
                        :alt="currentMainAd.name || 'Advertisement'"
                        :class="['buynew-main-image', { 'is-loaded': mainImageLoadedUrl === currentMainAd.ad_img }]"
                        @load="handleMainImageLoad" @error="handleImageError" />
                </Transition>

                <div v-if="apiError && !currentMainAd" class="buynew-ad-message">
                    {{ apiError }}
                </div>

                <div v-else-if="!loading && !currentMainAd" class="buynew-ad-message">
                    No advertisements available.
                </div>

                <!-- Previous -->
                <button v-if="mainAds.length > 1" type="button" class="buynew-ad-arrow left-3" @click="previousSlide">
                    <i class="fas fa-chevron-left"></i>
                </button>

                <!-- Next -->
                <button v-if="mainAds.length > 1" type="button" class="buynew-ad-arrow right-3" @click="nextSlide">
                    <i class="fas fa-chevron-right"></i>
                </button>

                <!-- Dots -->
                <div v-if="mainAds.length > 1" class="buynew-ad-dots">
                    <button v-for="(ad, index) in mainAds" :key="ad.name || index" type="button"
                        :class="currentIndex === index ? 'active-dot' : 'normal-dot'"
                        @click="goToSlide(index)"></button>
                </div>

            </div>

            <!-- Side Banner -->
            <div class="buynew-side-banner">
                <div v-if="!sideImageLoaded && !sideImageFailed" class="buynew-image-skeleton" role="status"
                    aria-label="Loading advertisement image"></div>
                <img v-if="!sideImageFailed" :src="bigFashImage" alt="Big Fashion Advertisement"
                    :class="['buynew-side-image', { 'is-loaded': sideImageLoaded }]"
                    @load="sideImageLoaded = true" @error="handleSideImageError" />
                <div v-else class="buynew-ad-message">Advertisement unavailable.</div>
            </div>

        </div>

    </section>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import bigFashImage from '../assets/BigFash.webp'

// Advertisement data
const ads = ref([])
const loading = ref(true)
const apiError = ref('')
const currentIndex = ref(0)
const mainImageLoadedUrl = ref('')
const sideImageLoaded = ref(false)
const sideImageFailed = ref(false)

let slideTimer = null

// Main banner advertisements
const mainAds = computed(() => {
    if (ads.value.length > 1) {
        return ads.value.slice(0, -1)
    }

    return ads.value
})

// Current banner
const currentMainAd = computed(() => {
    return mainAds.value[currentIndex.value] || null
})

// Preload next image
const preloadNextSlide = () => {
    if (mainAds.value.length < 2) return

    const nextIndex =
        (currentIndex.value + 1) % mainAds.value.length

    const imageUrl = mainAds.value[nextIndex]?.ad_img

    if (imageUrl) {
        const image = new Image()
        image.src = imageUrl
    }
}

// Next slide
const nextSlide = () => {
    if (mainAds.value.length <= 1) return

    currentIndex.value =
        (currentIndex.value + 1) % mainAds.value.length

    startAutoSlide()
}

// Previous slide
const previousSlide = () => {
    if (mainAds.value.length <= 1) return

    currentIndex.value =
        (currentIndex.value - 1 + mainAds.value.length) %
        mainAds.value.length

    startAutoSlide()
}

// Select slide
const goToSlide = (index) => {
    currentIndex.value = index
    startAutoSlide()
}

// Stop slider
const stopAutoSlide = () => {
    if (slideTimer) {
        clearInterval(slideTimer)
        slideTimer = null
    }
}

// Start slider
const startAutoSlide = () => {
    stopAutoSlide()

    if (mainAds.value.length > 1) {
        preloadNextSlide()

        slideTimer = setInterval(() => {
            currentIndex.value =
                (currentIndex.value + 1) % mainAds.value.length

            preloadNextSlide()
        }, 7000)
    }
}

// Main image error
const handleMainImageLoad = (event) => {
    mainImageLoadedUrl.value = event.currentTarget.getAttribute('src') || ''
}

const handleImageError = (event) => {
    const failedImage = event.currentTarget.getAttribute('src')
    console.error('Main banner image failed:', event.currentTarget.src)

    if (!failedImage) return

    if (mainImageLoadedUrl.value === failedImage) {
        mainImageLoadedUrl.value = ''
    }

    ads.value = ads.value.filter(ad => ad.ad_img !== failedImage)
    currentIndex.value = 0
    startAutoSlide()
}

// Side image error
const handleSideImageError = (event) => {
    console.error('Side banner image failed:', event.target.src)
    sideImageFailed.value = true
}

// Fetch advertisements
const getAds = async () => {
    loading.value = true
    apiError.value = ''

    try {
        const response = await fetch(
            '/api/method/buy_new.api.get_ads',
            {
                method: 'GET',
                credentials: 'same-origin',
                headers: {
                    Accept: 'application/json'
                }
            }
        )

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`)
        }

        const result = await response.json()

        if (result.exc) {
            throw new Error('Frappe API error. Check server logs.')
        }

        if (!Array.isArray(result.message)) {
            throw new Error('Invalid advertisements response.')
        }

        ads.value = result.message.filter(ad => {
            return ad && ad.ad_img
        })

        currentIndex.value = 0

        startAutoSlide()

    } catch (error) {
        console.error('Advertisement loading error:', error)
        apiError.value = error.message || 'Unable to load advertisements.'

    } finally {
        loading.value = false
    }
}

onMounted(() => {
    getAds()
})

onUnmounted(() => {
    stopAutoSlide()
})
</script>

<style scoped>
/* Banner layout */
.buynew-ads-layout {
    display: flex !important;
    flex-direction: row !important;
    align-items: stretch;
    gap: 12px;
    width: 100%;
    height: 216px;
}

/* Main banner */
.buynew-main-banner {
    position: relative;
    flex: 3 1 0 !important;
    width: 75%;
    min-width: 0;
    height: 100%;
    overflow: hidden;
    border-radius: 12px;
    background: #f3f4f6;
}

.buynew-main-image {
    position: relative;
    z-index: 2;
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center;
    opacity: 0;
    transition: opacity .25s ease;
}

.buynew-main-image.is-loaded,
.buynew-side-image.is-loaded {
    opacity: 1;
}

.buynew-image-skeleton {
    position: absolute;
    inset: 0;
    z-index: 1;
    overflow: hidden;
    background: linear-gradient(100deg, #e5e7eb 25%, #f3f4f6 45%, #e5e7eb 65%);
    background-size: 200% 100%;
    animation: buynew-skeleton-shimmer 1.25s ease-in-out infinite;
}

@keyframes buynew-skeleton-shimmer {
    from { background-position: 100% 0; }
    to { background-position: -100% 0; }
}

/* Side banner */
.buynew-side-banner {
    display: block !important;
    position: relative;
    flex: 1 1 0 !important;
    width: 25%;
    min-width: 0;
    height: 100%;
    overflow: hidden;
    border-radius: 12px;
    background: #f3f4f6;
    visibility: visible !important;
    opacity: 1 !important;
}

.buynew-side-image {
    position: relative;
    z-index: 2;
    display: block !important;
    width: 100% !important;
    height: 100% !important;
    max-width: none;
    object-fit: cover;
    object-position: center;
    opacity: 0;
    transition: opacity .25s ease;
}

/* Fade animation */
.ad-fade-enter-active,
.ad-fade-leave-active {
    transition: opacity .45s ease;
}

.ad-fade-enter-from,
.ad-fade-leave-to {
    opacity: 0;
}

.ad-fade-leave-active {
    position: absolute;
    inset: 0;
}

/* Arrows */
.buynew-ad-arrow {
    position: absolute;
    top: 50%;
    z-index: 5;
    display: flex;
    width: 36px;
    height: 36px;
    align-items: center;
    justify-content: center;
    transform: translateY(-50%);
    border: none;
    border-radius: 50%;
    background: rgba(255, 255, 255, .85);
    color: #222;
    cursor: pointer;
}

.buynew-ad-arrow:hover {
    background: #fff;
}

/* Dots */
.buynew-ad-dots {
    position: absolute;
    bottom: 10px;
    left: 50%;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 5px 10px;
    transform: translateX(-50%);
    border-radius: 20px;
    background: rgba(0, 0, 0, .2);
}

.active-dot {
    width: 11px;
    height: 11px;
    border: none;
    border-radius: 50%;
    background: #fff;
    cursor: pointer;
}

.normal-dot {
    width: 10px;
    height: 10px;
    border: none;
    border-radius: 50%;
    background: rgba(255, 255, 255, .45);
    cursor: pointer;
}

/* Messages */
.buynew-ad-message {
    display: flex;
    width: 100%;
    height: 100%;
    align-items: center;
    justify-content: center;
    gap: 10px;
    color: #6b7280;
    font-size: 14px;
}

/* Tablet */
@media (max-width: 1023px) {
    .buynew-ads-layout {
        height: 180px;
    }
}

/* Mobile */
@media (max-width: 767px) {
    .buynew-ads-layout {
        flex-direction: column !important;
        height: auto;
        gap: 10px;
    }

    .buynew-main-banner {
        flex: none !important;
        width: 100%;
        height: 155px;
    }

    .buynew-side-banner {
        display: none !important;
    }

    .buynew-ad-arrow {
        width: 30px;
        height: 30px;
        font-size: 12px;
    }
}

/* Small mobile */
@media (max-width: 380px) {
    .buynew-main-banner {
        height: 125px;
    }

}

@media (prefers-reduced-motion: reduce) {

    .ad-fade-enter-active,
    .ad-fade-leave-active {
        transition: none;
    }
}
</style>
