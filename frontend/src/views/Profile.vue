<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const loading = ref(true)
const saving = ref(false)
const error = ref('')
const editError = ref('')
const editing = ref(false)
const showLogoutConfirm = ref(false)
const profileImageInput = ref(null)
const selectedProfileImage = ref(null)
const profileImagePreview = ref('')
const profileImagePreviewUrl = ref('')

const user = ref({
    name: '',
    full_name: '',
    email: '',
    mobile_no: '',
    user_image: ''
})

const editForm = ref({
    full_name: '',
    mobile_no: ''
})

const primaryColor = '#82103c'

const menuItems = [
    { label: 'My Profile', icon: 'fas fa-user', active: true },
    { label: 'My Orders', icon: 'fas fa-box-open' }
]

const getCsrfToken = () => (
    document.querySelector('meta[name="csrf-token"]')?.content ||
    window.frappe?.csrf_token ||
    ''
)

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
            console.error(err)
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

// Load Profile
const getProfile = async () => {
    loading.value = true
    error.value = ''

    try {
        const response = await fetch(
            '/api/method/buy_new.api.get_current_user_profile',
            {
                method: 'GET',
                credentials: 'same-origin',
                headers: {
                    Accept: 'application/json'
                }
            }
        )

        const result = await readApiResponse(response)

        if (!response.ok || result.exc || result.exception) {
            const details = `${result.exc_type || ''} ${result.exception || ''} ${result.message || ''}`

            if (
                [401, 403].includes(response.status) ||
                /PermissionError|Please login/i.test(details)
            ) {
                await router.replace('/login')
                return
            }

            throw new Error(
                getApiErrorMessage(result, 'Unable to load profile.')
            )
        }

        if (!result.message || typeof result.message !== 'object') {
            throw new Error('Profile details not available.')
        }

        user.value = result.message

    } catch (err) {
        console.error('Profile Error:', err)
        error.value = err.message || 'Unable to load profile.'
    } finally {
        loading.value = false
    }
}

// Open Edit
const openEdit = () => {
    editForm.value = {
        full_name: user.value.full_name || '',
        mobile_no: user.value.mobile_no || ''
    }

    clearProfileImagePreview()
    selectedProfileImage.value = null
    profileImagePreview.value = user.value.user_image || ''
    if (profileImageInput.value) profileImageInput.value.value = ''
    editError.value = ''
    editing.value = true
}

const clearProfileImagePreview = () => {
    if (profileImagePreviewUrl.value) {
        URL.revokeObjectURL(profileImagePreviewUrl.value)
        profileImagePreviewUrl.value = ''
    }
}

const chooseProfileImage = () => {
    profileImageInput.value?.click()
}

const handleProfileImageChange = (event) => {
    const file = event.target.files?.[0]
    if (!file) return

    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif']
    if (!allowedTypes.includes(file.type)) {
        editError.value = 'Please choose a JPG, PNG or GIF image.'
        event.target.value = ''
        return
    }

    if (file.size > 5 * 1024 * 1024) {
        editError.value = 'Profile image must be 5 MB or smaller.'
        event.target.value = ''
        return
    }

    clearProfileImagePreview()
    selectedProfileImage.value = file
    profileImagePreviewUrl.value = URL.createObjectURL(file)
    profileImagePreview.value = profileImagePreviewUrl.value
    editError.value = ''
}

// Close Edit
const closeEdit = () => {
    editing.value = false
    editError.value = ''
    selectedProfileImage.value = null
    profileImagePreview.value = ''
    clearProfileImagePreview()
    if (profileImageInput.value) profileImageInput.value.value = ''
}

const uploadSelectedProfileImage = async () => {
    const formData = new FormData()
    formData.append('file', selectedProfileImage.value)

    const response = await fetch(
        '/api/method/buy_new.api.update_current_user_profile_image',
        {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                Accept: 'application/json',
                'X-Frappe-CSRF-Token': getCsrfToken()
            },
            body: formData
        }
    )

    const result = await readApiResponse(response)
    if (!response.ok || result.exc || result.exception || !result.message?.user_image) {
        throw new Error(
            getApiErrorMessage(result, 'Unable to update profile photo.')
        )
    }

    return result.message.user_image
}

