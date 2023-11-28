*** Settings ***
Documentation      Tests fake interfaces

Metadata           Author            "XdoctorwhoZ"

Resource           bench.resource
Suite Setup        Setup Bench Fake Interfaces




*** Test Cases ***

Test Fake AmpereMeter interfaces
    Test Basic Access Of Ammeter Interface        fake_ammeter_0

Test Fake VoltMeter interfaces
    Test Basic Access Of VoltMeter Interface        fake_voltmeter_0

Test Fake BPC interfaces
    Log    "message"
    Interface Bpc Basic Controls    fake_bpc_0


