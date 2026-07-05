import sys
import time

import usb.core

from silhouette.connection import SilhouetteCameoConnection
from silhouette.DeviceConstants import *

usb_reset_needed = False  # https://github.com/fablabnbg/inkscape-silhouette/issues/10

sys_platform = sys.platform.lower()
if sys_platform.startswith('win'):
  import usb.core
elif sys_platform.startswith('darwin'):
  import usb1, usb.core
  usb1ctx = usb1.USBContext()
else:   # if sys_platform.startswith('linux'):
  try:
    import usb.core  # where???
  except Exception as e:
      try:
          import libusb1 as usb
      except Exception as e1:
        try:
          import usb
        except Exception as e2:
          print("The python usb module could not be found. Try", file=sys.stderr)
          print("\t sudo zypper in python-usb \t\t# if you run SUSE", file=sys.stderr)
          print("\t sudo apt-get install python-usb   \t\t# if you run Ubuntu", file=sys.stderr)
          print("\n\n\n", file=sys.stderr)
          raise e2

try:
    try:
      usb_vi = usb.version_info[0]
      usb_vi_str = str(usb.version_info)
    except AttributeError:
      usb_vi = 0
      if sys_platform.startswith('win'):
        usb_vi = 1
        pass # windows does not seem to detect the usb.version , gives attribute error. Other tests of pyusb work, pyusb is installed.
      usb_vi_str = 'unknown'


    if usb_vi < 1:
      print("Your python usb module appears to be "+usb_vi_str+" -- We need version 1.x", file=sys.stderr)
      print("For Debian 8 try:\n  echo > /etc/apt/sources.list.d/backports.list 'deb http://ftp.debian.org debian jessie-backports main\n  apt-get update\n  apt-get -t jessie-backports install python-usb", file=sys.stderr)
      print("\n\n\n", file=sys.stderr)
      print("For Ubuntu 14.04try:\n  pip install pyusb --upgrade", file=sys.stderr)
      print("\n\n\n", file=sys.stderr)
      sys.exit(0)
except NameError:
    pass # on OS X usb.version_info[0] will always fail as libusb1 is being used


