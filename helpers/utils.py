def fmt_phone(phone: str) -> str:
    """Format the provided phone number as a phone number with dashes."""
    if len(phone) != 10:
        raise ValueError(f"Invalid length phone number provided. Expected: 10, got: {len(phone)}.")

    return f"{phone[:3]}-{phone[3:6]}-{phone[6::]}"
