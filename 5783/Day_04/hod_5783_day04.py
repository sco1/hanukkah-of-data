import sqlite3
from pathlib import Path


def find_matching_customers(
    db_path: Path,
    query_sku: str = "BKY",
    n_most: int = 1,
    filter_hours: tuple[int, int] = (4, 9),
) -> list[str]:
    """Find the n most common purchasers of the provided SKU category during the specified hours."""
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    res = cur.execute(
        """
        SELECT customers.name, customers.phone, count(customers.name) as n_visits
        FROM customers
            INNER JOIN orders ON customers.customerid = orders.customerid
            INNER JOIN orders_items ON orders.orderid = orders_items.orderid
        WHERE orders_items.sku LIKE :sku AND strftime("%H", orders.ordered) BETWEEN :start and :end
        GROUP BY customers.name
        HAVING COUNT(customers.name) > 1
        ORDER BY n_visits DESC
        """,
        {
            "sku": f"{query_sku}%",
            "start": f"{filter_hours[0]:02d}",
            "end": f"{filter_hours[1]:02d}",
        },
    ).fetchall()

    con.close()

    return res[:n_most]


if __name__ == "__main__":
    dataset = Path(__file__).parent.parent / Path("Dataset/noahs.sqlite")

    # What we know about the mystery person:
    #    * Bike mechanic
    #    * Purchases baked goods before dawn
    #    * Baked good SKUs start with "BKY"
    print(f"Answer: {find_matching_customers(dataset)}")
