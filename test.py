import cv2
import numpy as np
import pyloudnorm as pyln

import config
from colors import Color, ColorWheel, process_image
from dsp import ExpFilter
from stream import stream

r = Color(255, 0, 0)
g = Color(0, 255, 0)
b = Color(0, 0, 255)
c = Color(0, 255, 255)
m = Color(255, 0, 255)
y = Color(255, 255, 0)

m1 = Color(39, 103, 191)
m2 = Color(32, 175, 219)
m3 = Color(53, 232, 206)
wheel = ColorWheel({0: b, 108: c, 128: g, 148: c})

image_wheel_dct = {"flower.jpg": [wheel, None],
                   "triangles.png": [wheel, None]}

# wheel = ColorWheel({0:r, 63:y, 85:g, 128:c, 171:b, 213:m}, True)
# wheel = ColorWheel({0: m1, 54: m2, 118: m3, 138: m3, 202: m2})
for filename, lst in image_wheel_dct.items():
    arr = cv2.cvtColor(cv2.imread(f"images/{filename}"), cv2.COLOR_RGB2GRAY)
    lst[1] = arr
    cv2.namedWindow(filename, cv2.WINDOW_NORMAL)

table = wheel.generate_lookup()
total = 0
power_filter = ExpFilter(0.1, 0.1)
meter = pyln.Meter(config.RATE, block_size=1/config.FPS)
while True:
    y = np.mean(
        np.fromstring(stream.read(512, exception_on_overflow=False), dtype=np.int16).reshape(-1, 2),
        axis=1)
    y = y.astype(np.float32)
    stream.read(stream.get_read_available(), exception_on_overflow=False)
    power = np.mean(y.astype(float)**2)/10000000
    print(power)
    total += power_filter.update(power)

    for filename, (wheel, arr) in image_wheel_dct.items():
        process = (arr+int(total)).astype(np.uint8)
        out = process_image(table, process)
        cv2.imshow(filename, cv2.cvtColor(out, cv2.COLOR_BGR2RGB))

    if cv2.waitKey(5) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break



