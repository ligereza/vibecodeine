import sys
from math import floor

def seconds_to_timecode(seconds: float, fps: int = 30) -> str:
    if seconds < 0 or fps <= 0:
        raise ValueError("seconds must be >= 0 and fps must be > 0")
    
    total_frames = round(seconds * fps + 0.5)
    ff = total_frames % fps
    ss = (total_frames // fps) % 60
    mm = ((total_frames // fps) // 60) % 60
    hh = (((total_frames // fps) // 60) // 60)
    
    return f"{hh:02d}:{mm:02d}:{ss:02d}:{ff:02d}"

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert seconds to timecode in the format HH:MM:SS:FF at 30 fps.")
    parser.add_argument("seconds", type=float, help="Time in seconds to convert")
    parser.add_argument("-f", "--fps", type=int, default=30, help="Frames per second (default is 30)")
    
    args = parser.parse_args()
    
    try:
        assert args.seconds >= 0, "seconds must be >= 0"
        assert args.fps > 0, "fps must be > 0"
        
        timecode = seconds_to_timecode(args.seconds, args.fps)
        print(timecode)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except AssertionError as e:
        print(f"Assertion failed: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not sys.argv[1:]:  # Run asserts when no arguments are provided
        try:
            assert seconds_to_timecode(3661.0, 30) == "01:01:01:00"
            assert seconds_to_timecode(1/30, 30) == "00:00:00:01"
            assert seconds_to_timecode(3599.999, 30) == "01:00:00:00"
            print("PRUEBAS OK")
        except AssertionError as e:
            print(f"Assertion failed in test mode: {e}", file=sys.stderr)
            sys.exit(1)
