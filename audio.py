# ### final with TCPIP
# import socket
# import os
# import numpy as np
# import librosa
# import sounddevice as sd
# import soundfile as sf
# import tempfile
# from scipy import signal
# import threading
# import socket

# class AudioClassifierApp:
#     def __init__(self):
#         # Set default folder for audio files
#         self.default_folder = r"D:\node_tcp\uploads"  # Change this to your desired path
        
#         # Ensure the folder exists
#         os.makedirs(self.default_folder, exist_ok=True)
#         print("folder exists")
#         # Initialize file paths and variables
#         self.master_audio_path = os.path.join(self.default_folder, "master_audio.wav")
#         self.test_audio_path = os.path.join(self.default_folder, "test_audio.wav")
#         print("folder exists", self.master_audio_path)
#         # self.tolerance_percentage = 10  # Updated tolerance percentage for frequency comparison
#         self.sample_rate = 44100  # Sample rate for recording
#         self.master_duration = 2  # Duration of master recording in seconds
#         self.test_duration = 0.7  # Duration of test recording in seconds
#         self.window_size = 2048  # Size of FFT window
        
#         # Frequency range of interest (example: 100 Hz to 5000 Hz)
#         self.min_freq = 100
#         self.max_freq = 5000
        
#         # Flag for continuous test recording
#         self.continuous_test_recording = False
#         self.recording_thread = None

#     # Function to record audio with noise reduction and measure peak frequency
#     def record_audio(self, filename, duration):
#         try:
#             # Record audio
#             recording = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, channels=1, dtype='float32')
#             sd.wait()  # Wait until recording is finished
            
#             # Apply band-pass filter (example: using scipy.signal.butter for band-pass filter)
#             b, a = signal.butter(4, [self.min_freq/(self.sample_rate/2), self.max_freq/(self.sample_rate/2)], 'band')
#             filtered_recording = signal.filtfilt(b, a, recording[:, 0])
            
#             # Save the filtered recording
#             sf.write(filename, filtered_recording, self.sample_rate)
            
#             return filename
#         except Exception as e:
#             print(f"Error recording audio: {e}")
#             return None

#     # Function to record master audio
#     def record_master_audio(self):
#         try:
#             print("1111111")
#             filename = self.master_audio_path
#             print("filename", filename)
#             recorded_file = self.record_audio(filename, self.master_duration)
            
#             if recorded_file:
#                 print("222222")
#                 print(f"Recorded master audio: {recorded_file}")
                
#                 # Start listening for test audio
#                 self.continuous_test_recording = True
#                 self.recording_thread = threading.Thread(target=self.listen_for_test_audio)
#                 self.recording_thread.start()
#         except Exception as e:
#             print(f"Error recording master audio: {e}")
    
#     # Function to stop test audio recording
#     # def stop_test_audio(self):
#     #     self.continuous_test_recording = False
#     #     print("Stopped test audio recording.")
    
#     # Function to stop all processes
#     def stop_all_processes(self):
#         self.continuous_test_recording = False
#         if self.recording_thread:
#             self.recording_thread.join()
#         print("Stopped all processes.")
    
#     # Function to find peak frequency in a given audio segment
#     def find_peak_frequency(self, audio_segment):
#         try:
#             # Compute FFT
#             n = len(audio_segment)
#             yf = np.fft.fft(audio_segment)
#             xf = np.fft.fftfreq(n, 1 / self.sample_rate)[:n // 2]
#             yf_abs = np.abs(yf[:n // 2])
            
#             # Find the dominant frequency within the specified range
#             valid_indices = np.where((xf >= self.min_freq) & (xf <= self.max_freq))
#             dominant_freq_index = valid_indices[0][np.argmax(yf_abs[valid_indices])]
#             dominant_freq = xf[dominant_freq_index]
            
#             return dominant_freq
#         except Exception as e:
#             print(f"Error processing audio segment: {e}")
#             return None

#     # Function to listen for test audio continuously
#     def listen_for_test_audio(self):
#         try:
#             while self.continuous_test_recording:
#                 filename = self.test_audio_path
#                 self.record_audio(filename, self.test_duration)
                
