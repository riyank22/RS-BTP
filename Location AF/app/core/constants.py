QOS_TEMPLATES = {
    "EMERGENCY_C2": { # 5QI 1
        "medType": "AUDIO",
        "marBw": "2 Mbps",
        "mirBw": "500 Kbps",
        "5qi": 1,
        "priority": 10
    },
    "VIDEO": { # 5QI 2
        "medType": "VIDEO",
        "marBw": "10 Mbps",
        "mirBw": "2 Mbps",
        "5qi": 2,
        "priority": 12
    },
    "UAV_CRITICAL": { # 5QI 3
        "medType": "UAV_CRITICAL",
        "marBw": "2 Mbps",
        "mirBw": "1 Mbps",
        "5qi": 3,
        "priority": 8
    },
    "TELEMETRY": { # 5QI 4
        "medType": "UAV_TELEMETRY",
        "marBw": "1 Mbps",
        "mirBw": "256 Kbps",
        "5qi": 4,
        "priority": 14
    }
}