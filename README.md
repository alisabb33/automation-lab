# automation-lab

Three small projects that solve real problems (alarm escalation logic, date math utilities, and a log parser).
Each project includes a short spec, a working implementation (when applicable), and example inputs/outputs.

## Projects
- [Alarm Escalation](projects/alarm_escalation/README.md)
- [Date Math](projects/date_math/README.md)
- [Log Parser](projects/log_parser/README.md)

## Why this repo exists
I want clear, reviewable proof of practical automation/problem-solving work: define a problem, document constraints, implement or specify, and show examples.


# Alarm Escalation (Spec)

## Problem
I need a reliable wake-up alarm that escalates intensity over time and requires phone movement before acknowledging.

## Constraints
- Runs on Android using MacroDroid (no custom Android app).
- Must not be easy to dismiss while half-asleep.
- Escalation should stop immediately after a successful "ACK wake" action.

## Behavior (high level)
- Alarm sequence starts at scheduled time.
- Escalates in steps: volume up + vibration + optional torch + loud audio app.
- Repeats until acknowledged OR max duration reached.
- Acknowledge requires recent motion (movement within the last 60 seconds).

## Artifacts
- Full spec: `alarm_escalation_spec.md`



# Alarm Escalation Spec (MacroDroid-oriented)

## Variables
- `wakeActive` (0/1): whether alarm sequence is active
- `alarmVol` (0–100): current alarm/media volume target
- `lastMoveTime` (ms epoch): last detected movement timestamp
- `escalationStep` (int): optional, current escalation step

## Events / Triggers (conceptual)
1. **Start Alarm**: scheduled time OR manual test trigger
2. **Movement Detected**: accelerometer/shake/step/any motion trigger updates `lastMoveTime`
3. **ACK Wake**: user action (quick tile/button/notification action)

## State machine
### State: Idle
- `wakeActive = 0`

### State: Escalating
- Set `wakeActive = 1`
- Initialize:
  - `alarmVol = 20` (example)
  - `escalationStep = 0`
- Loop for N cycles or until `wakeActive = 0`:
  1. Apply volumes to Alarm + Media = `alarmVol`
  2. Escalation actions:
     - Vibrate
     - Optional: Torch ON
     - Optional: Launch audio app / play loud sound
  3. Wait 60 seconds
  4. If `wakeActive = 0` → exit loop
  5. Increase `alarmVol` by +10 (cap at 100)

### State: Acknowledged
- Triggered only by ACK Wake **and** recent movement:
  - if `(nowMs - lastMoveTime) <= 60000` then `wakeActive = 0`
  - else show "Move phone then ACK again" message and keep `wakeActive = 1`

## Acceptance criteria
- Alarm escalates at least every 60 seconds while active.
- User cannot acknowledge without movement in the past 60 seconds.
- After successful acknowledge, escalation stops within 1 cycle.
