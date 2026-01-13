#!/usr/bin/env python3
"""
Alarm escalation simulation (portable proof-of-logic).

Models the same state machine used in MacroDroid:
- wakeActive controls whether escalation continues
- alarmVol increases by step each tick
- ACK requires recent movement (now_ms - lastMoveTimeMs <= MOVE_WINDOW_MS)

Usage examples:
  python simulate_alarm_escalation.py --scenario move_required
  python simulate_alarm_escalation.py --scenario ack_success
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import argparse


@dataclass
class Config:
    move_window_ms: int = 60_000
    step_ms: int = 60_000
    max_steps: int = 12
    start_volume: int = 40
    volume_step: int = 10
    volume_cap: int = 100


@dataclass
class State:
    wake_active: int = 1
    alarm_vol: int = 40
    last_move_time_ms: int = 0
    now_ms: int = 0


def clamp(n: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, n))


def log_line(lines: List[str], msg: str) -> None:
    lines.append(msg)


def ack(state: State, cfg: Config, lines: List[str]) -> None:
    """Attempt to ACK. Enforces move-before-ack."""
    delta = state.now_ms - state.last_move_time_ms
    if delta > cfg.move_window_ms:
        log_line(lines, f"ACK: REJECTED (no recent movement; delta_ms={delta})")
        return
    state.wake_active = 0
    log_line(lines, f"ACK: ACCEPTED (delta_ms={delta}) -> wakeActive=0")


def move(state: State, lines: List[str]) -> None:
    """Simulate a movement event updating lastMoveTimeMs."""
    state.last_move_time_ms = state.now_ms
    log_line(lines, f"MOVE: lastMoveTimeMs updated to {state.last_move_time_ms}")


def tick(state: State, cfg: Config, lines: List[str], step_index: int) -> None:
    """One escalation tick."""
    # "Set volumes"
    log_line(lines, f"TICK {step_index:02d}: wakeActive={state.wake_active} alarmVol={state.alarm_vol}")

    # "Escalation actions" (represented as log lines)
    log_line(lines, "  actions: set volumes; vibrate; (optional torch/audio)")

    # Wait STEP_MS
    state.now_ms += cfg.step_ms

    # If acknowledged, stop
    if state.wake_active == 0:
        log_line(lines, "  loop: wakeActive=0 -> stopping escalation")
        return

    # Increase volume for next tick
    next_vol = clamp(state.alarm_vol + cfg.volume_step, 0, cfg.volume_cap)
    if next_vol != state.alarm_vol:
        log_line(lines, f"  volume: {state.alarm_vol} -> {next_vol}")
    state.alarm_vol = next_vol


def run_scenario(scenario: str, cfg: Config) -> List[str]:
    lines: List[str] = []
    state = State(wake_active=1, alarm_vol=cfg.start_volume, last_move_time_ms=0, now_ms=0)

    log_line(lines, f"SCENARIO={scenario}")
    log_line(lines, f"CONFIG: move_window_ms={cfg.move_window_ms} step_ms={cfg.step_ms} max_steps={cfg.max_steps} "
                    f"start_volume={cfg.start_volume} volume_step={cfg.volume_step} cap={cfg.volume_cap}")
    log_line(lines, "-" * 60)

    # Schedule events by tick number (after tick increments time, we can do actions at new now_ms if desired).
    # For simplicity, we'll model events as happening at specific step indices BEFORE running that tick.
    # step_index starts at 1.

    for step_index in range(1, cfg.max_steps + 1):
        # Scenario-specific events
        if scenario == "move_required":
            # User tries to ACK at step 3 without moving -> rejected.
            if step_index == 3:
                ack(state, cfg, lines)
            # User moves at step 4 (updates lastMoveTimeMs), then ACK at step 5 -> accepted.
            if step_index == 4:
                move(state, lines)
            if step_index == 5:
                ack(state, cfg, lines)

        elif scenario == "ack_success":
            # User moves early, then ACK within window.
            if step_index == 2:
                move(state, lines)
            if step_index == 3:
                ack(state, cfg, lines)

        elif scenario == "no_ack":
            # Never ACK; runs to max steps.
            pass

        else:
            raise ValueError(f"Unknown scenario: {scenario}")

        # Stop if already acknowledged before ticking
        if state.wake_active == 0:
            log_line(lines, "STATE: wakeActive=0 before tick -> escalation ends")
            break

        tick(state, cfg, lines, step_index)

        # Stop if tick ended due to ACK state
        if state.wake_active == 0:
            break

    log_line(lines, "-" * 60)
    if state.wake_active == 1:
        log_line(lines, "RESULT: Max steps reached (still wakeActive=1)")
    else:
        log_line(lines, "RESULT: Acknowledged (wakeActive=0)")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scenario",
        choices=["move_required", "ack_success", "no_ack"],
        default="move_required",
        help="Which event pattern to simulate",
    )
    parser.add_argument("--start-volume", type=int, default=40)
    parser.add_argument("--max-steps", type=int, default=12)
    parser.add_argument("--step-ms", type=int, default=60_000)
    parser.add_argument("--move-window-ms", type=int, default=60_000)
    parser.add_argument("--volume-step", type=int, default=10)
    args = parser.parse_args()

    cfg = Config(
        move_window_ms=args.move_window_ms,
        step_ms=args.step_ms,
        max_steps=args.max_steps,
        start_volume=args.start_volume,
        volume_step=args.volume_step,
    )

    lines = run_scenario(args.scenario, cfg)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
