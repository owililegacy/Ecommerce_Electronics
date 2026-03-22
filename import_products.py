# In Django shell
import sqlite3
import json
from eshop.models import Product, Category

# Export and import in one go
old_conn = sqlite3.connect("old_db_backup.sqlite3")
old_conn.row_factory = sqlite3.Row

# Get products
products =[]
try:
    cursor = old_conn.execute("""
        SELECT p.name, p.slug, p.description, p.price, p.stock, p.image, c.name as category_name
        FROM eshop_product p
        LEFT JOIN eshop_category c ON p.category_id = c.id
    """)
    products = [dict(row) for row in cursor.fetchall()]
    old_conn.close()
except Exception as e:
    import json
    with open("products_export.json", "r") as f:
        products = json.load(f)
    print(f"Error fetching from old DB: {e}. Loaded from JSON backup.")
    print(f"Products loaded: {len(products)}")

if len(products) == 0:
    print("No products to import.")
    exit()

# Create categories and import products
for product_data in products:
    # Create/get category
    category, _ = Category.objects.get_or_create(
        name=product_data.get("category_name", "Uncategorized"),
        defaults={
            "slug": product_data.get("category_name", "uncategorized")
            .lower()
            .replace(" ", "-")
        },
    )

    # Create product
    product, created = Product.objects.get_or_create(
        name=product_data["name"],
        defaults={
            "slug": product_data.get(
                "slug", product_data["name"].lower().replace(" ", "-")
            ),
            "description": product_data.get("description", ""),
            "price": product_data.get("price", 0),
            "stock": product_data.get("stock", 0),
            "image": product_data.get("image", ""),
            "category": category,
        },
    )
    if created:
        print(f"Imported: {product.name}")

print(f"\n✅ Done! Total products: {Product.objects.count()}")
