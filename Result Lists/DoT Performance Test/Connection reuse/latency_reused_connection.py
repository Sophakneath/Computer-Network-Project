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
                start_time = time.time()
                with socket.create_connection((resolver_ip, resolver_port), timeout=30) as sock:
                    with context.wrap_socket(sock, server_hostname=resolver_ip) as ssock:
                        end_time = time.time()
                        handshake_latency = (end_time - start_time) * 1000  # Latency in milliseconds
                        print(f"Initial Handshake: {handshake_latency} ms")

                        query_domain = "google.com"  # Example query domain
                        query_latency, response = measure_query(ssock, resolver_ip, query_domain)
                        print(f"Query time: {query_latency:.2f} ms")
                        print(f"--------------------------------------------------------------------")

                        session = ssock.session

                        for query_num in range(num_queries):
                            start = time.time()
                            with socket.create_connection((resolver_ip, resolver_port), timeout=30) as sock2:
                                with context.wrap_socket(sock2, server_hostname=resolver_ip, session=session) as ssock2:
                                    end = time.time()
                                    latency = (end - start) * 1000  # Latency in milliseconds
                                    total_handshake_latency += latency
                                    print(f"After reused Handshake: {latency} ms")
                                    # Perform another query with the same session
                                    reused_query_latency, response = measure_query(ssock, resolver_ip, "google.com")
                                    total_query_latency += reused_query_latency
                                    # Convert response time to milliseconds            
                                    print(f"Query {query_num + 1} time: {reused_query_latency:.2f} ms")
                                    print(f"Reused Session ID: {ssock2.session.id.hex()}")
                                    print(f"Session Reused After Query: {ssock2.session_reused}")
                            
                            # Store results for each query
                            results.append({
                                'Country': country,
                                'Port': current_port,
                                'Reuse Query Latency': reused_query_latency,
                                'Handshake Latency (Resume)': latency,
                                'Initial Handshake Latency': handshake_latency
                            })      

                            print(f"--------------------------------------------------------------------")                                    

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
        'Reuse Query Latency': avg_query_latency,
        'Handshake Latency (Resume)': avg_handshake_latency,
        'Initial Handshake Latency': ''
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
resolver_ip = '9.9.9.9'  # Replace with your DNS resolver IP
resolver_port = 853  # Replace with your DNS resolver port

username = 'sophakneath-country-KR'  # Initial username for the first country
password = 'KKCLGFC-OF99MOZ-AUKPJ6A-HASD9RF-LSOUOZK-ALIWYTW-JH8JE6S'  # Replace with your ProxyRack password

# Perform measurement
results = measure_dot_performance(ports, proxy_host, resolver_ip, resolver_port, username, password, num_queries)

# Write results to CSV
output_file = 'dot_performance_results_9.9.9.9.csv'

# Define field names for CSV header
fieldnames = ['Country', 'Port', 'Reuse Query Latency', 'Handshake Latency (Resume)', 'Initial Handshake Latency']

with open(output_file, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print(f"Results saved to {output_file}")