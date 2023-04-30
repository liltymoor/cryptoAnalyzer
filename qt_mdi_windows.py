from qt_imports import *
from currency_handler import LiveCycler, CurrencyLiveCycle, IndicatorsCalculator
from constants import INDICATORS_VOCABULARY_NAMES, \
SELECTION_DIALOG_WIDTH, SELECTION_DIALOG_HEIGHT, BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM, BOKEH_SUBWINDOW_MINIMUM_HEIGHT, BOKEH_SUBWINDOW_MINIMUM_WIDTH

from bokeh.plotting import curdoc, figure, show
from bokeh.embed import file_html


class MdiWidget(QWidget):
    def __init__(self, parent):
        super(MdiWidget, self).__init__()
        self.setParent(parent)

        self.close = QPushButton()
        self.mainLayout = QVBoxLayout()
        self.bokehWidget = QWidget()
        self.bokehWidget.setMouseTracking(True)
        uic.loadUi("qt_designer/bokeh_tool.ui")


        self.startPos = self.pos()
        self.isDragging = False

        self.isResizing = False
        self.resizingStartPos = 0
        self.cursor = 9

        self.close.clicked.connect(parent.close)
        self.setMouseTracking(True)

    # ========================================================================
    # ===================Overloaded events of widget==========================
    # ========================================================================

    def eventFilter(self, object: 'QObject', event: 'QEvent') -> bool:
        if event.type() is QEvent.Type.MouseMove:
            self.setCursorByBorder(self.mainLayout, event.pos())
        return super(MdiWidget, self).eventFilter(object, event)

    def mouseMoveEvent(self, eventArgs: QtGui.QMouseEvent) -> None:
        difference = eventArgs.pos() - self.startPos
        print(eventArgs.scenePosition().toPoint())
        if self.isDragging:
            newPos = self.parent().pos()
            point = eventArgs.scenePosition().toPoint()
            newPos -= (self.startPos - point)
            self.parent().move(newPos)
            self.startPos = point

        if self.isResizing:
            self.resizeByCursor(eventArgs)
        else:
            self.cursor = self.setCursorByBorder(self.mainLayout, eventArgs.pos())
        return super(MdiWidget, self).mouseMoveEvent(eventArgs)

    def mouseReleaseEvent(self, eventArgs: QtGui.QMouseEvent) -> None:
        if self.isDragging:
            self.isDragging = False
        if self.isResizing:
            self.isResizing = False
            self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
        return super(MdiWidget, self).mouseReleaseEvent(eventArgs)

    def mousePressEvent(self, eventArgs: QtGui.QMouseEvent) -> None:

        # Code 9 means the cursor is Qt.ArrowCursor
        if self.cursor != 9:
            self.resizingStartPos = eventArgs.scenePosition().toPoint()
            self.isResizing = True

        elif type(self.childAt(eventArgs.pos())) is QLabel:
            if self.childAt(eventArgs.pos()).text() == "Drag":
                self.isDragging = True
                self.startPos = eventArgs.scenePosition().toPoint()

        return super(MdiWidget, self).mousePressEvent(eventArgs)

    # ========================================================================
    # ===========================Over methods=================================
    # ========================================================================

    def setupTheFilter(self):
        self.bokehWidget.focusProxy().installEventFilter(self)

    def setCursorByBorder(self, object_to_check, pos):
        rect = object_to_check.geometry()

        top_left, top_right, bot_left, bot_right = \
            (rect.topLeft(), rect.topRight(), rect.bottomLeft(), rect.bottomRight())

        # top catch
        if pos in QRect(QPoint(top_left.x() + BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM,
                               top_left.y()),
                        QPoint(top_right.x() - BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM,
                               top_right.y() - BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM)):
            self.setCursor(QtCore.Qt.CursorShape.SizeVerCursor)
            return 1

        # bottom catch
        elif pos in QRect(QPoint(bot_left.x() + BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM,
                                 bot_left.y() + BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM),
                          QPoint(bot_right.x() - BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM,
                                 bot_right.y())):
            self.setCursor(QtCore.Qt.CursorShape.SizeVerCursor)
            return 2

        # right catch
        elif pos in QRect(QPoint(top_right.x() + BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM,
                                 top_right.y() + BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM),
                          QPoint(bot_right.x(), bot_right.y() - BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM)):
            self.setCursor(QtCore.Qt.CursorShape.SizeHorCursor)
            return 3

        # left catch
        elif pos in QRect(QPoint(top_left.x() - BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM,
                                 top_left.y() + BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM),
                          QPoint(bot_left.x(),
                                 bot_left.y() - BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM)):
            self.setCursor(QtCore.Qt.CursorShape.SizeHorCursor)
            return 4

        # top_right catch
        elif pos in QRect(QPoint(top_right.x(), top_right.y()),
                          QPoint(top_right.x() + BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM,
                                 top_right.y() - BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM)):
            self.setCursor(QtCore.Qt.CursorShape.SizeBDiagCursor)
            return 5

        # bottom_left catch
        elif pos in QRect(QPoint(bot_left.x(), bot_left.y()),
                          QPoint(bot_left.x() - BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM,
                                 bot_left.y() + BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM)):
            self.setCursor(QtCore.Qt.CursorShape.SizeBDiagCursor)
            return 6

        # top_left catch
        elif pos in QRect(QPoint(top_left.x(), top_left.y()),
                          QPoint(top_left.x() - BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM,
                                 top_left.y() - BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM)):
            self.setCursor(QtCore.Qt.CursorShape.SizeFDiagCursor)
            return 7

        # bottom_right catch
        elif pos in QRect(QPoint(bot_right.x(), bot_right.y()),
                          QPoint(bot_right.x() + BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM,
                                 bot_right.y() + BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM)):
            self.setCursor(QtCore.Qt.CursorShape.SizeFDiagCursor)
            return 8

        if self.isResizing:
            return self.cursor

        self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
        return 9

    def resizeByCursor(self, eventArgs: QtGui.QMouseEvent):

        geo = self.parent().geometry()
        difference = self.startPos
        current_pos = eventArgs.scenePosition().toPoint()

        # bottom
        if self.cursor == 2:
            difference = current_pos - self.resizingStartPos
            newHeight = geo.height() + difference.y()
            newWidth = int(newHeight * (BOKEH_SUBWINDOW_MINIMUM_WIDTH / BOKEH_SUBWINDOW_MINIMUM_HEIGHT))
            print(newHeight, newWidth, self.parent().minimumWidth(), self.parent().minimumHeight())
            if newWidth > self.parent().minimumWidth() - 1 and \
                    newHeight > self.parent().minimumHeight() - 1:
                self.resizeWidget(newWidth, newHeight)

        # bottom_right
        if self.cursor == 8:
            difference = current_pos - self.resizingStartPos
            newWidth = geo.width() + difference.x()
            newHeight = int(newWidth / (BOKEH_SUBWINDOW_MINIMUM_WIDTH / BOKEH_SUBWINDOW_MINIMUM_HEIGHT))
            if newWidth > self.parent().minimumWidth() and \
                    newHeight > self.parent().minimumHeight():
                self.resizeWidget(newWidth, newHeight)

        # bottom_left
        if self.cursor == 6:
            difference = self.resizingStartPos - current_pos
            newWidth = geo.width() + difference.x()
            newHeight = int(newWidth / (BOKEH_SUBWINDOW_MINIMUM_WIDTH / BOKEH_SUBWINDOW_MINIMUM_HEIGHT))
            if newWidth > self.parent().minimumWidth() and \
                    newHeight > self.parent().minimumHeight():
                self.resizeWidget(newWidth, newHeight)
        self.resizingStartPos = current_pos

    def resizeWidget(self, newWidth, newHeight):
        self.parent().setFixedSize(newWidth, newHeight)
        self.parent().setMinimumSize(BOKEH_SUBWINDOW_MINIMUM_WIDTH - 1, BOKEH_SUBWINDOW_MINIMUM_HEIGHT - 1)
        # self.bokehWidget.setZoomFactor(newWidth / BOKEH_SUBWINDOW_MINIMUM_WIDTH)