class SilhouetteCameoUSBConnection(SilhouetteCameoConnection):
  """Cameo plotter connected via USB"""

  def __init__(self, force_hardware, log, progress_cb):
    """
    Finds the first supported plotter on USB bus and sets up self.dev
    Do not call outside __init__!
    """
    self.log = log
    self.need_interface = False  # probably never needed, but harmful on some versions of usb.core
    self.progress_cb = progress_cb
    usbdev = None

    for hardware in DEVICE:
      try:
        if sys_platform.startswith('win'):
          print("device lookup under windows not tested. Help adding code!", file=self.log)
          usbdev = usb.core.find(idVendor=hardware['vendor_id'], idProduct=hardware['product_id'])

        elif sys_platform.startswith('darwin'):
          usbdev = usb1ctx.openByVendorIDAndProductID(hardware['vendor_id'], hardware['product_id'])

        else:  # linux
          usbdev = usb.core.find(idVendor=hardware['vendor_id'], idProduct=hardware['product_id'])
      except usb.core.NoBackendError:
        usbdev = None
      if usbdev:
        self.hardware = hardware
        break
    if usbdev is None:
      try:
        if sys_platform.startswith('win'):
          print("device fallback under windows not tested. Help adding code!", file=self.log)
          usbdev = usb.core.find(idVendor=VENDOR_ID_GRAPHTEC)
          self.hardware = {'name': 'Unknown Graphtec device'}
          if usbdev:
            self.hardware['name'] += " 0x%04x" % usbdev.idProduct
            self.hardware['product_id'] = usbdev.idProduct
            self.hardware['vendor_id'] = usbdev.idVendor

        elif sys_platform.startswith('darwin'):
          print("device fallback under macosx not implemented. Help adding code!", file=self.log)

        else:  # linux
          usbdev = usb.core.find(idVendor=VENDOR_ID_GRAPHTEC)
          self.hardware = {'name': 'Unknown Graphtec device '}
          if usbdev:
            self.hardware['name'] += " 0x%04x" % usbdev.idProduct
            self.hardware['product_id'] = usbdev.idProduct
            self.hardware['vendor_id'] = usbdev.idVendor
      except usb.core.NoBackendError:
        usbdev = None
    if usbdev is None:
      msg = ''
      try:
        for usbdev in usb.core.find(find_all=True):
          msg += "(%04x,%04x) " % (usbdev.idVendor, usbdev.idProduct)
      except NameError:
        msg += "unable to list devices on OS X"
      raise ValueError('No Graphtec Silhouette devices found.\nCheck USB and Power.\nDevices: ' + msg)
    try:
      dev_bus = usbdev.bus
    except:
      dev_bus = -1
    try:
      dev_addr = usbdev.address
    except:
      dev_addr = -1
    print("%s found on usb bus=%d addr=%d" % (self.hardware['name'], dev_bus, dev_addr), file=self.log)
    if usbdev is not None:
      if sys_platform.startswith('win'):
        print("device init under windows not implemented. Help adding code!", file=self.log)

      elif sys_platform.startswith('darwin'):
        usbdev.claimInterface(0)
        # usb_enpoint = 1
        # dev.bulkWrite(usb_endpoint, data)

      else:  # linux
        try:
          if usbdev.is_kernel_driver_active(0):
            print("is_kernel_driver_active(0) returned nonzero", file=self.log)
            if usbdev.detach_kernel_driver(0):
              print("detach_kernel_driver(0) returned nonzero", file=self.log)
        except usb.core.USBError as e:
          print("usb.core.USBError:", e, file=self.log)
          if e.errno == 13:
            msg = """
  If you are not running as root, this might be a udev issue.
  Try a file /etc/udev/rules.d/99-graphtec-silhouette.rules
  with the following example syntax:
  SUBSYSTEM=="usb", ATTR{idVendor}=="%04x", ATTR{idProduct}=="%04x", MODE="666"

  Then run 'sudo udevadm trigger' to load this file.

  Alternatively, you can add yourself to group 'lp' and logout/login.""" % (
              self.hardware['vendor_id'], self.hardware['product_id'])
            print(msg, file=self.log)
            print(msg, file=sys.stderr)
          sys.exit(0)

        if usb_reset_needed:
          for i in range(5):
            try:
              usbdev.reset()
              break
            except usb.core.USBError as e:
              print("reset failed: ", e, file=self.log)
              print("retrying reset in 5 sec", file=self.log)
              time.sleep(5)

        try:
          usbdev.set_configuration()
          usbdev.set_interface_altsetting()  # Probably not really necessary.
        except usb.core.USBError:
          pass
    for hardware in DEVICE:
      if hardware["name"] == force_hardware:
        print("NOTE: Overriding device from", self.hardware.get('name', 'None'),
              "to", hardware['name'], file=self.log)
        self.hardware = hardware
        break
    self.dev = usbdev

  def read(self, size=64, timeout=5000):
    """Low level read method, returns response as bytes"""
    endpoint = 0x82
    data = None

    if self.need_interface:
        try:
            data = self.dev.read(endpoint, size, timeout=timeout, interface=0)
        except AttributeError:
            data = self.dev.bulkRead(endpoint, size, timeout=timeout, interface=0)
    else:
        try:
            data = self.dev.read(endpoint, size, timeout=timeout)
        except AttributeError:
            data = self.dev.bulkRead(endpoint, size, timeout=timeout)
    if data is None:
      raise ValueError('read failed: none')
    if isinstance(data, (bytes, bytearray)):
        return data
    elif isinstance(data, str):
        return data.encode()
    else:
        try:
            return data.tobytes() # with py3
        except:
            return data.tostring().encode() # with py2/3 - dropped in py39


  def write(self, data, is_query=False, timeout=10000):
    """Long commands are sent in chunks of 4096 bytes.
       A nonblocking read() is attempted before write(), to find spurious diagnostics."""
    data = to_bytes(data)

    # robocut/Plotter.cpp:73 says: Send in 4096 byte chunks. Not sure where I got this from, I'm not sure it is actually necessary.
    try:
      resp = self.read(timeout=10) # poll the inbound buffer
      if resp:
        print("response before write('%s'): '%s'" % (data, resp), file=self.log)
    except:
      pass
    endpoint = 0x01
    chunksz = 4096
    r = 0
    o = 0
    msg=''
    retry = 0
    while o < len(data):
      if o:
        if self.progress_cb:
          self.progress_cb(o,len(data),msg)
        elif self.log:
          self.log.write(" %d%% %s\r" % (100.*o/len(data),msg))
          self.log.flush()
      chunk = data[o:o+chunksz]
      try:
        if self.need_interface:
          try:
            r = self.dev.write(endpoint, chunk, interface=0, timeout=timeout)
          except AttributeError:
            r = self.dev.bulkWrite(endpoint, chunk, interface=0, timeout=timeout)
        else:
          try:
            r = self.dev.write(endpoint, chunk, timeout=timeout)
          except AttributeError:
            r = self.dev.bulkWrite(endpoint, chunk, timeout=timeout)
      except TypeError as te:
        # write() got an unexpected keyword argument 'interface'
        raise TypeError("Write Exception: %s, %s dev=%s" % (type(te), te, type(self.dev)))
      except AttributeError as ae:
        # write() got an unexpected keyword argument 'interface'
        raise TypeError("Write Exception: %s, %s dev=%s" % (type(ae), ae, type(self.dev)))

      except Exception as e:
        # raise USBError(_str_error[ret], ret, _libusb_errno[ret])
        # usb.core.USBError: [Errno 110] Operation timed
        #print("Write Exception: %s, %s errno=%s" % (type(e), e, e.errno), file=s.log)
        import errno
        try:
          if e.errno == errno.ETIMEDOUT:
            time.sleep(1)
            msg += 't'
            continue
        except Exception as ee:
          msg += "s.dev.write Error:  {}".format(ee)
      else:
        if len(msg):
          msg = ''
          self.log.write("\n")

      # print("write([%d:%d], len=%d) = %d" % (o,o+chunksz, len(chunk), r), file=s.log)
      if r == 0 and retry < 5:
        time.sleep(1)
        retry += 1
        msg += 'r'
      elif r <= 0:
        raise ValueError('write %d bytes failed: r=%d' % (len(chunk), r))
      else:
        retry = 0
      o += r

    if o != len(data):
      raise ValueError('write all %d bytes failed: o=%d' % (len(data), o))

  def close(self):
    if self.dev:
      self.dev.close()
    self.dev = None

def to_bytes(b_or_s):
  """Ensure a value is bytes"""
  if isinstance(b_or_s, str): return b_or_s.encode()
  if isinstance(b_or_s, bytes): return b_or_s
  raise TypeError("Value must be a string or bytes.")