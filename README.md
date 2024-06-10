# Computer-Network-Project: 
# DoT Measurement

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
python3 validateTLS.py]
// input the open resolver list file
```

# DoH Measurement
- The purpose is to obtain a verified list of Internet resolvers offering DNS over HTTPS (DoH) service.
- The list was created by active scanning of the IPv4 address space.
- The scanning was done in May and June 2024.
- The list contains different IP addresses with their reverse DNS record, supported DoH method, and TLS 1.3 support.
- The scanning is done in 3 phases
- This test was ran on native Linux[Ubuntu] environment
## 1. scan the IPv4 address space for opened port 443 [use masscan]
### Installing Masscan on Linux
Update package list 
```
sudo apt update
```
Install dependencies 
```
sudo apt install git build-essential
```
Clone Masscan repository and navigate to dirtectory
```
git clone https://github.com/robertdavidgraham/masscan
cd masscan
```
Compile and Install masscan 
```
make
sudo make install
```
### Running Masscan on Linux
After installation, you can run the Masscan commands to scan IPv4 and IPv6 address spaces [we only scan the IPv4 address space].
Scanning IPv4 Address Space
```
sudo masscan 0.0.0.0/0 -p443 --rate=100000 --exclude 255.255.255.255 -oX ipv4_scan_results.csv
```
Scanning IPv6 Address Space
```
sudo masscan 2001:db8::/32 -p443 --rate=100000 --exclude ff02::1 -oX ipv6_scan_results.xml
```
## 2. Verify DoH support [using custom Nmap-NSE script] 
IP addresses found in the previous step were scanned for DoH support using a custom Nmap-NSE script
```
nmap -p443 --script dns-doh.nse --script-args target=<target>,query=<query type>
```
HTTP2 support [done by lua-http library](https://daurnimator.github.io/lua-http/0.3/)
```
dnf install lua-http
// install for fedora
// Since it is installed into /usr instead of /usr/local, there is an update of path and cpath in the script
```
DoH modes
- HTTP1
  - not recommended but some DoH resolvers support it
```
DoH-GET-PARAMS
// sends request as GET params /dns-query?name=www.example.com&type=A
DoH-BASE64-PARAM
// sends request as GET param in base64 encoded DNS request /dns-query?dns=q80BAAABAAAAAAAAA3d3dwdleGFtcGxlA2NvbQAAAQAB
DoH-POST
// sends request as POST content to URL /dns-query, the body is in DNS wirefire format
```
- HTTP2
  - recommended by DoH standard [3 modes]
```
DoH2-BASE64-PARAMS

DoH2-POST

DoH2-GET-PARAMS
```
# EXAMPLES
```
$ nmap -P0 -p443 --script=dns-doh-check 8.8.8.8
Starting Nmap 7.80 ( https://nmap.org ) at 2021-03-02 21:55 CET
Nmap scan report for dns.google (8.8.8.8)
Host is up (0.0039s latency).

PORT    STATE SERVICE
443/tcp open  https
| dns-doh-check: 
|   DoH2-BASE64-PARAMS: true
|   DoH-GET-PARAMS: false
|   DoH-BASE64-PARAM: true
|   DoH2-POST: false
|   DoH-POST: false
|_  DoH2-GET-PARAMS: false

Nmap done: 1 IP address (1 host up) scanned in 1.43 seconds
```
```
$ nmap  --script=doh-h2-bin -p 443 1.1.1.1
Starting Nmap 7.80 ( https://nmap.org ) at 2021-03-02 22:51 CET
Nmap scan report for one.one.one.one (1.1.1.1)
Host is up (0.011s latency).

PORT    STATE SERVICE
443/tcp open  https
| doh-h2-bin:
|_  response: 200

Nmap done: 1 IP address (1 host up) scanned in 0.95 seconds
```
```
$ nmap  --script=doh-h2-post -p 443 1.1.1.1
Starting Nmap 7.80 ( https://nmap.org ) at 2021-03-02 23:01 CET
Nmap scan report for one.one.one.one (1.1.1.1)
Host is up (0.015s latency).

PORT    STATE SERVICE
443/tcp open  https
| doh-h2-post:
|   response: { [":status"] = 200,["date"] = Tue, 02 Mar 2021 22:01:29 GMT,["content-type"] = application/dns-message,["content-length"] = 49,["access-control-allow-origin"] = *,["cf-request-id"] = 08968ef5b8000027884c0c7000000001,["expect-ct"] = max-age=604800, report-uri="https://report-uri.cloudflare.com/cdn-cgi/beacon/expect-ct",["server"] = cloudflare,["cf-ray"] = 629de7692a602788-PRG,}
|   body: \xAB\xCD\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x03www\x07example\x03com\x00\x00\x01\x00\x01\xC0\x0C\x00\x01\x00\x01\x00\x01'Y\x00\x04]\xB8\xD8"
|_  request: { ["port"] = 443,["host"] = 1.1.1.1,["version"] = 2,["headers"] = { [":method"] = POST,[":authority"] = 1.1.1.1,[":path"] = /dns-query,[":scheme"] = https,["user-agent"] = example/client,["accept"] = application/dns-message,["content-type"] = application/dns-message,["content-length"] = 33,} ,["body"] = \xAB\xCD\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03www\x07example\x03com\x00\x00\x01\x00\x01,["ctx"] = SSL_CTX*: 0x55b83f623cd8,["tls"] = true,}

Nmap done: 1 IP address (1 host up) scanned in 0.91 seconds
```
```
$ nmap  --script=doh-h2 -p 443 1.1.1.1
Starting Nmap 7.80 ( https://nmap.org ) at 2021-03-02 23:06 CET
Nmap scan report for one.one.one.one (1.1.1.1)
Host is up (0.016s latency).

PORT    STATE SERVICE
443/tcp open  https
| doh-h2:
|_  body: {"Status":0,"TC":false,"RD":true,"RA":true,"AD":true,"CD":false,"Question":[{"name":"www.example.com","type":1}],"Answer":[{"name":"www.example.com","type":1,"TTL":75396,"data":"93.184.216.34"}]}

Nmap done: 1 IP address (1 host up) scanned in 0.64 seconds
```

## Test references
- [List of DNS over HTTPS resolvers on the internet](https://pages.github.com/](https://zenodo.org/records/4923371))
- [NMAP Scripts for DNS over HTTPS](https://github.com/robvandenbrink/dns-doh.nse)
- [Custom Nmap-NSE script](https://github.com/cejkato2/dns-doh.nse?tab=readme-ov-file)
- [List of DNS over HTTPS resolvers on the internet]([https://pages.github.com/](https://zenodo.org/records/4923371))




