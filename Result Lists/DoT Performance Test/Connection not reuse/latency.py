import socket
import socks
import ssl
import time
import dns.message
import dns.query
import csv

def setup_socks_proxy(proxy_host, proxy_port, username=None, password=None):
    if username and password:
        socks.set_default_proxy(socks.SOCKS5, proxy_host, proxy_port, username=username, password=password)
    else:
        socks.set_default_proxy(socks.SOCKS5, proxy_host, proxy_port)
    socket.socket = socks.socksocket

def measure_dot_performance(ports, proxy_host, resolver_ip, resolver_port=853, username=None, password=None, num_queries=5):
    results = []

    total_handshake_latency = 0
    total_query_latency = 0
    port_index = 0

    for country in countries:
        for _ in range(num_queries):
            current_port = ports[port_index]
            username = f'sophakneath-country-{country}'  # Adjust username based on country
            print(f"Testing {country} with port {current_port}")

            setup_socks_proxy(proxy_host, current_port, username, password)

            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            try:
                for query_num in range(num_queries):
                    start_time = time.time()
                    with socket.create_connection((resolver_ip, resolver_port), timeout=30) as sock:
                        with context.wrap_socket(sock, server_hostname=resolver_ip) as ssock:
                            end_time = time.time()
                            handshake_latency = (end_time - start_time) * 1000  # Latency in milliseconds
                            print(f"Initial Handshake: {handshake_latency} ms")
                            total_handshake_latency += handshake_latency

                            query_latency, response = measure_query(ssock, resolver_ip, "google.com")
                            total_query_latency += query_latency
                            print(f"Query {query_num + 1} time: {query_latency:.2f} ms")
                            print(f"--------------------------------------------------------------------")

                             # Store results for each query
                            results.append({
                                'Country': country,
                                'Port': current_port,
                                'Query Latency': query_latency,
                                'Handshake Latency': handshake_latency
                            })

            except Exception as e:
                print(f"Error during measurement: {e}")
            
            print(f"--------------------------------------------------------------------")

            port_index = port_index + 1

    avg_handshake_latency = total_handshake_latency / (len(countries) * num_queries)
    avg_query_latency = total_query_latency / (len(countries) * num_queries)

    print(f"\nAverage Handshake Latency: {avg_handshake_latency:.2f} ms")
    print(f"Average Query Latency: {avg_query_latency:.2f} ms")

    # Store average latencies at the end
    results.append({
        'Country': 'Average',
        'Port': '',
        'Query Latency': avg_query_latency,
        'Handshake Latency': avg_handshake_latency
    })

    return results

def measure_query(ssock, resolver_ip, query_domain):
    query = dns.message.make_query(query_domain, dns.rdatatype.A)
    response = dns.query.tls(query, resolver_ip, ssl_context=ssock.context, sock=ssock)
    latency = response.time * 1000
    return latency, response

# Define countries, ports, and number of queries per port
countries = ['JP', 'ID', 'IN', 'KR', 'US']  # Adjust country codes as per your needs
ports = [10000, 10001, 10002, 10003, 10004, 10025, 10006, 10007, 10036, 10009, 10026, 10011, 10012, 10013, 10014, 10015, 10016, 10033, 10018, 10019, 10020, 10028, 10029, 10023, 10030]  # Adjust port range as per your needs
num_queries = 5  # Number of queries per port

# Example usage
proxy_host = 'premium.residential.proxyrack.net'  # Replace with your ProxyRack proxy host
resolver_ip = '8.8.8.8'  # Replace with your DNS resolver IP
resolver_port = 853  # Replace with your DNS resolver port

username = 'sophakneath-country-KR'  # Initial username for the first country
password = 'KKCLGFC-OF99MOZ-AUKPJ6A-HASD9RF-LSOUOZK-ALIWYTW-JH8JE6S'  # Replace with your ProxyRack password

# Perform measurement
results = measure_dot_performance(ports, proxy_host, resolver_ip, resolver_port, username, password, num_queries)

# Write results to CSV
output_file = 'dot_performance_results_8.8.8.8.csv'

# Define field names for CSV header
fieldnames = ['Country', 'Port', 'Query Latency', 'Handshake Latency']

with open(output_file, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print(f"Results saved to {output_file}")
