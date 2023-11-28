import json
from panduza import Core
from hamcrest import assert_that, has_length, has_key, equal_to

# ---

def create_test_platform_alias_from_scan(scan_json, alias_name):
    topic = next(iter(scan_json.keys()))
    platform_alias = {
        "test_server": {
            "url": "localhost", "port": 1883,
            "interfaces": {
                alias_name: topic
            }
        }
    }
    Core.LoadAliases(platform_alias)
