<template>
  <div class="min-h-screen bg-gray-50">

    <!-- Navbar -->
    <nav class="sticky top-0 z-50 w-full border-b border-gray-200 bg-white shadow-sm">

      <div class="mx-auto max-w-7xl px-4 py-3 sm:px-6">

        <!-- Navbar First Row -->
        <div class="flex items-center justify-between gap-3 sm:gap-6">

          <!-- Logo -->
          <RouterLink to="/" class="flex shrink-0 items-center">
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

            <!-- Login -->
            <RouterLink to="/login"
              class="hidden text-sm font-medium text-gray-700 transition hover:text-blue-600 sm:block">
              Login
            </RouterLink>

            <!-- Register -->
            <RouterLink to="/register"
              class="rounded-lg bg-blue-600 px-3 py-2.5 text-xs font-semibold text-white shadow-sm transition hover:bg-blue-700 sm:px-5 sm:text-sm">
              Register
            </RouterLink>

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
