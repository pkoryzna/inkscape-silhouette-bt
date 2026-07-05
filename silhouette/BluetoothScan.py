import asyncio

from ble_serial.scan import main as scanner
import wx

adapter = "hci0"
scan_duration = 2.0

app = wx.App(0)


async def scan_devices():
    devices = await scanner.scan(adapter, scan_duration, None)
    return {
        dev.address: f"{dev.name} {dev.address} (rssi={adv.rssi})"
        for (dev, adv) in devices.values()
    }


def ask_for_scan():
    dlg = wx.MessageDialog(
        None,
        "No plotter was selected. Do you want to scan for a Bluetooth plotter now? It will take up to 2 seconds.",
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
    if ask_for_scan():
        devices = asyncio.run(scan_devices())
        return select_device(devices)
