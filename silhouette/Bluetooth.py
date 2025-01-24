import random
import subprocess
import sys
import time
import socket

from silhouette.DeviceConstants import *
from silhouette.connection import SilhouetteCameoConnection

UART_SERVICE_UUID = "e2088282-4fde-42f9-bb22-6ec3c7ed8f91"
WRITE_UUID = "6d92661d-f429-4d67-929b-28e7a9780912"
READ_UUID = "8dcf199a-30e7-4bd4-beb6-beb57dca866c"


class SilhouetteBleSerialConnection(SilhouetteCameoConnection):
    # FIXME: ble_serial is all async, to use it directly from this interface we'd need an async version of Graphtec.py
    def __init__(self, device_id=None):
        self.port = None
        self.ble_serial_proc = None
        for attempt in range(0,10):
            port = random.choice(range(2000, 20000))
            ble_serial_args = [
                sys.executable,
                "-m",
                "ble_serial",
                "-s",
                UART_SERVICE_UUID.upper(),
                "-r",
                READ_UUID,
                "-w",
                WRITE_UUID,
                "--expose-tcp-port",
                str(port),
                "--write-with-response",
            ]

            if device_id:
                ble_serial_args.append('-d')
                ble_serial_args.append(device_id)

            print(f"opening ble_serial: {ble_serial_args}", file=sys.stderr, flush=True)

            self.ble_serial_proc = subprocess.Popen(ble_serial_args)
            time.sleep(10.0)
            print(f"checking ble_serial status", file=sys.stderr)
            self.ble_serial_proc.poll()
            if self.ble_serial_proc.returncode is not None:
                self.ble_serial_proc.kill()
                self.ble_serial_proc = None
            else:
                self.port = port
                break
        if self.ble_serial_proc is None:
            raise Exception("Failed to connect with ble_serial after 10 attempts")
        print(f"connecting to ble_serial on {self.port}", file=sys.stderr)
        self.sock = socket.socket()
        self.sock.settimeout(10000)
        self.sock.connect(("localhost", self.port))
        self.hardware = { 'vendor_id': VENDOR_ID_GRAPHTEC, 'product_id': PRODUCT_ID_SILHOUETTE_CAMEO4, 'name': 'Silhouette_Cameo4',
   # margin_top_mm is just for safety when moving backwards with thin media
   # margin_left_mm is a physical limit, but is relative to width_mm!
   'width_mm':  304.8, 'length_mm': 3000, 'margin_left_mm':0.0, 'margin_top_mm':0.0, 'regmark': True }


    def __del__(self):
        if self.sock:
            self.sock.close()
        if self.ble_serial_proc:
            self.ble_serial_proc.kill()

    def read(self, size=64, timeout=5000):
        self.sock.settimeout(timeout/1000.0)
        return self.sock.recv(size)

    def write(self, data, is_query=False, timeout=10000):
        if isinstance(data, str):
            data = data.encode("utf-8")

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
            # todo error handling
            sent_total =+ sent

