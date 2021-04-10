import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from collections import deque
import asyncio
import threading
import warnings
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import sys

warnings.resetwarnings()
warnings.simplefilter('ignore')

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

fft_queue = deque([np.zeros(CHUNK)]*length,maxlen=length*21)#0.5/((1/44100)*1024) = 21.5....

def plot_audio():
	global x, data, alive
	while alive:
		#print(str(x.shape)+str(data.shape))
		plt.ylim(-32768, 32767)
		plt.plot(x,data,label="audio")
		plt.pause(0.02)
		plt.clf()
	print("plot end")
	plt.clf()
	plt.close("all")

def get_buff():
	global CHUNK, data, alive, queue
	while stream_in.is_active() and stream_out.is_active() and alive:
		input_buff = stream_in.read(CHUNK)
		output_buff = signal_proc(input_buff)
		#stream_out.write(output_buff)
		#print(type(output_buff))
		queue.append(np.frombuffer(output_buff,dtype="int16"))
		data = np.concatenate(queue)
		#print(len(data))
	print("get Buff end")
	stream_in.stop_stream()
	stream_in.close()
	stream_out.stop_stream()
	stream_out.close()
	p.terminate()

def spectrogram():
	global CHUNK, data, alive, queue
	while alive:
		pass

def command():
	global alive
	alive = True
	ESC = 0x1B
	while alive:
		cmd = input("command > ")
		if cmd == "exit":
			alive = False

class PlotGraph:
	def __init__(self):
		print("graph")
		global g_len

		self.win = pg.GraphicsWindow()
		self.win.setWindowTitle('plot')
		self.plt = self.win.addPlot()
		self.plt.setYRange(-32768, 32767)
		self.curve = self.plt.plot(pen=(0, 0, 255))

		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.update)
		self.timer.start(20)

		self.data = np.zeros(g_len)

	def update(self):
		global data
		self.data = data
		self.curve.setData(self.data)

def plot_audio_qt():
	global x, data, alive
	graphWin = PlotGraph()
	if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
		QtGui.QApplication.instance().exec_()
	#graphWin.close()


if __name__ == "__main__":
	alive = True
	thread_1 = threading.Thread(target=get_buff)
	#thread_2 = threading.Thread(target=plot_audio)
	thread_3 = threading.Thread(target=plot_audio_qt)
	thread_1.setDaemon(True)
	#thread_2.setDaemon(True)
	thread_3.setDaemon(True)
	thread_1.start()
	#thread_2.start()
	thread_3.start()
	command()
	thread_1.join()
	#thread_2.join()
	thread_3.join()

"""
stream_in.stop_stream()
stream_in.close()
stream_out.stop_stream()
stream_out.close()
p.terminate()
"""