#!/bin/python

import sys, random, math
from PyQt5.QtCore import Qt, QObject, QThread, QSize, QUrl, QTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QPixmap, QColor, QFont, QBrush, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QSlider, QSpinBox, QComboBox, QTextBrowser, QShortcut

# Global variables

w = 1200 # window width
h = 480 # window height
tm = 50 # top margin for buttons
bm = 80 # bottom margin for buttons
m = 25 # margin for pixmap
hh = h - tm - bm - 2 * m + 75 # pixmap height
ww = 800 # pixmap width

# Defaults
elements = 64
subdiv = 32
delay = 250
 
list = [[]]
colors = [[]]

class Display(QLabel):
	def __init__(self, x, y, w, h, parent = None):
		QLabel.__init__(self, parent)
		self.width = w
		self.height = h
		self.setGeometry(x, y, w, h)
		self.pixmap = QPixmap(w, h)
		self.pixmap.fill(QColor(0, 0, 0, 0))

		self.regular = QColor(255, 70, 70, 255)
		self.highlight = QColor(100, 170, 70)
		self.painter = QPainter(self.pixmap)
		self.painter.setBrush(self.regular)
		self.painter.setPen(QColor(0, 0, 0, 0))

	def draw(self, index):
		self.pixmap.fill(QColor(255, 255, 255, 0))
		global list, elements, subdiv, colors

		current = list[index]
		x = self.width // elements
		barS = x / 10
		barW = x - barS
		pos = 0
		for i in range(len(list[index])):
			barH = self.height / subdiv * current[i]
			try:
				if i in colors[index]:
					self.painter.setBrush(self.highlight)
				else:
					self.painter.setBrush(self.regular)
			except:
				self.painter.setBrush(self.regular)
			self.painter.drawRect(pos, self.height - barH, barW, barH)
			pos += barW + barS

		self.setPixmap(self.pixmap)

class Controller(QObject):
	def __init__(self, parent = None):
		QObject.__init__(self, parent)
		self.sortMode = False

	init = pyqtSignal()
	sort = pyqtSignal()

	def genElements(self, x):
		global elements, subdiv
		elements = x
		subdiv = math.ceil(elements / 2)
		self.init.emit()

	def setSortMode(self, x):
		self.sortMode = x
		startButton.setVisible(x)
		prevButton.setVisible(x)
		playButton.setVisible(x)
		nextButton.setVisible(x)
		endButton.setVisible(x)
		delLabel.setVisible(x)
		delSlider.setVisible(x)
		title.setVisible(x)

		reButton.setVisible(not x)
		elsLabel.setVisible(not x)
		elsBox.setVisible(not x)
		typeLabel.setVisible(not x)
		typeBox.setVisible(not x)
		algLabel.setVisible(not x)
		algBox.setVisible(not x)
		title.setVisible(x)

	def switch(self):
		if self.sortMode:
			self.setSortMode(False)
			switchButton.setIcon(QIcon("icons/sort.png"))
		else:
			self.setSortMode(True)
			switchButton.setIcon(QIcon("icons/conf.png"))
			self.sort.emit()

	def swapButton(self, x):
		if x:
			playButton.setVisible(False)
			pauseButton.setVisible(True)
		else:
			playButton.setVisible(True)
			pauseButton.setVisible(False)

	def genBrowser(self):
		global algBox, browser, title
		i = algBox.currentIndex()

		if i == 0:
			browser.setSource(QUrl("doc/bubble.html"))
			title.setText("Bubble Sort")
		elif i == 1:
			browser.setSource(QUrl("doc/insertion.html"))
			title.setText("Insertion Sort")
		elif i == 2:
			browser.setSource(QUrl("doc/selection.html"))
			title.setText("Selection Sort")
		elif i == 3:
			browser.setSource(QUrl("doc/merge.html"))
			title.setText("Merge Sort")
		elif i == 4:
			browser.setSource(QUrl("doc/shell.html"))
			title.setText("Shell Sort")
		elif i == 5:
			browser.setSource(QUrl("doc/shaker.html"))
			title.setText("Shaker Sort")
		elif i == 6:
			browser.setSource(QUrl("doc/comb.html"))
			title.setText("Comb Sort")

