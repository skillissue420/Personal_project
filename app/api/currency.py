"""Frankfurter exchange-rate client."""

import requests

TIMEOUT = 12


def get_exchange_rate(query="USD PHP"):
    parts = query.upper().split()
    base, target = (parts + ["USD", "PHP"])[:2] if len(parts) >= 2 else ("USD", "PHP")
    response = requests.get(
        "https://api.frankfurter.dev/v1/latest",
        params={"base": base, "symbols": target}, timeout=TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()
    rate = data["rates"].get(target)
    if rate is None:
        raise ValueError("Use ISO currency codes, for example: USD PHP")
    return f"{base} to {target}", f"1 {base} = {rate:,.4f} {target}\nUpdated: {data['date']}"
