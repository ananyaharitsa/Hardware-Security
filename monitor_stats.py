
import requests
import random
import time
import statistics
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

NUM_THREADS = 20
NUM_REQUESTS = 1000
POST_RATIO = 0.10  # 10% writes
MONITOR_INTERVAL = 1  # seconds

USER_POOL = {
    "secure": [f"user_name_{i}" for i in range(2000)],
    "vanilla": [f"user_name_{i}" for i in range(2000)]
}

TARGETS = {
    "secure": {
        "base": "https://35.222.200.67:5000",
    },
    "vanilla": {
        "base": "https://35.222.200.67:5001",
    }
}


def send_get(base_url, user_id):
    try:
        start = time.time()
        r = requests.get(f"{base_url}/get_latest?user_id={user_id}", verify=False)
        r.raise_for_status()
        latency = (time.time() - start) * 1000
        return "GET", latency
    except Exception:
        return "GET", None




def send_post(base_url, user_id):
    payload = {
        "user_id": user_id,
        "timestamp": int(time.time()),
        "heart_rate": random.randint(60, 180),
        "blood_pressure": f"{random.randint(110, 140)}/{random.randint(70, 90)}",
        "notes": "benchmarking"
    }
    try:
        start = time.time()
        r = requests.post(f"{base_url}/insert_record", json=payload, verify=False)
        r.raise_for_status()
        latency = (time.time() - start) * 1000
        return "POST", latency
    except Exception:
        return "POST", None

def monitor_system_metrics(name, stop_flag):
    print(f"\n Starting system monitoring for [{name.upper()}]...\n")
    while not stop_flag["stop"]:
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent
        print(f"[{time.strftime('%H:%M:%S')}] CPU: {cpu:5.1f}% | Mem: {mem:5.1f}%")
        time.sleep(MONITOR_INTERVAL)

def run_benchmark(name, base_url, user_pool):
    print(f"\n Starting benchmark for [{name.upper()}]")

    latencies = {"GET": [], "POST": []}
    failures = {"GET": 0, "POST": 0}
    start_time = time.time()
    stop_flag = {"stop": False}

    monitor_thread = threading.Thread(target=monitor_system_metrics, args=(name, stop_flag))
    monitor_thread.start()

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = []
        for _ in range(NUM_REQUESTS):
            user_id = random.choice(user_pool)
            if random.random() < POST_RATIO:
                futures.append(executor.submit(send_post, base_url, user_id))
            else:
                futures.append(executor.submit(send_get, base_url, user_id))

        for future in as_completed(futures):
            method, latency = future.result()
            if latency is not None:
                latencies[method].append(latency)
            else:
                failures[method] += 1
    total_time = time.time() - start_time  # End timer

    total_success = len(latencies["GET"]) + len(latencies["POST"])
    throughput = total_success / total_time

    stop_flag["stop"] = True
    monitor_thread.join()
    total_success = len(latencies["GET"]) + len(latencies["POST"])
    total_failures = failures["GET"] + failures["POST"]
    overall_throughput = total_success / total_time
    read_throughput = len(latencies["GET"]) / total_time
    write_throughput = len(latencies["POST"]) / total_time

    print(f"\n[{name.upper()}] Workload Summary:")
    print(f"Total Success: {total_success} | Total Failures: {total_failures}")
    print(f"Overall Throughput: {overall_throughput:.2f} req/sec")
    print(f"Read Throughput (GET):  {read_throughput:.2f} req/sec")
    print(f"Write Throughput (POST): {write_throughput:.2f} req/sec")
    for method in ["GET", "POST"]:
        print(f"\n[{name.upper()}] {method} stats:")
        success = len(latencies[method])
        fail = failures[method]
        print(f"Success: {success} | Failures: {fail}")
        if success > 0:
            print(f"Avg latency:     {statistics.mean(latencies[method]):.2f} ms")
            print(f"Median latency:  {statistics.median(latencies[method]):.2f} ms")
            print(f"95th percentile: {statistics.quantiles(latencies[method], n=100)[94]:.2f} ms")
            print(f"99th percentile: {statistics.quantiles(latencies[method], n=100)[98]:.2f} ms")
    #:print(f"\n[{name.upper()}] Overall throughput: {throughput:.2f} requests/sec")

if __name__ == "__main__":
    for name, config in TARGETS.items():
        run_benchmark(name, config["base"], USER_POOL[name])