import pyaudio
import numpy as np

CHUNK = 1024
FORMAT = pyaudio.paFloat32
RATE = 48000
CHANNELS = 2

p = pyaudio.PyAudio()

def callback(in_data, frame_count, time_info, status):
    return (in_data, pyaudio.paContinue)

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                frames_per_buffer=CHUNK,
                stream_callback=callback)

print("Starting audio passthrough. Press Ctrl+C to stop.")

try:
    stream.start_stream()
    while stream.is_active():
        pass
except KeyboardInterrupt:
    print("Stopping...")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()

print("Audio passthrough stopped.")
