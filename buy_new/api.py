
import frappe


@frappe.whitelist(allow_guest=True)
def get_ads():

    ads = frappe.get_list(
        "Ad Img",
        fields=["name", "ad_img"],
        order_by="creation asc",
        page_length=100
    )

    return ads


@frappe.whitelist(allow_guest=True)
def get_products():

    products = frappe.get_all(
        "Products",
        fields=[
            "name",
            "products_name",
            "products_code",
            "brand",
            "category",
            "description",
            "short_description",
            "product_image",
            "selling_price",
            "mrp",
            "discount_percentage",
            "stock_quantity",
            "stock_status"
        ],
        limit_page_length=100,
        order_by="creation desc"
    )

    return products



import re
import frappe
from frappe.utils.password import update_password


@frappe.whitelist(allow_guest=True)
def register_customer(first_name, email, password):

    # Clean input
    first_name = (first_name or "").strip()
    email = (email or "").strip().lower()
    password = password or ""

    # Validate name
    if not first_name:
        frappe.throw("Please enter your name")

    # Validate email
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        frappe.throw("Please enter a valid email address")

    # Validate password
    if len(password) < 8:
        frappe.throw("Password must contain at least 8 characters")

    # Check existing user
    if frappe.db.exists("User", email):
        frappe.throw("This email is already registered")

    # Create Frappe User
    user = frappe.get_doc({
        "doctype": "User",
        "email": email,
        "first_name": first_name,
        "enabled": 1,
        "user_type": "Website User",
        "send_welcome_email": 0
    })

    user.insert(ignore_permissions=True)

    # Set password securely
    update_password(email, password)

    frappe.db.commit()

    return {
        "success": True,
        "message": "Account created successfully",
        "email": email
    }
