import configparser
from distutils.util import strtobool

__all__ = ["DEVICE_INDEX", "RATE", "CHANNELS", "AS_LOOPBACK", "FPS", "FRAMES_PER_BUFFER"]
parser = configparser.ConfigParser()
CONFIG_FILE = "stream.ini"


def gen_ini():
    import pyaudio
    new_parser = configparser.ConfigParser()

    # Use module
    p = pyaudio.PyAudio()

    # Select Device
    print("Valid devices:\n")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        is_input = info["maxInputChannels"] > 0
        is_wasapi = (p.get_host_api_info_by_index(info["hostApi"])["name"]).find("WASAPI") != -1
        if is_input or is_wasapi:
            print("%s: \t %s \n \t %s \n \t Loopback: %s \n" % (info["index"],
            info["name"], p.get_host_api_info_by_index(info["hostApi"])["name"], not is_input))

    # Get input or default
    device_id = int(input("Choose device: "))

    # Get device info
    device_info = p.get_device_info_by_index(device_id)

    # Choose between loopback or standard mode
    is_input = device_info["maxInputChannels"] > 0
    if is_input:
        useloopback = False
    else:
        useloopback = True

    channelcount = device_info["maxInputChannels"] if (
                device_info["maxOutputChannels"] < device_info["maxInputChannels"]) else device_info[
        "maxOutputChannels"]
    dct = dict(channels=channelcount,
               rate=int(device_info["defaultSampleRate"]),
               input_device_index=device_info["index"],
               as_loopback=useloopback)
    new_parser.add_section("STREAM")
    for k, v in dct.items():
        new_parser.set("STREAM", k, str(v))
    with open(CONFIG_FILE, "w") as f:
        new_parser.write(f)
    return parser


try:
    with open(CONFIG_FILE, "r") as f:
        parser.read_file(f)
except (FileNotFoundError, configparser.Error):
    parser = gen_ini()

DEVICE_INDEX = int(parser["STREAM"]["input_device_index"])
"""Index of audio device"""

RATE = int(parser["STREAM"]["rate"])
"""Sampling frequency of audio device in Hz"""

CHANNELS = int(parser["STREAM"]["channels"])
"""Number of channels of audio device"""

AS_LOOPBACK = strtobool(parser["STREAM"]["as_loopback"])

FPS = 60
"""Desired refresh rate of the visualization (frames per second)"""

FRAMES_PER_BUFFER = int(RATE / FPS)
"""Number of frames to sample each read"""

if __name__ == '__main__':
    gen_ini()