// Update Profile
const saveProfile = async () => {
    if (!editForm.value.full_name.trim()) {
        editError.value = 'Please enter your full name.'
        return
    }

    if (!user.value.name) {
        editError.value = 'User information not available.'
        return
    }

    saving.value = true
    editError.value = ''
    let profileDetailsSaved = false

    try {
        const response = await fetch(
            '/api/method/frappe.client.set_value',
            {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Frappe-CSRF-Token': getCsrfToken()
                },
                body: JSON.stringify({
                    doctype: 'User',
                    name: user.value.name,
                    fieldname: {
                        full_name: editForm.value.full_name.trim(),
                        mobile_no: editForm.value.mobile_no.trim()
                    }
                })
            }
        )

        const result = await readApiResponse(response)

        if (!response.ok || result.exc || result.exception) {
            throw new Error(
                getApiErrorMessage(result, 'Unable to update profile.')
            )
        }

        user.value = {
            ...user.value,
            full_name: editForm.value.full_name.trim(),
            mobile_no: editForm.value.mobile_no.trim()
        }
        profileDetailsSaved = true

        if (selectedProfileImage.value) {
            user.value = {
                ...user.value,
                user_image: await uploadSelectedProfileImage()
            }
        }

        window.dispatchEvent(new Event('buynew-profile-updated'))

        closeEdit()

    } catch (err) {
        console.error('Update Profile Error:', err)
        if (profileDetailsSaved) {
            window.dispatchEvent(new Event('buynew-profile-updated'))
        }
        editError.value = err.message || 'Unable to update profile.'
    } finally {
        saving.value = false
    }
}

// Logout
const logout = async () => {
    error.value = ''

    try {
        const response = await fetch('/api/method/logout', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'X-Frappe-CSRF-Token': getCsrfToken()
            }
        })

        const result = await readApiResponse(response)

        if (!response.ok || result.exc || result.exception) {
            throw new Error(
                getApiErrorMessage(result, 'Logout failed.')
            )
        }

        window.dispatchEvent(new Event('buynew-auth-changed'))

        await router.replace('/home')

    } catch (err) {
        console.error('Logout Error:', err)
        error.value = err.message || 'Unable to logout.'
    }
}

// Confirm Logout
const confirmLogout = async () => {
    showLogoutConfirm.value = false
    await logout()
}

onMounted(() => {
    getProfile()
})

onUnmounted(() => {
    clearProfileImagePreview()
})
</script>