#                 # Compare with master audio
#                 self.compare_audio()
#         except Exception as e:
#             print(f"Error recording or comparing test audio: {e}")

#     # Function to compare audio
#     def compare_audio(self):
#         if not self.master_audio_path or not self.continuous_test_recording:
#             return
        
#         try:
#             print("In try block")
#             # Find peak frequency for master audio
#             master_audio, _ = librosa.load(self.master_audio_path, sr=self.sample_rate)
#             master_freq = self.find_peak_frequency(master_audio)
            
#             if master_freq is None:
#                 print("Master frequency not found")
#                 return
            
#             # Calculate tolerance for proceeding with comparison (10% of master frequency)
#             proceed_tolerance = (15 / 100) * master_freq
            
#             # Calculate tolerance for determining a match (5% of master frequency)
#             match_tolerance = (12 / 100) * master_freq
            
#             # Define the valid frequency range for proceeding with comparison (±10% of master frequency)
#             valid_freq_range = (master_freq - proceed_tolerance, master_freq + proceed_tolerance)
            
#             # Find peak frequency for current test audio
#             test_audio_path = self.test_audio_path
#             test_audio, _ = librosa.load(test_audio_path, sr=self.sample_rate)
#             test_freq = self.find_peak_frequency(test_audio)

#             client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             client_socket.connect(('192.168.0.112', 5002))  # Connect to the server

#             message = {test_freq}
#             print(test_freq)
#             client_socket.send(message.encode('utf-8'))  # Send a message
#             client_socket.close()  # Close the connection

#             if test_freq is None:
#                 return
            
#             # Check if test frequency is within ±10% range of master frequency
#             if valid_freq_range[0] <= test_freq <= valid_freq_range[1]:
#                 # Compare frequencies within valid range
#                 freq_diff = np.abs(master_freq - test_freq)
#                 print("In frequency difference check")
                
#                 # Check if frequency difference is within 5% tolerance for match/mismatch
#                 if freq_diff <= match_tolerance:
#                     result_message = f"Matched: Master Frequency = {master_freq:.2f} Hz, Test Frequency = {test_freq:.2f} Hz"
#                     print(f"Matched: {result_message}")
#                     self.send_message_to_server(result_message)
#                     print("1111111111111",result_message)
#                     client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#                     client_socket.connect(('192.168.0.112', 5002))  # Connect to the server
#                     message = result_message
#                     client_socket.send(message.encode('utf-8'))  # Send a message
#                     client_socket.close()  # Close the connection
#                 else:
#                     result_message = f"Mismatched: Master Frequency = {master_freq:.2f} Hz, Test Frequency = {test_freq:.2f} Hz"
#                     print(f"Mismatched: {result_message}")
#                     self.send_message_to_server(result_message)
#                     print("222222222222",result_message)
#                     client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#                     client_socket.connect(('192.168.0.112', 5002))  # Connect to the server

#                     message = result_message
#                     client_socket.send(message.encode('utf-8'))  # Send a message
#                     client_socket.close()  # Close the connection
#             else:
#                 result_message = f"Ignored: Test Frequency = {test_freq:.2f} Hz (Outside ±10% range of Master Frequency)"
#                 print(f"Ignored: {result_message}")
#                 self.send_message_to_server(result_message)
#                 print('333333333333333333',result_message)
        
#         except Exception as e:
#             print(f"Error comparing audio files: {e}")

#     def send_message_to_server(self, message):
#         try:
#             client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             client_socket.connect(('192.168.0.112', 5002))  # Connect to the server

#             client_socket.send(message.encode('utf-8'))  # Send a message
#             client_socket.close()  # Close the connection
#         except Exception as e:
#             print(f"Error sending message to server: {e}")

#     def start_comparison(self):
#         try:
#             if self.master_audio_path:
#                 print(f"Starting comparison with last recorded master audio: {self.master_audio_path}")
                
