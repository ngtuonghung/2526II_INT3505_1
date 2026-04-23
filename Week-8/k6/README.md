# k6 quick guide

## Prerequisites
- API server is running at http://localhost:8080
- k6 is installed

Install k6 on Ubuntu:
```bash
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

## Run
From the Week-8 directory:
```bash
k6 run k6/load.js
k6 run k6/stress.js
k6 run k6/spike.js
k6 run k6/soak.js
```

Load variables from k6/.env:
```bash
set -a
source k6/.env
set +a
```

Run after loading .env:
```bash
k6 run k6/load.js
k6 run k6/stress.js
k6 run k6/spike.js
k6 run k6/soak.js
```

Use a different target URL (one run only):
```bash
BASE_URL=http://localhost:8080 k6 run k6/load.js
```

Override VUs for one run:
```bash
LOAD_VUS=30 k6 run k6/load.js
STRESS_VUS_1=30 STRESS_VUS_2=60 STRESS_VUS_3=100 k6 run k6/stress.js
SPIKE_BASE_VUS=10 SPIKE_PEAK_VUS=120 k6 run k6/spike.js
SOAK_VUS=20 k6 run k6/soak.js
```

## Test types
- load.js: steady traffic
- stress.js: increasing traffic to find limits
- spike.js: sudden traffic burst
- soak.js: low traffic for longer duration
