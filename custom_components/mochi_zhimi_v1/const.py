"""Constants for the Mochi Zhimi Purifier V1 integration.

Built for Warren's 1st-gen Mijia Air Purifier (zhimi.airpurifier.v1,
AC-M1-CA). Only device features verified live on the unit are exposed:

- reads:  aqi (PM2.5 in ug/m3), mode, filter1_life, motor1_speed,
          motor2_speed, bright (illuminance), led, buzzer
- writes: set_mode (auto/silent/strong/idle), set_led, set_buzzer,
          reset_filter1 (the filter counter reset)

Deliberately NOT exposed (dead on this firmware, all verified):
set_power / power property, favorite mode & level, child lock,
temperature, humidity, average AQI, filter hours, LED brightness.

Power on/off is emulated honestly through mode: "idle" is the unit's
standby (motors at 0), any run mode wakes it. This mirrors what the
Xiaomi Home app does for this model.
"""

DOMAIN = "mochi_zhimi_v1"

CONF_HOST = "host"
CONF_TOKEN = "token"
CONF_NAME = "name"

MODEL = "zhimi.airpurifier.v1"

# Properties the unit actually answers, in one get_prop call.
PROPS = [
    "aqi",
    "mode",
    "filter1_life",
    "motor1_speed",
    "motor2_speed",
    "bright",
    "led",
    "buzzer",
]

# Wire mode -> display label.
MODE_LABELS = {
    "auto": "Auto",
    "silent": "Silent",
    "strong": "Strong",
    "idle": "Idle",
}
RUN_MODES = ["auto", "silent", "strong"]
DEFAULT_RUN_MODE = "auto"

SCAN_SECONDS = 30