#                 # Continue listening for test audio and comparing
#                 self.continuous_test_recording = True
#                 self.recording_thread = threading.Thread(target=self.listen_for_test_audio)
#                 self.recording_thread.start()
                
#             else:
#                 print("No master audio recorded yet.")
#         except Exception as e:
#             print(f"Error starting comparison: {e}")

# # Main function to run the server and initiate the application
# def start_server():
#     app = AudioClassifierApp()
    
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server_socket.bind(('192.168.0.112', 5001))
#     server_socket.listen(1)
#     print("Server is listening...")

#     while True:
#         client_socket, client_address = server_socket.accept()
#         print(f"Connection from {client_address} has been established.")

#         message = client_socket.recv(1024).decode('utf-8')
#         print(f"Received message: {message}")
        
#         if message == 'master':
#             app.record_master_audio()
#         elif message == 'compare':
#             app.start_comparison()
#         elif message == 'stop all':
#             app.stop_all_processes()
#         # elif message == 'stop test':
#         #     app.stop_test_audio()

#         response = f"Echo: {message}"
#         client_socket.send(response.encode('utf-8'))

#         client_socket.close()



#         response = f"Echo: {message}"
#         #client_socket.send(response.encode('utf-8'))

#         #client_socket.close()

# if __name__ == "__main__":
#     start_server()




# import socket
# import os
# import numpy as np
# import librosa
# import sounddevice as sd
# import soundfile as sf
# from scipy import signal
# import threading

# class AudioClassifierApp:
#     def __init__(self):
#         # Set default folder for audio files
#         self.default_folder = r"D:\node_tcp\uploads"  # Change this to your desired path
        
#         # Ensure the folder exists
#         os.makedirs(self.default_folder, exist_ok=True)
#         print("Folder exists or created")
        
#         # Initialize file paths and variables
#         self.master_audio_path = os.path.join(self.default_folder, "master_audio.wav")
#         self.test_audio_path = os.path.join(self.default_folder, "test_audio.wav")
#         print(f"Master audio path: {self.master_audio_path}")
#         print(f"Test audio path: {self.test_audio_path}")
        
#         self.sample_rate = 44100  # Sample rate for recording
#         self.master_duration = 2  # Duration of master recording in seconds
#         self.test_duration = 0.7  # Duration of test recording in seconds
#         self.window_size = 2048  # Size of FFT window
        
#         # Frequency range of interest (example: 100 Hz to 5000 Hz)
#         self.min_freq = 100
#         self.max_freq = 5000
        
#         # Flag for continuous test recording
#         self.continuous_test_recording = False
#         self.recording_thread = None

#     # Function to record audio with noise reduction and measure peak frequency
#     def record_audio(self, filename, duration):
#         try:
#             print(f"Recording audio for {duration} seconds and saving to {filename}")
#             # Record audio
#             recording = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, channels=1, dtype='float32')
#             print("Recording in progress...")
#             sd.wait()  # Wait until recording is finished
#             print("Recording finished")

#             # Apply band-pass filter (example: using scipy.signal.butter for band-pass filter)
#             print("Applying band-pass filter")
#             b, a = signal.butter(4, [self.min_freq/(self.sample_rate/2), self.max_freq/(self.sample_rate/2)], 'band')
#             filtered_recording = signal.filtfilt(b, a, recording[:, 0])
#             print("Band-pass filter applied")
            
#             # Save the filtered recording
#             print(f"Saving the filtered recording to {filename}")
#             sf.write(filename, filtered_recording, self.sample_rate)
#             print("Recording saved successfully")
            
#             return filename
#         except Exception as e:
#             print(f"Error recording audio: {e}")
#             return None

#     # Function to record master audio
#     def record_master_audio(self):
#         try:
#             print("Starting to record master audio")
#             filename = self.master_audio_path
#             recorded_file = self.record_audio(filename, self.master_duration)
            
#             if recorded_file:
#                 print(f"Recorded master audio: {recorded_file}")
                
