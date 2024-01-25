"""
    Support for Niu Scooters by Marcel Westra.
    Asynchronous version implementation by Giovanni P. (@pikka97)
"""
from datetime import timedelta
import logging

from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

from .api import NiuApi
from .const import *

import math

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    niu_auth = entry.data.get(CONF_AUTH, None)
    if niu_auth == None:
        _LOGGER.error(
            "The authenticator of your Niu integration is None.. can not setup the integration..."
        )
        return False

    username = niu_auth[CONF_USERNAME]
    password = niu_auth[CONF_PASSWORD]
    scooter_id = niu_auth[CONF_SCOOTER_ID]
    sensors_selected = niu_auth[CONF_SENSORS]

    api = NiuApi(username, password, scooter_id)
    await hass.async_add_executor_job(api.initApi)

    # add sensors
    devices = []
    for sensor in sensors_selected:
        if sensor != "LastTrackThumb":
            sensor_config = SENSOR_TYPES[sensor]
            devices.append(
                NiuSensor(
                    hass,
                    api,
                    sensor,
                    sensor_config[0],
                    sensor_config[1],
                    sensor_config[2],
                    sensor_config[3],
                    api.sensor_prefix,
                    sensor_config[4],
                    api.sn,
                    sensor_config[5],
                )
            )
        else:
            # Last Track Thumb sensor will be used as camera... now just skip it
            pass

    async_add_entities(devices)
    return True


class NiuSensor(Entity):
    def __init__(
        self,
        hass,
        api: NiuApi,
        name,
        sensor_id,
        uom,
        id_name,
        sensor_grp,
        sensor_prefix,
        device_class,
        sn,
        icon,
    ):
        self._unique_id = "sensor.niu_scooter_" + sn + "_" + sensor_id
        self._name = (
            "NIU Scooter " + sensor_prefix + " " + name
        )  # Scooter name as sensor prefix
        self._hass = hass
        self._uom = uom
        self._api = api
        self._device_class = device_class
        self._id_name = id_name  # info field for parsing the URL
        self._sensor_grp = sensor_grp  # info field for choosing the right URL
        self._icon = icon
        self._state = 0

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def name(self):
        return self._name

    @property
    def unit_of_measurement(self):
        return self._uom

    @property
    def icon(self):
        return self._icon

    @property
    def state(self):
        return self._state

    @property
    def device_class(self):
        return self._device_class

    @property
    def device_info(self):
        device_name = (
                "NIU Scooter - " + self._api.sensor_prefix
        ) # "Niu E-scooter"
        return {
            "identifiers": {("niu", device_name)},
            "name": device_name,
            "manufacturer": "NIU",
            "model": "1.0.202401251631",
        }

    @property
    def extra_state_attributes(self):
        if self._sensor_grp == SENSOR_TYPE_MOTO and self._id_name == "isConnected":

            lng = self._api.getDataPos("lng")
            lat = self._api.getDataPos("lat")
            _lng, _lat = gcj02towgs84(lng, lat)

            return {
                "bmsId": self._api.getDataBat("bmsId"),
                "latitude": _lat,
                "longitude": _lng,
                "gsm": self._api.getDataMoto("gsm"),
                "gps": self._api.getDataMoto("gps"),
                "time": self._api.getDataDist("time"),
                "range": self._api.getDataMoto("estimatedMileage"),
                "battery": self._api.getDataBat("batteryCharging"),
                "battery_grade": self._api.getDataBat("gradeBattery"),
                "centre_ctrl_batt": self._api.getDataMoto("centreCtrlBattery"),
            }

    @Throttle(timedelta(minutes=2))
    async def async_update(self):
        if self._sensor_grp == SENSOR_TYPE_BAT:
            await self._hass.async_add_executor_job(self._api.updateBat)
            self._state = self._api.getDataBat(self._id_name)

        elif self._sensor_grp == SENSOR_TYPE_MOTO:
            await self._hass.async_add_executor_job(self._api.updateMoto)
            self._state = self._api.getDataMoto(self._id_name)

        elif self._sensor_grp == SENSOR_TYPE_POS:
            await self._hass.async_add_executor_job(self._api.updateMoto)
            self._state = self._api.getDataPos(self._id_name)

        elif self._sensor_grp == SENSOR_TYPE_DIST:
            await self._hass.async_add_executor_job(self._api.updateBat)
            self._state = self._api.getDataDist(self._id_name)

        elif self._sensor_grp == SENSOR_TYPE_OVERALL:
            await self._hass.async_add_executor_job(self._api.updateMotoInfo)
            self._state = self._api.getDataOverall(self._id_name)

        elif self._sensor_grp == SENSOR_TYPE_TRACK:
            await self._hass.async_add_executor_job(self._api.updateTrackInfo)
            self._state = self._api.getDataTrack(self._id_name)

PI = 3.1415926535897932384626
a = 6378245.0
ee = 0.00669342162296594323

def gcj02towgs84(lng, lat):
    lat = float(lat)
    lng = float(lng)

    if out_of_china(lng, lat):
        return [lng, lat]
    else:
        dlat = transformlat(lng - 105.0, lat - 35.0)
        dlng = transformlng(lng - 105.0, lat - 35.0)
        radlat = lat / 180.0 * PI
        magic = math.sin(radlat)
        magic = 1 - ee * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * PI)
        dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * PI)
        mglat = lat + dlat
        mglng = lng + dlng
        return lng * 2 - mglng, lat * 2 - mglat

def out_of_china(lng, lat):
    lat = float(lat)
    lng = float(lng)
    # 纬度3.86~53.55,经度73.66~135.05
    return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)

def transformlat(lng, lat):
    lat = float(lat)
    lng = float(lng)
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 * math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * PI) + 40.0 * math.sin(lat / 3.0 * PI)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * PI) + 320 * math.sin(lat * PI / 30.0)) * 2.0 / 3.0
    return ret

def transformlng(lng, lat):
    lat = float(lat)
    lng = float(lng)
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 * math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * PI) + 40.0 * math.sin(lng / 3.0 * PI)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * PI) + 300.0 * math.sin(lng / 30.0 * PI)) * 2.0 / 3.0
    return ret
