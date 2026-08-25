"""CLI for the C04 read-only media observer."""

from __future__ import annotations

import argparse
import sys

from media_observer import DEFAULT_MEDIA_PATH, observe_media, json_document


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Observe one MP4 with ffprobe")
    parser.add_argument("media", nargs="?", default=str(DEFAULT_MEDIA_PATH))
    parser.add_argument("--ffprobe", default="ffprobe")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args(argv)
    observation = observe_media(
        args.media,
        ffprobe_bin=args.ffprobe,
        timeout_seconds=args.timeout,
    )
    sys.stdout.write(json_document(observation) + "\n")
    return 0 if observation.get("status") == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())
