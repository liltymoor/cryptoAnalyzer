
from PyQt6.QtWidgets import QHBoxLayout

import pyqtgraph as pg
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
        # difference = eventArgs.pos() - self.startPos
        #print(eventArgs.scenePosition().toPoint())
        if self.isDragging:
            newPos = self.parent().pos()
            point = eventArgs.scenePosition().toPoint()
            newPos -= (self.startPos - point)
            self.parent().move(newPos)
            self.startPos = point

        # if self.isResizing:
        #     self.resizeByCursor(eventArgs)
        # else:
        #     self.cursor = self.setCursorByBorder(self.mainLayout, eventArgs.pos())
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
    def __init__(self, parent, currency: CurrencyLiveCycle):
        super(CurrencyBokehWindow, self).__init__(parent)

        self.setParent(parent)
        self.currency = currency
        currency.updated.connect(self.PYQTGRAPH_update)
        self.horizontalLayout = QHBoxLayout()
        uic.loadUi("qt_python/qt_designer/bokeh_tool.ui", self)
        self.close.clicked.connect(parent.close)
        self.setMouseTracking(True)

        self.plotWidget = pg.PlotWidget(background='w')
        self.setLayout(QVBoxLayout())


        self.horizontalLayout.setContentsMargins(0,10,0,0)
        self.horizontalLayout.addWidget(self.plotWidget)
        self.plotWidget.getAxis('bottom').setPen('k')
        self.plotWidget.getAxis('left').setPen('k')

        font = QtGui.QFont()
        font.setPixelSize(15)
        self.plotWidget.getAxis('bottom').tickFont = font
        self.plotWidget.getAxis('left').tickFont = font

        self.plotWidget.showGrid(x=True, y=True, alpha=0.5)

        self.plotWidget.setLabel('left', 'Close Price', color='black', size=15)
        self.plotWidget.setLabel('bottom', 'Index', color='black', size=15)
        self.plotWidget.setTitle(currency.currency_pair, color='black', size='20pt')

        self.infoWindow = QLabel()
        self.infoWindow.setStyleSheet("QLabel { background-color : white; color : black; }")
        self.infoWindow.setWindowFlags(
            Qt.WindowType.ToolTip |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowTransparentForInput
        )
        self.infoWindow.setWindowOpacity(0.8)
        self.infoWindow.hide()

        self.point_pos = [None, None]

        self.plotWidget.scene().sigMouseMoved.connect(self.mouseMoved)

        self.scatterPlot = pg.ScatterPlotItem()

        self.plotWidget.addItem(self.scatterPlot)
        currency.window_created()

    def PYQTGRAPH_update(self, df: pd.DataFrame):
        self.current_df = df.copy()
        self.drawPyQtGraph(df)

    def drawPyQtGraph(self, df: pd.DataFrame):
        if df is None:
            return

        self.plotWidget.clear()
        pen = pg.mkPen(color='#1f77b4', width=2)
        self.plotWidget.plot(np.arange(1, len(df) + 1), df["Close"],
                             pen=pen)

        if None not in self.point_pos:
            self.plotWidget.removeItem(self.scatterPlot)

            pen = pg.mkPen(color='#FF5B1E')
            scatter = pg.ScatterPlotItem()
            scatter.addPoints([self.point_pos[0]], [self.point_pos[1]],
                              symbol='o', pen=pen, brush='#FF5B1E', size=4)
            self.plotWidget.addItem(scatter)
            self.scatterPlot = scatter

    def addPoint(self):
        new_date = self.current_df.index[-1] + pd.DateOffset(days=1)
        new_value = np.random.randn()
        new_point = pd.DataFrame(
            {"Close": new_value},
            index=[new_date])

        self.current_df = pd.concat([self.current_df, new_point])

        self.drawPyQtGraph(self.current_df)

    def showInfoWindow(self, x, y):
        self.infoWindow.setText(f"Date: {x}\nY: {y}")
        mouse_pos = QtGui.QCursor.pos()
        window_pos = mouse_pos + QtCore.QPoint(15, 15)
        self.infoWindow.move(window_pos)
        self.infoWindow.show()

    def hideInfoWindow(self):
        self.infoWindow.hide()

    def mouseMoved(self, pos):
        if self.current_df is None:
            return

        mousePoint = self.plotWidget.plotItem.vb.mapSceneToView(pos)
        index = int(mousePoint.x())
        if 0 <= index < len(self.current_df):
            x = self.current_df.index[index].strftime('%Y-%m-%d %H:%M')
            y = self.current_df.iloc[index]['Close']
            self.showInfoWindow(x, y)

            self.plotWidget.removeItem(self.scatterPlot)

            pen = pg.mkPen(color='r')
            scatter = pg.ScatterPlotItem()
            scatter.addPoints([index + 1], [y], symbol='o', pen=pen, brush='r', size=4)
            self.plotWidget.addItem(scatter)
            self.scatterPlot = scatter

            self.point_pos = [index + 1, y]

        else:
            self.hideInfoWindow()

    def handleApplicationStateChanged(self, state):
        if state == QtCore.Qt.WindowMinimized:
            self.hideInfoWindow()

    def windowStateChanged(self, event):
        if event.oldState() == Qt.WindowNoState and event.newState() == Qt.WindowMinimized:
            self.hideInfoWindow()

    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange and self.isMinimized():
            self.hideInfoWindow()
        super(CurrencyBokehWindow, self).changeEvent(event)

    def resizeEvent(self, event):
        super(CurrencyBokehWindow, self).resizeEvent(event)
        self.drawPyQtGraph(self.current_df)

    def leaveEvent(self, event):
        self.hideInfoWindow()
        event.ignore()

    def closeEvent(self, event):
        self.hideInfoWindow()
        super(CurrencyBokehWindow, self).closeEvent(event)