class CurrencyBokehWindow(MdiWidget):
    def __init__(self, parent, currency: CurrencyLiveCycle):
        super(CurrencyBokehWindow, self).__init__(parent)
        self.setParent(parent)
        self.currency = currency

        self.bokehWidget = QWebEngineView()
        self.bokehWidget.setMouseTracking(True)
        uic.loadUi("qt_designer/bokeh_tool.ui", self)

        #self.bokehWidget.setHtml(bokeh)

        self.close.clicked.connect(parent.close)
        self.setMouseTracking(True)


    # ========================================================================
    # ===================Overloaded events of widget==========================
    # ========================================================================



    # ========================================================================
    # ===========================Over methods=================================
    # ========================================================================

    def drawBokeh(self):
        df, ind_df = self.currency.get_dataframes()

        curdoc().theme = 'caliber'
        x = [df["Close"]]
        p = figure(title='CryptoAnalyzer', width=300, height=300)
        #p.line(x, y)
        #p.line(x, y2)
        #html = file_html(p, CDN, "plotik")

        self.bokehWidget.setHtml()

    def resizeWidget(self, newWidth, newHeight):
        super(CurrencyBokehWindow, self).resizeWidget(newWidth, newHeight)
        self.bokehWidget.setZoomFactor(newWidth / BOKEH_SUBWINDOW_MINIMUM_WIDTH)



