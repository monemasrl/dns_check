#!/usr/bin/env python3
import argparse
import csv
import json
import socket
import ssl
from datetime import datetime, timezone
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="Check SSL certificate info for a list of URLs.")
    parser.add_argument("-i", "--input", help="Input file with list of URLs (one per line)")
    parser.add_argument("-f", "--format", choices=["stdout", "csv", "json"], default="stdout", help="Output format")
    parser.add_argument("-o", "--output", help="Output file (required for csv or json)")
    parser.add_argument("urls", nargs="*", help="List of URLs to check if no input file is provided")
    return parser.parse_args()


def get_ssl_info(hostname, port=443):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                not_after = cert.get('notAfter')
                if not_after:
                    expires = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z').replace(tzinfo=timezone.utc)
                    days_to_expiry = (expires - datetime.now(timezone.utc)).days
                else:
                    expires = None
                    days_to_expiry = None
                return {
                    "hostname": hostname,
                    "issuer": dict(x[0] for x in cert.get('issuer', [])),
                    "subject": dict(x[0] for x in cert.get('subject', [])),
                    "not_before": cert.get('notBefore', ''),
                    "not_after": not_after or '',
                    "days_to_expiry": days_to_expiry if days_to_expiry is not None else '',
                    "serial_number": cert.get('serialNumber', ''),
                    "version": cert.get('version', ''),
                }
    except Exception as e:
        return {
            "hostname": hostname,
            "issuer": "ERROR",
            "subject": "ERROR",
            "not_before": "ERROR",
            "not_after": "ERROR",
            "days_to_expiry": "ERROR",
            "serial_number": "ERROR",
            "version": "ERROR",
            "error": str(e)
        }


def main():
    args = parse_args()

    if args.input:
        with open(args.input) as f:
            urls = [line.strip() for line in f if line.strip()]
    elif args.urls:
        urls = [u.strip() for u in args.urls if u.strip()]
    else:
        print("Error: provide either --input file or a list of URLs as arguments", file=sys.stderr)
        exit(1)

    # Remove protocol if present
    def clean_url(url):
        if url.startswith('https://'):
            url = url[8:]
        elif url.startswith('http://'):
            url = url[7:]
        return url.split('/')[0]

    results = [get_ssl_info(clean_url(url)) for url in urls]

    if args.format == "stdout":
        for r in results:
            print(f"Host: {r['hostname']}")
            print(f"  Issuer: {r['issuer']}")
            print(f"  Subject: {r['subject']}")
            print(f"  Not Before: {r['not_before']}")
            print(f"  Not After: {r['not_after']}")
            print(f"  Days to Expiry: {r['days_to_expiry']}")
            print(f"  Serial Number: {r['serial_number']}")
            print(f"  Version: {r['version']}")
            if 'error' in r:
                print(f"  Error: {r['error']}")
            print()
    elif args.format == "json":
        if not args.output:
            raise ValueError("Output filename required for JSON format")
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2, default=str)
    elif args.format == "csv":
        if not args.output:
            raise ValueError("Output filename required for CSV format")
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "hostname", "issuer", "subject", "not_before", "not_after", "days_to_expiry", "serial_number", "version"
            ])
            writer.writeheader()
            for r in results:
                writer.writerow({k: r.get(k, "") for k in writer.fieldnames})

if __name__ == "__main__":
    main()
