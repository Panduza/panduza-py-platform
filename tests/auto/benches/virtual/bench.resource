*** Settings ***

Library      Collections
Library      panduza.robof.Keywords

Library      libraries.bench_helper
Library      libraries.scan_checks

Variables    bench_data.py

*** Keywords ***

Setup Bench Config
    Set Log Level    DEBUG
    ${PLATFORMS}     Panduza Scan All Platforms    localhost    1883
    Log     ${PLATFORMS}
    Create test platform alias from scan    ${PLATFORMS}    test_platform
    Panduza platform load dtree    test_platform    ${EMPTY}
    Sleep    1


Setup Bench Fake Interfaces
    Set Log Level    DEBUG
    ${PLATFORMS}     Panduza Scan All Platforms    localhost    1883
    Log     ${PLATFORMS}
    Create test platform alias from scan    ${PLATFORMS}    test_platform
    Panduza platform load dtree    test_platform    ${FAKE_INTERFACES_DTREE}
    Sleep    1
    Log     ${PZA_ALIASES}
    Load Pza Interfaces From Aliases    ${PZA_ALIASES}

