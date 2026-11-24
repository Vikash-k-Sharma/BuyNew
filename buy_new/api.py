
import io
import mimetypes
import re
from urllib.parse import quote, urlparse

import frappe
import requests
from PIL import Image
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
CUSTOMER_ROLE = "BuyNew Customer"
MAX_PROFILE_IMAGE_SIZE = 5 * 1024 * 1024
MAX_PRODUCT_IMAGE_SIZE = 8 * 1024 * 1024
PROFILE_IMAGE_EXTENSIONS = {
    "JPEG": "jpg",
    "PNG": "png",
    "GIF": "gif",
}
PRODUCT_IMAGE_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
    "image/avif": "avif",
}


def _get_product_image_url(product_name, image_url):
    """Route private catalog images through the public product image endpoint."""
    if urlparse(image_url or "").path.startswith("/private/files/"):
        return (
            "/api/method/buy_new.api.get_product_image"
            f"?product_name={quote(product_name, safe='')}"
        )

    return image_url


def _get_user_cart_quantities():
    user = frappe.session.user

    if not user or user == "Guest":
        return {}

    return {
        item.product: cint(item.quantity)
        for item in frappe.get_all(
            CART_DOCTYPE,
            filters={"user": user},
            fields=["product", "quantity"]
        )
    }


# GET ADS

AD_IMAGE_HOST = "rukminim2.flixcart.com"
MAX_AD_IMAGE_BYTES = 8 * 1024 * 1024
ALLOWED_AD_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/avif"
}


@frappe.whitelist(allow_guest=True)
def get_ads():
    ads = frappe.get_all(
        "Ad Img",
        fields=["name", "ad_img"],
        order_by="creation asc",
        page_length=100
    )

    frappe.local.response_headers["Cache-Control"] = "public, max-age=300"

    for ad in ads:
        image_url = ad.ad_img or ""

        if urlparse(image_url).hostname == AD_IMAGE_HOST:
            ad.ad_img = (
                f"/api/method/buy_new.api.get_ad_image"
                f"?name={quote(ad.name, safe='')}"
            )

    return ads


@frappe.whitelist(allow_guest=True)
def get_ad_image(name):
    image_url = frappe.db.get_value("Ad Img", name, "ad_img")
    parsed_url = urlparse(image_url or "")

    if parsed_url.scheme != "https" or parsed_url.hostname != AD_IMAGE_HOST:
        frappe.throw(
            "Advertisement image URL is not allowed.",
            frappe.PermissionError
        )

    try:
        with requests.get(
            image_url,
            timeout=(5, 15),
            stream=True
        ) as upstream:
            upstream.raise_for_status()

            content_type = upstream.headers.get(
                "Content-Type", ""
            ).split(";", 1)[0].lower()

            if content_type not in ALLOWED_AD_IMAGE_TYPES:
                frappe.throw(
                    "Advertisement URL did not return an image.",
                    frappe.ValidationError
                )

            content_length = int(
                upstream.headers.get("Content-Length", 0) or 0
            )

            if content_length > MAX_AD_IMAGE_BYTES:
                frappe.throw(
                    "Advertisement image is too large.",
                    frappe.ValidationError
                )

            image_content = bytearray()

            for chunk in upstream.iter_content(chunk_size=64 * 1024):
                image_content.extend(chunk)

                if len(image_content) > MAX_AD_IMAGE_BYTES:
                    frappe.throw(
                        "Advertisement image is too large.",
                        frappe.ValidationError
                    )

    except requests.RequestException:
        frappe.throw(
            "Could not load advertisement image.",
            frappe.ValidationError
        )

    extension = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/webp": "webp",
        "image/gif": "gif",
        "image/avif": "avif",
    }[content_type]

    frappe.response.update({
        "type": "download",
        "filename": f"advertisement.{extension}",
        "content_type": content_type,
        "display_content_as": "inline",
        "filecontent": bytes(image_content),
    })

    frappe.local.response_headers["Cache-Control"] = "public, max-age=86400"


