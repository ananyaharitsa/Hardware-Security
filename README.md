# FitHealth

FitHealth is a secure remote health monitoring service that uses Intel TDX for confidential computing and SQLCipher to encrypt user health records.

It includes:
- A Flask app with endpoints to insert, fetch, and attest records
- A Docker setup with SQLCipher compiled inside
- Benchmarking tools to compare performance in secure (TDX) vs. vanilla VMs
- Scripts to analyze latency, throughput, and resource usage
- You will need to set up fithealth.db (AES encrypted for secure and plain for vanilla)


1. Build the docker container
```bash
cd app
docker build -t fithealth-container .

2. Run the app on the docker container
docker run -it --rm -p 5000:5000 fithealth-container

3. Run benchmarking tests - monitor_stats.py
4. Load more rows into the db - bulk_load.py

monitor_stats.py
 - simulates concurrent GET/POST requests using multithreading and records request latencies, throughput, CPU, and memory usage for later analysis.

bulk_load.py
 -  populates the database with synthetic user records to enable realistic benchmarking.
