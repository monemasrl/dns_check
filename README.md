# domaintools
A simple Python toolkit to check DNS records (NS, MX, TXT), DNSSEC status, WHOIS info, and SSL certificate details (including expiry date and days to expiry) for a list of domains or URLs.

# 📘 Domain Tools

This project provides scripts to analyze DNS, WHOIS, and SSL certificate information for domains and websites, supporting multiple output formats and batch processing.

## 🛠️ Features

- Checks if a domain exists
- Retrieves:
  - **NS (Name Server)**
  - **MX (Mail Exchange)**
  - **TXT (Text Records)** — e.g., SPF, DKIM
  - **DNSSEC status** (enabled or not)
  - **WHOIS info** (registrar, registrant, creation/expiration dates, status, days to expiry)
  - **SSL certificate info** (issuer, subject, not before, not after, days to expiry, serial number, version)
- Exports results as:
  - Standard output (`stdout`)
  - CSV file
  - JSON file

## 📦 Requirements

- Python 3.7+
- [`dnspython`](https://www.dnspython.org/)
- [`tqdm`](https://tqdm.github.io/) (optional, for progress bar)
- [`whois`](https://pypi.org/project/whois/) (for WHOIS queries)

Install with:

```bash
pip install dnspython tqdm whois
```

Alternatively, to install all dependencies from the requirements.txt file:

```bash
pip install -r requirements.txt
```

Or, using pipenv:

```bash
pipenv install
```

## 🚀 Usage

### DNS Check

```bash
python check_dns.py --input domains.txt [OPTIONS]
```

#### Options

| Option           | Description                                      |
|------------------|--------------------------------------------------|
| `--input, -i`     | Input file containing a list of domains          |
| `--ns`            | Retrieve NS records                             |
| `--mx`            | Retrieve MX records                             |
| `--txt`           | Retrieve TXT records                            |
| `--dnssec`        | Check whether DNSSEC is enabled                 |
| `--format, -f`    | Output format: `stdout`, `csv`, `json` (default: `stdout`) |
| `--output, -o`    | Output filename (required if format is `csv` or `json`) |

#### Input file format

The input file must contain one domain per line, for example:

```
example.com
google.com
invalid-domain.xyz
```

#### Output examples

Print NS and DNSSEC to stdout:
```bash
python check_dns.py -i domains.txt --ns --dnssec
```
Export MX and TXT records to JSON:
```bash
python check_dns.py -i domains.txt --mx --txt -f json -o output.json
```
Export all to CSV:
```bash
python check_dns.py -i domains.txt --ns --mx --txt --dnssec -f csv -o results.csv
```

### WHOIS Check

```bash
python check_whois.py -i domains_whois.txt
```
Oppure, senza file di input, passando i domini direttamente:
```bash
python check_whois.py example.com google.com
```

#### Options

| Option           | Description                                      |
|------------------|--------------------------------------------------|
| `--input, -i`     | Input file containing a list of domains          |
| `--format, -f`    | Output format: `stdout`, `csv`, `json` (default: `stdout`) |
| `--output, -o`    | Output filename (required if format is `csv` or `json`) |
| `domains`         | List of domains to check if no input file is provided |

#### Output fields

- domain
- registrar
- registrant
- creation_date
- expiration_date
- last_updated
- days_to_expiry
- status

#### Output example (stdout)
```
Domain: example.com
  Registrar: Example Registrar
  Registrant: Example Org
  Creation Date: 2000-01-01T00:00:00
  Expiration Date: 2030-01-01T00:00:00
  Days to Expiry: 1800
  Status: active
  Last Updated: 2024-01-01T00:00:00
```

### SSL Certificate Check

```bash
python check_ssl.py -i urls.txt
```
Oppure, senza file di input, passando le URL direttamente:
```bash
python check_ssl.py https://example.com google.com
```

#### Options

| Option           | Description                                      |
|------------------|--------------------------------------------------|
| `--input, -i`     | Input file containing a list of URLs              |
| `--format, -f`    | Output format: `stdout`, `csv`, `json` (default: `stdout`) |
| `--output, -o`    | Output filename (required if format is `csv` or `json`) |
| `urls`            | List of URLs to check if no input file is provided |

#### Output fields

- hostname
- issuer
- subject
- not_before
- not_after
- days_to_expiry
- serial_number
- version

#### Output example (stdout)
```
Host: example.com
  Issuer: {'C': 'US', 'O': 'Let's Encrypt', 'CN': 'R3'}
  Subject: {'C': 'US', 'ST': 'California', 'L': 'San Francisco', 'O': 'Example Inc', 'CN': 'example.com'}
  Not Before: May  1 00:00:00 2025 GMT
  Not After: Jul 30 23:59:59 2025 GMT
  Days to Expiry: 55
  Serial Number: 04A1B2C3D4E5F6
  Version: 3
```

## ⚠️ Notes

- If no records are found or the domain does not exist, the script marks it as:
  - `NON-EXISTENT` (domain does not resolve)
  - `ERROR` (temporary or unknown DNS/WHOIS error)
- DNSSEC is checked by verifying the presence of `DS` records in the parent zone.
- WHOIS output fields may vary depending on the TLD and registry.

## 📄 License

MIT License – feel free to use and adapt.
