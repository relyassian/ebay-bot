"""Test config pinned to the original $100 floor so the profit-math tests keep their meaning
when config.yaml's floor is changed (Rafael, Nov 3: floor 50)."""
from bot.config import load_config as _real


def load_config(*a, **k):
    c = _real(*a, **k)
    c["profit"] = dict(c["profit"], floor=100)
    return c
