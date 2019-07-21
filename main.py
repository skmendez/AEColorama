import cv2
import numpy as np

import config
from colors import Color, ColorWheel, table_from_cmap
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
wheel = ColorWheel({0: m1, 54: m2, 118: m3, 138: m3, 202: m2})


class Colorama:
    def __init__(self, filename, table):
        self.filename = filename
        self.arr = cv2.cvtColor(cv2.imread(f"images/{filename}"), cv2.COLOR_RGB2GRAY)
        self.table = table
        self._generated = False

    def create_window(self):
        if not self._generated:
            cv2.namedWindow(self.filename, cv2.WINDOW_NORMAL)
            self._generated = True


table = wheel.generate_lookup()

image_wheels = [Colorama("hands.jpg", table),
                Colorama("scale.png", table)]


total = 0
power_filter = ExpFilter(alpha_decay=0.2, alpha_rise=0.2)
y_roll = np.random.rand(4, config.FRAMES_PER_BUFFER) / 1e16
while True:

    y = np.mean(
        np.frombuffer(stream.read(config.FRAMES_PER_BUFFER, exception_on_overflow=False), dtype=np.int16).reshape(-1, 2),
        axis=1)/2 ** 16
    stream.read(stream.get_read_available(), exception_on_overflow=False)
    y_roll[:-1] = y_roll[1:]
    y_roll[-1, :] = np.copy(y)
    y_data = np.concatenate(y_roll, axis=0)
    inter = (y_data.astype(float)**2)
    power = np.mean(inter)
    power *= 10 ** config.GAIN
    total += power_filter.update(power)

    for iw in image_wheels:
        iw.create_window()
        process = (iw.arr+int(total)).astype(np.uint8)
        out = iw.table.process_image(process)
        cv2.imshow(iw.filename, cv2.cvtColor(out, cv2.COLOR_BGR2RGB))

    if cv2.waitKey(5) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break



