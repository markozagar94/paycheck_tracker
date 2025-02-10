import logging

EXCHANGE_RATE = 7.53450  # Fixed conversion rate


def convert_kn_to_eur(data: dict) -> dict:
    """
    Converts salary values from HRK (kn) to EUR (€).

    Args:
        data (dict): The salary data extracted from PDFs.

    Returns:
        dict: Updated dictionary with converted values.
    """
    converted_data = {}

    for key, value in data.items():
        if isinstance(value, str):
            try:
                if value.endswith("kn"):
                    numeric_value = float(value.replace("kn", "").strip())
                    converted_data[key] = round(numeric_value / EXCHANGE_RATE, 2)
                elif value.endswith("€"):
                    converted_data[key] = float(value.replace("€", "").strip())
                else:
                    converted_data[key] = value
            except ValueError:
                logging.warning(f"Skipping invalid value: {value}")
        else:
            converted_data[key] = value

    converted_data["Currency"] = "€"
    return converted_data
