# Standard Library
import json
import os
import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

CONFIG_DIR = os.path.join(BASE_DIR, "..", "..", "config")
NOTA_CONFIG_PATH = os.path.join(CONFIG_DIR, "nota_config.json")
PRINTER_CONFIG_PATH = os.path.join(CONFIG_DIR,"printer_config.json")

def ambil_printer_default():
    """Reads and returns the default printer configuration from a JSON file.

    Returns:
        Optional[Dict[str, Any]]: Loaded JSON configuration dictionary if file
        exists, else None.
    """
    config_path = os.path.join(os.getcwd(), "config", "printer_config.json")
    if not os.path.exists(config_path):
        return None
    with open(config_path, "r") as f:
        return json.load(f)