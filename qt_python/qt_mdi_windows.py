import html

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QPainter
import PyQt6.QtGui
import pyqtgraph
import requests
from PyQt6.QtWidgets import QHBoxLayout

import pyqtgraph as pg
from pyqtgraph import *

from qt_python.qt_imports import *
from data.currency_handler import LiveCycler, CurrencyLiveCycle, IndicatorsCalculator
from constants import *
import numpy as np
import pandas as pd


class MdiWidget(QWidget):
    def __init__(self, parent, isInherit=False):
        super(MdiWidget, self).__init__()
        self.setParent(parent)

        self.close = QPushButton()
        self.mainLayout = QVBoxLayout()
        self.bokehWidget = QWidget()
        self.bokehWidget.setMouseTracking(True)

        if not isInherit:
            uic.loadUi("qt_python/qt_designer/mdi_widget.ui")


        self.startPos = self.pos()
        self.isDragging = False

        self.isResizing = False
        self.resizingStartPos = 0
        self.cursor = 9

        self.close.clicked.connect(parent.close)
        #self.setMouseTracking(True)

    # ========================================================================
    # ===================Overloaded events of widget==========================
    # ========================================================================

    # def eventFilter(self, object: 'QObject', event: 'QEvent') -> bool:
    #     if event.type() is QEvent.Type.MouseMove:
    #         self.setCursorByBorder(self.mainLayout, event.pos())
    #     return super(MdiWidget, self).eventFilter(object, event)

    def mouseMoveEvent(self, eventArgs: QtGui.QMouseEvent) -> None:

        if self.isDragging:
            newPos = self.parent().pos()
            point = eventArgs.scenePosition().toPoint()
            newPos -= (self.startPos - point)
            self.parent().move(newPos)
            self.startPos = point

        return super(MdiWidget, self).mouseMoveEvent(eventArgs)

    def mouseReleaseEvent(self, eventArgs: QtGui.QMouseEvent) -> None:
        if self.isDragging:
            self.isDragging = False
        return super(MdiWidget, self).mouseReleaseEvent(eventArgs)

    def mousePressEvent(self, eventArgs: QtGui.QMouseEvent) -> None:

        if type(self.childAt(eventArgs.pos())) is QLabel:
            if self.childAt(eventArgs.pos()).text() == "Drag":
                self.isDragging = True
                self.startPos = eventArgs.scenePosition().toPoint()

        return super(MdiWidget, self).mousePressEvent(eventArgs)

    # ========================================================================
    # ===========================Over methods=================================
    # ========================================================================

    @staticmethod
    def debug_msg(*msg):
        print("[MDI_WIDGET]", ' '.join([str(i) for i in msg]))

    def resizeWidget(self, newSize: QtCore.QSize):
        #self.parent().setFixedSize(newWidth, newHeight)
        #self.parent().setMinimumSize(BOKEH_SUBWINDOW_MINIMUM_WIDTH - 1, BOKEH_SUBWINDOW_MINIMUM_HEIGHT - 1)
        # self.bokehWidget.setZoomFactor(newWidth / BOKEH_SUBWINDOW_MINIMUM_WIDTH)
        pass


class CurrencyBokehWindow(MdiWidget):
    headers = {'Accept-Encoding': 'identity'}
    def __init__(self, parent, currency: CurrencyLiveCycle, labels: InfoLabels):
        super(CurrencyBokehWindow, self).__init__(parent)
        self.prevSize = self.size()
        self.setParent(parent)

        self.currency = currency
        self.topside_area = QHBoxLayout()
        self.bokehWidget = QWebEngineView()
        currency.updated.connect(self.graphUpdate)

        #self.horizontalLayout = QHBoxLayout()
        uic.loadUi("qt_python/qt_designer/bokeh_tool.ui", self)

        self.close.clicked.connect(parent.close)
        self.setMouseTracking(True)

        #self.setLayout(QVBoxLayout())

        self.labels = labels

        #self.horizontalLayout.setContentsMargins(0,10,0,0)
        currency.window_created()

    def graphUpdate(self, df: pd.DataFrame):
        self.current_df = df.copy()
        self.drawPyQtGraph()
    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        pass

    def drawPyQtGraph(self):
        self.bokehWidget.setUrl(QUrl("http://127.0.0.1:5000/?crypto=" + self.currency.currency_pair))

    def resizeEvent(self, event: PyQt6.QtGui.QResizeEvent):
        super(CurrencyBokehWindow, self).resizeEvent(event)
        coef_width = event.size().width() / self.prevSize.width()
        coef_height = event.size().height() / self.prevSize.height()
        self.drawPyQtGraph()



