import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from collections import deque

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

queue = deque([], maxlen=10)

while stream_in.is_active() and stream_out.is_active():
	input_buff = stream_in.read(CHUNK)
	output_buff = signal_proc(input_buff)
	stream_out.write(output_buff)
	#print(type(output_buff))
	queue.append(np.frombuffer(output_buff,dtype="int16"))#ほんとは結合したい。1024*10長さのnparrayがほしい。

stream_in.stop_stream()
stream_in.close()
stream_out.stop_stream()
stream_out.close()
p.terminate()