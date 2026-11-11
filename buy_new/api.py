
import re
import frappe
from frappe.utils import cint
from frappe.utils.password import update_password


PRODUCT_DISPLAY_FIELDS = (
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
    "stock_status",
)

CART_DOCTYPE = "BuyNew Cart Item"


# GET ADS

@frappe.whitelist(allow_guest=True)
def get_ads():

    return frappe.get_list(
        "Ad Img",
        fields=["name", "ad_img"],
        order_by="creation asc",
        page_length=100
    )


# GET PRODUCTS

@frappe.whitelist(allow_guest=True)
def get_products():

    # Only ask the database for fields present in the installed DocType. This
    # keeps this public endpoint safe if optional product fields are changed.
    meta = frappe.get_meta("Products")
    fields = ["name"] + [field for field in PRODUCT_DISPLAY_FIELDS if meta.has_field(field)]

    products = frappe.get_all(
        "Products",
        fields=fields,
        limit_page_length=100,
        order_by="creation desc"
    )

    # Keep a stable response shape for the existing Vue product cards.
    for product in products:
        for field in PRODUCT_DISPLAY_FIELDS:
            product.setdefault(field, None)

    return products


# REGISTER CUSTOMER

@frappe.whitelist(allow_guest=True)
def register_customer(first_name, email, password):

    first_name = (first_name or "").strip()
    email = (email or "").strip().lower()
    password = password or ""

    if not first_name:
        frappe.throw("Please enter your name")

    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        frappe.throw("Please enter a valid email address")

    if len(password) < 8:
        frappe.throw("Password must be at least 8 characters")

    if frappe.db.exists("User", email):
        frappe.throw("This email is already registered")

    user = frappe.get_doc({
        "doctype": "User",
        "email": email,
        "first_name": first_name,
        "enabled": 1,
        "user_type": "Website User",
        "send_welcome_email": 0
    })

    user.insert(ignore_permissions=True)

    update_password(email, password)

    return {
        "success": True,
        "message": "Account created successfully",
        "email": email
    }


# CHECK LOGIN

def check_cart_user():

    user = frappe.session.user

    if not user or user == "Guest":
        frappe.throw("Please login to continue", frappe.PermissionError)

    return user


# CURRENT USER PROFILE

@frappe.whitelist()
def get_current_user_profile():

    user = check_cart_user()
    profile = frappe.db.get_value(
        "User",
        user,
        ["name", "full_name", "email", "mobile_no", "user_image"],
        as_dict=True
    )

    if not profile:
        frappe.throw("User profile not found", frappe.DoesNotExistError)

    return profile


# ADD TO CART

@frappe.whitelist()
def add_to_cart(product):

    user = check_cart_user()

    product = (product or "").strip()
    if not product:
        frappe.throw("Product is required")

    if not frappe.db.exists("Products", product):
        frappe.throw("Product not found")

    item = frappe.get_doc("Products", product)

    if cint(item.stock_quantity) <= 0 or "out of stock" in (item.stock_status or "").lower():
        frappe.throw("Out of Stock")

    existing = frappe.db.get_value(
        CART_DOCTYPE,
        {
            "user": user,
            "product": product
        },
        "name"
    )

    if existing:

        cart_item = frappe.get_doc(
            CART_DOCTYPE,
            existing
        )

        current_quantity = cint(cart_item.quantity)
        if current_quantity >= 10:
            frappe.throw("You can add up to 10 of this product")

        cart_item.quantity = current_quantity + 1
        cart_item.save(ignore_permissions=True)

    else:

        cart_item = frappe.get_doc({
            "doctype": CART_DOCTYPE,
            "user": user,
            "product": product,
            "product_name": item.products_name,
            "product_image": item.product_image,
            "selling_price": item.selling_price,
            "quantity": 1
        })

        cart_item.insert(ignore_permissions=True)

    return {
        "success": True,
        "message": "Product added to cart",
        "quantity": cart_item.quantity
    }


# GET CART

@frappe.whitelist()
def get_cart():

    user = check_cart_user()

    return frappe.get_all(
        CART_DOCTYPE,
        filters={
            "user": user
        },
        fields=[
            "name",
            "user",
            "product",
            "product_name",
            "product_image",
            "selling_price",
            "quantity"
        ],
        order_by="creation desc"
    )


# UPDATE CART QUANTITY

@frappe.whitelist()
def update_cart_quantity(cart_item, quantity):

    user = check_cart_user()

    quantity = cint(quantity)

    if quantity < 1 or quantity > 10:
        frappe.throw("Quantity must be between 1 and 10")

    if not cart_item:
        frappe.throw("Cart item not found")

    owned_item = frappe.db.get_value(
        CART_DOCTYPE,
        {"name": cart_item, "user": user},
        "name"
    )
    if not owned_item:
        frappe.throw("Cart item not found")

    doc = frappe.get_doc(CART_DOCTYPE, owned_item)
    doc.quantity = quantity
    doc.save(ignore_permissions=True)

    return {
        "success": True,
        "message": "Cart quantity updated",
        "quantity": quantity
    }


# REMOVE FROM CART

@frappe.whitelist()
def remove_from_cart(cart_item):

    user = check_cart_user()

    if not cart_item:
        frappe.throw("Cart item is required")

    owned_item = frappe.db.get_value(
        CART_DOCTYPE,
        {"name": cart_item, "user": user},
        "name"
    )
    if not owned_item:
        frappe.throw("Cart item not found")

    frappe.delete_doc(
        CART_DOCTYPE,
        owned_item,
        ignore_permissions=True
    )

    return {
        "success": True,
        "message": "Product removed from cart"
    }
# GET PRODUCT

@frappe.whitelist(allow_guest=True)
def get_product(product_name):

    if not frappe.db.exists("Products", product_name):
        frappe.throw("Product not found")

    product = frappe.get_doc("Products", product_name)

    return {
        "name": product.name,
        "products_name": product.products_name,
        "products_code": product.products_code,
        "brand": product.brand,
        "category": product.category,
        "description": product.description,
        "short_description": product.short_description,
        "product_image": product.product_image,
        "selling_price": product.selling_price,
        "mrp": product.mrp,
        "discount_percentage": product.discount_percentage,
        "stock_quantity": product.stock_quantity,
        "stock_status": product.stock_status
    }
