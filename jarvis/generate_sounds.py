"""Notification ovoz yaratish - Jarvis eshita boshlaganda"""
import struct
import wave
import math
import os

def generate_listen_sound():
    """Qisqa 'ding' ovoz yaratish"""
    sample_rate = 44100
    duration = 0.3  # 300ms
    
    # Ikki nota: yuqoriga ko'tariluvchi ding
    frequencies = [880, 1320]  # A5 -> E6
    durations = [0.15, 0.15]
    
    samples = []
    for freq, dur in zip(frequencies, durations):
        n_samples = int(sample_rate * dur)
        for i in range(n_samples):
            t = i / sample_rate
            # Fade in/out
            envelope = min(1.0, t * 20) * max(0, 1 - (t / dur) * 1.5)
            # Sine wave
            sample = envelope * 0.4 * math.sin(2 * math.pi * freq * t)
            # Harmonik
            sample += envelope * 0.15 * math.sin(2 * math.pi * freq * 2 * t)
            samples.append(sample)
    
    # Convert to 16-bit PCM
    pcm_data = b""
    for s in samples:
        s = max(-1, min(1, s))
        pcm_data += struct.pack("<h", int(s * 32767))
    
    # WAV faylga yozish
    sounds_dir = os.path.join(os.path.dirname(__file__), "assets", "sounds")
    os.makedirs(sounds_dir, exist_ok=True)
    filepath = os.path.join(sounds_dir, "listen_start.wav")
    
    with wave.open(filepath, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_data)
    
    print(f"Ovoz yaratildi: {filepath}")
    return filepath


def generate_listen_stop_sound():
    """Eshitish tugaganda qisqa ovoz"""
    sample_rate = 44100
    
    # Pastga tushuvchi nota
    frequencies = [1320, 880]  # E6 -> A5
    durations = [0.1, 0.15]
    
    samples = []
    for freq, dur in zip(frequencies, durations):
        n_samples = int(sample_rate * dur)
        for i in range(n_samples):
            t = i / sample_rate
            envelope = min(1.0, t * 30) * max(0, 1 - (t / dur) * 1.5)
            sample = envelope * 0.3 * math.sin(2 * math.pi * freq * t)
            sample += envelope * 0.1 * math.sin(2 * math.pi * freq * 2 * t)
            samples.append(sample)
    
    pcm_data = b""
    for s in samples:
        s = max(-1, min(1, s))
        pcm_data += struct.pack("<h", int(s * 32767))
    
    sounds_dir = os.path.join(os.path.dirname(__file__), "assets", "sounds")
    os.makedirs(sounds_dir, exist_ok=True)
    filepath = os.path.join(sounds_dir, "listen_stop.wav")
    
    with wave.open(filepath, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_data)
    
    print(f"Ovoz yaratildi: {filepath}")
    return filepath


if __name__ == "__main__":
    generate_listen_sound()
    generate_listen_stop_sound()
