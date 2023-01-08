import datetime as dt
import sqlite3
import typing as t
from pathlib import Path

from helpers.utils import fmt_phone


def get_customer_info(
    db_path: Path, transaction_year: int = 2017, filter_sku: str = "HOM8601"
) -> list[tuple[str, str]]:
    """Collect initials & phone info for specific item transactions made in the specified year."""
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    info_pairs = []
    res = cur.execute(
        """
        SELECT DISTINCT customers.name, customers.phone
        FROM customers
            INNER JOIN orders ON customers.customerid = orders.customerid
            INNER JOIN orders_items ON orders.orderid = orders_items.orderid
        WHERE orders_items.sku = :sku AND orders.ordered BETWEEN :start AND :end
        """,
        {
            "sku": filter_sku,
            "start": dt.datetime(transaction_year, 1, 1),
            "end": dt.datetime(transaction_year, 12, 31),
        },
    ).fetchall()
    if res:
        for full_name, phone in res:
            first, *_, last = full_name.split()
            info_pairs.append((f"{first[0]}{last[0]}".upper(), phone.replace("-", "")))

    con.close()

    return info_pairs


def locate_contractor(
    customer_info: t.Iterable[tuple[str, str]], query_initials: str = "JD"
) -> str:
    """Locate the first customer matching the provided query initials."""
    for initials, phone in customer_info:
        if initials.upper() == query_initials.upper():
            return fmt_phone(phone)

    raise ValueError(f"Could not locate contractor initials matching '{query_initials}'")


if __name__ == "__main__":
    dataset = Path(__file__).parent.parent / Path("Dataset/noahs.sqlite")

    info = get_customer_info(dataset)
    print(f"Answer: {locate_contractor(info)}")
