import warnings
from typing import Dict

import cv2
import numpy as np
from skimage import img_as_float, img_as_ubyte

TYPE = 'uint8'
WHEEL_SIZE = (2 ** 8) ** np.dtype(TYPE).itemsize


class Color:
    __slots__ = ["r", "g", "b", "a"]

    def __init__(self, r: int, g: int, b: int, a=None):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    @property
    def rgb(self):
        if self.a is not None:
            return np.uint8([self.r, self.g, self.b, self.a])
        else:
            return np.uint8([self.r, self.g, self.b])

    def __repr__(self):
        if self.a is not None:
            return f"Color({self.r}, {self.g}, {self.b}, {self.a})"
        else:
            return f"Color({self.r}, {self.g}, {self.b})"

    def interp(self, other, ratio):
        colors = [self, other]
        if sum(color.a is None for color in colors) == 1:  # We'll cast them both to having an alpha channel
            for color in colors:
                color.a = 255 if color.a is None else color.a
        to_float = (img_as_float(color.rgb[:3]).astype(np.float32) for color in colors)
        labs = [cv2.cvtColor(img_float[np.newaxis, np.newaxis], cv2.COLOR_RGB2LAB) for img_float in to_float]

        interp_lab = labs[0] + (labs[1] - labs[0]) * ratio
        interp_float_rgb = cv2.cvtColor(interp_lab, cv2.COLOR_LAB2RGB)[0, 0]
        # TODO: Catch warning
        with warnings.catch_warnings():
            new_rgb = img_as_ubyte(interp_float_rgb)
        if colors[0].a is not None:
            new_a = round(colors[0].a + (colors[1].a - colors[0].a) * ratio)
        else:
            new_a = None
        return Color(*new_rgb, new_a)


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
        return col_1.interp(col_2, ratio)

    def generate_lookup(self):
        return np.asarray([self.get_val(val).rgb for val in range(256)], dtype=np.uint8)


def table_from_cmap(cmap):
    import matplotlib.pyplot as plt
    if isinstance(cmap, str):
        cmap = plt.get_cmap(cmap)
    arr = np.asarray(cmap.colors)[np.newaxis]
    return cv2.resize(arr, (256, 1))[0]


def process_image(table, img):
    return table[img].reshape((*img.shape, table.shape[1]))
