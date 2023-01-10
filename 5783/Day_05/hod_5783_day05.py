import sqlite3
from pathlib import Path


def find_matching_customers(
    db_path: Path,
    query_city: str = "Queens Village",
    product_desc_filter: str = "cat",
    n_most: int = 1,
) -> list[str]:
    """Find the n most common purchasers of the provided product category from the query city."""
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    res = cur.execute(
        r"""
        SELECT customers.name, customers.phone, count(customers.name) as n_visits
        FROM customers
            INNER JOIN orders ON customers.customerid = orders.customerid
            INNER JOIN orders_items ON orders.orderid = orders_items.orderid
            INNER JOIN products ON orders_items.sku = products.sku
        WHERE customers.citystatezip LIKE :city AND products.desc LIKE "%cat%"
        GROUP BY customers.name
        HAVING COUNT(customers.name) > 1
        ORDER BY n_visits DESC
        """,
        {
            "city": f"{query_city}%",
            "desc_filter": f"%{product_desc_filter}%",
        },
    ).fetchall()

    con.close()

    return res[:n_most]


if __name__ == "__main__":
    dataset = Path(__file__).parent.parent / Path("Dataset/noahs.sqlite")

    # What we know about the mystery person:
    #    * From Queens Village
    #    * Owns a Noah's Market sweatshirt
    #    * Has a lot of (old?) cats
    print(f"Answer: {...}")