# GET PRODUCTS

@frappe.whitelist(allow_guest=True)
def get_products():
    meta = frappe.get_meta("Products")

    fields = ["name"] + [
        field for field in PRODUCT_DISPLAY_FIELDS
        if meta.has_field(field)
    ]

    products = frappe.get_all(
        "Products",
        fields=fields,
        limit_page_length=100,
        order_by="creation desc"
    )

    cart_quantities = _get_user_cart_quantities()

    for product in products:
        for field in PRODUCT_DISPLAY_FIELDS:
            product.setdefault(field, None)

        product.product_image = _get_product_image_url(
            product.name, product.product_image
        )
        product["cart_quantity"] = cart_quantities.get(product.name, 0)

    return products


@frappe.whitelist(allow_guest=True)
def get_product_image(product_name):
    """Serve only the private image attached to a public catalog product."""
    if not frappe.db.exists("Products", product_name):
        frappe.throw("Product not found", frappe.DoesNotExistError)

    image_url = frappe.db.get_value("Products", product_name, "product_image")
    if not urlparse(image_url or "").path.startswith("/private/files/"):
        frappe.throw("Private product image not found", frappe.PermissionError)

    file_name = frappe.db.get_value(
        "File",
        {"file_url": image_url, "is_private": 1},
        "name",
    )
    if not file_name:
        frappe.throw("Product image file not found", frappe.DoesNotExistError)

    image_file = frappe.get_doc("File", file_name)
    content_type = mimetypes.guess_type(image_file.file_name or image_url)[0]
    extension = PRODUCT_IMAGE_TYPES.get(content_type)
    if not extension:
        frappe.throw(
            "Product image must be a supported image file",
            frappe.ValidationError,
        )

    if cint(image_file.file_size) > MAX_PRODUCT_IMAGE_SIZE:
        frappe.throw("Product image is too large", frappe.ValidationError)

    image_content = image_file.get_content()
    if isinstance(image_content, str):
        image_content = image_content.encode("utf-8")

    if len(image_content) > MAX_PRODUCT_IMAGE_SIZE:
        frappe.throw("Product image is too large", frappe.ValidationError)

    frappe.response.update({
        "type": "download",
        "filename": f"product-image.{extension}",
        "content_type": content_type,
        "display_content_as": "inline",
        "filecontent": image_content,
    })
    frappe.local.response_headers["Cache-Control"] = "public, max-age=300"


# REGISTER CUSTOMER

@frappe.whitelist(allow_guest=True, methods=["GET"])
def get_csrf_token():
    """Return the current session's CSRF token for the standalone Vite frontend."""
    from frappe.sessions import get_csrf_token as get_session_csrf_token

    return get_session_csrf_token()


@frappe.whitelist(allow_guest=True, methods=["POST"])
def upload_profile_image():
    """Upload a validated public profile image before a guest creates an account."""
    if frappe.session.user != "Guest":
        frappe.throw("Profile images can only be uploaded during registration")

    uploaded_file = frappe.request.files.get("file")
    if not uploaded_file:
        frappe.throw("Please choose a profile image to upload")

    content = uploaded_file.stream.read(MAX_PROFILE_IMAGE_SIZE + 1)
    if not content:
        frappe.throw("The selected image is empty")
    if len(content) > MAX_PROFILE_IMAGE_SIZE:
        frappe.throw("Profile image must be 5 MB or smaller")

    try:
        with Image.open(io.BytesIO(content)) as image:
            image_format = image.format
            image_width, image_height = image.size
            image.verify()
    except Exception:
        frappe.throw("Please upload a valid JPG, PNG or GIF image")

    extension = PROFILE_IMAGE_EXTENSIONS.get(image_format)
    if not extension:
        frappe.throw("Only JPG, PNG and GIF images are allowed")
    if image_width * image_height > 20_000_000:
        frappe.throw("Image dimensions are too large")

    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_name": f"profile-image.{extension}",
        "folder": "Home",
        "is_private": 0,
        "content": content,
    })
    file_doc.insert(ignore_permissions=True)

    return {"file_url": file_doc.file_url}


