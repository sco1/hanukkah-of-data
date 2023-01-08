import sqlite3
import string
import typing as t
from pathlib import Path

from helpers.utils import fmt_phone

BUTTON_MAP = str.maketrans(string.ascii_lowercase, "22233344455566677778889999")


def get_customer_info(db_path: Path) -> list[tuple[str, str]]:
    """
    Collect customer last names & phone numbers from the provided customer database.

    Customer DB is assumed to have a `name` column, containing the customer's full name, and a
    `phone` column, containing their phone number (with dashes). Dashes are removed from the phone
    number before returning.

    NOTE: A customer's information is only returned if their last name is 10 characters long.
    """
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    info_pairs = []
    res = cur.execute("SELECT name,phone FROM customers").fetchall()
    if res:
        for full_name, full_phone in res:
            *_, last = full_name.split()
            if len(last) == 10:  # Last names have to be 10 letters to map to a phone number
                info_pairs.append((last, full_phone.replace("-", "")))

    con.close()

    return info_pairs


def find_matching_phone(info_pairs: t.Iterable[tuple[str, str]]) -> str:
    """Find the first customer whose last name maps to their phone number."""
    for last_name, phone in info_pairs:
        if last_name.lower().translate(BUTTON_MAP) == phone:
            return fmt_phone(phone)

    raise ValueError("Could not locate a telephone number that matches the customer's last name.")


if __name__ == "__main__":
    dataset = Path(__file__).parent.parent / Path("Dataset/noahs.sqlite")
    info_pairs = get_customer_info(dataset)

    print(f"Answer: {find_matching_phone(info_pairs)}")
