import json
import os

BASE_IMAGE_PATH = r"C:\Uni\MED6\Bachelor project\P6_Anti_Fouling\Interactive Interface\Panel Images"

def load_panel_and_fouling_data():
    """Loads panel data and fouling data, combines them, and returns the structured data."""

    # Initial panel data structure (as you provided)
    initial_panel_data = {
        "Baltic Asko": {
            "Month 1": ["AA1", "AA2", "AA3", "AB1", "AB2", "AB3",
                        "AC1", "AC2", "AC3", "AD1", "AD2", "AD3",
                        "AE1", "AE2", "AE3", "AN1", "AN2", "AN3", "AP1", "AP2"],
            "Month 2": ["AA1", "AA3", "AB1", "AB2", "AB3",
                        "AC1", "AC2", "AC3", "AD1", "AD2", "AD3",
                        "AE1", "AE2", "AE3", "AN1", "AN2", "AN3", "AP1", "AP2"],
            "Month 3": ["AA1", "AA2", "AA3", "AB1", "AB2", "AB3",
                        "AC1", "AC2", "AC3", "AD1", "AD2", "AD3",
                        "AE1", "AE2", "AE3", "AN1", "AN2", "AN3", "AP1", "AP2"],
            "Month 4": ["AA1", "AA2", "AA3", "AB1", "AB2", "AB3",
                        "AC1", "AC2", "AC3", "AD1", "AD2", "AD3",
                        "AE1", "AE2", "AE3", "AN1", "AN2", "AN3", "AP1", "AP2"],
            "Month 5": ["AA1", "AA2", "AA3", "AB1", "AB2", "AB3",
                        "AC1", "AC2", "AC3", "AD1", "AD2", "AD3",
                        "AE1", "AE2", "AE3", "AN1", "AN2", "AN3", "AP1", "AP2"],
        },
        "Baltic Transition Kristineberg": {
            "Month 1": ["KA1", "KA2", "KA3", "KB1", "KB2", "KB3",
                        "KC1", "KC2", "KC3", "KD1", "KD2", "KD3",
                        "KE1", "KE2", "KE3", "KN1", "KN2", "KN3", "KP1", "KP2"],
            "Month 2": ["KA1", "KA2", "KA3", "KB1", "KB2", "KB3",
                        "KC1", "KC2", "KC3", "KD1", "KD2", "KD3",
                        "KE1", "KE2", "KE3", "KN1", "KN2", "KN3", "KP1", "KP2"],
            "Month 3": ["KA1", "KA2", "KA3", "KB1", "KB2", "KB3",
                        "KC1", "KC2", "KC3", "KD1", "KD2", "KD3",
                        "KE1", "KE2", "KE3", "KN1", "KN2", "KN3", "KP1", "KP2"],
            "Month 4": ["KA1", "KA2", "KA3", "KB1", "KB2", "KB3",
                        "KC1", "KC2", "KC3", "KD1", "KD2", "KD3",
                        "KE1", "KE2", "KE3", "KN1", "KN2", "KN3", "KP1", "KP2"],
            "Month 5": ["KA1", "KA2", "KA3", "KB1", "KB2", "KB3",
                        "KC1", "KC2", "KC3", "KD1", "KD2", "KD3",
                        "KE1", "KE2", "KE3", "KN1", "KN2", "KN3", "KP1", "KP2"],
    },
        "Atlanten Brest": {
            "Month 1": ["BA1", "BA2", "BA3", "BB1", "BB2", "BB3",
                        "BC1", "BC2", "BC3", "BD1", "BD2", "BD3",
                        "BE1", "BE2", "BE3", "BN1", "BN2", "BN3", "BP1", "BP2"],
            "Month 2": ["BA1", "BA2", "BA3", "BB1", "BB2", "BB3",
                        "BC1", "BC2", "BC3", "BD1", "BD2", "BD3",
                        "BE1", "BE2", "BE3", "BN1", "BN2", "BN3", "BP1", "BP2"],
            "Month 3": ["BA1", "BA2", "BA3", "BB1", "BB2", "BB3",
                        "BC1", "BC2", "BC3", "BD1", "BD2", "BD3",
                        "BE1", "BE2", "BE3", "BN1", "BN2", "BN3", "BP1", "BP2"],
            "Month 4": ["BA1", "BA2", "BA3", "BB1", "BB2", "BB3",
                        "BC1", "BC2", "BC3", "BD1", "BD2", "BD3",
                        "BE1", "BE2", "BE3", "BN1", "BN2", "BN3", "BP1", "BP2"],
            "Month 5": ["BA1", "BA2", "BA3", "BB1", "BB2", "BB3",
                        "BC1", "BC2", "BC3", "BD1", "BD2", "BD3",
                        "BE1", "BE2", "BE3", "BN1", "BN2", "BN3", "BP1", "BP2"],
            "Month 6": ["BA1", "BA2", "BA3", "BB1", "BB2", "BB3",
                        "BC1", "BC2", "BC3", "BD1", "BD2", "BD3",
                        "BE1", "BE2", "BE3", "BN1", "BN2", "BN3", "BP1", "BP2"]
        }
    }

    # Initialize the fouling data dictionary
    fouling_data = {}

    # Load fouling percentage data from JSON file
    json_file_path = "fouling_percentages_inside_panel_real.json"

    try:
        if not os.path.exists(json_file_path):
            raise FileNotFoundError(f"File not found: {json_file_path}")

        with open(json_file_path, 'r') as f:
            data = json.load(f)

            # Handle the dictionary structure where values are lists
            if isinstance(data, dict):
                for key, value_list in data.items():
                    # Remove .json extension if present and convert to lowercase
                    clean_key = key.replace('.json', '').lower()

                    # Get the first value from the list (assuming single-element lists)
                    if isinstance(value_list, list) and len(value_list) > 0:
                        fouling_value = value_list[0]
                        if isinstance(fouling_value, (int, float)):
                            fouling_data[clean_key] = fouling_value  # Already in percentage
                        else:
                            print(f"Skipping non-numeric fouling value for {key}: {value_list}")
                    else:
                        print(f"Skipping empty or invalid list for {key}")
            else:
                print("Warning: JSON data is not in expected dictionary format.")

    except Exception as e:
        print(f"Error loading fouling data: {e}")

    # Combine data with fallback for missing fouling data
    structured_data = {}
    for location, months_data in initial_panel_data.items():
        structured_data[location] = {}
        for month, panels in months_data.items():
            structured_data[location][month] = {}
            for panel in panels:
                # Try multiple possible filename formats
                possible_keys = [
                    f"{panel}_{month.lower().replace(' ', '_')}".lower(),
                    f"{panel}{month.replace(' ', '').lower()}",
                    f"{panel.lower()}_{month.lower()}",
                    panel.lower()
                ]

                fouling_value = None
                for key in possible_keys:
                    if key in fouling_data:
                        fouling_value = fouling_data[key]
                        break

                structured_data[location][month][panel] = {
                    "fouling": fouling_value if fouling_value is not None else 0.0
                }

    return structured_data


PANEL_DATA = load_panel_and_fouling_data()