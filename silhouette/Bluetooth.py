import random
import subprocess
import sys
import time
import socket

from silhouette.DeviceConstants import *
from silhouette.connection import SilhouetteCameoConnection

PORT_RANGE = range(2000, 20000)

# UUID of service that emulates a serial port/UART over BLE
SILHOUETTE_BLE_UART_SERVICE_UUID = "e2088282-4fde-42f9-bb22-6ec3c7ed8f91"

# UUID of the characteristic of BLE UART service where our commands are written to
SILHOUETTE_BLE_UART_WRITE_UUID = "6d92661d-f429-4d67-929b-28e7a9780912"

# UUID of the characteristic of BLE UART service to read responses from
SILHOUETTE_BLE_UART_READ_UUID = "8dcf199a-30e7-4bd4-beb6-beb57dca866c"


class SilhouetteBleSerialConnection(SilhouetteCameoConnection):
    """
    Bluetooth Low Energy connection to Silhouette plotter.

    This is implemented using ble_serial running in a subprocess
    and communicating over TCP socket.

    you can obtain your device_id with `ble_serial.scan`:

    ```
    % python3 -m ble_serial.scan
    Started general BLE scan

    60A75E00-0000-0000-0000-123123123123 (rssi=-21): (some device)
    60A75E00-0000-0000-0000-999999999999 (rssi=-37): (some device)
    E476683A-AAAA-BBBB-CCCC-B9F2F60994C5 (rssi=-53): CAMEO 4-7351B    <--- a Cameo 4 plotter
    AAAAAAAA-AAAA-0000-0000-999999999999 (rssi=-92): (neighbors' washing machine)
    ...

    Finished general BLE scan
    ```

    Depending on the OS, you will see an UUID (macOS) or a MAC address for the device ID.

    """
    def __init__(self, device_id=None, progress_cb=None):
        self.port = None
        self.ble_serial_proc = None
        self._attempt_connect(device_id)
        # TODO autodetect based on GATT attributes
        self.hardware = None
        self.progress_cb = progress_cb

    def _attempt_connect(self, device_id, max_retries=10):
        """Run ble_serial on a random TCP port and connect"""
        for attempt in range(0, max_retries):
            port = random.choice(PORT_RANGE)
            ble_serial_args = [
                sys.executable,
                "-m",
                "ble_serial",
                "-s",
                SILHOUETTE_BLE_UART_SERVICE_UUID,
                "-r",
                SILHOUETTE_BLE_UART_READ_UUID,
                "-w",
                SILHOUETTE_BLE_UART_WRITE_UUID,
                "--expose-tcp-port",
                str(port),
                "--write-with-response",
            ]

            if device_id:
                ble_serial_args.append('-d')
                ble_serial_args.append(device_id)

            print(f"opening ble_serial: {ble_serial_args}", file=sys.stderr, flush=True)

            self.ble_serial_proc = subprocess.Popen(ble_serial_args)
            time.sleep(6.0)
            print(f"checking ble_serial status", file=sys.stderr)
            self.ble_serial_proc.poll()
            if self.ble_serial_proc.returncode is not None:
                self.ble_serial_proc = None
            else:
                print(f"connecting to ble_serial TCP server on {port}", file=sys.stderr)
                self.sock = socket.socket()
                self.sock.settimeout(10.0)
                self.sock.connect(("localhost", port))
                self.port = port
                break
        if self.ble_serial_proc is None:
            raise Exception("Failed to connect with ble_serial after 10 attempts")

    def __del__(self):
        if self.sock:
            self.sock.close()
        if self.ble_serial_proc:
            self.ble_serial_proc.kill()

    def read(self, size=64, timeout=5000):
        if not self.sock:
            raise Exception("Not connected to ble_serial server")
        self.sock.settimeout(timeout/1000.0)
        return self.sock.recv(size)

    def write(self, data, is_query=False, timeout=10000):
        if isinstance(data, str):
            data = data.encode("utf-8")
        if not self.sock:
            raise Exception("Not connected to ble_serial server")
        try:
            resp = self.read(timeout=10)  # poll the inbound buffer
            if resp:
                print("response before write('%s'): '%s'" % (data, resp), sys.stderr)
        except:
            pass


        self.sock.settimeout(timeout/1000.0)
        sent_total = 0
        chunk_size = 4096
        while sent_total < len(data):
            chunk = data[sent_total:sent_total+chunk_size]
            sent = self.sock.send(chunk)
            # TODO handle non-fatal timeouts like in usb
            self.progress_cb(sent_total, len(data), '')
            sent_total =+ sent

