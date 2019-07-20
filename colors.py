import warnings
from typing import Dict

import cv2
import numpy as np
from skimage import img_as_float, img_as_ubyte

WHEEL_SIZE = 2 ** 8


def interp(c1, c2, ratio):
    v1 = cv2.cvtColor(img_as_float(c1.rgb)[np.newaxis, np.newaxis].astype(np.float32), cv2.COLOR_RGB2LAB)
    v2 = cv2.cvtColor(img_as_float(c2.rgb)[np.newaxis, np.newaxis].astype(np.float32), cv2.COLOR_RGB2LAB)
    new_lab = (v1 + (v2 - v1) * ratio)
    new_rgb = cv2.cvtColor(new_lab, cv2.COLOR_LAB2RGB)[0][0]
    # TODO: Catch warning
    with warnings.catch_warnings():
        new_rgb = img_as_ubyte(new_rgb)
    return Color(*new_rgb)


class Color:
    __slots__ = ["r", "g", "b", "a", "rgb", "lab"]

    def __init__(self, r: int, g: int, b: int, a=255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        self.rgb = np.uint8([r, g, b])
        self.lab = cv2.cvtColor(self.rgb[np.newaxis, np.newaxis], cv2.COLOR_RGB2LAB)[0][0]

    @classmethod
    def from_lab(cls, lab):
        rgb = cv2.cvtColor(lab[np.newaxis, np.newaxis], cv2.COLOR_LAB2RGB)[0][0]
        return cls(*rgb)

    def __repr__(self):
        return f"Color({self.r}, {self.g}, {self.b})"

    def interp(self, color, ratio):
        if ratio == 0:
            return self
        elif ratio == 1:
            return color
        elif 0 < ratio < 1:
            other_lab = color.lab.astype(np.double)
            my_lab = self.lab.astype(np.double)
            new_lab = (my_lab + (other_lab - my_lab) * ratio).astype(np.uint8)
            return self.from_lab(new_lab)
        else:
            raise ValueError("Ratio is between 0 and 1 inclusive")

    def basic_interp(self, color, ratio):
        a = self.rgb.astype(np.double)
        b = color.rgb.astype(np.double)
        new_rgb = (a + (b - a) * ratio).astype(np.uint8)
        return Color(*new_rgb)


class ColorWheel:
    def __init__(self, colors: Dict[int, Color]):
        if 0 not in colors:
            raise ValueError("The start must be defined")
        self.colors = colors
        self._sorted_keys = sorted(colors.keys(), reverse=True)

    def get_val(self, val):
        val %= WHEEL_SIZE
        index = next(i for i, col_deg in enumerate(self._sorted_keys) if col_deg <= val)
        next_index = (index-1) % len(self.colors)
        deg_1 = self._sorted_keys[index]
        deg_2 = self._sorted_keys[next_index]
        col_1 = self.colors[deg_1]
        col_2 = self.colors[deg_2]
        dist = val - deg_1
        diff = (deg_2 - deg_1) % WHEEL_SIZE
        ratio = dist/diff
        return col_1.basic_interp(col_2, ratio)

    def generate_lookup(self):
        return np.asarray([self.get_val(val).rgb for val in range(256)], dtype=np.uint8)


def process_image(table, img):
    return table[img].reshape((*img.shape, table.shape[1]))
