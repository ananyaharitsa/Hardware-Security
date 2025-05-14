import requests
import time
import random
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

NUM_RECORDS = 10000  # Set this to 100000+ for GB scale
ENDPOINTS = {
    #"vanilla": "https://localhost:5001/insert_record",
    "secure": "https://localhost:5000/insert_record",
    "vanilla": "https://localhost:5001/insert_record"
}

def generate_payload(user_id):
    return {
        "user_id": user_id,
        "timestamp": int(time.time()),
        "heart_rate": random.randint(60, 180),
        "blood_pressure": f"{random.randint(110, 140)}/{random.randint(70, 90)}",
        "notes": "bulk upload simulation"*10000
    }

def insert_bulk(endpoint_name, endpoint_url):
    print(f"🔄  Inserting into [{endpoint_name.upper()}]...")
    success, fail = 0, 0
    for i in range( NUM_RECORDS+20000):
        user_id = f"user_name_{i}"
        payload = generate_payload(user_id)
        try:
            r = requests.post(endpoint_url, json=payload, verify=False, timeout=5)
            r.raise_for_status()
            success += 1
        except Exception as e:
            fail += 1
            print(f"Error on {i}: {e}")
        if i % 1000 == 0:
            print(f"Inserted {i} records...")

    print(f"✅  Done [{endpoint_name.upper()}] — Success: {success}, Failures: {fail}")

if __name__ == "__main__":
    for name, url in ENDPOINTS.items():
        insert_bulk(name, url)
