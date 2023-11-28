from hamcrest import assert_that, has_length, has_key, equal_to

# ---

def check_all_interfaces_scan_result_at_platform_boot(result):
    # Only 2 interfaces must be present when the platform boot
    assert_that(result, has_length(2))

# ---

def check_platform_interfaces_scan_result_at_platform_boot(result):
    # Only 1, the initial platform
    assert_that(result, has_length(1))

    # Get the first key
    key = next(iter(result.keys()))
    # Get the first value
    content = result[key]
    assert_that(content, has_key("number_of_devices"))
    assert_that(content["number_of_devices"], equal_to(1))

# ---

def check_device_interfaces_scan_result_at_platform_boot(result):
    # Only 1, the initial platform device
    assert_that(result, has_length(1))

    # Get the first key
    key = next(iter(result.keys()))
    # Get the first value
    content = result[key]
    assert_that(content, has_key("number_of_interfaces"))
    assert_that(content["number_of_interfaces"], equal_to(2))

# ---

def extract_device_topic_from_scan_result(result):
    key = list(result.keys())[0]
    # Remove "pza/"
    a = key.removeprefix("pza/")
    # Remove "/device"
    a = a.removesuffix("/device")
    nb = result[key]["number_of_interfaces"]
    return a, nb

# ---

def check_interfaces_in_the_only_device_after_scan_result_at_platform_boot(result):
    # Only 1, the initial platform device
    assert_that(result, has_length(2))

