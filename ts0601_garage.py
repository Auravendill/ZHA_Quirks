from typing import Dict
from zigpy.profiles import zha
from zigpy.quirks import CustomDevice
import zigpy.types as t
from zigpy.zcl.clusters.general import Basic, GreenPowerProxy, Groups, Ota, Scenes, Time
from zigpy.zcl.clusters.security import IasZone

from zhaquirks.const import (
    DEVICE_TYPE,
    ENDPOINTS,
    INPUT_CLUSTERS,
    MODELS_INFO,
    OUTPUT_CLUSTERS,
    PROFILE_ID,
)
from zhaquirks.tuya import TuyaLocalCluster
from zhaquirks.tuya.mcu import (
    TuyaMCUCluster,
    TuyaOnOff,
    DPToAttributeMapping

)

#    TuyaDPType,


from zhaquirks.tuya.mcu import ( TuyaMCUCluster
)

from zhaquirks.tuya.ts0601_dimmer import TuyaOnOffNM


ZONE_TYPE = 0x0001


class ContactSwitchCluster(TuyaLocalCluster, IasZone):
    """Tuya ContactSwitch Sensor."""

    _CONSTANT_ATTRIBUTES = {ZONE_TYPE: IasZone.ZoneType.Contact_Switch}

    def _update_attribute(self, attrid, value):
        self.debug("_update_attribute '%s': %s", attrid, value)
        super()._update_attribute(attrid, value)


class TuyaGarageManufCluster(TuyaMCUCluster):
    """Tuya garage door opener."""

    attributes = TuyaMCUCluster.attributes.copy()
    attributes.update(
        {
            # ramdom attribute IDs
            0xEF02: ("dp_2", t.uint32_t, True),
            0xEF04: ("dp_4", t.uint32_t, True),
            0xEF05: ("dp_5", t.uint32_t, True),
            0xEF0B: ("dp_11", t.Bool, True),
            0xEF0C: ("dp_12", t.enum8, True),
        }
    )

    dp_to_attribute: Dict[int, DPToAttributeMapping] = {
        # garage door trigger ¿on movement, on open, on closed?
        1: DPToAttributeMapping(
            TuyaOnOffNM.ep_attribute,
            "on_off",
            #dp_type=TuyaDPType.BOOL,
        ),
        2: DPToAttributeMapping(
            TuyaMCUCluster.ep_attribute,
            "dp_2",
            #dp_type=TuyaDPType.VALUE,
        ),
        3: DPToAttributeMapping(
            ContactSwitchCluster.ep_attribute,
            "zone_status",
            #dp_type=TuyaDPType.BOOL,
            converter=lambda x: IasZone.ZoneStatus.Alarm_1 if x else 0,
            endpoint_id=2,
        ),
        4: DPToAttributeMapping(
            TuyaMCUCluster.ep_attribute,
            "dp_4",
            #dp_type=TuyaDPType.VALUE,
        ),
        5: DPToAttributeMapping(
            TuyaMCUCluster.ep_attribute,
            "dp_5",
            #dp_type=TuyaDPType.VALUE,
        ),
        11: DPToAttributeMapping(
            TuyaMCUCluster.ep_attribute,
            "dp_11",
            #dp_type=TuyaDPType.BOOL,
        ),
        # garage door status (open, closed, ...)
        12: DPToAttributeMapping(
            TuyaMCUCluster.ep_attribute,
            "dp_12",
            #dp_type=TuyaDPType.ENUM,
        ),
    }

    data_point_handlers = {
        1: "_dp_2_attr_update",
        2: "_dp_2_attr_update",
        3: "_dp_2_attr_update",
        4: "_dp_2_attr_update",
        5: "_dp_2_attr_update",
        11: "_dp_2_attr_update",
        12: "_dp_2_attr_update",
    }


class TuyaGarageSwitchTO(CustomDevice):
    """Tuya Garage switch."""

    signature = {
        MODELS_INFO: [
            ("_TZE204_nklqjk62", "TS0601"),
        ],
        ENDPOINTS: {
            # <SimpleDescriptor endpoint=1 profile=260 device_type=0x0051
            # input_clusters=[0, 4, 5, 61184]
            # output_clusters=[10, 25]>
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.SMART_PLUG,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    TuyaGarageManufCluster.cluster_id,
                ],
                OUTPUT_CLUSTERS: [Time.cluster_id, Ota.cluster_id],
            },
            # <SimpleDescriptor endpoint=242 profile=41440 device_type=97
            # input_clusters=[]
            # output_clusters=[33]
            242: {
                PROFILE_ID: 41440,
                DEVICE_TYPE: 97,
                INPUT_CLUSTERS: [],
                OUTPUT_CLUSTERS: [GreenPowerProxy.cluster_id],
            },
        },
    }

    replacement = {
        ENDPOINTS: {
            1: {
                DEVICE_TYPE: zha.DeviceType.SMART_PLUG,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    TuyaGarageManufCluster,
                    TuyaOnOffNM,
                ],
                OUTPUT_CLUSTERS: [Time.cluster_id, Ota.cluster_id],
            },
            2: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.IAS_ZONE,
                INPUT_CLUSTERS: [
                    ContactSwitchCluster
                ],
                OUTPUT_CLUSTERS: [],
            },
            242: {
                PROFILE_ID: 0xA1E0,
                DEVICE_TYPE: 0x0061,
                INPUT_CLUSTERS: [],
                OUTPUT_CLUSTERS: [0x0021],
            },
        },
    }