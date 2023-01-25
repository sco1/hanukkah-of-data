import sqlite3
import typing as t
from pathlib import Path


class PurchaseInfo(t.NamedTuple):  # noqa: D101
    name: str
    phone: str
    customerid: int
    ordered: str
    sku: str
    desc: str


def find_close_purchases(
    db_path: Path,
    collision_customer_id: int = 8342,
    minute_tolerance: int = 60,
) -> list[PurchaseInfo]:
    """
    Locate all purchases made around the same time as purchases made by the queried customer ID.

    NOTE: Purchases made by the queried customer are also contained in the items returned from the
    database.
    """
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # First select purchases made by the queried customer ID, then use it to join with the remaining
    # purchases in the DB and bracket them using an absolute minute threshold
    res = cur.execute(
        r"""
        WITH filter_orders as (
            SELECT orders.ordered, products.sku, products.desc
            FROM customers
                INNER JOIN orders ON customers.customerid = orders.customerid
                INNER JOIN orders_items ON orders.orderid = orders_items.orderid
                INNER JOIN products ON orders_items.sku = products.sku
            WHERE customers.customerid = :filter_id
        )
        SELECT
            customers.name,
            customers.phone,
            customers.customerid,
            orders.ordered,
            products.sku,
            products.desc
        FROM customers
            INNER JOIN orders ON customers.customerid = orders.customerid
            INNER JOIN filter_orders ON customers.customerid AND (
                ABS(strftime('%s', orders.ordered) - strftime('%s', filter_orders.ordered)) <= :minute_threshold
            )
            INNER JOIN orders_items ON orders.orderid = orders_items.orderid
            INNER JOIN products ON orders_items.sku = products.sku
        """,
        {
            "filter_id": collision_customer_id,
            "minute_threshold": minute_tolerance,
        },
    ).fetchall()

    con.close()

    return [PurchaseInfo(*r) for r in res]


def _partition_item_color(description: str) -> tuple[str, str | None]:
    """
    Partition the item color from the item description if it has a color variation.

    An item is assumed to have a color variation if the final component of its description is a
    color enclosed by parentheses.
    """
    if "(" in description:
        *item, color = description.split()
        color = color.strip("()")
        return (" ".join(item), color)

    return (description, None)


def find_likely_boyfriend(
    close_purchases: t.Iterable[PurchaseInfo],
    gf_id: int = 8342,
) -> list[PurchaseInfo]:
    """
    Identify purchases likely made by the ex-BF of the provided query customer.

    The BF is assumed to have made a purchase of the same item as the query customer but in a
    different color.

    NOTE: It is assumed that if an item comes in varying colors that the color is appended to the
    end of the product description in parentheses (e.g. `"item (red)"` and `"item (blue)"`)
    """
    # Iterate through the filtered purchases and extract items the GF purchased that contain color
    # variations (has parentheses in the description), and separate non-GF's purchases into a
    # separate queue for the next step
    gf_purchase_descriptions = set()
    check_queue: list[PurchaseInfo] = []
    for purchase in close_purchases:
        if purchase.customerid == gf_id:
            item, _ = _partition_item_color(purchase.desc)
            gf_purchase_descriptions.add(item)
        else:
            check_queue.append(purchase)

    matching_purchases: list[PurchaseInfo] = []
    for potential_bf in check_queue:
        if "(" in potential_bf.desc:
            item, _ = _partition_item_color(potential_bf.desc)
            if item in gf_purchase_descriptions:
                matching_purchases.append(potential_bf)

    return matching_purchases


if __name__ == "__main__":
    dataset = Path(__file__).parent.parent / Path("Dataset/noahs.sqlite")

    # What we know about the mystery person:
    #    * Made a purchase at the same time as yesterday's customer (they bumped into each other)
    #    * Purchased the same thing as yesterday's customer, but in a different color
    suitors = find_likely_boyfriend(find_close_purchases(dataset))
    print(f"Answer: {[(suitor.name, suitor.phone) for suitor in suitors]}")
