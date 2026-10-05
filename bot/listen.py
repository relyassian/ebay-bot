"""Keeps the bot responsive for ~25 minutes per GitHub Actions run (the run then starts the next one):
- Telegram messages answered within seconds (long polling),
- new eBay sales checked every 10 minutes, approved drafts listed right away,
- state committed back to the repo after anything changes."""
from __future__ import annotations

import subprocess
import time

from bot.alerts import send


def _save(note: str) -> None:
    cmds = [["git", "add", "data", "plans"], ["git", "diff", "--cached", "--quiet"]]
    subprocess.run(cmds[0], check=False)
    if subprocess.run(cmds[1]).returncode == 0:
        return
    subprocess.run(["git", "commit", "-qm", f"bot: {note}"], check=False)
    subprocess.run(["bash", "scripts/push_state.sh"], check=False)   # retries if another job pushed at the same time


def _pull() -> None:
    """Pick up what other jobs committed (new price raises, drafts) before answering Rafael."""
    subprocess.run(["git", "pull", "-q", "--rebase", "--autostash"], check=False)


def run(minutes: int, live: bool) -> None:
    from bot import sales
    from bot.newlistings import inbox, publish
    end, next_sales = time.time() + minutes * 60, 0.0
    while time.time() < end:
        changed = False
        if time.time() >= next_sales:
            try:
                for a in sales.run():
                    send(a); changed = True
                for t in publish(live):
                    send(t); changed = True
            except Exception as e:
                print("sales/publish error:", e)
            next_sales = time.time() + 600
        _pull()
        try:
            for t in inbox(live, wait=min(50, max(1, int(end - time.time())))):
                send(t); changed = True
        except Exception as e:
            print("inbox error:", e); time.sleep(20)
        if changed:
            _save("alerts/replies")
    _save("listen state")
