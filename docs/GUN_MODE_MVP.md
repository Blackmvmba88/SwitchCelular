# Gun Mode MVP

## Goal

Use an Android phone as a motion pistol controller for desktop games.

## Scope

This document describes the first playable implementation path for the "phone as pistol" mode.

The objective is to keep the core small, explicit, and testable while the implementation grows in layers.

## Runtime Layers

1. `sensor_core`
   - Read gyroscope, accelerometer, and magnetometer samples.
   - Normalize timestamps, units, and sensor status.

2. `fusion_core`
   - Convert raw sensor samples into stable orientation frames.
   - Emit quaternion plus `yaw`, `pitch`, and `roll`.

3. `calibration_core`
   - Recenter the current aim.
   - Apply dead zones and sensitivity.
   - Compensate for drift.

4. `transport_core`
   - Send aim packets to the desktop host.
   - MVP transport is UDP.

5. `mapper_core`
   - Convert calibrated orientation into aim deltas.
   - Emit relative mouse movement on the host.

6. `trigger_core`
   - Map touch or physical inputs to fire, reload, zoom, and melee.

7. `profile_core`
   - Load and validate the pistol profile.
   - Keep game logic out of the core.

8. `diagnostics_core`
   - Track latency, jitter, packet loss, and drift score.

9. `regression_core`
   - Record traces.
   - Compare against goldens.
   - Detect trajectory drift.

## MVP Flow

```text
phone sensors
  ↓
sensor_core
  ↓
fusion_core
  ↓
calibration_core
  ↓
mapper_core
  ↓
transport_core
  ↓
desktop_host
  ↓
virtual mouse / virtual axis
```

## Required Features

- Read motion sensors.
- Produce orientation frames.
- Recenter on demand.
- Apply sensitivity and dead zones.
- Send aim packets over UDP.
- Receive packets on desktop.
- Emit relative mouse movement.
- Fire with a touch button.

## Non Goals

- No game-specific integration.
- No BLE in v1.
- No USB in v1.
- No advanced recoil model in v1.
- No multiplayer-specific logic.

## Suggested Commit Order

1. Create the workspace structure.
2. Define sensor, orientation, and aim packet contracts.
3. Add sensor normalization.
4. Add basic fusion and orientation output.
5. Add calibration transforms.
6. Add aim mapping.
7. Add UDP transport.
8. Add desktop receiver.
9. Add mouse-relative output.
10. Add pistol profile loading.
11. Add trigger handling.
12. Add diagnostics.
13. Add regression traces.
