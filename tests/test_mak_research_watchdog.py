"""Static guards for MAK research watchdog.

The script runs on MAK through cron, but the repo is the source of truth. These
tests protect the operational contract without starting real services.
"""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WATCHDOG = ROOT / "cultura" / "mak_research" / "watchdog.sh"


def test_cola_requires_ntfy_inbox_before_watchdog_starts_it():
    source = WATCHDOG.read_text(encoding="utf-8")
    assert "NTFY_TOPIC_IN" in source
    assert "grep -Eq '^[[:space:]]*NTFY_TOPIC_IN=.+$'" in source
    assert source.index("NTFY_TOPIC_IN") < source.index('ensure_unit "$QUEUE_UNIT"')


def test_missing_ntfy_inbox_is_reported_once_not_every_cron_tick():
    source = WATCHDOG.read_text(encoding="utf-8")
    assert 'COLA_DISABLED="$BASE/.cola.disabled.missing_ntfy"' in source
    assert 'if [ ! -f "$COLA_DISABLED" ]; then' in source
    assert ': > "$COLA_DISABLED"' in source
    assert "cola.py disabled: NTFY_TOPIC_IN is missing" in source
