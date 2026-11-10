<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink, RouterView } from 'vue-router'

const isLoggedIn = ref(false)
const fullName = ref('')

// Check Frappe Login Session
const checkLogin = async () => {
  try {
    const response = await fetch(
      '/api/method/frappe.auth.get_logged_user',
      {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
          Accept: 'application/json'
        }
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

// Update Navbar After Login
const handleAuthChange = () => {
  checkLogin()
}

onMounted(() => {
  checkLogin()

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
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">

    <!-- Navbar -->
    <nav class="sticky top-0 z-50 w-full border-b border-gray-200 bg-white shadow-sm">

      <div class="mx-auto max-w-7xl px-4 py-3 sm:px-6">

        <!-- Navbar First Row -->
        <div class="flex items-center justify-between gap-3 sm:gap-6">

          <!-- Logo -->
          <RouterLink to="/home" class="flex shrink-0 items-center">
            <img src="./assets/byn.png" alt="BuyNew Logo" class="h-9 w-auto object-contain sm:h-12" />
          </RouterLink>

          <!-- Desktop Search -->
          <div class="hidden h-[42px] w-full max-w-xl flex-1 md:flex">

            <div
              class="flex w-full items-center overflow-hidden rounded-lg border border-transparent bg-gray-50 transition focus-within:border-blue-600">

              <input type="text" placeholder="Search for products, brands and more..."
                class="w-full min-w-0 border-none bg-transparent px-4 py-3 text-sm text-gray-700 outline-none focus:border-none focus:outline-none focus:ring-0" />

              <button type="button" class="bg-blue-600 px-5 py-3 text-white transition hover:bg-blue-700">
                <i class="fas fa-search"></i>
              </button>

            </div>
          </div>

          <!-- Right Side -->
          <div class="flex shrink-0 items-center gap-4 sm:gap-5">

            <!-- Cart -->
            <RouterLink to="/cart" class="text-lg text-gray-700 transition hover:text-blue-600 sm:text-xl"
              title="Shopping Cart">
              <i class="fas fa-shopping-cart"></i>
            </RouterLink>

            <!-- Guest: Login and Register -->
            <template v-if="!isLoggedIn">

              <RouterLink to="/login"
                class="hidden text-sm font-medium text-gray-700 transition hover:text-blue-600 sm:block">
                Login
              </RouterLink>

              <RouterLink to="/register"
                class="rounded-lg bg-blue-600 px-3 py-2.5 text-xs font-semibold text-white shadow-sm transition hover:bg-blue-700 sm:px-5 sm:text-sm">
                Register
              </RouterLink>

            </template>

            <!-- Logged In: Profile Icon -->
            <template v-else>

              <RouterLink to="/profilepage" :title="fullName || 'My Profile'"
                class="flex h-10 w-10 items-center justify-center rounded-full border border-gray-200 bg-blue-50 text-lg text-blue-600 transition hover:bg-blue-100">
                <i class="fas fa-user"></i>
              </RouterLink>

            </template>

          </div>

        </div>

        <!-- Mobile Search -->
        <div class="mt-3 w-full md:hidden">

          <div
            class="flex w-full items-center overflow-hidden rounded-lg border border-transparent bg-gray-50 transition focus-within:border-blue-600">

            <input type="text" placeholder="Search products..."
              class="w-full min-w-0 border-none bg-transparent px-3 py-2.5 text-sm text-gray-700 outline-none focus:border-none focus:outline-none focus:ring-0" />

            <button type="button" class="bg-blue-600 px-5 py-2.5 text-white transition hover:bg-blue-700">
              <i class="fas fa-search"></i>
            </button>

          </div>

        </div>

      </div>
    </nav>

    <!-- Page Content -->
    <main class="mx-auto max-w-7xl px-4 py-6 sm:px-6 sm:py-8">
      <RouterView />
    </main>

  </div>
</template>