#                 # Start listening for test audio
#                 self.continuous_test_recording = True
#                 self.recording_thread = threading.Thread(target=self.listen_for_test_audio)
#                 self.recording_thread.start()
#         except Exception as e:
#             print(f"Error recording master audio: {e}")
    
#     # Function to stop all processes
#     def stop_all_processes(self):
#         self.continuous_test_recording = False
#         if self.recording_thread:
#             self.recording_thread.join()
#         print("Stopped all processes.")
    
#     # Function to find peak frequency in a given audio segment
#     def find_peak_frequency(self, audio_segment):
#         try:
#             # Compute FFT
#             n = len(audio_segment)
#             yf = np.fft.fft(audio_segment)
#             xf = np.fft.fftfreq(n, 1 / self.sample_rate)[:n // 2]
#             yf_abs = np.abs(yf[:n // 2])
            
#             # Find the dominant frequency within the specified range
#             valid_indices = np.where((xf >= self.min_freq) & (xf <= self.max_freq))
#             dominant_freq_index = valid_indices[0][np.argmax(yf_abs[valid_indices])]
#             dominant_freq = xf[dominant_freq_index]
            
#             return dominant_freq
#         except Exception as e:
#             print(f"Error processing audio segment: {e}")
#             return None

#     # Function to listen for test audio continuously
#     def listen_for_test_audio(self):
#         try:
#             while self.continuous_test_recording:
#                 filename = self.test_audio_path
#                 self.record_audio(filename, self.test_duration)
                
#                 # Compare with master audio
#                 self.compare_audio()
#         except Exception as e:
#             print(f"Error recording or comparing test audio: {e}")

#     # Function to compare audio
#     def compare_audio(self):
#         if not self.master_audio_path or not self.continuous_test_recording:
#             return
        
#         try:
#             print("Comparing test audio with master audio")
#             # Find peak frequency for master audio
#             master_audio, _ = librosa.load(self.master_audio_path, sr=self.sample_rate)
#             master_freq = self.find_peak_frequency(master_audio)
            
#             if master_freq is None:
#                 print("Master frequency not found")
#                 return
            
#             # Calculate tolerance for proceeding with comparison (10% of master frequency)
#             proceed_tolerance = (15 / 100) * master_freq
            
#             # Calculate tolerance for determining a match (5% of master frequency)
#             match_tolerance = (12 / 100) * master_freq
            
#             # Define the valid frequency range for proceeding with comparison (±10% of master frequency)
#             valid_freq_range = (master_freq - proceed_tolerance, master_freq + proceed_tolerance)
            
#             # Find peak frequency for current test audio
#             test_audio_path = self.test_audio_path
#             test_audio, _ = librosa.load(test_audio_path, sr=self.sample_rate)
#             test_freq = self.find_peak_frequency(test_audio)

#             print(f"Test frequency: {test_freq}")

#             if test_freq is None:
#                 return
            
#             # Check if test frequency is within ±10% range of master frequency
#             if valid_freq_range[0] <= test_freq <= valid_freq_range[1]:
#                 # Compare frequencies within valid range
#                 freq_diff = np.abs(master_freq - test_freq)
#                 print("In frequency difference check")
                
#                 # Check if frequency difference is within 5% tolerance for match/mismatch
#                 if freq_diff <= match_tolerance:
#                     result_message = f"Matched: Master Frequency = {master_freq:.2f} Hz, Test Frequency = {test_freq:.2f} Hz"
#                     print(f"Matched: {result_message}")
#                     self.send_message_to_server(result_message)
#                 else:
#                     result_message = f"Mismatched: Master Frequency = {master_freq:.2f} Hz, Test Frequency = {test_freq:.2f} Hz"
#                     print(f"Mismatched: {result_message}")
#                     self.send_message_to_server(result_message)
#             else:
#                 result_message = f"Ignored: Test Frequency = {test_freq:.2f} Hz (Outside ±10% range of Master Frequency)"
#                 print(f"Ignored: {result_message}")
#                 self.send_message_to_server(result_message)
        
#         except Exception as e:
#             print(f"Error comparing audio files: {e}")

