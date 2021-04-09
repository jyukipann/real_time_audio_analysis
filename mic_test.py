import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from collections import deque
import asyncio
import threading

"""
x = np.linspace(0, 1, 100)
y = x ** 2
plt.plot(x, y)
"""

RATE = 44100
CHUNK = 1024
CHANNEL_IN = 1
CHANNEL_OUT = 1

def signal_proc(input_buff, dtype=np.int16):
	# Convert framebuffer into nd-array
	input_data = np.frombuffer(input_buff, dtype=dtype)
	
	# Signal processing
	# Set output as L-ch
	output_data = np.zeros((CHANNEL_OUT, CHUNK))
	output_data[0] = input_data

	# Convert nd-array into framebuffer
	output_data = np.reshape(output_data.T, (CHUNK * CHANNEL_OUT))
	output_buff = output_data.astype(dtype).tobytes()
	return output_buff


p = pyaudio.PyAudio()

stream_in = p.open( 
		format=pyaudio.paInt16,
		channels=CHANNEL_IN,
		rate = RATE,
		frames_per_buffer=CHUNK,
		input = True,
		output = False,
	)

stream_out = p.open(
		format=pyaudio.paInt16,
		channels=CHANNEL_OUT,
		rate=RATE,
		frames_per_buffer=CHUNK,
		input=False,
		output=True,
	)

length = 100
g_len = length*CHUNK
queue = deque([np.zeros(CHUNK)]*length, maxlen=length)
x = np.array(range(g_len))
data = np.zeros(g_len)

def plot_audio():
	global x, data
	while True:
		#print(str(x.shape)+str(data.shape))
		plt.plot(x,data,label="audio")
		plt.pause(0.1)
		plt.cla()

def get_buff():
	global CHUNK, data
	while stream_in.is_active() and stream_out.is_active():
		input_buff = stream_in.read(CHUNK)
		output_buff = signal_proc(input_buff)
		stream_out.write(output_buff)
		#print(type(output_buff))
		queue.append(np.frombuffer(output_buff,dtype="int16"))#ほんとは結合したい。1024*10長さのnparrayがほしい。
		data = np.concatenate(queue)
		#print(len(data))

def command():
	while True:
		cmd = input()
		if cmd == "exit":
			exit(0)

if __name__ == "__main__":
	thread_1 = threading.Thread(target=get_buff)
	thread_2 = threading.Thread(target=plot_audio)
	thread_2.setDaemon(True)
	thread_1.setDaemon(True)
	thread_1.start()
	thread_2.start()
	command()
"""







stream_in.stop_stream()
stream_in.close()
stream_out.stop_stream()
stream_out.close()
p.terminate()
"""