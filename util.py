def parse_date_string(date_str: str) -> tuple:
    """Parse the date string with before/after parameters."""
    days_before = 2
    days_after = 2

    parts = date_str.split('/')
    date_part = parts[0]

    for part in parts[1:]:
        if part.startswith("before="):
            try:
                days_before = int(part.split('=')[1])
            except (IndexError, ValueError):
                print(f"Warning: Invalid before value in {part}, using default {days_before}")
        elif part.startswith("after="):
            try:
                days_after = int(part.split('=')[1])
            except (IndexError, ValueError):
                print(f"Warning: Invalid after value in {part}, using default {days_after}")

    return date_part, days_before, days_after