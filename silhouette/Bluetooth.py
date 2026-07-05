import asyncio
import random
import subprocess
import sys
import time
import socket

from silhouette import BluetoothScan
from silhouette.DeviceConstants import *
from silhouette.connection import SilhouetteCameoConnection

MAX_RETRY_LIMIT = 5

PORT_RANGE = range(2000, 20000)


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

    def __init__(
        self, device_id=None, force_hardware=None, progress_cb=None, log=sys.stderr
    ):
        self.log = log
        self.sock = None
        self.port = None
        self.ble_serial_proc = None
        self._attempt_connect(device_id)
        # TODO autodetect based on GATT attributes
        self.hardware = force_hardware
        self.progress_cb = progress_cb
        

    def _attempt_connect(self, device_id, max_retries=1):
        """Run ble_serial on a random TCP port and connect"""
        if not device_id and BluetoothScan.ask_for_scan():
            devices = asyncio.run(BluetoothScan.scan_devices())
            device_id = BluetoothScan.select_device(devices)
        if not device_id:
            raise IndexError("No device was selected")
        for attempt in range(0, max_retries):
            port = random.choice(PORT_RANGE)
            ble_serial_args = [
                sys.executable,
                "-m",
                "ble_serial",
                # "-s",
                # SILHOUETTE_BLE_UART_SERVICE_UUID,
                "-r",
                SILHOUETTE_BLE_UART_READ_UUID,
                "-w",
                SILHOUETTE_BLE_UART_WRITE_UUID,
                "--expose-tcp-port",
                str(port),
                "--write-with-response",
                "-d",
                device_id,
                "-t",
                "1"
            ]
            print(f"opening ble_serial: {ble_serial_args}", file=self.log, flush=True)

            self.ble_serial_proc = subprocess.Popen(ble_serial_args)
            time.sleep(6.0)
            print(f"checking ble_serial status", file=self.log)
            self.ble_serial_proc.poll()
            if self.ble_serial_proc.returncode is not None:
                print(
                    f"failed to connect on port {port} "
                    f"to ble_serial pid {self.ble_serial_proc.pid}",
                    file=self.log,
                )
                self.ble_serial_proc = None
            else:
                print(f"connecting to ble_serial TCP server on {port}", file=self.log)
                self.sock = socket.socket()
                self.sock.settimeout(10.0)
                self.sock.connect(("localhost", port))
                self.port = port
                print("successfully connected")
                break
        if self.ble_serial_proc is None:
            raise Exception("Failed to connect with ble_serial after 10 attempts")

    def close(self):
        try:
            if self.sock:
                self.sock.close()
                self.sock = None
        finally:
            if self.ble_serial_proc:
                self.ble_serial_proc.kill()
                self.ble_serial_proc = None


    def read(self, size=64, timeout=5000):
        if not self.sock:
            raise Exception("Not connected to ble_serial server")
        self.sock.settimeout(timeout / 1000.0)
        return self.sock.recv(size)

    def write(self, data, is_query=False, timeout=10000):
        if isinstance(data, str):
            data = data.encode("utf-8")
        if not self.sock:
            raise Exception("Not connected to ble_serial server")
        try:
            resp = self.read(timeout=10)  # poll the inbound buffer
            if resp:
                print("response before write('%s'): '%s'" % (data, resp), file=sys.stderr)
        except socket.timeout:
            pass

        self.sock.settimeout(timeout / 1000.0)
        sent_total = 0
        chunk_size = 4096
        retries = 0
        last_exc = None
        while sent_total < len(data):
            if retries > MAX_RETRY_LIMIT:
                e = Exception(f"Write failed after {MAX_RETRY_LIMIT} retries")
                if last_exc:
                    raise e from last_exc
                raise e
            try:
                chunk = data[sent_total : sent_total + chunk_size]
                sent = self.sock.send(chunk)
                sent_total = +sent
                self.progress_cb(sent_total, len(data), "")
            except socket.timeout as e:
                print("socket write timed out, waiting 1 sec and retrying",file=self.log)
                time.sleep(1)
                retries += 1
                last_exc = e
                continue
            if sent == 0:
                time.sleep(1)
                retries += 1
                last_exc = None
            else:
                retries = 0
                last_exc = None

