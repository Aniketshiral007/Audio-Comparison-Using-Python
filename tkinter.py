import tkinter as tk
import os
import numpy as np
import librosa
import sounddevice as sd
import soundfile as sf
import tempfile
from scipy import signal
import threading


class AudioClassifierApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Audio Comparison")
        
        # Create temporary directory for recorded files
        self.temp_dir = tempfile.mkdtemp()
        
        # Configure window size and position
        window_width = 400
        window_height = 400
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        master.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        # Create header label
        self.header_label = tk.Label(master, text="Audio Comparison", font=("Arial", 24, "bold"), pady=20)
        self.header_label.pack()
        
        # Create record buttons
        self.record_master_button = tk.Button(master, text="Record Master Audio", command=self.record_master_audio, font=("Arial", 14))
        self.record_master_button.pack(pady=10)
        
        self.stop_test_button = tk.Button(master, text="Stop Test Audio", command=self.stop_test_audio, font=("Arial", 14), state=tk.DISABLED)
        self.stop_test_button.pack(pady=10)
        
        self.stop_all_button = tk.Button(master, text="Stop All", command=self.stop_all_processes, font=("Arial", 14), state=tk.DISABLED)
        self.stop_all_button.pack(pady=10)
        
        # Create compare button
        self.compare_button = tk.Button(master, text="Compare Audio", command=self.compare_audio, font=("Arial", 16, "bold"), bg="#4CAF50", fg="white", state=tk.DISABLED)
        self.compare_button.pack(pady=20)
        
        # Label to show result
        self.result_label = tk.Label(master, text="", font=("Arial", 14))
        self.result_label.pack(pady=20)
        
        # Initialize file paths and variables
        self.master_audio_path = None
        self.test_audio_path = None
        self.tolerance_percentage = 10  # Updated tolerance percentage for frequency comparison
        self.sample_rate = 44100  # Sample rate for recording
        self.master_duration = 2  # Duration of master recording in seconds
        self.test_duration = 0.7  # Duration of test recording in seconds
        self.window_size = 2048  # Size of FFT window
        
        # Frequency range of interest (example: 100 Hz to 5000 Hz)
        self.min_freq = 100
        self.max_freq = 5000
        
        # Flag for continuous test recording
        self.continuous_test_recording = False
        self.recording_thread = None

    # Function to record audio with noise reduction and measure peak frequency
    def record_audio(self, filename, duration):
        try:
            # Record audio
            recording = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, channels=1, dtype='float32')
            sd.wait()  # Wait until recording is finished
            
            # Apply band-pass filter (example: using scipy.signal.butter for band-pass filter)
            b, a = signal.butter(4, [self.min_freq/(self.sample_rate/2), self.max_freq/(self.sample_rate/2)], 'band')
            filtered_recording = signal.filtfilt(b, a, recording[:, 0])
            
            # Save the filtered recording
            sf.write(filename, filtered_recording, self.sample_rate)
            
            return filename
        except Exception as e:
            self.result_label.config(text=f"Error recording audio: {e}", fg="red")
            return None

    # Function to record master audio
    def record_master_audio(self):
        try:
            filename = os.path.join(self.temp_dir, "master_audio.wav")
            recorded_file = self.record_audio(filename, self.master_duration)
            
            if recorded_file:
                self.master_audio_path = recorded_file
                self.result_label.config(text=f"Recorded master audio: {recorded_file}", fg="green")
                
                # Enable stop test and stop all buttons, disable record master button
                self.record_master_button.config(state=tk.DISABLED)
                self.stop_test_button.config(state=tk.NORMAL)
                self.stop_all_button.config(state=tk.NORMAL)
                self.compare_button.config(state=tk.NORMAL)
                
                # Start listening for test audio
                self.continuous_test_recording = True
                self.recording_thread = threading.Thread(target=self.listen_for_test_audio)
                self.recording_thread.start()
        except Exception as e:
            self.result_label.config(text=f"Error recording master audio: {e}", fg="red")
    
    # Function to stop test audio recording
    def stop_test_audio(self):
        self.continuous_test_recording = False
        self.result_label.config(text="Stopped test audio recording.", fg="blue")
        
        # Disable stop test button
        self.stop_test_button.config(state=tk.DISABLED)
    
    # Function to stop all processes
    def stop_all_processes(self):
        self.continuous_test_recording = False
        if self.recording_thread:
            self.recording_thread.join()
        
        self.result_label.config(text="Stopped all processes.", fg="blue")
        
        # Disable stop all button
        self.stop_all_button.config(state=tk.DISABLED)
        
        # Enable record master button
        self.record_master_button.config(state=tk.NORMAL)
    
    # Function to listen for test audio continuously
    def listen_for_test_audio(self):
        try:
            while self.continuous_test_recording:
                filename = os.path.join(self.temp_dir, "test_audio.wav")
                self.record_audio(filename, self.test_duration)
                
                # Compare with master audio
                self.compare_audio()
        except Exception as e:
            self.result_label.config(text=f"Error recording or comparing test audio: {e}", fg="red")
    
    # Function to find peak frequency in a given audio segment
    def find_peak_frequency(self, audio_segment):
        try:
            # Compute FFT
            n = len(audio_segment)
            yf = np.fft.fft(audio_segment)
            xf = np.fft.fftfreq(n, 1 / self.sample_rate)[:n // 2]
            yf_abs = np.abs(yf[:n // 2])
            
            # Find the dominant frequency within the specified range
            valid_indices = np.where((xf >= self.min_freq) & (xf <= self.max_freq))
            dominant_freq_index = valid_indices[0][np.argmax(yf_abs[valid_indices])]
            dominant_freq = xf[dominant_freq_index]
            
            return dominant_freq
        except Exception as e:
            self.result_label.config(text=f"Error processing audio segment: {e}", fg="red")
            return None

    # Function to compare audio
        # Function to compare audio
    def compare_audio(self):
        if not self.master_audio_path or not self.continuous_test_recording:
            return
        
        try:
            # Find peak frequency for master audio
            master_audio, _ = librosa.load(self.master_audio_path, sr=self.sample_rate)
            master_freq = self.find_peak_frequency(master_audio)
            
            if master_freq is None:
                return
            
            # Calculate tolerance for proceeding with comparison (10% of master frequency)
            proceed_tolerance = (15 / 100) * master_freq
            
            # Define the valid frequency range for proceeding with comparison (±10% of master frequency)
            valid_freq_range = (master_freq - proceed_tolerance, master_freq + proceed_tolerance)
            
            # Find peak frequency for current test audio
            test_audio_path = os.path.join(self.temp_dir, "test_audio.wav")
            test_audio, _ = librosa.load(test_audio_path, sr=self.sample_rate)
            test_freq = self.find_peak_frequency(test_audio)
            
            if test_freq is None:
                return
            
            # Check if test frequency is within ±15% range of master frequency
            if valid_freq_range[0] <= test_freq <= valid_freq_range[1]:
                # Add extra frequency of 2000 Hz to both master and test audio
                master_freq_with_extra = master_freq + 2000
                test_freq_with_extra = test_freq + 2000
                
                # Compare frequencies with the added extra frequency
                freq_diff = np.abs(master_freq_with_extra - test_freq_with_extra)
                
                # Check if frequency difference is within 5% tolerance for match/mismatch
                match_tolerance = (10 / 100) * master_freq_with_extra
                if freq_diff <= match_tolerance:
                    result_message = f"Matched: Master Frequency = {master_freq_with_extra:.2f} Hz, Test Frequency = {test_freq_with_extra:.2f} Hz"
                    self.result_label.config(text=result_message, fg="green")
                else:
                    result_message = f"Mismatched: Master Frequency = {master_freq:.2f} Hz, Test Frequency = {test_freq:.2f} Hz"
                    self.result_label.config(text=result_message, fg="red")
            else:
                result_message = f"Ignored: Master Frequency = {master_freq_with_extra:.2f} Hz, Test Frequency = {test_freq_with_extra:.2f} Hz (Outside ±10% range)"
                self.result_label.config(text=result_message, fg="orange")
        
        except Exception as e:
            self.result_label.config(text=f"Error comparing audio files: {e}", fg="red")

# Main function to run the Tkinter app
def main():
    root = tk.Tk()
    app = AudioClassifierApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
