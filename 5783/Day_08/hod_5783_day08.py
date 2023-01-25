import sqlite3
from pathlib import Path


def find_best_collectors(
    db_path: Path,
    filter_sku: str = "COL",
    n_most: int = 1,
) -> list[tuple[str, str, int]]:
    """Identify the customer(s) who have collected the most collectible items."""
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    res = cur.execute(
        r"""
        SELECT customers.name, customers.phone, COUNT(customers.name) as n_collectibles
        FROM customers
            INNER JOIN orders ON customers.customerid = orders.customerid
            INNER JOIN orders_items ON orders.orderid = orders_items.orderid
            INNER JOIN products ON orders_items.sku = products.sku
        WHERE orders_items.sku like :filter_sku
        GROUP BY customers.name
        ORDER BY n_collectibles DESC
        """,
        {
            "filter_sku": f"{filter_sku}%",
        },
    ).fetchall()

    con.close()

    return res[:n_most]


if __name__ == "__main__":
    dataset = Path(__file__).parent.parent / Path("Dataset/noahs.sqlite")

    # What we know about the mystery person:
    #    * Sister of yesterday's customer
    #    * Lives in Manhattan
    #    * Owns an entire set of Noah's collectibles (SKU starts with "COL")
    print(f"Answer: {find_best_collectors(dataset)[0]}")
