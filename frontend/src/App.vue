<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute, RouterLink, RouterView } from 'vue-router'

const router = useRouter()
const route = useRoute()

const isLoggedIn = ref(false)
const fullName = ref('')

const searchQuery = ref('')
const allProducts = ref([])
const showSuggestions = ref(false)

// Check Login Session
const checkLogin = async () => {
  try {
    const response = await fetch(
      '/api/method/frappe.auth.get_logged_user',
      {
        credentials: 'same-origin',
        headers: { Accept: 'application/json' }
      }
    )

    const data = await response.json()

    isLoggedIn.value =
      response.ok &&
      data.message &&
      data.message !== 'Guest'

    fullName.value = isLoggedIn.value ? data.message : ''

  } catch (error) {
    console.error('Login Check Error:', error)
    isLoggedIn.value = false
    fullName.value = ''
  }
}

// Fetch Products For Suggestions
const getSearchProducts = async () => {
  try {
    const response = await fetch(
      '/api/method/buy_new.api.get_products',
      {
        method: 'GET',
        credentials: 'same-origin',
        headers: { Accept: 'application/json' }
      }
    )

    const result = await response.json()

    if (!response.ok || result.exc) {
      throw new Error('Unable to fetch search products')
    }

    allProducts.value = result.message || []

  } catch (error) {
    console.error('Search Products Error:', error)
  }
}

// Filter Suggestions
const searchSuggestions = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()

  if (!query) return []

  return allProducts.value
    .filter(product => {
      const searchableText = [
        product.products_name,
        product.products_code,
        product.brand,
        product.category,
        product.short_description
      ]
        .map(value => String(value || '').toLowerCase())

      return searchableText.some(value =>
        value.includes(query)
      )
    })
    .sort((a, b) => {
      const nameA = String(a.products_name || '').toLowerCase()
      const nameB = String(b.products_name || '').toLowerCase()

      const startsA = nameA.startsWith(query) ? 0 : 1
      const startsB = nameB.startsWith(query) ? 0 : 1

      return startsA - startsB
    })
    .slice(0, 7)
})

// Search All Products
const searchProducts = () => {
  const query = searchQuery.value.trim()

  showSuggestions.value = false

  router.push({
    path: '/products',
    query: query ? { search: query } : {}
  })
}

// Select Suggestion
const selectSuggestion = (product) => {
  searchQuery.value = product.products_name || ''
  searchProducts()
}

// Close Suggestions
let blurTimer = null

const hideSuggestions = () => {
  clearTimeout(blurTimer)

  blurTimer = setTimeout(() => {
    showSuggestions.value = false
  }, 180)
}

// Sync Search With URL
watch(
  () => route.query.search,
  value => {
    searchQuery.value =
      typeof value === 'string' ? value : ''

    showSuggestions.value = false
  },
  { immediate: true }
)

// Navbar Update After Login
const handleAuthChange = () => {
  checkLogin()
}

onMounted(() => {
  checkLogin()
  getSearchProducts()

  window.addEventListener(
    'buynew-auth-changed',
    handleAuthChange
  )
})