class Array(QObject):
	def __init__(self, parent = None):
		QObject.__init__(self, parent)
		self.sorted = False
		self.imsorted.connect(self.setSorted)
		self.timer = QTimer(self)
		self.timer.timeout.connect(self.stepRight)
		self.timer.setInterval(delay)
		self.index = 0

	draw = pyqtSignal(int)
	imsorted = pyqtSignal(bool)
	sorting = pyqtSignal(bool)

	def init(self):
		global typeBox, elements
		
		i = typeBox.currentIndex()
		if i == 0:
			self.initRand()
		elif i == 1:
			self.initInversed()
		elif i == 2:
			self.initNearly()
		elif i == 3:
			self.initFew()

		colors = [[]]
		self.index = 0
		self.imsorted.emit(False)
		self.draw.emit(0)

	def initRand(self):
		global list, subdiv, elements
		list = [[]]
		for i in range(elements):
			list[0].append(random.randint(1, subdiv))

	def initInversed(self):
		global list
		self.initRand()
		list[0] = self.simpleSort(list[0])
		list[0] = list[0][::-1]

	def initNearly(self):
		global list, subdiv, elements
		self.initRand()
		list[0] = self.simpleSort(list[0])

		step = 2
		for i in range(elements):
			list[0][i] += random.randint(-step, step)
			if list[0][i] > subdiv:
				list[0][i] = subdiv
			elif list[0][i] < 1:
				list[0][i] = 1

	def initFew(self):
		global list, subdiv, elements
		list = [[]]
		step = (subdiv + 1) // 6
		if step < 1:
			step = 1
		for i in range(elements):
			list[0].append(random.randrange(1, subdiv + 1, step))

	def simpleSort(self, list):
		for i in range(1, len(list)):
			j = i
			while j > 0 and list[j-1] > list[j]:
				list[j-1], list[j] = list[j], list[j-1]
				j -= 1
		return list

	def genPratt(self, max):
		numbers = []

		pow3 = 1
		while pow3 <= max:
			pow2 = pow3
			while pow2 <= max:
				numbers.append(pow2)
				pow2 *= 2
			pow3 *= 3

		numbers = self.simpleSort(numbers)
		return numbers

	def setSorted(self, x):
		self.sorted = x

	def clear(self):
		global list, colors
		colors = [[]]
		if self.index < len(list) - 1:
			self.imsorted.emit(False)
		list = [list[self.index]]
		self.index = 0
		self.draw.emit(0)

	def sort(self):
		if not self.sorted:
			global algBox, list, colors
			colors = [[]]
			i = algBox.currentIndex()
			if i == 0:
				self.sortBubble()
			elif i == 1:
				self.sortInsert()
			elif i == 2:
				self.sortSelect()
			elif i == 3:
				self.sortMerge(list[0][:], 0)
			elif i == 4:
				self.sortShell()
			elif i == 5:
				self.sortShaker()
			elif i == 6:
				self.sortComb()

			self.imsorted.emit(True)

	def sortBubble(self):
		global list, colors
		els = len(list[-1])
		current = list[-1][:]

		toappend = []
		while True:
			swapped = False
			list.append(current[:])
			colors.append([0] + toappend[:])
			for i in range(els - 1):
				if current[i] > current[i+1]:
					current[i], current[i+1] = current[i+1], current[i]
					swapped = True
				list.append(current[:])
				colors.append([i+1] + toappend[:])
			toappend.append(els-1)
			if not swapped:
				break
			els -= 1

		for i in range(toappend[-1] - 1, -1, -1):
			toappend.append(i)
		list.append(current[:])
		colors.append(toappend[:])

	def sortInsert(self):
		global list, colors
		els = len(list[-1])
		current = list[-1][:]

		for i in range(1, els):
			j = i
			list.append(current[:])
			colors.append([i])
			while j > 0 and current[j-1] > current[j]:
				current[j-1], current[j] = current[j], current[j-1]
				list.append(current[:])
				colors.append([j-1, i])
				j -= 1

		list.append(current[:])
		colors.append([])
		for i in range(len(list)):
			colors[-1].append(i)		

	def sortSelect(self):
		global list, colors
		els = len(list[-1])
		current = list[-1][:]

		toappend = []
		for i in range(els):
			min = i
			for j in range(i+1, els):
				if current[j] < current[min]:
					min = j
				list.append(current[:])
				colors.append(toappend + [min, j])
			min = current.pop(min)
			current.insert(i, min)
			toappend.append(i)
			list.append(current[:])
			colors.append(toappend[:])

	def sortMerge(self, current, k):
		global list, colors
		if len(current) < 2:
			return

		m = len(current) // 2
		left = current[:m]
		right = current[m:]

		self.sortMerge(left, k)
		self.sortMerge(right, k+m)
		
		toappend = []
		i = l = r = 0
		while l < len(left) and r < len(right):
			if left[l] < right[r]:
				current[i] = left[l]
				l += 1
			else:
				current[i] = right[r]
				r += 1
			list.append(list[-1][:])
			list[-1][k+i] = current[i]
			toappend.append(k+i)
			colors.append(toappend[:])
			i += 1

		if l == len(left):
			remain = right
			j = r
		else:
			remain = left
			j = l

		while j < len(remain):
			current[i] = remain[j]
			list.append(list[-1][:])
			list[-1][k+i] = current[i]
			toappend.append(k+i)
			colors.append(toappend[:])
			j += 1
			i += 1

	def sortShell(self):
		global list, colors
		current = list[-1][:]
		n = len(current)
		gaps = self.genPratt(n)
		gaps = gaps[::-1]

		for gap in gaps:
			for i in range(gap):
				toappend = []
				for j in range(i, n, gap):
					toappend.append(j)
				for j in range(i+gap, n, gap):
					k = j
					while k > i and current[k] < current[k-gap]:
						current[k], current[k-gap] = current[k-gap], current[k]
						list.append(current[:])
						colors.append(toappend[:])
						k -= gap

	def sortShaker(self):
		global list, colors
		current = list[-1][:]
		top = len(list[-1])
		bottom = 0

		toappend = []
		while True:
			swapped = False
			list.append(current[:])
			colors.append(toappend + [bottom])
			for i in range(bottom, top-1):
				if current[i] > current[i+1]:
					current[i], current[i+1] = current[i+1], current[i]
					swapped = True
				list.append(current[:])
				colors.append(toappend + [i+1])
			toappend.append(top - 1)

			if not swapped:
				break

			top -= 1

			list.append(current[:])
			colors.append(toappend + [top-1])
			for i in range(top-1, bottom, -1):
				if current[i] < current[i-1]:
					current[i], current[i-1] = current[i-1], current[i]
					swapped = True
				list.append(current[:])
				colors.append(toappend + [i-1])
			toappend.append(bottom)

			if not swapped:
				break

			bottom += 1

		list.append(current[:])
		colors.append([])
		for i in range(len(list[-1])):
			colors[-1].append(i)

	def sortComb(self):
		global list, colors
		current = list[-1][:]
		n = len(list[-1])
		k = 1.3
		gap = int(n / k)

		while gap > 1:
			for i in range(n - gap):
				if current[i] > current[i + gap]:
					current[i], current[i+gap] = current[i+gap], current[i]
				list.append(current[:])
				colors.append([i, i+gap])
			gap = int(gap / k)
		self.sortBubble()


	def stepRight(self):
		global list
		if self.index < len(list) - 1:
			self.index += 1
			self.draw.emit(self.index)
		elif self.timer.isActive():
			self.timer.stop()
			self.sorting.emit(False)

	def stepLeft(self):
		if self.index > 0:
			self.index -= 1
			self.draw.emit(self.index)

	def play(self):
		global list
		if len(list) < 2:
			return
		if self.index == len(list) - 1:
			self.index = 0
		self.sorting.emit(True)
		self.timer.start()

	def stop(self):
		self.sorting.emit(False)
		self.timer.stop()

	def toStart(self):
		self.index = 0
		self.draw.emit(self.index)

	def toEnd(self):
		global list
		self.index = len(list) - 1
		self.draw.emit(self.index)

