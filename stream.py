import pyaudio
import config

p = pyaudio.PyAudio()

frames_per_buffer = int(config.RATE / config.FPS)
stream = p.open(format=pyaudio.paInt16,
                channels=config.CHANNELS,
                rate=config.RATE,
                input=True,
                frames_per_buffer=frames_per_buffer,
                input_device_index=config.DEVICE_INDEX,
                as_loopback=config.AS_LOOPBACK)