onUnmounted(() => {
  window.removeEventListener(
    'buynew-auth-changed',
    handleAuthChange
  )

  clearTimeout(blurTimer)
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">

    <!-- Navbar -->
    <nav class="sticky top-0 z-50 w-full border-b border-gray-200 bg-white shadow-sm">

      <div class="mx-auto max-w-7xl px-4 py-3 sm:px-6">

        <!-- First Row -->
        <div class="flex items-center justify-between gap-3 sm:gap-6">

          <!-- Logo -->
          <RouterLink to="/home" class="flex shrink-0 items-center">
            <img src="./assets/byn.png" alt="BuyNew Logo" class="h-9 w-auto object-contain sm:h-12" />
          </RouterLink>

          <!-- Desktop Search -->
          <form @submit.prevent="searchProducts" class="hidden h-[42px] w-full max-w-xl flex-1 md:flex">
            <div class="relative w-full">

              <div
                class="flex w-full items-center overflow-hidden rounded-lg border border-gray-200 bg-gray-50 focus-within:border-[#82103c]">

                <input v-model="searchQuery" type="search" placeholder="Search for products, brands and more..."
                  autocomplete="off" @focus="showSuggestions = true" @input="showSuggestions = true"
                  @blur="hideSuggestions"
                  class="w-full min-w-0 border-none bg-transparent px-4 py-3 text-sm text-gray-700 outline-none focus:ring-0" />

                <button type="submit" class="bg-[#82103c] px-5 py-3 text-white transition hover:bg-[#6b0b30]">
                  <i class="fas fa-search"></i>
                </button>

              </div>

              <!-- Desktop Suggestions -->
              <div v-if="showSuggestions && searchQuery.trim()"
                class="absolute left-0 right-0 top-full z-[100] mt-1 max-h-[420px] overflow-y-auto rounded-xl border border-gray-200 bg-white shadow-xl">

                <button v-for="product in searchSuggestions" :key="product.name" type="button"
                  @mousedown.prevent="selectSuggestion(product)"
                  class="flex w-full items-center gap-4 border-b border-gray-100 px-4 py-3 text-left transition hover:bg-gray-50">

                  <div class="flex h-14 w-14 shrink-0 items-center justify-center rounded-lg bg-gray-50">
                    <img v-if="product.product_image" :src="product.product_image" :alt="product.products_name"
                      class="h-full w-full object-contain p-1" />
                    <i v-else class="fas fa-image text-xl text-gray-300"></i>
                  </div>

                  <div class="min-w-0 flex-1">
                    <p class="truncate text-sm font-semibold text-gray-800">
                      {{ product.products_name }}
                    </p>

                    <p class="mt-1 text-xs text-gray-500">
                      {{ product.brand || product.category || 'Product' }}
                    </p>

                    <p class="mt-1 text-sm font-bold text-[#82103c]">
                      ₹{{ Number(product.selling_price || 0).toLocaleString('en-IN') }}
                    </p>
                  </div>

                  <i class="fas fa-arrow-up-left text-gray-400"></i>

                </button>

                <!-- No Suggestions -->
                <div v-if="searchSuggestions.length === 0" class="px-4 py-5 text-center text-sm text-gray-500">
                  No matching products found.
                </div>

                <!-- View All -->
                <button type="submit"
                  class="flex w-full items-center gap-3 bg-gray-50 px-4 py-3 text-left text-sm font-semibold text-[#82103c] hover:bg-gray-100">
                  <i class="fas fa-search"></i>
                  Search for "{{ searchQuery }}"
                  <i class="fas fa-arrow-right ml-auto"></i>
                </button>

              </div>

            </div>
          </form>

          <!-- Right Side -->
          <div class="flex shrink-0 items-center gap-4 sm:gap-5">

            <!-- Cart -->
            <RouterLink to="/cart" class="text-lg text-gray-700 transition hover:text-[#82103c] sm:text-xl"
              title="Shopping Cart">
              <i class="fas fa-shopping-cart"></i>
            </RouterLink>

            <!-- Guest -->
            <template v-if="!isLoggedIn">

              <RouterLink to="/login" class="hidden text-sm font-medium text-gray-700 hover:text-[#82103c] sm:block">
                Login
              </RouterLink>

              <RouterLink to="/register"
                class="rounded-lg bg-[#82103c] px-3 py-2.5 text-xs font-semibold text-white hover:bg-[#6b0b30] sm:px-5 sm:text-sm">
                Register
              </RouterLink>

            </template>

            <!-- Logged In -->
            <template v-else>

              <RouterLink to="/profilepage" :title="fullName || 'My Profile'"
                class="flex h-10 w-10 items-center justify-center rounded-full border border-gray-200 bg-[#82103c]/5 text-lg text-[#82103c] hover:bg-[#82103c]/10">
                <i class="fas fa-user"></i>
              </RouterLink>

            </template>

          </div>

        </div>

        <!-- Mobile Search -->
        <form @submit.prevent="searchProducts" class="mt-3 w-full md:hidden">
          <div class="relative w-full">

            <div
              class="flex w-full items-center overflow-hidden rounded-lg border border-gray-200 bg-gray-50 focus-within:border-[#82103c]">

              <input v-model="searchQuery" type="search" placeholder="Search products..." autocomplete="off"
                @focus="showSuggestions = true" @input="showSuggestions = true" @blur="hideSuggestions"
                class="w-full min-w-0 border-none bg-transparent px-3 py-2.5 text-sm text-gray-700 outline-none focus:ring-0" />

              <button type="submit" class="bg-[#82103c] px-5 py-2.5 text-white hover:bg-[#6b0b30]">
                <i class="fas fa-search"></i>
              </button>

            </div>

            <!-- Mobile Suggestions -->
            <div v-if="showSuggestions && searchQuery.trim()"
              class="absolute left-0 right-0 top-full z-[100] mt-1 max-h-[65vh] overflow-y-auto rounded-xl border border-gray-200 bg-white shadow-xl">

              <button v-for="product in searchSuggestions" :key="product.name" type="button"
                @mousedown.prevent="selectSuggestion(product)"
                class="flex w-full items-center gap-3 border-b border-gray-100 px-3 py-3 text-left hover:bg-gray-50">

                <div class="flex h-14 w-14 shrink-0 items-center justify-center rounded-lg bg-gray-50">
                  <img v-if="product.product_image" :src="product.product_image" :alt="product.products_name"
                    class="h-full w-full object-contain p-1" />
                  <i v-else class="fas fa-image text-xl text-gray-300"></i>
                </div>

                <div class="min-w-0 flex-1">
                  <p class="truncate text-sm font-semibold text-gray-800">
                    {{ product.products_name }}
                  </p>

                  <p class="mt-1 text-xs text-gray-500">
                    {{ product.brand || product.category || 'Product' }}
                  </p>

                  <p class="mt-1 text-sm font-bold text-[#82103c]">
                    ₹{{ Number(product.selling_price || 0).toLocaleString('en-IN') }}
                  </p>
                </div>

                <i class="fas fa-arrow-up-left text-gray-400"></i>

              </button>

              <div v-if="searchSuggestions.length === 0" class="px-4 py-5 text-center text-sm text-gray-500">
                No matching products found.
              </div>

              <button type="submit"
                class="flex w-full items-center gap-3 bg-gray-50 px-4 py-3 text-left text-sm font-semibold text-[#82103c]">
                <i class="fas fa-search"></i>
                Search for "{{ searchQuery }}"
                <i class="fas fa-arrow-right ml-auto"></i>
              </button>

            </div>

          </div>
        </form>

      </div>
    </nav>

    <!-- Page Content -->
    <main class="mx-auto max-w-7xl px-4 py-6 sm:px-6 sm:py-8">
      <RouterView />
    </main>

  </div>
</template>
