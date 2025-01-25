class SilhouetteCameoConnection:
  """Represents a (physical) connection to the plotter that can be written to and read from, like USB, Bluetooth LE, ..."""
  def read(self, size=64, timeout=5000):
    raise NotImplementedError()

  def write(self, data, is_query=False, timeout=10000):
    """Send a command to the device."""
    raise NotImplementedError()

  def close(self):
    """Close the connection"""
    pass

  def __del__(self):
    self.close()

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.close()
