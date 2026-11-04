
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
