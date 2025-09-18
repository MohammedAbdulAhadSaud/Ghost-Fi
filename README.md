# Ghost-Fi

> A Linux-based ethical Wi-Fi brute-force tool for educational and security auditing purposes.  
> **Author**: Mohammed Abdul Ahad Saud  
> **GitHub**: [Ghost-Fi Repository](https://github.com/MohammedAbdulAhadSaud/Ghost-Fi)

---

## Description

**Ghost-Fi** is a command-line tool written in Python that uses `nmcli` to scan nearby Wi-Fi networks and attempts to connect using a brute-force approach with a specified password list.

It is designed for **penetration testers**, **security researchers**, and **ethical hackers** who want to audit the security of their own wireless networks.

Performs a brute-force attack on Wi-Fi without requiring a Wi-Fi adapter..

## Features

-  Scan and list available Wi-Fi networks with signal strength, security type, and more.
-  Validate presence of specific SSID and BSSID before attempting connection.
-  Brute-force WPA/WPA2-secured Wi-Fi networks using a wordlist.
-  Automatically deletes and recreates profiles to test each password cleanly.
-  Handles timeouts and connection failures gracefully with detailed error handling.
-  Clear and colored terminal output with `colorama` and `pyfiglet`.

---

## 🛠 Requirements

- Linux with **NetworkManager** and `nmcli`
- Python 3.6+
- **Root privileges** (required to manage network connections)

---

### Required Python Packages:

- `colorama`
- `pyfiglet`

### Install dependencies:

```bash
pip install colorama pyfiglet

```

### Ensure `nmcli` is installed:
- if not :
```bash
sudo apt install network-manager
```

### Clone the repository:

```bash
git clone https://github.com/MohammedAbdulAhadSaud/Ghost-Fi.git
cd Ghost-Fi
```
## Create a virtual environment:
```bash
python -m venv .pymodule
source .pymodule/bin/activate
pip install colorama pyfiglet
chmod +x ghost-fi.py
sudo .pymodule/bin/python ghost-fi.py
```
## Do not use sudo python ghost-fi.py inside the virtual environment,as it uses the system Python which may not have the required packages.

### Must be run as root (using sudo); otherwise, the NetworkManager Connection Editor GUI will repeatedly pop up after every password attempt.
---
## ⚖️ Disclaimer / Ethical Use

🛑 **Legal Note**: This tool is intended strictly for **educational purposes** and **authorized security testing only**.

- By using this tool, you agree to:

- Use it **only on networks you own** or have **explicit permission** to test.
- Abide by all **local, national, and international laws** regarding cybersecurity.

- The author is **not responsible** for any misuse or illegal activities conducted using this software.

## 📬 Feedback & Contributions

- Pull requests and suggestions are welcome!
- Feel free to fork the repository and make improvements.

