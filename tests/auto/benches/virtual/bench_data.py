

FAKE_INTERFACES_DTREE={
    "devices": [
        {
            "ref": "Panduza.FakeBps",
            "settings": {
                "number_of_channel": 2
            }
        }
    ]
}

PZA_ALIASES={
    "local": {
        "url": "localhost",
        "port": 1883,
        "interfaces": {
            "fake_ammeter_0": "pza/default/Panduza_FakeBps/:channel_0:_am",
            "fake_voltmeter_0": "pza/default/Panduza_FakeBps/:channel_0:_vm",
            "fake_bpc_0": "pza/default/Panduza_FakeBps/:channel_0:_ctrl",
        }
    }
}


