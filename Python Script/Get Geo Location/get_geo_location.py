import ipinfo
import csv

# Initialize the IPinfo client with your API token
access_token = '04c76ddfcb630d'  # Replace with your actual IPinfo API token
handler = ipinfo.getHandler(access_token)

def get_location(ip_address):
    details = handler.getDetails(ip_address)
    return {
        'ip': ip_address,
        'asn': details.asn,
        'city': details.city,
        'region': details.region,
        'country': details.country,
        'loc': details.loc
    }

def read_ips_from_csv(file_path):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        ips = [row[0] for row in reader]
    return ips

def write_locations_to_csv(locations, output_file):
    if not locations:
        print("No locations to write.")
        return

    keys = locations[0].keys()
    with open(output_file, 'w', newline='') as output:
        dict_writer = csv.DictWriter(output, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(locations)

def main(input_file, output_file):
    ips = read_ips_from_csv(input_file)
    locations = []

    for ip in ips:
        try:
            location = get_location(ip)
            locations.append(location)
            print(f"Location for {ip}: {location}")
        except Exception as e:
            print(f"Error getting location for {ip}: {e}")

    write_locations_to_csv(locations, output_file)
    print(f"Geolocation information saved to {output_file}")

if __name__ == "__main__":
    input_file = 'successful_resolvers.csv'  # Input CSV file containing resolver IPs, one per line
    output_file = 'resolver_locations.csv'  # Output CSV file for locations
    main(input_file, output_file)
