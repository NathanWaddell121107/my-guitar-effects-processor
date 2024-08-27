import pyaudio
import numpy as np

CHUNK = 1024
FORMAT = pyaudio.paFloat32
RATE = 44100

# Global variable for gain control
gain = 1.0

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
    global gain
    audio_data = np.frombuffer(in_data, dtype=np.float32)
    
    # Apply gain
    processed_data = audio_data * gain
    
    # Clip the signal to prevent distortion
    processed_data = np.clip(processed_data, -1.0, 1.0)
    
    output_data = processed_data.tobytes()
    return (output_data, pyaudio.paContinue)

def main():
    global gain
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

    print(f"Audio processor is running with {channels} channel(s).")
    print("Use the following commands:")
    print("  'g <value>' to set gain (e.g., 'g 1.5' for 150% volume)")
    print("  'q' to quit")
    
    try:
        stream.start_stream()
        while stream.is_active():
            command = input("Enter command: ").strip().lower()
            if command.startswith('g '):
                try:
                    new_gain = float(command[2:])
                    gain = new_gain
                    print(f"Gain set to {gain}")
                except ValueError:
                    print("Invalid gain value. Please enter a number.")
            elif command == 'q':
                break
            else:
                print("Unknown command")
    except KeyboardInterrupt:
        print("Stopping audio processor...")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    main()