<template>
    <div class="min-h-screen bg-slate-50 px-3 py-5 sm:px-5 sm:py-8">

        <div class="mx-auto max-w-7xl">

            <!-- Page Heading -->
            <div class="mb-7 flex items-center gap-4">
                <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-pink-100">
                    <i class="fas fa-user text-2xl text-[#82103c]"></i>
                </div>

                <div>
                    <h1 class="text-2xl font-bold text-gray-900 sm:text-3xl">
                        My Profile
                    </h1>

                    <p class="mt-1 text-xs text-gray-500 sm:text-sm">
                        Manage your BuyNew account information, security and preferences.
                    </p>
                </div>
            </div>

            <!-- Loading -->
            <div v-if="loading" class="rounded-2xl border border-gray-100 bg-white p-12 text-center shadow-sm">
                <i class="fas fa-spinner fa-spin text-3xl text-[#82103c]"></i>

                <p class="mt-3 text-sm text-gray-500">
                    Loading profile...
                </p>
            </div>

            <!-- Error -->
            <div v-else-if="error" class="rounded-2xl border border-red-200 bg-white p-8 text-center">
                <i class="fas fa-exclamation-circle text-3xl text-red-500"></i>

                <p class="mt-3 text-sm text-red-600">
                    {{ error }}
                </p>

                <button @click="getProfile"
                    class="mt-4 rounded-lg bg-[#82103c] px-6 py-2.5 text-sm font-semibold text-white hover:bg-[#6b0b30]">
                    Try Again
                </button>
            </div>

            <!-- Profile Layout -->
            <div v-else
                class="grid grid-cols-1 items-stretch gap-5 md:grid-cols-[210px_minmax(250px,310px)_minmax(0,1fr)] lg:gap-6">

                <!-- Sidebar -->
                <aside class="h-fit rounded-2xl border border-gray-100 bg-white p-3 shadow-sm">

                    <nav class="grid grid-cols-2 gap-2 md:flex md:flex-col">

                        <div v-for="item in menuItems" :key="item.label" :class="[
                            'flex min-w-0 items-center gap-3 rounded-lg px-3 py-3 text-left text-sm font-medium transition',
                            item.active
                                ? 'bg-[#a7194d] text-white shadow-sm'
                                : 'text-gray-700 hover:bg-gray-50'
                        ]">
                            <i :class="[item.icon, 'w-5 shrink-0 text-center text-lg']"></i>

                            <span class="truncate">
                                {{ item.label }}
                            </span>
                        </div>

                    </nav>

                    <div class="my-3 border-t border-gray-200"></div>

                    <!-- Logout Button -->
                    <button type="button" @click="showLogoutConfirm = true"
                        class="hidden w-full items-center gap-3 rounded-lg px-3 py-3 text-sm font-semibold text-red-600 transition hover:bg-red-50 md:flex">

                        <i class="fas fa-sign-out-alt w-5 text-center text-lg"></i>
                        Logout
                    </button>

                </aside>

                <!-- Profile Card -->
                <section class="overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-sm">

                    <!-- Cover -->
                    <div
                        class="relative h-32 overflow-hidden bg-gradient-to-br from-[#82103c] via-[#a7194d] to-[#58102d]">

                        <div class="absolute -left-10 -top-16 h-40 w-64 rounded-full bg-white/10"></div>

                        <div class="absolute -right-12 top-10 h-32 w-52 rounded-full bg-pink-300/10"></div>

                        <div class="absolute -bottom-16 left-1/4 h-28 w-64 rounded-full bg-white/10"></div>

                    </div>

                    <div class="relative px-4 pb-6 text-center">

                        <!-- Profile Picture -->
                        <div class="-mt-16 flex justify-center">

                            <div
                                class="flex h-28 w-28 items-center justify-center overflow-hidden rounded-full border-4 border-white bg-pink-50 shadow-md">

                                <img v-if="user.user_image" :src="user.user_image" alt="Profile"
                                    class="h-full w-full object-cover" />

                                <i v-else class="fas fa-user text-5xl text-[#82103c]"></i>

                            </div>

                        </div>

                        <h2 class="mt-3 break-words text-xl font-bold text-gray-900">
                            {{ user.full_name || user.name }}
                        </h2>

                        <p class="mt-1 break-all text-sm text-gray-500">
                            {{ user.email || user.name }}
                        </p>

                        <!-- Account Status -->
                        <div
                            class="mt-4 inline-flex items-center gap-2 rounded-full bg-green-100 px-4 py-2 text-xs font-semibold text-green-800">

                            <span class="h-2.5 w-2.5 rounded-full bg-green-600"></span>
                            Active Account
                        </div>

                        <!-- Edit Profile -->
                        <div class="mt-5">
                            <button type="button" @click="openEdit"
                                class="inline-flex w-full max-w-[170px] items-center justify-center gap-2 rounded-xl border border-[#a7194d] px-4 py-2.5 text-sm font-semibold text-[#82103c] transition hover:bg-pink-50">

                                <i class="fas fa-pen"></i>
                                Edit Profile
                            </button>
                        </div>

                    </div>

                </section>

                <!-- Personal Information -->
                <section class="min-w-0 rounded-2xl border border-gray-100 bg-white p-4 shadow-sm sm:p-6">

                    <!-- Header -->
                    <div class="mb-6 flex flex-wrap items-center justify-between gap-3">

                        <div class="flex items-center gap-3">

                            <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-pink-50">
                                <i class="fas fa-id-card text-xl text-[#82103c]"></i>
                            </div>

                            <h2 class="text-lg font-bold text-gray-900">
                                Personal Information
                            </h2>

                        </div>

                        <button type="button" @click="openEdit"
                            class="inline-flex items-center gap-2 rounded-xl bg-[#a7194d] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-[#82103c]">

                            <i class="fas fa-pen"></i>
                            Edit
                        </button>

                    </div>

                    <!-- Information Rows -->
                    <div class="space-y-3">

                        <!-- Name -->
                        <div
                            class="grid grid-cols-1 gap-2 rounded-xl border border-gray-100 bg-gray-50 p-3 sm:grid-cols-[170px_minmax(0,1fr)] sm:items-center sm:gap-3 sm:p-4">

                            <div class="flex items-center gap-3">
                                <i class="fas fa-user w-5 text-center text-lg text-[#82103c]"></i>

                                <span class="text-sm font-medium text-gray-700">
                                    Full Name
                                </span>
                            </div>

                            <span class="break-words text-sm font-semibold text-gray-900 sm:pl-2">
                                {{ user.full_name || 'Not available' }}
                            </span>

                        </div>

                        <!-- Email -->
                        <div
                            class="grid grid-cols-1 gap-2 rounded-xl border border-gray-100 bg-gray-50 p-3 sm:grid-cols-[170px_minmax(0,1fr)] sm:items-center sm:gap-3 sm:p-4">

                            <div class="flex items-center gap-3">
                                <i class="fas fa-envelope w-5 text-center text-lg text-[#82103c]"></i>

                                <span class="text-sm font-medium text-gray-700">
                                    Email Address
                                </span>
                            </div>

                            <span class="break-all text-sm font-semibold text-gray-900 sm:pl-2">
                                {{ user.email || user.name }}
                            </span>

                        </div>

                        <!-- Mobile -->
                        <div
                            class="grid grid-cols-1 gap-2 rounded-xl border border-gray-100 bg-gray-50 p-3 sm:grid-cols-[170px_minmax(0,1fr)] sm:items-center sm:gap-3 sm:p-4">

                            <div class="flex items-center gap-3">
                                <i class="fas fa-phone w-5 text-center text-lg text-[#82103c]"></i>

                                <span class="text-sm font-medium text-gray-700">
                                    Mobile Number
                                </span>
                            </div>

                            <span class="break-words text-sm font-semibold text-gray-900 sm:pl-2">
                                {{ user.mobile_no || 'Not available' }}
                            </span>

                        </div>

                        <!-- Mobile Logout -->
                        <button type="button" @click="showLogoutConfirm = true"
                            class="flex w-full items-center justify-center gap-2 rounded-xl border border-red-200 bg-white px-4 py-3 text-sm font-semibold text-red-600 shadow-sm transition hover:bg-red-50 md:hidden">
                            <i class="fas fa-sign-out-alt"></i>
                            Logout
                        </button>

                    </div>

                </section>

            </div>

        </div>

        <!-- Edit Profile Modal -->
        <div v-if="editing" class="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-black/50 p-4"
            @click.self="closeEdit">

            <div class="w-full max-w-md rounded-2xl bg-white p-5 shadow-2xl sm:p-7">

                <div class="mb-6 flex items-center justify-between">

                    <h2 class="text-xl font-bold text-gray-900">
                        Edit Profile
                    </h2>

                    <button type="button" @click="closeEdit"
                        class="flex h-9 w-9 items-center justify-center rounded-full bg-gray-100 text-gray-600 hover:bg-gray-200">

                        <i class="fas fa-times"></i>
                    </button>

                </div>

                <form @submit.prevent="saveProfile" class="space-y-5">

                    <!-- Profile Photo -->
                    <div>
                        <label class="mb-2 block text-sm font-semibold text-gray-700">
                            Profile Photo
                        </label>

                        <div class="flex items-center gap-4">
                            <div
                                class="flex h-20 w-20 shrink-0 items-center justify-center overflow-hidden rounded-full border border-gray-200 bg-pink-50">
                                <img v-if="profileImagePreview" :src="profileImagePreview" alt="Profile photo preview"
                                    class="h-full w-full object-cover" />
                                <i v-else class="fas fa-user text-3xl text-[#82103c]"></i>
                            </div>

                            <div class="min-w-0">
                                <input ref="profileImageInput" type="file" accept="image/jpeg,image/png,image/gif"
                                    class="sr-only" @change="handleProfileImageChange" />

                                <button type="button" @click="chooseProfileImage" :disabled="saving"
                                    class="rounded-xl border border-[#a7194d] px-4 py-2.5 text-sm font-semibold text-[#82103c] transition hover:bg-pink-50 disabled:opacity-60">
                                    <i class="fas fa-camera mr-2"></i>
                                    {{ selectedProfileImage ? 'Choose Another Photo' : 'Change Photo' }}
                                </button>

                                <p class="mt-2 text-xs text-gray-500">
                                    JPG, PNG or GIF · Max 5 MB
                                </p>
                            </div>
                        </div>
                    </div>

                    <!-- Full Name -->
                    <div>
                        <label class="mb-2 block text-sm font-semibold text-gray-700">
                            Full Name
                        </label>

                        <input v-model="editForm.full_name" type="text" required placeholder="Enter your full name"
                            class="w-full rounded-xl border border-gray-200 px-4 py-3 text-sm outline-none transition focus:border-[#82103c] focus:ring-2 focus:ring-pink-100" />
                    </div>

                    <!-- Email -->
                    <div>
                        <label class="mb-2 block text-sm font-semibold text-gray-700">
                            Email Address
                        </label>

                        <input :value="user.email || user.name" type="email" disabled
                            class="w-full cursor-not-allowed rounded-xl border border-gray-200 bg-gray-100 px-4 py-3 text-sm text-gray-500" />

                        <p class="mt-1 text-xs text-gray-400">
                            Email address cannot be changed here.
                        </p>
                    </div>

                    <!-- Mobile -->
                    <div>
                        <label class="mb-2 block text-sm font-semibold text-gray-700">
                            Mobile Number
                        </label>

                        <input v-model="editForm.mobile_no" type="tel" maxlength="15" placeholder="Enter mobile number"
                            class="w-full rounded-xl border border-gray-200 px-4 py-3 text-sm outline-none transition focus:border-[#82103c] focus:ring-2 focus:ring-pink-100" />
                    </div>

                    <!-- Error -->
                    <div v-if="editError" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
                        {{ editError }}
                    </div>

                    <!-- Buttons -->
                    <div class="flex gap-3 pt-2">

                        <button type="button" @click="closeEdit"
                            class="flex-1 rounded-xl border border-gray-200 px-4 py-3 text-sm font-semibold text-gray-700 transition hover:bg-gray-50">

                            Cancel
                        </button>

                        <button type="submit" :disabled="saving"
                            class="flex-1 rounded-xl bg-[#82103c] px-4 py-3 text-sm font-semibold text-white transition hover:bg-[#6b0b30] disabled:cursor-not-allowed disabled:opacity-60">

                            <i v-if="saving" class="fas fa-spinner fa-spin mr-2"></i>

                            {{ saving ? 'Saving...' : 'Save Changes' }}
                        </button>

                    </div>

                </form>

            </div>

        </div>

        <!-- Logout Confirmation Popup -->
        <div v-if="showLogoutConfirm" class="fixed inset-0 z-[60] flex items-center justify-center bg-black/50 p-4"
            @click.self="showLogoutConfirm = false">

            <div class="w-full max-w-sm rounded-2xl bg-white p-6 text-center shadow-2xl">

                <!-- Logout Icon -->
                <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-red-100">
                    <i class="fas fa-sign-out-alt text-2xl text-red-600"></i>
                </div>

                <!-- Heading -->
                <h2 class="mt-4 text-xl font-bold text-gray-900">
                    Confirm Logout
                </h2>

                <!-- Message -->
                <p class="mt-2 text-sm text-gray-500">
                    Are you sure you want to logout from your BuyNew account?
                </p>

                <!-- Yes No Buttons -->
                <div class="mt-6 flex gap-3">

                    <!-- No Button -->
                    <button type="button" @click="showLogoutConfirm = false"
                        class="flex-1 rounded-xl border border-gray-200 px-4 py-3 text-sm font-semibold text-gray-700 transition hover:bg-gray-100">

                        No
                    </button>

                    <!-- Yes Button -->
                    <button type="button" @click="confirmLogout"
                        class="flex-1 rounded-xl bg-[#82103c] px-4 py-3 text-sm font-semibold text-white transition hover:bg-[#6b0b30]">

                        Yes, Logout
                    </button>

                </div>

            </div>

        </div>

    </div>
</template>