# Initial commands
app = QApplication(sys.argv)
styles = open('stylesheet.qss')
app.setStyleSheet(styles.read())
window = QWidget()
window.setFixedSize(QSize(w, h))
window.setWindowTitle("Sorting Algorithms")
font = QFont("Ubuntu", 12)

# Instantiation
array = Array()
display = Display(m, tm + m, ww, hh, window)
controller = Controller()

# Buttons
switchButton = QPushButton(window)
switchButton.setGeometry(m, m/4, 4*m, 2*m)
switchButton.setIcon(QIcon("icons/sort.png"))
switchButton.setIconSize(QSize(4*m, 2*m))
switchButton.clicked.connect(controller.switch)

reButton = QPushButton(window)
reButton.setGeometry(155, m/4, 2*m, 2*m)
reButton.setIcon(QIcon("icons/re.png"))
reButton.setIconSize(QSize(2*m, 2*m))
reButton.clicked.connect(array.init)

startButton = QPushButton(window)
startButton.setGeometry(155, m/4, 2*m, 2*m)
startButton.setIcon(QIcon("icons/start.png"))
startButton.setIconSize(QSize(2*m, 2*m))
startButton.clicked.connect(array.toStart)

prevButton = QPushButton(window)
prevButton.setGeometry(155 + 3*m, m/4, 2*m, 2*m)
prevButton.setIcon(QIcon("icons/prev.png"))
prevButton.setIconSize(QSize(2*m, 2*m))
prevButton.clicked.connect(array.stepLeft)

