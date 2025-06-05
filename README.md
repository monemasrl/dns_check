# dns_check
A simple Python tool to check DNS records (NS, MX, TXT) and DNSSEC status for a list of domains.

# 📘 DNS Record Checker

This script reads a list of domains from a file and retrieves selected DNS records (NS, MX, TXT) and whether **DNSSEC** is enabled.

## 🛠️ Features

- Checks if a domain exists
- Retrieves:
  - **NS (Name Server)**
  - **MX (Mail Exchange)**
  - **TXT (Text Records)** — e.g., SPF, DKIM
  - **DNSSEC status** (enabled or not)
- Exports results as:
  - Standard output (`stdout`)
  - CSV file
  - JSON file

## 📦 Requirements

- Python 3.7+
- [`dnspython`](https://www.dnspython.org/)

Install with:

```bash
pip install dnspython
```

## 🚀 Usage

```bash
python check_dns.py --input domains.txt [OPTIONS]
```

## 🎛️ Options

| Option           | Description                                      |
|------------------|--------------------------------------------------|
| `--input, -i`     | Input file containing a list of domains          |
| `--ns`            | Retrieve NS records                             |
| `--mx`            | Retrieve MX records                             |
| `--txt`           | Retrieve TXT records                            |
| `--dnssec`        | Check whether DNSSEC is enabled                 |
| `--format, -f`    | Output format: `stdout`, `csv`, `json` (default: `stdout`) |
| `--output, -o`    | Output filename (required if format is `csv` or `json`) |

## 📂 Input file format

The input file must contain one domain per line, for example:

```
example.com
google.com
invalid-domain.xyz
```

## 📤 Output examples

### Example 1 – Print NS and DNSSEC to stdout

```bash
python check_dns.py -i domains.txt --ns --dnssec
```

### Example 2 – Export MX and TXT records to JSON

```bash
python check_dns.py -i domains.txt --mx --txt -f json -o output.json
```

### Example 3 – Export all to CSV

```bash
python check_dns.py -i domains.txt --ns --mx --txt --dnssec -f csv -o results.csv
```

## 📝 Output example (stdout)

```
Domain: example.com
  NS: ns1.example.com, ns2.example.com
  MX: 10 mail.example.com
  TXT: v=spf1 include:example.com ~all
  DNSSEC: ENABLED

Domain: nosuchdomain.tld
  NS: NON-EXISTENT
  MX: NON-EXISTENT
  TXT: NON-EXISTENT
  DNSSEC: NON-EXISTENT
```


## ⚠️ Notes

- If no records are found or the domain does not exist, the script marks it as:
  - `NON-EXISTENT` (domain does not resolve)
  - `ERROR` (temporary or unknown DNS error)
- DNSSEC is checked by verifying the presence of `DS` records in the parent zone.

## 📄 License

MIT License – feel free to use and adapt.
