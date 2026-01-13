# Alarm Escalation

## Problem
I need a wake-up alarm flow that escalates until I’m actually awake, while still allowing a deliberate “acknowledge” action. Normal alarms are too easy to silence half-asleep.

## Constraints
- Platform: Android + MacroDroid
- Must work without network access
- Must prevent accidental dismissal while half-asleep
- Must enforce “must move phone” before ACK
- Must be maintainable (few macros, clear variables)

## Solution (two layers)
### Layer A — MacroDroid (real device)
A state variable (`wakeActive`) controls whether escalation is active. While active, an escalation loop increases alert intensity (volume/vibration/optional torch/audio) once per minute until:
- user ACKs correctly (and has moved recently), or
- max duration is reached.

Movement is enforced by comparing `now_ms - lastMoveTime_ms`. If the user hasn’t moved within the window, ACK is rejected and escalation continues.

### Layer B — Python simulation (reviewable proof)
A small Python script simulates the same state machine:
- escalates volume in steps
- enforces move-before-ack
- logs each tick and decision
This gives reviewers something runnable even if they don’t know MacroDroid.

## Variables / State
- `wakeActive` (0/1): whether escalation is running
- `alarmVol` (0–100): current alarm/media volume used for escalation
- `lastMoveTimeMs` (epoch ms): last detected significant movement timestamp

Constants:
- `MOVE_WINDOW_MS = 60000` (must have moved in last 60s to ACK)
- `STEP_MS = 60000` (escalation tick interval)
- `MAX_STEPS = 12` (max escalation ticks = 12 minutes)

## MacroDroid mapping (high level)
- Macro “Escalate”:
  - Runs while `wakeActive = 1`
  - Each loop tick:
    - set volumes to `alarmVol`
    - vibrate / optional torch / optional loud audio
    - wait `STEP_MS`
    - if `wakeActive = 0` break
    - `alarmVol = min(alarmVol + 10, 100)`
- Macro “ACK (must move)”:
  - Triggered by your ACK action (tile/button/notification action)
  - If `nowMs - lastMoveTimeMs > MOVE_WINDOW_MS`: show “Move phone then ACK again” and exit
  - Else: `wakeActive = 0` (stop escalation)

## Python simulation
File: `simulate_alarm_escalation.py`

Example runs:
- Reject ACK if no movement
- Accept ACK after movement within window

## Notes / Future improvements
- Add a “vacation override” variable/date
- Log events to a file from MacroDroid for debugging (start, ACK, max reached)