playButton = QPushButton(window)
playButton.setGeometry(155 + 6*m, m/4, 2*m, 2*m)
playButton.setIcon(QIcon("icons/play.png"))
playButton.setIconSize(QSize(2*m, 2*m))
playButton.clicked.connect(array.play)

pauseButton = QPushButton(window)
pauseButton.setGeometry(155 + 6*m, m/4, 2*m, 2*m)
pauseButton.setIcon(QIcon("icons/pause.png"))
pauseButton.setIconSize(QSize(2*m, 2*m))
pauseButton.clicked.connect(array.play)
pauseButton.setVisible(False)
pauseButton.clicked.connect(array.stop)

nextButton = QPushButton(window)
nextButton.setGeometry(155 + 9*m, m/4, 2*m, 2*m)
nextButton.setIcon(QIcon("icons/next.png"))
nextButton.setIconSize(QSize(2*m, 2*m))
nextButton.clicked.connect(array.stepRight)

endButton = QPushButton(window)
endButton.setGeometry(155 + 12*m, m/4, 2*m, 2*m)
endButton.setIcon(QIcon("icons/end.png"))
endButton.setIconSize(QSize(2*m, 2*m))
endButton.clicked.connect(array.toEnd)

# Options
delLabel = QLabel("Delay:", window)
delLabel.setGeometry(550, 0, 100, tm)
delLabel.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
delLabel.setFont(font)
delSlider = QSlider(window)
delSlider.setGeometry(625, 3, 200, tm-3)
delSlider.setOrientation(Qt.Horizontal)
delSlider.setMinimum(5)
delSlider.setMaximum(500)
delSlider.setSliderPosition(delay)
delSlider.valueChanged.connect(array.timer.setInterval)

elsLabel = QLabel("Number of elements:", window)
elsLabel.setGeometry(250, 0, 155, tm)
elsLabel.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
elsLabel.setFont(font)
elsBox = QSpinBox(window)
elsBox.setGeometry(420, 10, 100, tm-20)
elsBox.setMinimum(5)
elsBox.setMaximum(256)
elsBox.setValue(elements)
elsBox.setAlignment(Qt.AlignHCenter)
elsBox.setFont(font)
elsBox.valueChanged.connect(controller.genElements)

typeLabel = QLabel("Array type:", window)
typeLabel.setGeometry(550, 0, 100, tm)
typeLabel.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
typeLabel.setFont(font)
typeBox = QComboBox(window)
typeBox.setFont(font)
typeBox.setGeometry(650, 10, 200, tm - 20)
typeBox.addItem("Random")
typeBox.addItem("Inversed")
typeBox.addItem("Nearly sorted")
typeBox.addItem("Few unique")
typeBox.currentIndexChanged.connect(array.init)

algLabel = QLabel("Algorithm:", window)
algLabel.setGeometry(885, 0, 100, tm)
algLabel.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
algLabel.setFont(font)
algBox = QComboBox(window)
algBox.setFont(font)
algBox.setGeometry(1000 - m, 10, 200, tm - 20)
algBox.addItem("Bubble")
algBox.addItem("Insertion")
algBox.addItem("Selection")
algBox.addItem("Merge")
algBox.addItem("Shell")
algBox.addItem("Shaker")
algBox.addItem("Comb")
algBox.setCurrentIndex(0)
algBox.currentIndexChanged.connect(array.clear)
algBox.currentIndexChanged.connect(controller.genBrowser)

title = QLabel(window)
title.setStyleSheet("font-size: 18pt;")
title.setGeometry(850, 0, 325, tm)

browser = QTextBrowser(window)
browser.setGeometry(2*m + ww, tm + m, w - ww - 3*m, hh)
browser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
controller.genBrowser()

# Signals connection
array.draw.connect(display.draw)
array.sorting.connect(switchButton.setDisabled)
array.sorting.connect(startButton.setDisabled)
array.sorting.connect(prevButton.setDisabled)
array.sorting.connect(nextButton.setDisabled)
array.sorting.connect(endButton.setDisabled)
array.sorting.connect(controller.swapButton)
controller.init.connect(array.init)
controller.sort.connect(array.sort)

# Final commands
array.init()
controller.setSortMode(False)
window.show()
sys.exit(app.exec_())