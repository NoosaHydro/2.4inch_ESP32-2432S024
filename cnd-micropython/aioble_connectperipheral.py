# Either from scan result
device = result.device
# Or with known address
device = aioble.Device(aioble.PUBLIC, "aa:bb:cc:dd:ee:ff")

try:
    connection = await device.connect(timeout_ms=2000)
except asyncio.TimeoutError:
    print('Timeout')

