# Architecture

A map of the code for contributors. For installation and usage, see the
[README](README.md).

## Design principles

1. **Verified surface only.** The integration exposes exactly the features
   the `zhimi.airpurifier.v1` firmware provably answers over the miio LAN
   protocol — no more. Every property in the read set and every write method
   was verified live against real hardware. Speculative features are worse
   than missing ones: on this firmware they error, return constants, or lie.
2. **Local only.** All traffic is LAN miio via
   [python-miio](https://github.com/rytilahti/python-miio). No cloud account,
   no cloud API, no discovery. (`iot_class: local_polling`.)
3. **Honest emulation.** Where the firmware lacks a capability Home Assistant
   users expect (a power switch), the integration emulates it on top of a
   mechanism that really works, and documents the substitution rather than
   hiding it.

## System overview

```
Home Assistant
  └─ config entry (host + token, stored by HA)
       └─ ZhimiV1Coordinator ── polls every 30 s ──┐
            ├─ sensor × 6                            │ executor
            ├─ switch × 3                            ▼
            ├─ select × 1                    ZhimiV1Client
            └─ button × 1                    (python-miio Device)
                                                     │ miio / UDP 54321
                                                     ▼
                                          zhimi.airpurifier.v1 (LAN)
```

Entities never talk to the device directly. Reads flow through the
coordinator's single poll; writes go through coordinator methods that call
the client in the executor and then patch local state.

## Components

| File | Responsibility |
| --- | --- |
| `__init__.py` | Entry setup/teardown: build client + coordinator, first refresh (`ConfigEntryNotReady` on failure so HA retries), forward the four platforms. |
| `const.py` | The contract: domain, model id, the exact property list (`PROPS`), the mode vocabulary, poll interval. The header comment is the authoritative list of what is and is not exposed, and why. |
| `client.py` | Thin synchronous wrapper over `miio.Device.send` — plus the pure `us_aqi_from_pm25()` function. |
| `coordinator.py` | `DataUpdateCoordinator` (30 s): owns the polling cycle, brokers all writes, tracks `last_run_mode`, applies optimistic state patches after writes. |
| `entity.py` | `ZhimiV1Entity` base (`CoordinatorEntity`): unique ids of the form `<entry_id>_<key>`, one `DeviceInfo` per config entry. |
| `config_flow.py` | UI setup: host, token, name. Validates by connecting and reading before creating the entry. |
| `sensor.py` | PM2.5, US AQI, filter life, motor 1 & 2 speed, illuminance. |
| `switch.py` | Power (mode-based, see below), LED, buzzer. |
| `select.py` | Mode select: Auto / Silent / Strong / Idle. |
| `button.py` | Reset Filter button. |

## The wire contract

One `get_prop` call per poll, with exactly these properties (in
`const.PROPS`): `aqi`, `mode`, `filter1_life`, `motor1_speed`,
`motor2_speed`, `bright`, `led`, `buzzer`. The result list is zipped
positionally onto the property names.

Writes:

| Intent | Wire call |
| --- | --- |
| Set mode | `set_mode [auto\|silent\|strong\|idle]` |
| LED | `set_led [on\|off]` |
| Buzzer | `set_buzzer [on\|off]` |
| Reset filter counter | `reset_filter1` (no params) |

Deliberately absent, because this firmware rejects or ignores them
(all verified): `set_power` and the `power` property, the `favorite`
mode and favourite level, child lock, temperature, humidity, average AQI,
filter hours used, LED brightness levels, and `reset_filter_time`
(the working reset method is `reset_filter1`).

## Key decisions

### Power is a mode, not a property

This firmware has no working power control: `set_power` returns
method-not-supported. Its standby state is mode `idle`, in which both
motors read 0 rpm, and setting any run mode (`auto` / `silent` /
`strong`) wakes it — the same net effect the vendor's cloud app produces
for this model. So:

- `PowerSwitch.is_on` is derived: `mode != "idle"`. The switch can never
  disagree with the device.
- Turning **off** sends `set_mode idle`; turning **on** sends
  `set_mode <last_run_mode>`. The coordinator remembers the last non-idle
  mode it has seen (default `auto`), so the purifier resumes what it was
  doing instead of always restarting in a fixed mode.
- `Idle` is also offered in the Mode select, making the model explicit
  rather than hidden behind the switch.

### The device's "aqi" is not an AQI

The raw `aqi` property is a PM2.5 **concentration** in µg/m³ despite its
name. The integration surfaces it truthfully as the PM2.5 sensor, and
computes a genuine US EPA AQI from it in `us_aqi_from_pm25()`:
concentration truncated to 0.1 µg/m³, piecewise-linear interpolation over
the EPA breakpoints, rounded to the nearest integer, capped at 500. It is
an instantaneous conversion of the current reading — not a 24-hour
NowCast average — and the README says so.

### Optimistic patching after writes

A write (`coordinator.async_set_*`) runs the client call in the executor
and, on success, immediately patches the coordinator's data
(`async_set_updated_data`) so the UI reflects the change at once instead
of up to 30 s later at the next poll. The next poll reconciles with the
device, which remains the source of truth. Filter reset is the exception:
it requests a full refresh, because the interesting effect (life back to
100%) is a device-side value worth reading rather than assuming.

### Config flow validates, then identifies by MAC

Setup performs a real `info()` + `fetch()` before creating the entry,
fails with `cannot_connect` if the device cannot be reached or read, and
rejects a reachable device whose model is not `zhimi.airpurifier.v1`
(`wrong_model`). The entry's unique id is the device MAC (falling back to
the host), so re-adding the same unit is detected. The token lives only
in the config entry's data, in Home Assistant's own storage.

## Failure handling

- Poll failure (`DeviceException`) → `UpdateFailed` → all entities go
  unavailable until a poll succeeds; nothing is cached fictitiously.
- First-refresh failure during setup → `ConfigEntryNotReady`, so Home
  Assistant retries setup with backoff instead of loading a dead entry.
- No retries are implemented inside the client: the 30 s coordinator
  cycle is the retry.

## Non-goals and limitations

- **One model only**: `zhimi.airpurifier.v1` (AC-M1-CA). Other generations
  speak different property sets — the 2nd gen's sensor board uses a
  different dust-sensor protocol entirely — and are out of scope by
  design; the config flow refuses them.
- No fan entity: the mode-based switch + select pair models this device
  more truthfully than a fan with a percentage it cannot honour.
- No `favorite` mode: the firmware rejects it.
- Requires the device's miio token (see README for extraction options)
  and LAN reachability from Home Assistant.