@frappe.whitelist(methods=["POST"])
def update_current_user_profile_image():
    """Upload a public profile image and assign it to the signed-in user."""
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw("Please login first", frappe.PermissionError)

    uploaded_file = frappe.request.files.get("file")
    if not uploaded_file:
        frappe.throw("Please choose a profile image to upload")

    content = uploaded_file.stream.read(MAX_PROFILE_IMAGE_SIZE + 1)
    if not content:
        frappe.throw("The selected image is empty")
    if len(content) > MAX_PROFILE_IMAGE_SIZE:
        frappe.throw("Profile image must be 5 MB or smaller")

    try:
        with Image.open(io.BytesIO(content)) as image:
            image_format = image.format
            image_width, image_height = image.size
            image.verify()
    except Exception:
        frappe.throw("Please upload a valid JPG, PNG or GIF image")

    extension = PROFILE_IMAGE_EXTENSIONS.get(image_format)
    if not extension:
        frappe.throw("Only JPG, PNG and GIF images are allowed")
    if image_width * image_height > 20_000_000:
        frappe.throw("Image dimensions are too large")

    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_name": f"profile-image-{frappe.generate_hash(length=8)}.{extension}",
        "folder": "Home",
        "is_private": 0,
        "content": content,
    })
    file_doc.insert(ignore_permissions=True)

    frappe.db.set_value("User", user, "user_image", file_doc.file_url)

    return {"user_image": file_doc.file_url}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def register_customer(
    first_name,
    email,
    password,
    confirm_password,
    last_name="",
    profile_image=""
):
    first_name = (first_name or "").strip()
    last_name = (last_name or "").strip()
    email = (email or "").strip().lower()
    password = password or ""
    confirm_password = confirm_password or ""
    profile_image = (profile_image or "").strip()

    if not first_name:
        frappe.throw("Please enter your first name")

    if not email:
        frappe.throw("Please enter your email address")

    if not password:
        frappe.throw("Please enter your password")

    if not confirm_password:
        frappe.throw("Please confirm your password")

    if not profile_image:
        frappe.throw("Please upload your profile photo")

    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        frappe.throw("Please enter a valid email address")

    if len(password) < 8:
        frappe.throw("Password must be at least 8 characters")

    if len(password) > 512:
        frappe.throw("Password is too long")

    if password != confirm_password:
        frappe.throw("Passwords do not match")

    if frappe.db.exists("User", email):
        frappe.throw("This email is already registered")

    if not frappe.db.exists("Role", CUSTOMER_ROLE):
        frappe.throw(
            "BuyNew Customer role does not exist. Please create the role first."
        )

    # Validate uploaded profile image
    if not profile_image.startswith("/files/"):
        frappe.throw("Invalid profile image")

    uploaded_files = frappe.get_all(
        "File",
        filters={
            "file_url": profile_image,
            "is_private": 0,
            "owner": frappe.session.user,
        },
        fields=[
            "name",
            "file_url",
            "file_name",
            "file_size",
            "owner"
        ],
        limit_page_length=1
    )

    if not uploaded_files:
        frappe.throw("Profile image not found. Please upload again.")

    image_file = uploaded_files[0]

    if image_file.owner != frappe.session.user:
        frappe.throw("Invalid profile image upload")

    content_type = mimetypes.guess_type(image_file.file_name or "")[0]
    if (content_type or "").lower() not in {
        "image/jpeg",
        "image/png",
        "image/gif"
    }:
        frappe.throw("Only JPG, PNG and GIF images are allowed")

    if cint(image_file.file_size) > 5 * 1024 * 1024:
        frappe.throw("Profile image must be less than 5 MB")

    # Create customer account
    user = frappe.get_doc({
        "doctype": "User",
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "user_image": image_file.file_url,
        "enabled": 1,
        "user_type": "Website User",
        "send_welcome_email": 0,
        "roles": [{"role": CUSTOMER_ROLE}]
    })

    user.flags.no_welcome_mail = True
    user.insert(ignore_permissions=True)

    update_password(user.name, password)
    frappe.local.login_manager.login_as(user.name)

    return {
        "success": True,
        "logged_in": True,
        "message": "Account created successfully",
        "user": {
            "email": user.name,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "user_image": user.user_image,
            "role": CUSTOMER_ROLE
        }
    }


