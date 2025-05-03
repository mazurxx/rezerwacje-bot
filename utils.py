
from datetime import datetime, timedelta

# Lista usług i czas trwania w minutach
SERVICE_DURATIONS = {
    "makijaż ślubny": 120,
    "paznokcie hybrydowe": 90,
    "brwi": 30,
    "manicure klasyczny": 60,
    "fryzjer – strzyżenie": 60
}

def get_service_duration(service_name):
    return SERVICE_DURATIONS.get(service_name.lower())

def find_available_slot(slots, duration):
    slot_length = 30  # minut
    required_slots = duration // slot_length

    for i in range(len(slots) - required_slots + 1):
        group = slots[i:i+required_slots]
        if all(s['status'].lower() == 'wolny' for s in group):
            same_day = all(s['data'] == group[0]['data'] for s in group)
            consecutive = True
            for j in range(len(group) - 1):
                t1 = datetime.strptime(group[j]['godzina'], '%H:%M')
                t2 = datetime.strptime(group[j+1]['godzina'], '%H:%M')
                if (t2 - t1) != timedelta(minutes=30):
                    consecutive = False
                    break
            if same_day and consecutive:
                return group[0]
    return None
