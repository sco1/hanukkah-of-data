import datetime as dt
import sqlite3
from collections import namedtuple
from enum import Enum, IntEnum
from pathlib import Path


class ChineseZodiac(IntEnum):  # noqa: D101
    BASE = 2000

    DRAGON = 0
    SNAKE = 1
    HORSE = 2
    GOAT = 3
    MONKEY = 4
    ROOSTER = 5
    DOG = 6
    PIG = 7
    RAT = 8
    OX = 9
    TIGER = 10
    RABBIT = 11


MonthDay = namedtuple("MonthDay", ("month", "day"))


class Zodiac(Enum):  # noqa: D101
    AQUARIUS = (MonthDay(1, 20), MonthDay(2, 18))
    PICES = (MonthDay(2, 19), MonthDay(3, 20))
    ARIES = (MonthDay(3, 21), MonthDay(4, 19))
    TAURUS = (MonthDay(4, 20), MonthDay(5, 20))
    GEMINI = (MonthDay(5, 21), MonthDay(6, 20))
    CANCER = (MonthDay(6, 21), MonthDay(7, 22))
    LEO = (MonthDay(7, 23), MonthDay(8, 22))
    VIRGO = (MonthDay(8, 23), MonthDay(9, 22))
    LIBRA = (MonthDay(9, 23), MonthDay(10, 22))
    SCORPIO = (MonthDay(10, 23), MonthDay(11, 21))
    SAGITTARIUS = (MonthDay(11, 22), MonthDay(12, 21))
    CAPRICORN = (MonthDay(12, 22), MonthDay(1, 19))

    def in_range(self, query_date: dt.date) -> bool:  # noqa: D102
        left_md, right_md = self.value
        left = dt.date(query_date.year, left_md.month, left_md.day)
        right = dt.date(query_date.year, right_md.month, right_md.day)

        return left <= query_date <= right


def find_matching_customers(
    db_path: Path,
    chinese_sign: ChineseZodiac = ChineseZodiac.DOG,
    zodiac: Zodiac = Zodiac.ARIES,
    query_zip: int = 11420,
) -> list[str]:
    """Locate phone number of customer(s) who match the provided query parameters."""
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    matching_customers = []
    # Birthdate is stored as a string in the db, so we can just work with it in Python
    res = cur.execute(
        """
        SELECT customers.birthdate, customers.phone FROM customers
        WHERE customers.citystatezip LIKE :zip
        """,
        {"zip": f"%{query_zip}"},
    ).fetchall()
    if res:
        for raw_birthdate, phone in res:
            birthdate = dt.date.fromisoformat(raw_birthdate)
            if (birthdate.year - ChineseZodiac.BASE) % 12 != chinese_sign:
                continue

            if zodiac.in_range(birthdate):
                matching_customers.append(phone)

    con.close()

    return matching_customers


if __name__ == "__main__":
    dataset = Path(__file__).parent.parent / Path("Dataset/noahs.sqlite")

    # What we know about the mystery person:
    #    * Aries
    #    * Year of the Dog
    #    * Lives in the same neighborhood (same zip code?) as customer identified yesterday
    print(f"Answer: {find_matching_customers(dataset)[0]}")
