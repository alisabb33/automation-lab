# Date Math

## Problem
I often need to calculate dates relative to “today” or another reference date (e.g., +18 days, −7 days, next occurrence), and present them in a human-readable format. Many tools make this harder than it should be.

## Constraints
- Must be deterministic and explicit
- Must handle month/year boundaries correctly
- No reliance on system locale quirks
- Simple enough to audit at a glance

## Solution
Use standard date arithmetic with an explicit reference date and offset (in days). All calculations are done in UTC date space to avoid time-of-day edge cases.

## Example
**Input**
- Reference date: `2026-01-10`
- Offset: `+18 days`

**Output**
- Result date: `2026-01-28`

**Input**
- Reference date: `2026-01-03`
- Offset: `-7 days`

**Output**
- Result date: `2025-12-27`

## Python reference implementation
See `date_offset.py` for a minimal, readable implementation.

## Notes
- This logic mirrors what I use in automation tools (e.g., scheduling, alarms) where clarity matters more than cleverness.
- Timezones and times-of-day are intentionally excluded.
