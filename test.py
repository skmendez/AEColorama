import cv2
import pyaudio
import config
import numpy as np

from colors import Color, ColorWheel, process_image
import config
from dsp import ExpFilter

p = pyaudio.PyAudio()

frames_per_buffer = int(config.MIC_RATE / config.FPS)
device = p.get_default_output_device_info()
stream = p.open(format=pyaudio.paInt16,
                channels=2,
                rate=config.MIC_RATE,
                input=True,
                frames_per_buffer=frames_per_buffer,
                input_device_index=config.DEVICE_INDEX,
                as_loopback=True)
r = Color(255, 0, 0)
g = Color(0, 255, 0)
b = Color(0, 0, 255)
c = Color(0, 255, 255)
m = Color(255,0,255)
y = Color(255,255,0)

m1 = Color(39, 103, 191)
m2 = Color(32, 175, 219)
m3 = Color(53, 232, 206)
# wheel = ColorWheel({0: b, 108: c, 128: g, 148: c}, True)
# wheel = ColorWheel({0:r, 63:y, 85:g, 128:c, 171:b, 213:m}, True)
wheel = ColorWheel({0: m1, 54: m2, 118: m3, 138: m3, 202: m2})
cv2.namedWindow('image1', cv2.WINDOW_NORMAL)
cv2.namedWindow('image2', cv2.WINDOW_NORMAL)
arr1 = cv2.cvtColor(cv2.imread("../maxresdefault.jpg"), cv2.COLOR_RGB2GRAY)
arr2 = cv2.cvtColor(cv2.imread("../scale.png"), cv2.COLOR_RGB2GRAY)
table = wheel.generate_lookup()
total = 0
power_filter = ExpFilter(0.1, 0.1)
while True:
    y = np.mean(
        np.fromstring(stream.read(512, exception_on_overflow=False), dtype=np.int16).reshape(-1, 2),
        axis=1)
    y = y.astype(np.float32)
    stream.read(stream.get_read_available(), exception_on_overflow=False)
    power = np.mean(y.astype(float)**2)/10000000
    print(power)
    total += power_filter.update(power)

    process1 = (arr1+int(total)).astype(np.uint8)
    process2 = (arr2+int(total)).astype(np.uint8)
    #process = arr
    out1 = process_image(table, process1)
    out2 = process_image(table, process2)


    cv2.imshow('image1', cv2.cvtColor(out1, cv2.COLOR_BGR2RGB))
    cv2.imshow('image2', cv2.cvtColor(out2, cv2.COLOR_BGR2RGB))
    if cv2.waitKey(5) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break



