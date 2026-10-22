"""Sensors for the Mochi Zhimi Purifier V1.

PM2.5 is what the device measures (its raw 'aqi' property is a PM2.5
concentration in ug/m3, despite the name). The AQI sensor is a true
US EPA AQI calculated from that PM2.5 reading.
"""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    LIGHT_LUX,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .client import us_aqi_from_pm25
from .const import DOMAIN
from .entity import ZhimiV1Entity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities(
        [
            Pm25Sensor(coordinator, entry),
            UsAqiSensor(coordinator, entry),
            FilterLifeSensor(coordinator, entry),
            MotorSpeedSensor(coordinator, entry, 1),
            MotorSpeedSensor(coordinator, entry, 2),
            IlluminanceSensor(coordinator, entry),
        ]
    )


class Pm25Sensor(ZhimiV1Entity, SensorEntity):
    _attr_name = "PM2.5"
    _attr_device_class = SensorDeviceClass.PM25
    _attr_native_unit_of_measurement = CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "pm25")

    @property
    def native_value(self):
        return self.coordinator.data.get("aqi")


class UsAqiSensor(ZhimiV1Entity, SensorEntity):
    _attr_name = "AQI (US)"
    _attr_device_class = SensorDeviceClass.AQI
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:weather-hazy"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "us_aqi")

    @property
    def native_value(self):
        return us_aqi_from_pm25(self.coordinator.data.get("aqi"))


class FilterLifeSensor(ZhimiV1Entity, SensorEntity):
    _attr_name = "Filter Life"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:air-filter"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "filter_life")

    @property
    def native_value(self):
        return self.coordinator.data.get("filter1_life")


class MotorSpeedSensor(ZhimiV1Entity, SensorEntity):
    _attr_native_unit_of_measurement = "rpm"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:fan"

    def __init__(self, coordinator, entry, motor: int) -> None:
        super().__init__(coordinator, entry, f"motor{motor}_speed")
        self._motor = motor
        self._attr_name = "Motor Speed" if motor == 1 else "Motor 2 Speed"

    @property
    def native_value(self):
        return self.coordinator.data.get(f"motor{self._motor}_speed")


class IlluminanceSensor(ZhimiV1Entity, SensorEntity):
    _attr_name = "Illuminance"
    _attr_device_class = SensorDeviceClass.ILLUMINANCE
    _attr_native_unit_of_measurement = LIGHT_LUX
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "illuminance")

    @property
    def native_value(self):
        return self.coordinator.data.get("bright")
