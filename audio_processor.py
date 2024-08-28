import pyaudio
import numpy as np
from scipy import signal

CHUNK = 1024  # Increased for better processing
FORMAT = pyaudio.paFloat32
RATE = 48000
CHANNELS = 2

# Global variables for effect control
gain = 10.0
distortion = 35.0
noise_gate_threshold = 0.0
pre_eq_freq = 2000  # Hz
post_eq_low = 100  # Hz
post_eq_high = 5000  # Hz

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

def apply_noise_gate(audio_data, threshold):
    mask = np.abs(audio_data) > threshold
    return audio_data * mask

def apply_pre_eq(audio_data, cutoff):
    nyquist = RATE / 2
    normalized_cutoff = cutoff / nyquist
    b, a = signal.butter(4, normalized_cutoff, btype='low')
    return signal.lfilter(b, a, audio_data)

def apply_distortion(audio_data, amount):
    # Combine soft and hard clipping for a smoother distortion
    soft_clip = 2 / np.pi * np.arctan(audio_data * amount)
    hard_clip = np.clip(audio_data * amount, -0.8, 0.8)
    return 0.7 * soft_clip + 0.3 * hard_clip

def apply_cabinet_sim(audio_data):
    # Simple cabinet simulation using a low-pass filter
    nyquist = RATE / 2
    cutoff = 5000 / nyquist
    b, a = signal.butter(2, cutoff, btype='low')
    return signal.lfilter(b, a, audio_data)

def apply_post_eq(audio_data, low_freq, high_freq):
    nyquist = RATE / 2
    low = low_freq / nyquist
    high = high_freq / nyquist
    b, a = signal.butter(2, [low, high], btype='band')
    return signal.lfilter(b, a, audio_data)

def audio_callback(in_data, frame_count, time_info, status):
    global gain, distortion, noise_gate_threshold, pre_eq_freq, post_eq_low, post_eq_high
    audio_data = np.frombuffer(in_data, dtype=np.float32).copy()
    
    # Apply noise gate
    audio_data = apply_noise_gate(audio_data, noise_gate_threshold)
    
    # Apply pre-EQ
    # audio_data = apply_pre_eq(audio_data, pre_eq_freq)
    
    # Apply gain
    audio_data *= gain
    
    # Apply distortion
    audio_data = apply_distortion(audio_data, distortion)
    
    # Apply cabinet simulation
    # audio_data = apply_cabinet_sim(audio_data)
    
    # Apply post-EQ
    # audio_data = apply_post_eq(audio_data, post_eq_low, post_eq_high)
    
    # Final clipping
    np.clip(audio_data, -1.0, 1.0, out=audio_data)
    
    return (audio_data.tobytes(), pyaudio.paContinue)

def main():
    global gain, distortion, noise_gate_threshold, pre_eq_freq, post_eq_low, post_eq_high
    list_devices()
    
    input_device = int(input("Enter input device index: "))
    output_device = int(input("Enter output device index: "))
    
    p = pyaudio.PyAudio()

    try:
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        output=True,
                        input_device_index=input_device,
                        output_device_index=output_device,
                        frames_per_buffer=CHUNK,
                        stream_callback=audio_callback)

        print(f"Audio processor is running.")
        print(f"Buffer size: {CHUNK}, Sample rate: {RATE}, Channels: {CHANNELS}")
        print("Use the following commands:")
        print("  'g <value>' to set gain (e.g., 'g 1.0' for 100% volume)")
        print("  'd <value>' to set distortion (e.g., 'd 20.0' for heavy distortion)")
        print("  'n <value>' to set noise gate threshold (e.g., 'n 0.005')")
        print("  'pre <value>' to set pre-EQ frequency (e.g., 'pre 2000')")
        print("  'post <low> <high>' to set post-EQ (e.g., 'post 100 5000')")
        print("  'q' to quit")
        
        stream.start_stream()

        while stream.is_active():
            command = input("Enter command: ").strip().lower()
            if command.startswith('g '):
                try:
                    gain = float(command[2:])
                    print(f"Gain set to {gain}")
                except ValueError:
                    print("Invalid gain value. Please enter a number.")
            elif command.startswith('d '):
                try:
                    distortion = float(command[2:])
                    print(f"Distortion set to {distortion}")
                except ValueError:
                    print("Invalid distortion value. Please enter a number.")
            elif command.startswith('n '):
                try:
                    noise_gate_threshold = float(command[2:])
                    print(f"Noise gate threshold set to {noise_gate_threshold}")
                except ValueError:
                    print("Invalid noise gate value. Please enter a number.")
            elif command.startswith('pre '):
                try:
                    pre_eq_freq = float(command[4:])
                    print(f"Pre-EQ frequency set to {pre_eq_freq} Hz")
                except ValueError:
                    print("Invalid pre-EQ frequency value. Please enter a number.")
            elif command.startswith('post '):
                try:
                    parts = command.split()
                    post_eq_low = float(parts[1])
                    post_eq_high = float(parts[2])
                    print(f"Post-EQ set to {post_eq_low}Hz - {post_eq_high}Hz")
                except (ValueError, IndexError):
                    print("Invalid post-EQ values. Please enter two numbers.")
            elif command == 'q':
                break
            else:
                print("Unknown command")

    except KeyboardInterrupt:
        print("Stopping audio processor...")
    finally:
        if 'stream' in locals():
            stream.stop_stream()
            stream.close()
        p.terminate()

if __name__ == "__main__":
    main()