#     def send_message_to_server(self, message):
#         try:
#             client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             client_socket.connect(('192.168.0.112', 5002))  # Connect to the server

#             client_socket.send(message.encode('utf-8'))  # Send a message
#             client_socket.close()  # Close the connection
#         except Exception as e:
#             print(f"Error sending message to server: {e}")

#     def start_comparison(self):
#         try:
#             if self.master_audio_path:
#                 print(f"Starting comparison with last recorded master audio: {self.master_audio_path}")
                
#                 # Continue listening for test audio and comparing
#                 self.continuous_test_recording = True
#                 self.recording_thread = threading.Thread(target=self.listen_for_test_audio)
#                 self.recording_thread.start()
                
#             else:
#                 print("No master audio recorded yet.")
#         except Exception as e:
#             print(f"Error starting comparison: {e}")

# # Main function to run the server and initiate the application
# def start_server():
#     app = AudioClassifierApp()
    
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server_socket.bind(('192.168.0.112', 5001))
#     server_socket.listen(1)
#     print("Server is listening...")

#     while True:
#         client_socket, client_address = server_socket.accept()
#         print(f"Connection from {client_address} has been established.")

#         message = client_socket.recv(1024).decode('utf-8')
#         print(f"Received message: {message}")
        
#         if message == 'master':
#             app.record_master_audio()
#         elif message == 'compare':
#             app.start_comparison()
#         elif message == 'stop all':
#             app.stop_all_processes()

#         response = f"Echo: {message}"
#         client_socket.send(response.encode('utf-8'))

#         client_socket.close()

# if __name__ == "__main__":
#     start_server()



import socket
import os
import numpy as np
import librosa
import sounddevice as sd
import soundfile as sf
from scipy import signal
import multiprocessing

