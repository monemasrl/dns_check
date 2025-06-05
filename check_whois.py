#!/usr/bin/env python3
import argparse
import json
import csv
from whois import whois as whois_query
from datetime import datetime, timezone
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
_logger = logging.getLogger(__name__)



def parse_args():
    parser = argparse.ArgumentParser(description="Check WHOIS info for a list of domains.")
    parser.add_argument("-i", "--input", help="Input file with list of domains")
    parser.add_argument("-f", "--format", choices=["stdout", "csv", "json"], default="stdout", help="Output format")
    parser.add_argument("-o", "--output", help="Output file (required for csv or json)")
    parser.add_argument("domains", nargs="*", help="List of domains to check if no input file is provided")
    return parser.parse_args()

def safe_str(value):
    if isinstance(value, list):
        return ", ".join(str(v) for v in value if v)
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value) if value else ""

def get_whois_info(domain):
    try:
        w = whois_query(domain)
        # Calcolo giorni alla scadenza
        expiration = w.expiration_date
        if isinstance(expiration, list):
            expiration = expiration[0] if expiration else None
        days_to_expiry = None
        if expiration and isinstance(expiration, datetime):
            # Rende expiration timezone-aware se necessario
            if expiration.tzinfo is None:
                expiration = expiration.replace(tzinfo=timezone.utc)
            days_to_expiry = (expiration - datetime.now(timezone.utc)).days
        status = safe_str(getattr(w, 'status', ''))
        return {
            "domain": domain,
            "registrar": safe_str(w.registrar),
            "registrant": safe_str(getattr(w, 'registrant_organization', getattr(w, 'org', getattr(w, 'name', '')))),
            "creation_date": safe_str(w.creation_date),
            "expiration_date": safe_str(w.expiration_date),
            "last_updated": safe_str(w.updated_date),
            "days_to_expiry": days_to_expiry if days_to_expiry is not None else '',
            "status": status
        }
    except Exception as e:
        return {
            "domain": domain,
            "registrar": "ERROR",
            "registrant": "ERROR",
            "creation_date": "ERROR",
            "expiration_date": "ERROR",
            "last_updated": "ERROR",
            "days_to_expiry": "ERROR",
            "status": "ERROR",
            "error": str(e)
        }

def main():
    args = parse_args()

    if args.input:
        with open(args.input) as f:
            domains = [line.strip() for line in f if line.strip()]
    elif args.domains:
        domains = [d.strip() for d in args.domains if d.strip()]
    else:
        print("Error: provide either --input file or a list of domains as arguments", file=sys.stderr)
        exit(1)

    results = [get_whois_info(domain) for domain in domains]

    if args.format == "stdout":
        for r in results:
            print(f"Domain: {r['domain']}")
            print(f"  Registrar: {r['registrar']}")
            print(f"  Registrant: {r['registrant']}")
            print(f"  Creation Date: {r['creation_date']}")
            print(f"  Expiration Date: {r['expiration_date']}")
            print(f"  Days to Expiry: {r['days_to_expiry']}")
            print(f"  Status: {r['status']}")
            print(f"  Last Updated: {r['last_updated']}")
            if "error" in r:
                print(f"  Error: {r['error']}")
            print()
    elif args.format == "json":
        if not args.output:
            raise ValueError("Output filename required for JSON format")
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
    elif args.format == "csv":
        if not args.output:
            raise ValueError("Output filename required for CSV format")
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "domain", "registrar", "registrant", "creation_date", "expiration_date", "days_to_expiry", "status", "last_updated"
            ])
            writer.writeheader()
            for r in results:
                writer.writerow({k: r.get(k, "") for k in writer.fieldnames})

if __name__ == "__main__":
    main()
