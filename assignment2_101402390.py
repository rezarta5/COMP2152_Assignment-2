"""
Author: Rezarta Marku
Assignment: #2
Description: Port Scanner — A tool that scans a target machine for open network ports
"""

import socket
import threading
import sqlite3
import os
import platform
import datetime


print("Python Version:", platform.python_version())
print("Operating System:", os.name)

# Common ports dictionary storing port numbers and their typical services
common_ports = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    8080: "HTTP-Alt"
}



# NetworkTool parent class
class NetworkTool:
    def __init__(self, target):
        self.__target = target


# Q3: What is the benefit of using @property and @target.setter?
    # Using @property allows controlled access to the private __target variable.
    # The setter validates input and prevents empty targets, keeping the program safe.
    @property
    def target(self):
        return self.__target

    @target.setter
    def target(self, value):
        if value != "":
            self.__target = value
        else:
            print("Error: Target cannot be empty")

    def __del__(self):
        print("NetworkTool instance destroyed")



# Q1: How does PortScanner reuse code from NetworkTool?
# PortScanner inherits from NetworkTool, so it automatically uses the target property and its validation logic.
# For example, the constructor calls super().__init__(target) to set the target without duplicating code.
# This allows PortScanner to focus on scanning functionality while reusing shared code from the parent class.

class PortScanner(NetworkTool):
    def __init__(self, target):
        super().__init__(target)       
        self.scan_results = []          
        self.lock = threading.Lock()    

    def __del__(self):
        print("PortScanner instance destroyed")
        super().__del__()

    def scan_port(self, port):
#     Q4: What would happen without try-except here?
#     # Without a try-except block, any network error (like unreachable host or timeout) would crash the program.
      # Using try-except ensures the program continues scanning other ports even if one fails.
      # It also allows printing informative error messages instead of stopping abruptly.
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.target, port))

            status = "Open" if result == 0 else "Closed"
            service_name = common_ports.get(port, "Unknown")

            # Thread-safe append using a context manager
            with self.lock:
                self.scan_results.append((port, status, service_name))

        except socket.error as e:
            print(f"Error scanning port {port}: {e}")

        finally:
            sock.close()

    def get_open_ports(self):
        # Return only the results where the port is "Open" using a list comprehension
        return [res for res in self.scan_results if res[1] == "Open"]
#
#     Q2: Why do we use threading instead of scanning one port at a time?
#     # Threading allows multiple ports to be scanned at the same time, which speeds up the scan significantly.
      # Without threads, scanning many ports sequentially would take much longer due to network delays.
      # Threads enable concurrent connections, improving efficiency and allowing faster detection of open ports.
    def scan_range(self, start_port, end_port):
        threads = []
        for port in range(start_port, end_port + 1):
            t = threading.Thread(target=self.scan_port, args=(port,))
            threads.append(t)
        # Start all threads
        for t in threads:
            t.start()
        # Wait for all threads to complete
        for t in threads:
            t.join()


def save_results(target, results):
    try:
        conn = sqlite3.connect("scan_history.db")
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target TEXT,
            port INTEGER,
            status TEXT,
            service TEXT,
            scan_date TEXT
        )
        """)
        for port, status, service in results:
            cursor.execute(
                "INSERT INTO scans (target, port, status, service, scan_date) VALUES (?, ?, ?, ?, ?)",
                (target, port, status, service, str(datetime.datetime.now()))
            )
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print("Database error:", e)


def load_past_scans():
    try:
        conn = sqlite3.connect("scan_history.db")
        cursor = conn.cursor()
        cursor.execute("SELECT target, port, status, service, scan_date FROM scans")
        rows = cursor.fetchall()
        if not rows:
            print("No past scans found.")
        for target, port, status, service, date in rows:
            print(f"[{date}] {target} : Port {port} ({service}) - {status}")
        conn.close()
    except sqlite3.Error:
        print("No past scans found.")


# ============================================================
# MAIN PROGRAM
# ============================================================
if __name__ == "__main__":
    try:
        # Get target IP
        target = input("Enter target IP (default 127.0.0.1): ")
        if target == "":
            target = "127.0.0.1"

        # Get port range
        start_port = int(input("Enter start port (1-1024): "))
        end_port = int(input("Enter end port (1-1024): "))

        # Validate port range
        if not (1 <= start_port <= 1024 and 1 <= end_port <= 1024):
            print("Port must be between 1 and 1024.")
            exit()

        if end_port < start_port:
            print("End port must be >= start port.")
            exit()

    except ValueError:
        print("Invalid input. Please enter a valid integer.")
        exit()

    # Create scanner object
    scanner = PortScanner(target)

    print(f"Scanning {target} from port {start_port} to {end_port}...")
    scanner.scan_range(start_port, end_port)

    # Get and print open ports
    open_ports = scanner.get_open_ports()

    print(f"\n--- Scan Results for {target} ---")
    for port, status, service in open_ports:
        print(f"Port {port}: {status} ({service})")

    print("------")
    print(f"Total open ports found: {len(open_ports)}")

    # Save results to database
    save_results(target, scanner.scan_results)

    # Ask user to view history
    choice = input("Would you like to see past scan history? (yes/no): ")
    if choice.lower() == "yes":
        load_past_scans()


# Q5: New Feature Proposal
# I would add a feature that allows users to filter scan results by service name using a list comprehension.
# The user could enter a service like "HTTP", and the program would display only the ports associated with that service by filtering the scan_results list.
# This would improve usability by helping users quickly focus on specific services instead of scanning through all results.
# Diagram: See diagram_101402390.png in the repository root