class AudioClassifierApp:
    def __init__(self):
        # Set default folder for audio files
        self.default_folder = os.path.join(os.path.expanduser("~"), "audio_uploads")  # Change this to your desired path
        
        # Ensure the folder exists
        os.makedirs(self.default_folder, exist_ok=True)
        
        # Initialize file paths and variables
        self.master_audio_path = os.path.join(self.default_folder, "master_audio.wav")
        self.test_audio_path = os.path.join(self.default_folder, "test_audio.wav")
        self.tolerance_percentage = 10  # Updated tolerance percentage for frequency comparison
        self.sample_rate = 44100  # Sample rate for recording
        self.master_duration = 2  # Duration of master recording in seconds
        self.test_duration = 0.5  # Duration of test recording in seconds
        self.window_size = 2048  # Size of FFT window
        
        # Frequency range of interest (example: 100 Hz to 5000 Hz)
        self.min_freq = 100
        self.max_freq = 5000
        
        # Flag for continuous test recording
        self.continuous_test_recording = multiprocessing.Value('b', False)
        self.recording_process = None

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
            print(f"Error recording audio: {e}")
            return None

    # Function to record master audio
    def record_master_audio(self):
        try:
            filename = self.master_audio_path
            recorded_file = self.record_audio(filename, self.master_duration)
            
            if recorded_file:
                print(f"Recorded master audio: {recorded_file}")
                
                # Start listening for test audio
                with self.continuous_test_recording.get_lock():
                    self.continuous_test_recording.value = True
                self.recording_process = multiprocessing.Process(target=self.listen_for_test_audio)
                self.recording_process.start()
        except Exception as e:
            print(f"Error recording master audio: {e}")
    
    # Function to stop test audio recording
    def stop_test_audio(self):
        with self.continuous_test_recording.get_lock():
            self.continuous_test_recording.value = False
        print("Stopped test audio recording.")
    
    # Function to stop all processes
    def stop_all_processes(self):
        with self.continuous_test_recording.get_lock():
            self.continuous_test_recording.value = False
        if self.recording_process:
            self.recording_process.join()
        print("Stopped all processes.")
    
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
            print(f"Error processing audio segment: {e}")
            return None

    # Function to listen for test audio continuously
    def listen_for_test_audio(self):
        try:
            while True:
                with self.continuous_test_recording.get_lock():
                    if not self.continuous_test_recording.value:
                        break
                filename = self.test_audio_path
                self.record_audio(filename, self.test_duration)
                
                # Compare with master audio
                self.compare_audio()
        except Exception as e:
            print(f"Error recording or comparing test audio: {e}")

    # Function to compare audio
    def compare_audio(self):
        if not self.master_audio_path or not self.continuous_test_recording.value:
            return
        
        try:
            print("In try block")
            # Find peak frequency for master audio
            master_audio, _ = librosa.load(self.master_audio_path, sr=self.sample_rate)
            master_freq = self.find_peak_frequency(master_audio)
            
            if master_freq is None:
                print("Master frequency not found")
                return
            
            # Calculate tolerance for proceeding with comparison (10% of master frequency)
            proceed_tolerance = (15 / 100) * master_freq
            
            # Calculate tolerance for determining a match (5% of master frequency)
            match_tolerance = (10 / 100) * master_freq
            
            # Define the valid frequency range for proceeding with comparison (±10% of master frequency)
            valid_freq_range = (master_freq - proceed_tolerance, master_freq + proceed_tolerance)
            
            # Find peak frequency for current test audio
            test_audio_path = self.test_audio_path
            test_audio, _ = librosa.load(test_audio_path, sr=self.sample_rate)
            test_freq = self.find_peak_frequency(test_audio)

            if test_freq is None:
                return
            
            # Check if test frequency is within ±10% range of master frequency
            if valid_freq_range[0] <= test_freq <= valid_freq_range[1]:
                # Compare frequencies within valid range
                freq_diff = np.abs(master_freq - test_freq)
                print("In frequency difference check")
                
                # Check if frequency difference is within 5% tolerance for match/mismatch
                if freq_diff <= match_tolerance:
                    result_message = f"Matched: Master Frequency = {master_freq:.2f} Hz, Test Frequency = {test_freq:.2f} Hz"
                    print(f"Matched: {result_message}")
                    self.send_message_to_server(result_message)
                else:
                    result_message = f"Mismatched: Master Frequency = {master_freq:.2f} Hz, Test Frequency = {test_freq:.2f} Hz"
                    print(f"Mismatched: {result_message}")
                    self.send_message_to_server(result_message)
            else:
                result_message = f"Ignored: Test Frequency = {test_freq:.2f} Hz (Outside ±10% range of Master Frequency)"
                print(f"Ignored: {result_message}")
                self.send_message_to_server(result_message)
        
        except Exception as e:
            print(f"Error comparing audio files: {e}")

    def send_message_to_server(self, message):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('192.168.0.112', 5002))  # Connect to the server

            client_socket.send(message.encode('utf-8'))  # Send a message
            client_socket.close()  # Close the connection
        except Exception as e:
            print(f"Error sending message to server: {e}")

    def start_comparison(self):
        try:
            if self.master_audio_path:
                print(f"Starting comparison with last recorded master audio: {self.master_audio_path}")
                
                # Continue listening for test audio and comparing
                with self.continuous_test_recording.get_lock():
                    self.continuous_test_recording.value = True
                self.recording_process = multiprocessing.Process(target=self.listen_for_test_audio)
                self.recording_process.start()
                
            else:
                print("No master audio recorded yet.")
        except Exception as e:
            print(f"Error starting comparison: {e}")

# Main function to run the server and initiate the application
def start_server():
    app = AudioClassifierApp()
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('192.168.0.112', 5001))
    server_socket.listen(1)
    print("Server is listening...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address} has been established.")

        message = client_socket.recv(1024).decode('utf-8')
        print(f"Received message: {message}")
        
        if message == 'master':
            app.record_master_audio()
        elif message == 'compare':
            app.start_comparison()
        elif message == 'stop all':
            app.stop_all_processes()
        elif message == 'stop test':
            app.stop_test_audio()

        response = f"Echo: {message}"
        client_socket.send(response.encode('utf-8'))

        client_socket.close()

if __name__ == "__main__":
        start_server()
