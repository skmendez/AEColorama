import pyaudio
import config

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=config.CHANNELS,
                rate=config.RATE,
                input=True,
                frames_per_buffer=config.FRAMES_PER_BUFFER,
                input_device_index=config.DEVICE_INDEX,
                as_loopback=config.AS_LOOPBACK)
