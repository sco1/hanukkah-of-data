import sqlite3
from pathlib import Path


def find_matching_customers(db_path: Path, n_most: int = 1) -> list[str]:
    """Find the n customers who have saved the most money."""
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # We have access to the products' wholesale cost, along with how much the customer ends up
    # paying for them. Let's try assuming that our mystery customer is the person who has cost Noah
    # the most profit
    res = cur.execute(
        r"""
        SELECT
            customers.name,
            customers.phone,
            customers.customerid,
            SUM(orders_items.qty * (orders_items.unit_price - products.wholesale_cost)) as total_saved
        FROM customers
            INNER JOIN orders ON customers.customerid = orders.customerid
            INNER JOIN orders_items ON orders.orderid = orders_items.orderid
            INNER JOIN products ON orders_items.sku = products.sku
        GROUP BY customers.customerid
        ORDER BY total_saved
        """,
    ).fetchall()

    con.close()

    return res[:n_most]


if __name__ == "__main__":
    dataset = Path(__file__).parent.parent / Path("Dataset/noahs.sqlite")

    # What we know about the mystery person:
    #    * Cousin of yesterday's mystery person
    #    * Frugal; clips coupons & shops sales
    #    * Has to take the subway to visit her cousin
    print(f"Answer: {find_matching_customers(dataset)[0]}")
