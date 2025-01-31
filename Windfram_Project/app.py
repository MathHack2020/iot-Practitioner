import boto3
import random
import time, json
from typing import Dict, List
from uuid import uuid4

# Replace these with your actual property IDs from IoT SiteWise
POWER_OUTPUT_PROPERTY_ID = "23ef9177-41a0-4705-9b59-a05fe49a9779"
BLADE_ROTATION_PROPERTY_ID = "0302bab5-d47d-4ee5-9ce4-74b91af3da48"

# Replace these with the IoT SiteWise asset IDs for each of your wind turbines
WIND_TURBINE_ASSET_IDS = [
    "abefd94f-bc3d-443a-aece-157b5faeaf76",
    "55fd5905-aecf-4b75-9d93-79305c19423a"
]


class WindTurbine:
    def __init__(self, asset_id: str):
        self.asset_id = asset_id
        # Initialize random values, rounded to 2 decimals
        self.power_output = round(random.uniform(200.0, 1000.0), 2)  # kW
        self.blade_rotation = round(random.uniform(5.0, 15.0), 2)    # rpm

    def update_readings(self):
        """Randomly adjust power_output and blade_rotation, rounding to 2 decimals."""
        delta_power = random.uniform(-10.0, 10.0)
        self.power_output = max(self.power_output + delta_power, 0.0)
        self.power_output = round(self.power_output, 2)

        delta_rpm = random.uniform(-0.5, 0.5)
        self.blade_rotation = max(self.blade_rotation + delta_rpm, 0.0)
        self.blade_rotation = round(self.blade_rotation, 2)

    def build_sitewise_entries(self) -> List[Dict]:
        """
        Builds the list of property updates for AWS IoT SiteWise.
        One entry for PowerOutput and one for BladeRotation.
        """
        current_time = int(time.time())

        power_output_entry = {
            "entryId": str(uuid4()),
            "assetId": self.asset_id,
            "propertyId": POWER_OUTPUT_PROPERTY_ID,
            "propertyValues": [{
                "value": {"doubleValue": self.power_output},
                "timestamp": {"timeInSeconds": current_time},
            }],
        }

        blade_rotation_entry = {
            "entryId": str(uuid4()),
            "assetId": self.asset_id,
            "propertyId": BLADE_ROTATION_PROPERTY_ID,
            "propertyValues": [{
                "value": {"doubleValue": self.blade_rotation},
                "timestamp": {"timeInSeconds": current_time},
            }],
        }

        return [power_output_entry, blade_rotation_entry]

    def to_json_dict(self) -> Dict:
        """
        Returns a simple dictionary showing the asset ID
        and the latest readings in the desired format.
        """
        return {
            "ASSET_ID_": self.asset_id,
            "POWER_OUTPUT": self.power_output,
            "BLADE_ROTATION": self.blade_rotation
        }


def main():
    client = boto3.client('iotsitewise')

    # Create a WindTurbine instance for each asset
    turbines = [WindTurbine(asset_id) for asset_id in WIND_TURBINE_ASSET_IDS]

    while True:
        # Prepare the data for each turbine
        all_entries = []
        log_entries = []  # For printing in the desired JSON format

        for turbine in turbines:
            # Update the turbine's readings
            turbine.update_readings()
            
            # Build SiteWise property updates
            sitewise_entries = turbine.build_sitewise_entries()
            all_entries.extend(sitewise_entries)
            
            # Build the short JSON structure you want to print
            log_entries.append(turbine.to_json_dict())

        # 1. Print the JSON you want to see (only once per loop)
        #    Example format for multiple turbines: 
        #    [
        #       { "ASSET_ID_": "...", "POWER_OUTPUT": 123.45, "BLADE_ROTATION": 6.78 },
        #       { "ASSET_ID_": "...", "POWER_OUTPUT": 987.65, "BLADE_ROTATION": 9.01 }
        #    ]
        print(json.dumps(log_entries, indent=2))

        # 2. Send data to IoT SiteWise
        client.batch_put_asset_property_value(entries=all_entries)

        # Wait for next iteration
        time.sleep(5)


if __name__ == "__main__":
    main()