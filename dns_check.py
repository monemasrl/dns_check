import dns.resolver
import dns.name
import dns.exception
import csv
import json
import argparse
import sys
import time
try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

def read_domains_from_file(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def resolve_record(domain, record_type):
    try:
        response = dns.resolver.resolve(domain, record_type, lifetime=5)
        return [rdata.to_text() for rdata in response]
    except dns.resolver.NXDOMAIN:
        return 'NON-EXISTENT'
    except dns.exception.DNSException:
        return 'ERROR'

def check_dnssec_enabled(domain):
    try:
        response = dns.resolver.resolve(domain, 'DS', lifetime=5)
        if response.rrset and len(response.rrset) > 0:
            return 'ENABLED'
        else:
            return 'NOT ENABLED'
    except dns.resolver.NoAnswer:
        return 'NOT ENABLED'
    except dns.resolver.NXDOMAIN:
        return 'NON-EXISTENT'
    except dns.exception.DNSException:
        return 'ERROR'

def export_csv(data, filename):
    with open(filename, 'w', newline='') as f:
        fieldnames = list(data[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for entry in data:
            row = {k: ', '.join(v) if isinstance(v, list) else v for k, v in entry.items()}
            writer.writerow(row)

def export_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def print_stdout(data):
    for entry in data:
        print(f"Domain: {entry['domain']}")
        for key, value in entry.items():
            if key == 'domain':
                continue
            if isinstance(value, list):
                print(f"  {key}: {', '.join(value)}")
            else:
                print(f"  {key}: {value}")
        print()

def main():
    parser = argparse.ArgumentParser(description="Check DNS records for domains from a file")
    parser.add_argument('--input', '-i', required=True, help="Input file with the list of domains")
    parser.add_argument('--format', '-f', choices=['csv', 'json', 'stdout'], default='stdout', help="Output format")
    parser.add_argument('--output', '-o', help="Output file (not used if --format is stdout)")

    parser.add_argument('--ns', action='store_true', help="Retrieve NS records")
    parser.add_argument('--mx', action='store_true', help="Retrieve MX records")
    parser.add_argument('--txt', action='store_true', help="Retrieve TXT records")
    parser.add_argument('--dnssec', action='store_true', help="Check if DNSSEC is enabled")

    args = parser.parse_args()

    try:
        domains = read_domains_from_file(args.input)
    except FileNotFoundError:
        print(f"Error: input file '{args.input}' not found.", file=sys.stderr)
        sys.exit(1)

    if not any([args.ns, args.mx, args.txt, args.dnssec]):
        print("Error: you must specify at least one record type (--ns, --mx, --txt, --dnssec)", file=sys.stderr)
        sys.exit(1)

    results = []
    domain_iter = tqdm(domains, desc="Checking domains") if tqdm else domains
    for domain in domain_iter:
        entry = {'domain': domain}

        if args.ns:
            entry['NS'] = resolve_record(domain, 'NS')

        if args.mx:
            entry['MX'] = resolve_record(domain, 'MX')

        if args.txt:
            entry['TXT'] = resolve_record(domain, 'TXT')

        if args.dnssec:
            entry['DNSSEC'] = check_dnssec_enabled(domain)

        results.append(entry)

    if args.format == 'stdout':
        print_stdout(results)
    elif args.format == 'csv':
        if not args.output:
            print("Error: please specify --output for CSV format", file=sys.stderr)
            sys.exit(1)
        export_csv(results, args.output)
    elif args.format == 'json':
        if not args.output:
            print("Error: please specify --output for JSON format", file=sys.stderr)
            sys.exit(1)
        export_json(results, args.output)

if __name__ == "__main__":
    main()
