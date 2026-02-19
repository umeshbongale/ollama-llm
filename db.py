import psycopg2
import os

def get_connection():
    return psycopg2.connect(
        dbname="productdb",
        user="postgres",
        password="StrongPassword123",
        host="localhost",
        port="5432"
    )
