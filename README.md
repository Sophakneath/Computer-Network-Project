# Computer-Network-Project: DoT Measurement

## 1. Run on: Windows Subsystem for Linux (WSL)
To install WSL, open a PowerShell terminal as Administrator and run:
```sh
wsl --install
```

## 2. Prerequisites
- ZMap: To install ZMap and run a scan:

```sh
sudo apt update
sudo apt install zmap
sudo zmap -p 853 -r 1000000 -o results.csv
```

- getdns: To install getdns, run the following commands:

```sh
sudo apt install build-essential libunbound-dev libidn2-dev libssl-dev cmake
git clone https://github.com/getdnsapi/getdns.git
cd getdns && mkdir build
cd getdns && git submodule update --init
cd getdns/build && cmake .. && make && make install
```

## 3. Running the Script
- Colab: Use Colab for quick testing on getdns usage.

- After getting results from network scan: To send DNS queries to verify DNS resolver:

```sh
python3 dot_send_query.py
```

- To get geo-location information:
```sh
python3 geo_location.py
```
- To validate resolver's certificate:
```sh
python3 validateTLS.py
// input the open resolver list file
```



