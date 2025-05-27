import os

# === BASE NETWORK DEVICE CLASS AND EXTENSIONS ===

class NetworkDevice:
    all_devices = {
        "Switch": [],
        "Router": [],
        "Other": []
    }

    def __init__(self, name, ip_address):
        self.name = name
        self.ip_address = ip_address
        self.status = "active"

    @staticmethod
    def add_device(device_type, name, ip_address, save_to_file=True):
        device_type_lower = device_type.lower()

        if device_type_lower == "switch":
            device = Switch(name, ip_address)
            NetworkDevice.all_devices["Switch"].append(device)
        elif device_type_lower == "router":
            device = Router(name, ip_address)
            NetworkDevice.all_devices["Router"].append(device)
        else:
            device = NetworkDevice(name, ip_address)
            NetworkDevice.all_devices["Other"].append(device)

        print(f"{device_type.capitalize()} '{name}' added with IP {ip_address}.")

        if save_to_file:
            with open("devices.txt", "a") as file:
                file.write(f"{device_type.capitalize()},{name},{ip_address}\n")

    @staticmethod
    def show_devices():
        print("\n--- Current Network Devices ---")
        for category, devices in NetworkDevice.all_devices.items():
            print(f"\n{category}s:")
            if not devices:
                print("  No devices.")
            for d in devices:
                print(f"  - {d.name} ({d.ip_address})")

    @staticmethod
    def find_device_by_ip(ip):
        for device_list in NetworkDevice.all_devices.values():
            for device in device_list:
                if device.ip_address == ip:
                    return device
        return None

    @staticmethod
    def load_devices_from_file():
        if not os.path.exists("devices.txt"):
            return
        with open("devices.txt", "r") as file:
            for line in file:
                parts = line.strip().split(",")
                if len(parts) == 3:
                    device_type, name, ip_address = parts
                    NetworkDevice.add_device(device_type, name, ip_address, save_to_file=False)

    @staticmethod
    def save_connections_to_file():
        with open("connections.txt", "w") as f:
            for switch in NetworkDevice.all_devices["Switch"]:
                for device in switch.connected_devices:
                    f.write(f"{switch.name},{switch.ip_address},{device.name},{device.ip_address}\n")

    @staticmethod
    def load_connections_from_file():
        if not os.path.exists("connections.txt"):
            return
        with open("connections.txt", "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 4:
                    switch_name, switch_ip, device_name, device_ip = parts
                    switch = NetworkDevice.find_device_by_ip(switch_ip)
                    if not switch or not isinstance(switch, Switch):
                        continue
                    device = NetworkDevice.find_device_by_ip(device_ip)
                    if not device:
                        device = NetworkDevice(device_name, device_ip)
                        NetworkDevice.all_devices["Other"].append(device)
                    switch.connect(device)

# === SWITCH CLASS ===

class Switch(NetworkDevice):
    def __init__(self, name, ip_address):
        super().__init__(name, ip_address)
        self.connected_devices = []

    def connect(self, device):
        if device not in self.connected_devices:
            self.connected_devices.append(device)
            print(f"{self.name}: Connected to {device.name} ({device.ip_address})")
        else:
            print(f"{self.name}: Already connected to {device.name}")

    def show_connections(self):
        print(f"\n{self.name} connections:")
        if not self.connected_devices:
            print("  No devices connected.")
        for d in self.connected_devices:
            print(f"  - {d.name} ({d.ip_address})")

# === ROUTER CLASS ===

class Router(NetworkDevice):
    def __init__(self, name, ip_address):
        super().__init__(name, ip_address)
        self.routing_table = {}

    def add_route(self, network, next_hop):
        self.routing_table[network] = next_hop

    def forward_packet(self, destination_ip):
        for network in self.routing_table:
            if destination_ip.startswith(network):
                print(f"{self.name}: Forwarding packet to {self.routing_table[network]}")
                return
        print(f"{self.name}: No route found for {destination_ip}")

# === INTERACTIVE MENU ===

def main_menu():

    while True:
        print("\n===== NETWORK MENU =====")
        print("1. Add a Device")
        print("2. Load")
        print("3. Show All Devices")
        print("4. Connect Two Devices by IP (Switch must be first)")
        print("5. Show All Switch Connections")
        print("6. Exit")
        choice = input("Choose an option (1–5): ")

        if choice == "1":
            device_type = input("Enter device type (switch/router/other): ")
            name = input("Enter device name: ")
            ip_address = input("Enter IP address: ")
            NetworkDevice.add_device(device_type, name, ip_address)

        elif choice == "2":
            NetworkDevice.load_devices_from_file()
            NetworkDevice.load_connections_from_file()

        elif choice == "3":
            NetworkDevice.show_devices()

        elif choice == "4":
            ip1 = input("Enter IP of the switch: ")
            ip2 = input("Enter IP of the device to connect: ")
            dev1 = NetworkDevice.find_device_by_ip(ip1)
            dev2 = NetworkDevice.find_device_by_ip(ip2)
            if not dev1 or not dev2:
                print("One or both devices not found.")
            elif not isinstance(dev1, Switch):
                print("The first device must be a Switch.")
            else:
                dev1.connect(dev2)

        elif choice == "5":
            print("\n--- Switch Connections ---")
            for switch in NetworkDevice.all_devices["Switch"]:
                switch.show_connections()

        elif choice == "6":
            NetworkDevice.save_connections_to_file()
            print("Saving and exiting. Goodbye!")
            break

        else:
            print("Invalid option. Please try again.")

# Run menu
if __name__ == "__main__":
    main_menu()
