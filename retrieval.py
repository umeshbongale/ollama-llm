import re
import unicodedata
from embedding import get_embedding
from db import get_connection


import psycopg2




# ==============================
# GET ALL CATEGORIES
# ==============================

def get_all_categories():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT DISTINCT category FROM products")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [r[0] for r in rows]


# ==============================
# GET PRODUCTS BY CATEGORY
# ==============================

def get_products_by_category(category):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT name FROM products WHERE LOWER(category)=LOWER(%s)",
        (category,)
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [r[0] for r in rows]


# ==============================
# GET PRODUCT BY NAME
# ==============================

def get_product_by_name(name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT name, price, features
        FROM products
        WHERE LOWER(name) LIKE LOWER(%s)
        LIMIT 1
        """,
        (f"%{name}%",)
    )

    product = cur.fetchone()

    cur.close()
    conn.close()

    return product


# ==============================
# SMART FILTER SEARCH
# ==============================

def search_products_with_filters(category=None, min_price=None, max_price=None):

    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT name, price, features
        FROM products
        WHERE 1=1
    """

    params = []

    if category:
        query += " AND LOWER(category)=LOWER(%s)"
        params.append(category)

    if min_price:
        query += " AND price >= %s"
        params.append(min_price)

    if max_price:
        query += " AND price <= %s"
        params.append(max_price)

    query += " ORDER BY price ASC LIMIT 10"

    cur.execute(query, tuple(params))
    results = cur.fetchall()

    cur.close()
    conn.close()

    return results

