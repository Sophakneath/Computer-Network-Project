import socket
import ssl
import pandas as pd

# Function to check certificate validity for a given resolver IP
def check_certificate(ip, asn_info, count, domain):
    print(f"Checking certificate for {ip}...")
    try:
        # Create a socket and wrap it with SSL/TLS
        with socket.create_connection((ip, 853), timeout=5) as sock:
            with ssl.create_default_context().wrap_socket(sock, server_hostname=ip) as ssock:
                # Retrieve certificate and verify
                cert = ssock.getpeercert()
                if cert:
                    certificate_status = "Valid"
                    reason = ""
                else:
                    certificate_status = "Invalid"
                    reason = "No certificate found."

                # Store the result
                results.append({'IP': ip, 'ASN Info': asn_info, 'Count': count, 'Certificate Status': certificate_status, 'Reason': reason})
    except Exception as e:
        # Store the exception message
        certificate_status = "Invalid"
        reason = str(e)
        results.append({'IP': ip, 'ASN Info': asn_info, 'Count': count, 'Domain': domain, 'Certificate Status': certificate_status, 'Reason': reason})

# Read the CSV file containing IP data
df = pd.read_csv('3_ip_counts_per_asn.csv')

# List to store the results
results = []

# Iterate over each row in the DataFrame and check certificate for each resolver IP
for index, row in df.iterrows():
    ip = row['IP Address']
    asn_info = row['ASN Info']
    count = row['Count']
    domain = row['Domain']
    check_certificate(ip, asn_info, count, domain)

# Create a new DataFrame from the results
results_df = pd.DataFrame(results)

# Save the results to a new CSV file
results_df.to_csv('certificate_results.csv', index=False)