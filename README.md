# mochi_zhimi_v1 — Zhimi Air Purifier V1 (Mochi)

A deliberately small, local-only Home Assistant integration for the
1st-gen Mijia Air Purifier (**zhimi.airpurifier.v1**, AC-M1-CA).
Written after two existing integrations both failed on this unit's
firmware:

- **Xiaomi Miot (cloud)**: sensors/mode/light work; power reads stuck at
  false and power writes never land.
- **xiaomi_airpurifier_ng (local)**: rich sensors, but its fan power is
  the standard miio `set_power`, which this unit rejects
  (`method_not_supported`), so its fan state sits at "unknown".

## The key discovery

This firmware has **no working power property or `set_power`** — but it
doesn't need one. Its standby state is simply **mode `idle`** (motors at
0 rpm), and `set_mode` to any run mode wakes it. That is what the Xiaomi
Home app achieves through the cloud. The integration's Power switch is
therefore mode-based and always truthful: on ⇔ mode ≠ idle. Turning it
on restores the last run mode (default Auto).

## Verified wire protocol (live against the unit, 2026-10-20)

Working reads (single `get_prop`): `aqi` (= PM2.5 in µg/m³ despite the
name), `mode`, `filter1_life`, `motor1_speed`, `motor2_speed`, `bright`
(illuminance), `led`, `buzzer`. The two motor speeds are real: the gen-1
purifier is a dual-motor, 4-air-duct design (the Purifier 2 replaced it
with a single-motor design to shrink the body), so each motor reports
its own tachometer and they legitimately run at different rpm.

Working writes: `set_mode` with `auto` / `silent` / `strong` / `idle`,
`set_led`, `set_buzzer`, and `reset_filter1` (no params — note:
`reset_filter_time` is rejected).

Dead on this firmware (all probed, deliberately not exposed):
`set_power`, power property, `favorite` mode, `set_favorite_level`,
child lock (read null, write unsupported), temperature, humidity,
average AQI, filter hours used, LED brightness, volume, learn mode,
auto detect, use time, purify volume.

## Entities (device "Mijia Air Mochi")

- `switch.*_power` — mode-based standby/wake (see above)
- `select.*_mode` — Auto / Silent / Strong / Idle
- `switch.*_led`, `switch.*_buzzer`
- `sensor.*_pm2_5` — PM2.5, µg/m³
- `sensor.*_aqi_us` — **US EPA AQI calculated from PM2.5**
  (piecewise-linear breakpoints, instantaneous, capped at 500)
- `sensor.*_filter_life` — %
- `sensor.*_motor_speed`, `sensor.*_motor_2_speed` — rpm
- `sensor.*_illuminance` — lx
- `button.*_reset_filter` — sends `reset_filter1`

Poll interval: 30 s. Config flow: device IP + miio token (+ name).

## Install

Copy `custom_components/mochi_zhimi_v1` into HA's
`config/custom_components/`, restart HA, then
Settings → Devices & Services → Add Integration →
"Zhimi Air Purifier V1 (Mochi)". Requires `python-miio` (declared in the
manifest; HA installs it automatically).

## Credits and license

This integration stands on the Xiaomi miIO ecosystem's shoulders, and
the credit belongs upstream:

- **Teemu Rytilahti (rytilahti)** — author of `python-miio`, the
  library every miIO integration (this one included) talks through.
- **syssi** — author of the original `xiaomi_airpurifier` Home
  Assistant integration, the lineage this device support descends from.
- **dzerik** — author of `xiaomi_airpurifier_ng`
  (https://github.com/dzerik/xiaomi_airpurifier_ng), the maintained fork
  of syssi's work whose local readouts (motor speeds, illuminance)
  showed what this hardware can honestly report, and against which this
  integration was compared during development.

License: Apache License 2.0, matching the upstream lineage (the full
license text ships in `LICENSE` in the published repository).
