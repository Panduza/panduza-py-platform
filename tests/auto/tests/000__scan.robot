*** Settings ***
Documentation      Tests of the Panduza scan mechanism

Metadata           Author            "XdoctorwhoZ"

Resource           bench.resource
Suite Setup        Setup Bench Config


*** Test Cases ***

Scan all interfaces at platform boot
    [Tags]    REQ_SCAN_0001_00
    ${INTERFACES}     Panduza Scan All Interfaces    localhost    1883
    Log    ${INTERFACES}
    Check all interfaces scan result at platform boot     ${INTERFACES}

Scan all platform interfaces at platform boot
    [Tags]    REQ_SCAN_0002_00    REQ_ITF_PLATFORM_0010_00
    ${INTERFACES}     Panduza Scan All Platforms    localhost    1883
    Log    ${INTERFACES}
    Check platform interfaces scan result at platform boot     ${INTERFACES}

Scan all device interfaces at platform boot
    [Tags]    REQ_SCAN_0003_00    REQ_ITF_DEVICE_0010_00
    ${INTERFACES}     Panduza Scan All Devices    localhost    1883    1
    Log    ${INTERFACES}
    check device interfaces scan result at platform boot     ${INTERFACES}

Scan interfaces from a specific device at platform boot
    [Documentation]    At platform boot only the platform device must be up
    [Tags]    REQ_SCAN_0004_00
    ${INTERFACES}     Panduza Scan All Devices    localhost    1883    1
    Log    ${INTERFACES}
    ${TOPIC}    ${NB}    Extract device topic from scan result    ${INTERFACES}
    Log    ${TOPIC}
    ${INTERFACES}     Panduza scan device    localhost    1883    ${TOPIC}    ${NB}
    Log    ${INTERFACES}
    check interfaces in the only device after scan result at platform boot    ${INTERFACES}



