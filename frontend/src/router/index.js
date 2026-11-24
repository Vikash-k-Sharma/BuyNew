
import { createRouter, createWebHistory } from 'vue-router'

// Lazy Loaded Views
const Home = () => import('../views/Home.vue')
const Products = () => import('../views/Products.vue')
const Login = () => import('../views/Login.vue')
const Profile = () => import('../views/Profile.vue')
const Register = () => import('../views/Register.vue')
const Wishlist = () => import('../views/Wishlist.vue')
const ProductDetail = () => import('../views/ProductDetail.vue')
const Cart = () => import('../views/Cart.vue')
const Checkout = () => import('../views/Checkout.vue')
const OrderSuccess = () => import('../views/OrderSuccess.vue')

// Routes
const routes = [
    {
        path: '/',
        redirect: '/home'
    },
    {
        path: '/home',
        name: 'HomePage',
        component: Home
    },
    {
        path: '/products',
        name: 'Products',
        component: Products
    },
    {
        path: '/cart',
        name: 'Cart',
        component: Cart,
        meta: { requiresAuth: true }
    },
    {
        path: '/login',
        name: 'Login',
        component: Login
    },
    {
        path: '/register',
        name: 'Register',
        component: Register
    },
    {
        path: '/wishlist',
        name: 'Wishlist',
        component: Wishlist,
        meta: {
            requiresAuth: true
        }
    },
    {
        path: '/checkout',
        name: 'Checkout',
        component: Checkout,
        meta: { requiresAuth: true }
    },
    {
        path: '/order-success',
        name: 'OrderSuccess',
        component: OrderSuccess,
        meta: { requiresAuth: true }
    },
    {
        path: '/profilepage',
        name: 'Profile',
        component: Profile,
        meta: { requiresAuth: true }
    },
    {
        path: '/product/:id',
        name: 'ProductDetail',
        component: ProductDetail
    },
    {
        path: '/:pathMatch(.*)*',
        redirect: '/home'
    }
]

// Router
const router = createRouter({
    history: createWebHistory(),
    routes,

    // Smooth navigation
    scrollBehavior(to, from, savedPosition) {
        if (savedPosition) {
            return savedPosition
        }

        return { top: 0 }
    }
})

// Session Cache
let sessionCache = null
let sessionCacheTime = 0
let sessionRequest = null

async function checkLogin() {
    const now = Date.now()

    // Reuse recent session result
    if (sessionCache !== null && now - sessionCacheTime < 5000) {
        return sessionCache
    }

    // Avoid duplicate requests
    if (sessionRequest) {
        return sessionRequest
    }

    sessionRequest = fetch(
        '/api/method/buy_new.api.get_session_user',
        {
            method: 'GET',
            credentials: 'same-origin',
            headers: {
                Accept: 'application/json'
            }
        }
    )
        .then(async (response) => {
            if (!response.ok) {
                throw new Error('Session check failed')
            }

            const data = await response.json()
            const user = data.message

            sessionCache = Boolean(user && user !== 'Guest')
            sessionCacheTime = Date.now()

            return sessionCache
        })
        .finally(() => {
            sessionRequest = null
        })

    return sessionRequest
}

// Router Guard
router.beforeEach(async (to) => {
    if (!to.meta.requiresAuth &&
        to.name !== 'Login' &&
        to.name !== 'Register') {
        return true
    }

    try {
        const isLoggedIn = await checkLogin()

        if (
            isLoggedIn &&
            (to.name === 'Login' || to.name === 'Register')
        ) {
            return { name: 'HomePage' }
        }

        if (!isLoggedIn && to.meta.requiresAuth) {
            return {
                name: 'Login',
                query: { redirect: to.fullPath }
            }
        }

        return true

    } catch (error) {
        sessionCache = null

        if (to.meta.requiresAuth) {
            return { name: 'Login' }
        }

        return true
    }
})

// Refresh session after login/logout
function refreshSession() {
    sessionCache = null
    sessionCacheTime = 0
}

if (typeof window !== 'undefined') {
    window.addEventListener('buynew-auth-changed', refreshSession)
}

export default router