# CHECK LOGIN

def check_cart_user():
    user = frappe.session.user

    if not user or user == "Guest":
        frappe.throw(
            "Please login to continue",
            frappe.PermissionError
        )

    return user


# CURRENT SESSION USER

@frappe.whitelist(allow_guest=True)
def get_session_user():
    return frappe.session.user or "Guest"


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
        frappe.throw(
            "User profile not found",
            frappe.DoesNotExistError
        )

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

    if (
        cint(item.stock_quantity) <= 0
        or "out of stock" in (item.stock_status or "").lower()
    ):
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
        cart_item = frappe.get_doc(CART_DOCTYPE, existing)
        current_quantity = cint(cart_item.quantity)

        if current_quantity >= 10:
            return {
                "success": False,
                "limit_reached": True,
                "message": "You can add up to 10 of this product",
                "quantity": current_quantity
            }

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

    items = frappe.get_all(
        CART_DOCTYPE,
        filters={"user": user},
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

    for item in items:
        item.product_image = _get_product_image_url(
            item.product, item.product_image
        )

    return items


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
        {
            "name": cart_item,
            "user": user
        },
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
        {
            "name": cart_item,
            "user": user
        },
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
        "product_image": _get_product_image_url(
            product.name, product.product_image
        ),
        "selling_price": product.selling_price,
        "mrp": product.mrp,
        "discount_percentage": product.discount_percentage,
        "stock_quantity": product.stock_quantity,
        "stock_status": product.stock_status,
        "cart_quantity": _get_user_cart_quantities().get(product.name, 0)
    }


# CHECKOUT DATA

@frappe.whitelist()
def get_checkout_data():
    if frappe.session.user == "Guest":
        frappe.throw("Please login first")

    user = frappe.session.user

    cart_items = frappe.get_all(
        "BuyNew Cart Item",
        filters={"user": user},
        fields=[
            "name",
            "product",
            "product_name",
            "product_image",
            "selling_price",
            "quantity"
        ]
    )

    items = []
    subtotal = 0

    for item in cart_items:
        price = float(item.selling_price or 0)
        quantity = int(item.quantity or 0)
        amount = price * quantity

        items.append({
            "cart_item": item.name,
            "product": item.product,
            "product_name": item.product_name,
            "product_image": _get_product_image_url(
                item.product, item.product_image
            ),
            "selling_price": price,
            "quantity": quantity,
            "amount": amount
        })

        subtotal += amount

    return {
        "items": items,
        "subtotal": subtotal,
        "delivery_charge": 0 if subtotal >= 499 else 40,
        "grand_total": subtotal + (0 if subtotal >= 499 else 40)
    }


# PLACE ORDER

