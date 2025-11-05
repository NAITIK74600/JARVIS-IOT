# H:/jarvis/tools/network_tools.py (NEW FILE)

import socket
import whois
import requests
from langchain_core.tools import tool

@tool
def get_ip_address(_: str = "") -> str:
    """Gets the local IP address of this machine."""
    try:
        # Connect to a public DNS server to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return f"Local IP address: {local_ip}"
    except Exception as e:
        return f"Could not determine IP address: {e}"

@tool
def check_internet_connection(_: str = "") -> str:
    """Checks if there is an active internet connection."""
    try:
        response = requests.get("https://www.google.com", timeout=5)
        if response.status_code == 200:
            return "Internet connection is active."
        else:
            return f"Internet may be down (status code: {response.status_code})."
    except requests.ConnectionError:
        return "No internet connection detected."
    except Exception as e:
        return f"Error checking internet connection: {e}"

@tool
def get_domain_info(domain: str) -> str:
    """Performs a WHOIS lookup to find registration information for a domain name."""
    try:
        domain_info = whois.whois(domain)
        return str(domain_info)
    except Exception as e:
        return f"Error performing WHOIS lookup for {domain}: {e}"

@tool
def geolocate_ip(ip_address: str) -> str:
    """Finds the geographical location of an IP address using a public API."""
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}")
        response.raise_for_status()
        data = response.json()
        if data['status'] == 'success':
            return (f"IP: {data['query']}\n"
                    f"Location: {data['city']}, {data['regionName']}, {data['country']}\n"
                    f"ISP: {data['isp']}\n"
                    f"Organization: {data['org']}")
        else:
            return f"Could not find location data for IP: {ip_address}"
    except Exception as e:
        return f"Error geolocating IP: {e}"

@tool
def scan_local_ports(ports: str) -> str:
    """
    Scans a list of common ports on the local machine (127.0.0.1) to see if they are open.
    Args:
        ports (str): A comma-separated string of ports to check, e.g., "80,443,8080".
    """
    target = "127.0.0.1" # IMPORTANT: Hardcoded to only scan the local machine for safety.
    open_ports = []
    try:
        port_list = [int(p.strip()) for p in ports.split(',')]
        for port in port_list:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((target, port))
            if result == 0:
                open_ports.append(str(port))
            sock.close()
        return f"Scan complete. Open ports on localhost: {', '.join(open_ports) if open_ports else 'None found'}."
    except Exception as e:
        return f"Error during port scan: {e}"
        
def get_network_tools():
    return [get_ip_address, check_internet_connection, get_domain_info, geolocate_ip, scan_local_ports]