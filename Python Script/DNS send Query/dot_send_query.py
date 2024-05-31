import getdns
import sys
import csv

# Function to perform DNS resolution using getdns
def resolve_domain(domain, resolver_ip):
    try:
        # Create a context with the specified resolver
        context = getdns.Context()
        context.resolution_type = getdns.RESOLUTION_STUB
        context.upstream_recursive_servers = [
            {"address_data": resolver_ip, "address_type": "IPv4"}
        ]

        # Perform the DNS resolution
        results = context.address(name=domain)

        # Check if the query was successful
        if results.status == getdns.RESPSTATUS_GOOD:
            print(f"DNS resolution for {domain} succeeded using resolver {resolver_ip}.")
            for addr in results.just_address_answers:
                print(f"IP Address: {addr['address_data']}")
            return True
        else:
            print(f"DNS resolution for {domain} failed with status: {results.status} using resolver {resolver_ip}")
            return False
    except getdns.error as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        return False

# Function to read resolver IPs from a CSV file without headers
def read_csv(file_path):
    resolver_ips = []
    try:
        with open(file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                resolver_ips.append(row[0])
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}", file=sys.stderr)
    return resolver_ips

# Function to write successful resolver IPs to a CSV file
def write_csv(file_path, data):
    try:
        with open(file_path, mode='w', newline='') as file:
            csv_writer = csv.writer(file)
            for row in data:
                csv_writer.writerow([row])
    except Exception as e:
        print(f"An error occurred while writing to the CSV file: {e}", file=sys.stderr)

# Main function
def main():
    # resolver_ips = ["8.8.8.8", "125.211.207.212", "45.223.169.166", "156.73.49.44", "132.246.16.136", "168.221.185.25"]
    
    file_path = 'results.csv'  # Path to your CSV file
    resolver_ips = read_csv(file_path)

    domain = "google.com"  # Fixed domain to be resolved
    output_file_path = 'successful_resolvers.csv'
    # print(resolver_ips)
    
    successful_resolvers = []

    for resolver_ip in resolver_ips:
        if resolve_domain(domain, resolver_ip):
            successful_resolvers.append(resolver_ip)
    
    write_csv(output_file_path, successful_resolvers)

if __name__ == "__main__":
    main()
