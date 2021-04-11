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
x_fft = np.array(range(20,20000))
data = np.zeros(g_len)
fft_span_sec = 0.5
fft_d = int(fft_span_sec/((1/RATE)*CHUNK))
fft_queue = deque([np.zeros(CHUNK)]*length,maxlen=length*fft_d)#0.5/((1/44100)*1024) = 21.5....

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
		fft_queue.append(np.frombuffer(output_buff,dtype="int16"))
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

def x_label():
	x = [(0,0),(110,110)]
	while x[-1][0] < 4300:
		x.append((x[-1][0]*2,x[-1][0]*2))
	return x

class PlotGraph:
	def __init__(self):
		print("graph")
		global g_len,length,fft_d,CHUNK

		self.win = pg.GraphicsWindow()
		self.win.setWindowTitle('plot')
		self.plt = self.win.addPlot()
		self.plt.setYRange(0, 15)
		self.plt.setXRange(0, 4300)
		self.curve = self.plt.plot(pen=(0, 0, 255))
		self.plt.getAxis('bottom').setTicks([x_label(),[]])
		#self.plt.getAxis('bottom').setTicks([[0,1,2,3,4,5,6],[]])

		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.update)
		
		#self.timer.start(40)
		self.timer.start(500)

		#self.data = np.zeros(g_len)
		self.data = np.zeros(length*fft_d*CHUNK)

	def update(self):
		global data, fft_queue
		#self.data = data
		self.data,freqList = fft(fft_queue)
		self.curve.setData(freqList,self.data)

def plot_audio_qt():
	global x, data, alive
	graphWin = PlotGraph()
	if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
		QtGui.QApplication.instance().exec_()
	#graphWin.close()

def fft(fft_queue):
	global RATE
	fft_data = np.concatenate(fft_queue)
	fft_data = np.abs(np.fft.fft(data))/fft_data.shape[0]*2
	freqList = np.fft.fftfreq(fft_data.shape[0], d=1/RATE)
	return fft_data,freqList

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