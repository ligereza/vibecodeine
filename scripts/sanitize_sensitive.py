#!/usr/bin/env python3
"""sanitize_sensitive.py — Reemplaza información sensible por placeholders"""

import re
from pathlib import Path

PATTERNS = [
    (r'password\s*=\s*["\'][^"\']+["\']', 'password = "REDACTED"'),
    (r'api_key\s*=\s*["\'][^"\']+["\']', 'api_key = "REDACTED"'),
    (r'token\s*=\s*["\'][^"\']+["\']', 'token = "REDACTED"'),
    (r'C:\\\\Users\\\\[^\\\\]+', 'C:\\\\Users\\\\USER'),
    (r'/home/USER/]+', '/home/USER
