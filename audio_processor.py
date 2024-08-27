import pyaudio
import numpy as np

CHUNK = 1024
FORMAT = pyaudio.paFloat32
RATE = 44100

def list_devices():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')
    
    for i in range(num_devices):
        device = p.get_device_info_by_host_api_device_index(0, i)
        print(f"Device {i}: {device['name']}")
        print(f"  Input channels: {device['maxInputChannels']}")
        print(f"  Output channels: {device['maxOutputChannels']}")
    
    p.terminate()

def audio_callback(in_data, frame_count, time_info, status):
    # Convert input data to numpy array
    audio_data = np.frombuffer(in_data, dtype=np.float32)
    
    # For now, we're just passing the input directly to the output
    # Later, we'll add processing here
    output_data = audio_data.tobytes()
    
    return (output_data, pyaudio.paContinue)

def main():
    list_devices()
    
    input_device = int(input("Enter input device index: "))
    output_device = int(input("Enter output device index: "))
    
    p = pyaudio.PyAudio()

    input_info = p.get_device_info_by_index(input_device)
    output_info = p.get_device_info_by_index(output_device)

    input_channels = input_info['maxInputChannels']
    output_channels = output_info['maxOutputChannels']

    # Use the minimum number of channels supported by both devices
    channels = min(input_channels, output_channels)

    stream = p.open(format=FORMAT,
                    channels=channels,
                    rate=RATE,
                    input=True,
                    output=True,
                    input_device_index=input_device,
                    output_device_index=output_device,
                    frames_per_buffer=CHUNK,
                    stream_callback=audio_callback)

    print(f"Audio processor is running with {channels} channel(s). Press Ctrl+C to stop.")
    
    try:
        stream.start_stream()
        while stream.is_active():
            pass
    except KeyboardInterrupt:
        print("Stopping audio processor...")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    main()
