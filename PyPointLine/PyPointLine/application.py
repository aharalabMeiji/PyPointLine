
import tkinter as tk
import os

from utils import mousePosition, isNear, isIn
from pane import pane
from menuitem import *
from point import point
from line import line
from circle import circle
from module import *

class application:
	"""
	"""
	def __init__(self, root):
		""" """
		self.root = root
		self.headerCanvas=tk.Canvas(root, width=1000, height=100)
		self.headerCanvas.place(x=0, y=0)
		self.mainCanvas = tk.Canvas(root, width=1000, height=900)
		self.mainCanvas.place(x=0, y=100)
		self.mp=mousePosition()
		self.nextID=0
		self.pointName='A'
		self.lineName='a'
		self.pointRadius=5# global radius of a point in canvas
		self.lineWidth=3# global width of a line in canvas
		self.cx=500
		self.cy=500
		self.zoom=100
		self.points=[]
		self.lines=[]
		self.circles=[]
		self.modules=[]
		self.clickedPoint=None
		self.clickedLine=None
		self.clickedCircle=None
		
		self.dispMenu=False
		self.onMode=None
		self.dispPreference=False

		##self.file=fileIO(self)

		self.headerPane=pane(self, 0,0,1000,100)
		self.mainPane=pane(self,0,100,1000,900)
		self.rightPane=pane(self,1000,0,200,1000)
		self.initilizeMenuItems()


		point0=point(0,0)
		self.points.append(point0)
		point1=point(1,1)
		self.points.append(point1)
		point2=point(1,0)
		self.points.append(point2)
		point3=point(-1,0)
		self.points.append(point3)

		#line0=line(point0, point1)
		#self.lines.append(line0)

		
		self.circles.append(circle(point0, point1))
		
		self.circles.append(circle(point2, point3))


		#module20=point2point(point0,point1)
		#self.modules.append(module20)

		#module21=point2line(point2,line0)
		#self.modules.append(module21)

		#module31=point2circle(point3, circle0)
		#self.modules.append(module31)

		#module41=line2circle(line0, circle0)
		#self.modules.append(module41)
		
		module51=circle2circle(self.circles[0], self.circles[1])
		self.modules.append(module51)

		self.drawAll(self.mainCanvas)
		pass


	def world2Canvas(self, x,y):
		return self.cx+self.zoom * x, self.cy+self.zoom * y

	def canvas2World(self, x,y):
		return (-self.cx+ x) / self.zoom , (-self.cy+ y)/self.zoom


	def drawAll(self, canvas):
		""" """
		canvas.delete("all")
		if self.dispMenu==False:
			self.drawMenuOnIcon(canvas)
			self.drawAllObjects(canvas)
			#self.drawAllLogs()
			if self.dispPreference==True:
				#self.drawProference()
				pass
			pass
		else: # dispMenu==True:
			self.drawAllMenu(canvas)
			pass

	def drawAllObjects(self, canvas):
		## draw angles

		## draw lines
		for ln in self.lines:
			pt1=ln.point1
			pt2=ln.point2
			x1,y1=self.world2Canvas(pt1.x, pt1.y)
			x2,y2=self.world2Canvas(pt2.x, pt2.y)
			canvas.create_line(x1,y1,x2,y2, fill='grey', width=4)
		
		## draw circles
		for cn in self.circles:
			x1,y1=self.world2Canvas(cn.point.x, cn.point.y)
			r=cn.radius * self.zoom
			canvas.create_oval(x1-r,y1-r,x1+r,y1+r, outline='grey', width=4)

		## draw points
		for pt in self.points:
			xx0,yy0=self.world2Canvas(pt.x,pt.y)
			canvas.create_oval(xx0-5,yy0-5,xx0+5,yy0+5, fill='blue')

		## draw locus


	def updateCoordinates(self, event):
		""" """
		self.mp.canvasX, self.mp.canvasY = event.x, event.y
		self.mp.x, self.mp.y = self.canvas2World( event.x, event.y)
		pass



	def buttonDragging(self, event):
		""" """
		#self.mainCanvas.delete("all")
		self.updateCoordinates(event)
		if self.mp.magneticPoint!=None:
			if getattr(self.mp.magneticPoint, 'thisis', None)=='point':
				self.mp.magneticPoint.x, self.mp.magneticPoint.y=self.mp.x, self.mp.y
				self.calculatorEvaluate()
	# 

	def calculatorEvaluate(self):
		for i in range(10):
			for md in self.modules:
				md.evaluate()
		self.drawAll(self.mainCanvas)


	def buttonPressed(self, event):
		""" """
		self.updateCoordinates(event)
		self.mp.bpX, self.mp.bpY = self.mp.x, self.mp.y
		x,y = self.world2Canvas(self.mp.x, self.mp.y)
		if self.mainPane.inside(x,y):
			for pt in self.points:
				if isNear(pt.x, pt.y, self.mp.x, self.mp.y, 10/self.zoom):
					self.mp.magneticPoint = pt
					break
			pass

	def mouseOnPoint(self):
		for pt in self.points:
			if pt.thisis=='point':
				if isNear(pt.x, pt.y, self.mp.x, self.mp.y, 10/self.zoom):
					return pt
		return None

	def mouseOnLine(self):
		for ln in self.lines:
			if ln.thisis=='line':
				ax,ay=self.mp.x, self.mp.y
				bx,by=ln.point1.x, ln.point1.y
				cx,cy=ln.point2.x, ln.point2.y
				tn=(ax-bx)*(cx-bx)+(ay-by)*(cy-by)
				td=(cx-bx)*(cx-bx)+(cy-by)*(cy-by)
				if td==0:
					continue
				tt=tn/td
				dx, dy=tt*(cx-bx)+(bx-ax), tt*(cy-by)+(by-ay)
				if magnitude(dx, dy)<10/self.zoom:
					return ln
		return None

	def mouseOnCircle(self):
		for cc in self.circles:
			if cc.thisis=='circle':
				mag=dist(cc.point.x, cc.point.y, self.mp.x, self.mp.y)
				if math.abs(mag-cc.radius)<10/self.zoom:
					return cc

		return None

	def buttonReleased(self, event):
		""" """
		self.updateCoordinates(event)
		if isNear(self.mp.x,self.mp.y,self.mp.bpX,self.mp.bpY,5/self.zoom):## has clicked
			if self.dispMenu==False and isIn(self.mp.canvasX, self.mp.canvasY, 0, 0, 100, 100):
				self.dispMenu=True
				self.drawAll(self.mainCanvas)
			elif self.dispMenu==True and isIn(self.mp.canvasX, self.mp.canvasY, 0, 0, 100, 100):
				self.dispMenu=False
				self.drawAll(self.mainCanvas)
			elif self.dispMenu==False:
				self.clickedPoint = self.mouseOnPoint()
				self.clickedLine = self.mouseOnLine()
				self.clickedCircle = self.mouseOnCircle()
				if self.clickedPoint==None and self.clickedLine==None and self.clickedCircle==None:## free clicking
					self.onMode=self.menuAddPoint
					self.onModePhase=0
					self.headerText=self.onMode.headerText[self.onModePhase]
					self.drawAll(self.mainCanvas)
				self.onMode.phaseActions(self)
				pass
			elif self.dispMenu==True:
				self.onMode=None
				self.headerText=""
				for icon in self.allButtonIcons:
					if isIn(self.mp.canvasX, self.mp.canvasY, icon.left, icon.top, icon.width, icon.height):
						self.onMode=icon
						self.onModePhase=0
						self.headerText=icon.headerText[self.onModePhase]
						self.dispMenu=False
						self.drawAll(self.mainCanvas)
						break
			pass
		else:## finishing drag
			##if self.mp.magenticPoint
			#	if magneticPoint!=None:
			#		self.drawAll(self.mainCanvas)
			#		self.mp.magneticPoint=None
			#else:## ��h���b�O
			#	�}�S�̂𕽍s�ړ�����B		
			self.calculatorEvaluate()
			pass

	def wheelTurned(self, event):
		""" """
		pass

	def keyPressed(self, event):
		"""
		keyPressed event"""
		if event.keysym=="Up":
			self.cy -= 10
			self.drawAll(self.mainCanvas)		
			pass
		elif event.keysym=="Down":
			self.cy += 10
			self.drawAll(self.mainCanvas)		
			pass
		elif event.keysym=="Right":
			self.cx += 10
			self.drawAll(self.mainCanvas)		
			pass
		elif event.keysym=="Left":
			self.cx -= 10
			self.drawAll(self.mainCanvas)	
			pass
		pass

	def initilizeMenuItems(self):
		self.menuOn=menuItem("images\\MenuOn.png", 0, 0)
		self.menuOff=menuItem("images\\MenuOff.png", 0, 0)
		#####
		self.menuAddPoint=addPointItem("images\\AddPoint.png", 0, 0)
		self.menuMidPoint=midPointItem("images\\MidPoint.png", 1, 0)
		self.menuAddLine=addLineItem("images\\AddLine.png", 2, 0)
		self.menuAddCircle=addCircleItem("images\\AddCircle.png", 3, 0)
		self.menuAddAngle=addAngleItem("images\\Angle.png", 4, 0)
		self.menuAddLocus=addLocusItem("images\\AddLocus.png",5 , 0)
		#####
		self.menuP2P=menuItem("images\\P2P.png", 0, 1)
		self.menuP2L=menuItem("images\\P2L.png", 1, 1)
		self.menuP2C=menuItem("images\\P2C.png", 2, 1)
		self.menuTangentL2C=menuItem("images\\TangentL2C.png", 3, 1)
		self.menuTangentC2C=menuItem("images\\TangentC2C.png", 4, 1)
		#####
		self.menuIsom=menuItem("images\\Isom.png", 0, 2)
		self.menuRatioLength=menuItem("images\\RatioLength.png", 1, 2)
		self.menuPara=menuItem("images\\Para.png", 2, 2)
		self.menuPerp=menuItem("images\\Perp.png", 3, 2)
		self.menuHori=menuItem("images\\Hori.png", 4, 2)
		self.menuBisector=menuItem("images\\Bisector.png", 5, 2)
		#####
		self.menuFixPoint=menuItem("images\\FixPoint.png", 0, 3)
		self.menuUndo=menuItem("images\\Undo.png", 1, 3)
		self.menuRedo=menuItem("images\\Redo.png", 2, 3)
		self.menuDeletePoint=menuItem("images\\DeletePoint.png", 3, 3)
		self.menuDeleteLocus=menuItem("images\\DeleteLocus.png", 4, 3)
		self.menuDeleteAll=menuItem("images\\DeleteAll.png", 5, 3)
		#####
		self.menuLogs=menuItem("images\\Logs.png", 0, 4)
		self.menuOpen=menuItem("images\\Open.png", 1, 4)
		self.menuSave=menuItem("images\\Save.png", 2, 4)
		self.menuSave2TeX=menuItem("images\\Save2TeX.png", 3, 4)
		self.menuQuit=menuItem("images\\Quit.png", 4, 4)
		

	def drawMenuOnIcon(self, canvas):
		self.menuOn.showIcon(self.headerCanvas)

	@property
	def allButtonIcons(self):
		return [\
			self.menuAddPoint, self.menuMidPoint,self.menuAddLine,self.menuAddCircle,self.menuAddLocus,self.menuAddAngle,
			self.menuP2P,self.menuP2L,self.menuP2C,self.menuTangentL2C,self.menuTangentC2C,
			self.menuIsom,self.menuRatioLength,self.menuPara,self.menuPerp,self.menuHori,self.menuHori,self.menuBisector,
			self.menuFixPoint,self.menuUndo,self.menuRedo,self.menuDeletePoint,self.menuDeleteLocus,self.menuDeleteAll,
			self.menuLogs,self.menuOpen,self.menuSave,self.menuSave2TeX,self.menuSave2TeX,self.menuQuit
			]

	def drawAllMenu(self, canvas):
		self.menuOff.showIcon(self.headerCanvas)
		for icon in self.allButtonIcons:
			icon.showIcon(canvas)