@frappe.whitelist()
def place_order(
    customer_name,
    phone,
    address,
    city,
    state,
    pincode,
    payment_method
):
    if frappe.session.user == "Guest":
        frappe.throw("Please login first")

    user = frappe.session.user

    allowed_methods = ["COD", "UPI", "Card", "Net Banking"]

    if payment_method not in allowed_methods:
        frappe.throw("Invalid payment method")

    if not all([
        customer_name,
        phone,
        address,
        city,
        state,
        pincode
    ]):
        frappe.throw("Please fill all delivery details")

    cart_items = frappe.get_all(
        "BuyNew Cart Item",
        filters={"user": user},
        fields=[
            "name",
            "product",
            "product_name",
            "product_image",
            "selling_price",
            "quantity"
        ]
    )

    if not cart_items:
        frappe.throw("Your cart is empty")

    order_items = []
    subtotal = 0

    for item in cart_items:
        quantity = int(item.quantity or 0)
        price = float(item.selling_price or 0)

        if quantity <= 0:
            frappe.throw(f"Invalid quantity for {item.product_name}")

        product = frappe.get_doc("Products", item.product)
        available_stock = int(product.stock_quantity or 0)

        if available_stock < quantity:
            frappe.throw(
                f"Only {available_stock} quantity available for {item.product_name}"
            )

        amount = price * quantity
        subtotal += amount

        order_items.append({
            "product": item.product,
            "product_name": item.product_name,
            "product_image": item.product_image,
            "selling_price": price,
            "quantity": quantity,
            "amount": amount
        })

    delivery_charge = 0 if subtotal >= 499 else 40
    grand_total = subtotal + delivery_charge

    # Demo payment status
    if payment_method == "COD":
        payment_status = "Pending"
    else:
        payment_status = "Paid (Demo)"

    order = frappe.get_doc({
        "doctype": "BuyNew Order",
        "customer": user,
        "customer_name": customer_name,
        "email": user,
        "phone": phone,
        "address": address,
        "city": city,
        "state": state,
        "pincode": pincode,
        "payment_method": payment_method,
        "payment_status": payment_status,
        "order_status": "Confirmed",
        "subtotal": subtotal,
        "delivery_charge": delivery_charge,
        "grand_total": grand_total,
        "items": order_items
    })

    order.insert(ignore_permissions=True)

    # Update product stock
    for item in cart_items:
        product = frappe.get_doc("Products", item.product)

        product.stock_quantity = (
            int(product.stock_quantity or 0) - int(item.quantity or 0)
        )

        product.save(ignore_permissions=True)

    # Clear customer cart
    for item in cart_items:
        frappe.delete_doc(
            "BuyNew Cart Item",
            item.name,
            ignore_permissions=True
        )

    frappe.db.commit()

    return {
        "success": True,
        "order_id": order.name,
        "payment_method": payment_method,
        "payment_status": payment_status,
        "grand_total": grand_total
    }


@frappe.whitelist()
def add_to_wishlist(product):

    user = frappe.session.user

    if user == "Guest":
        frappe.throw("Please login first")

    if not frappe.db.exists("Products", product):
        frappe.throw("Product not found")

    existing = frappe.db.exists(
        "Wishlist Item",
        {
            "user": user,
            "product": product
        }
    )

    if existing:
        return {
            "success": True,
            "message": "Already in wishlist"
        }

    doc = frappe.get_doc({
        "doctype": "Wishlist Item",
        "user": user,
        "product": product
    })

    doc.insert(ignore_permissions=True)

    return {
        "success": True,
        "message": "Added to wishlist"
    }


@frappe.whitelist()
def get_wishlist():

    user = frappe.session.user

    if user == "Guest":
        frappe.throw("Please login first")

    wishlist = frappe.get_all(
        "Wishlist Item",
        filters={
            "user": user
        },
        fields=[
            "name",
            "product",
            "creation"
        ],
        order_by="creation desc"
    )

    products = []

    for item in wishlist:

        if not frappe.db.exists("Products", item.product):
            continue

        product = frappe.get_doc(
            "Products",
            item.product
        )

        products.append({
            "wishlist_id": item.name,
            "name": product.name,
            "products_name": product.products_name,
            "product_image": product.product_image,
            "selling_price": product.selling_price,
            "mrp": product.mrp,
            "category": product.category
        })

    return products


@frappe.whitelist()
def remove_from_wishlist(product):

    user = frappe.session.user

    if user == "Guest":
        frappe.throw("Please login first")

    wishlist_id = frappe.db.get_value(
        "Wishlist Item",
        {
            "user": user,
            "product": product
        },
        "name"
    )

    if not wishlist_id:
        return {
            "success": True,
            "message": "Product not found in wishlist"
        }

    frappe.delete_doc(
        "Wishlist Item",
        wishlist_id,
        ignore_permissions=True
    )

    return {
        "success": True,
        "message": "Removed from wishlist"
    }
