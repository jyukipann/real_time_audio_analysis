import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import sys


class PlotGraph:
	def __init__(self):
		# UIを設定
		self.win = pg.GraphicsWindow()
		self.win.setWindowTitle('Random plot')
		self.plt = self.win.addPlot()
		self.plt.setYRange(0, 1)
		self.curve = self.plt.plot(pen=(0, 0, 255))

		# データを更新する関数を呼び出す時間を設定
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.update)
		self.timer.start(100)

		self.data = np.zeros(100)

	def update(self):
		self.data = np.delete(self.data, 0)
		self.data = np.append(self.data, np.random.rand())
		self.curve.setData(self.data)


if __name__ == "__main__":
	graphWin = PlotGraph()

	if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
		QtGui.QApplication.instance().exec_()