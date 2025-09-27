import boto3
import random
import time, json
from typing import Dict, List
from uuid import uuid4

# Replace these with your actual property IDs from IoT SiteWise
POWER_OUTPUT_PROPERTY_ID = "1660fba4-bf0f-4686-a5f1-4eda005fa236"
BLADE_ROTATION_PROPERTY_ID = "4208f5bc-274d-4b5c-8eee-81a7ad5efe94"

# Replace these with the IoT SiteWise asset IDs for each of your wind turbines
WIND_TURBINE_ASSET_IDS = [
    "99ea7070-9b27-4fb7-8056-6404a7cc5c83",
    "d2337be6-10c2-49c5-b16e-d4f58c16fddd"
]

class WindTurbine:
    def __init__(self, asset_id: str):
        self.asset_id = asset_id
        # Initialize values, rounding to 2 decimals for blade_rotation, integer for power_output
        self.power_output = round(random.uniform(200.0, 1000.0))  # kW, integer
        self.blade_rotation = round(random.uniform(5.0, 15.0), 2)  # rpm, with decimals

    def update_readings(self):
        """Randomly adjust power_output and blade_rotation."""
        delta_power = round(random.uniform(-10.0, 10.0))  # Integer delta for power_output
        self.power_output = max(self.power_output + delta_power, 0)
        self.power_output = round(self.power_output)  # Ensure integer

        delta_rpm = random.uniform(-0.5, 0.5)  # Decimal delta for blade_rotation
        self.blade_rotation = max(self.blade_rotation + delta_rpm, 0.0)
        self.blade_rotation = round(self.blade_rotation, 2)  # Keep 2 decimals

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
            "value": {"integerValue": int(self.power_output)},  # Ensure integer
            "timestamp": {"timeInSeconds": current_time},
        }],
        }

        blade_rotation_entry = {
        "entryId": str(uuid4()),
        "assetId": self.asset_id,
        "propertyId": BLADE_ROTATION_PROPERTY_ID,
        "propertyValues": [{
            "value": {"integerValue": int(self.blade_rotation)},  # Changed to integerValue
            "timestamp": {"timeInSeconds": current_time},
        }],}

        return [power_output_entry, blade_rotation_entry]

    def to_json_dict(self) -> Dict:
        """
        Returns a simple dictionary showing the asset ID and the latest readings.
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

        # 1. Print the JSON you want to see
        print(json.dumps(log_entries, indent=2))

        # 2. Send data to IoT SiteWise
        try:
            response = client.batch_put_asset_property_value(entries=all_entries)
            print("API response:", response)
            if 'errorEntries' in response:
                print("Errors:", response['errorEntries'])
        except Exception as e:
            print(f"Error sending data to IoT SiteWise: {e}")

        # Wait for next iteration
        time.sleep(5)

if __name__ == "__main__":
    main()