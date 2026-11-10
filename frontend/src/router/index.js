import { createRouter, createWebHistory } from 'vue-router'

import Home from '../views/Home.vue'
import Products from '../views/Products.vue'
import Login from '../views/Login.vue'
import Profile from '../views/Profile.vue'
import Register from '../views/Register.vue'

const routes = [
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
        component: () => import('../views/Cart.vue'),
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
        path: '/profilepage',
        name: 'Profile',
        component: Profile
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// Check Frappe login session
router.beforeEach(async (to) => {
    try {
        const response = await fetch(
            '/api/method/frappe.auth.get_logged_user',
            {
                method: 'GET',
                credentials: 'same-origin'
            }
        )

        const data = await response.json()
        const user = data.message

        const isLoggedIn =
            response.ok && user && user !== 'Guest'

        // Already logged in: redirect Login/Register to Home
        if (
            isLoggedIn &&
            (to.name === 'Login' || to.name === 'Register')
        ) {
            return { name: 'HomePage' }
        }

        // Protect Cart page
        if (!isLoggedIn && to.meta.requiresAuth) {
            return { name: 'Login' }
        }

        return true

    } catch (error) {
        if (to.meta.requiresAuth) {
            return { name: 'Login' }
        }

        return true
    }
})

export default router
