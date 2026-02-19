import uuid
from db import get_connection
from embedding import get_embedding
import json

products = [
    {
        "name": "Greeno Biotech Growbag 12x12 inch",
        "category": "Growbag",
        "price": 500,
        "rating": 4.5,
        "description": "this is used for small plants ",
        "features": ["12x12", "with hole", "250 gsm"],
        "use_case": "plantation, grow bags, kitchen garden"
    },
    {
        "name": "Greeno Biotech Growbag 15x15 inch",
        "category": "Growbag",
        "price": 1000,
        "rating": 4.5,
        "description": "this is used for medium plants ",
        "features": ["15x15", "with hole", "250 gsm"],
        "use_case": "plantation, grow bags, kitchen garden"
    },
    {
        "name": "Greeno Biotech Growbag 18x18 inch",
        "category": "Growbag",
        "price": 2000,
        "rating": 4.5,
        "description": "this is used for medium plants ",
        "features": ["18x18", "with hole", "250 gsm"],
        "use_case": "plantation, grow bags, kitchen garden, medium plants"
    },
    {
        "name": "Greeno Biotech Growbag 20x20 inch",
        "category": "Growbag",
        "price": 3000,
        "rating": 4.5,
        "description": "this is used for small plants ",
        "features": ["20x20", "with hole", "250 gsm"],
        "use_case": "plantation, grow bags, kitchen garden"
    },
    {
        "name": "Greeno Biotech Growbag 24x24 inch",
        "category": "Growbag",
        "price": 4000,
        "rating": 4.5,
        "description": "this is used for big plants ",
        "features": ["24x24", "with hole", "250 gsm"],
        "use_case": "plantation, grow bags, kitchen garden, big plants"
    },
    {
        "name": "Greeno Biotech Azolla 6x6 feet",
        "category": "Azolla",
        "price": 1500,
        "rating": 4.5,
        "description": "this is used for small azolla ",
        "features": ["20x20", "with hole", "250 gsm"],
        "use_case": "plantation, grow bags, Azolla"
    },
    {
        "name": "Greeno Biotech Azolla 12x12 feet",
        "category": "Azolla",
        "price": 3500,
        "rating": 4.5,
        "description": "this is used for big plants ",
        "features": ["12x12", "with hole", "250 gsm"],
        "use_case": "plantation, grow bags, kitchen garden, big plants"
    }
    ,
    {
        "name": "Greeno Biotech vermibed 6x6 feet",
        "category": "Vermibed",
        "price": 2500,
        "rating": 4.5,
        "description": "this is used for vermi composts ",
        "features": ["6x6", "with hole", "250 gsm"],
        "use_case": "plantation, grow bags, Vermi compost"
    },
    {
        "name": "Greeno Biotech vermibed 12x12 feet",
        "category": "Vermibed",
        "price": 5000,
        "rating": 4.5,
        "description": "this is used for vermi composts ",
        "features": ["12x12", "with hole", "250 gsm"],
        "use_case": "plantation, grow bags, vermi compost"
    }
]

conn = get_connection()
cur = conn.cursor()

for p in products:
    text_for_embedding = (
        p["name"] + " " +
        p["description"] + " " +
        " ".join(p["features"]) + " " +
        p["use_case"]
    )

    embedding = get_embedding(text_for_embedding)

    cur.execute("""
        INSERT INTO products (
            id, name, category, price, rating,
            description, features, use_case, embedding
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        str(uuid.uuid4()),
        p["name"],
        p["category"],
        p["price"],
        p["rating"],
        p["description"],
        json.dumps(p["features"]),
        p["use_case"],
        embedding
    ))

conn.commit()
cur.close()
conn.close()
