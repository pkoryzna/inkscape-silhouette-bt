import asyncio
from pathlib import Path

from ble_serial.scan import main as scanner
import wx

adapter = "hci0"
scan_duration = 2.0

app = wx.App(0)


async def scan_devices():
    devices = await scanner.scan(adapter, scan_duration, None)
    return {
        dev.address: f"{dev.name} \t (rssi={adv.rssi})"
        for (dev, adv) in devices.values()
    }


def load_last_used_id():
    f = Path(__file__).parent/"last_plotter_used.cfg"
    if not f.exists():
        return None
    return f.read_text()

def save_last_used_id(device_id):
    f = Path(__file__).parent/"last_plotter_used.cfg"
    return f.write_text(device_id)

def ask_for_scan(reason: str):
    dlg = wx.MessageDialog(
        None,
        reason+" Do you want to scan for a Bluetooth plotter now? It will take up to 2 seconds.",
        "Silhouette Bluetooth connection",
        wx.YES_NO | wx.ICON_QUESTION,
    )
    result = dlg.ShowModal() == wx.ID_YES
    dlg.Destroy()
    app.MainLoop()
    return result


def select_device(devices: dict):
    choices = list(devices.values())
    dialog = wx.SingleChoiceDialog(
        parent=None,
        message="Select your plotter",
        caption="Silhouette Bluetooth connection",
        choices=choices,
    )
    result = dialog.ShowModal()
    if result == wx.CANCEL:
        return None
    selected = dialog.GetStringSelection()
    for dev_id, str_value in devices.items():
        if str_value == selected:
            return dev_id
    return None


def interactive_scan():
    device_id = load_last_used_id()
    reason = None
    if device_id:
        devices = asyncio.run(scan_devices())
        if device_id not in devices:
            reason = "Last used device was not found."
            device_id = None
        else:
            return device_id
    else:
        reason = "There is no saved plotter."
    if not device_id and ask_for_scan(reason):
        devices = asyncio.run(scan_devices())
        selected = select_device(devices)
        if selected:
            save_last_used_id(selected)
        return selected
