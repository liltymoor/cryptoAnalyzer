import sys
import time as t
import traceback
from constants import INDICATORS_VOCABULARY_NAMES, \
SELECTION_DIALOG_WIDTH, SELECTION_DIALOG_HEIGHT, BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM, BOKEH_SUBWINDOW_MINIMUM_HEIGHT, BOKEH_SUBWINDOW_MINIMUM_WIDTH
from qt_imports import *
from qt_fetcher import QPairFetcher, QBinanceDfFetcher
from qt_selection_dialog import *

from currency_handler import *




class BokehToolWindow(QWidget):
    def __init__(self, bokeh, parent):
        super(BokehToolWindow, self).__init__()

        self.setParent(parent)

        self.mainLayout = QVBoxLayout()
        self.bokehWidget = QWebEngineView()
        self.bokehWidget.setMouseTracking(True)


        #self.bokehWidget.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)
        #self.bokehWidget.focusProxy().installEventFilter(self)

        self.close = QPushButton

        uic.loadUi("qt_designer/bokeh_tool.ui", self)
        self.bokehWidget.setHtml(bokeh)

        self.startPos = self.pos()
        self.isDragging = False

        self.isResizing = False
        self.resizingStartPos = 0
        self.cursor = 9

        self.close.clicked.connect(parent.close)
        self.setMouseTracking(True)


#========================================================================
#===================Overloaded events of widget==========================
#========================================================================

    def eventFilter(self, object: 'QObject', event: 'QEvent') -> bool:
        if event.type() is QEvent.Type.MouseMove:
            self.setCursorByBorder(self.mainLayout, event.pos())
        return super(BokehToolWindow, self).eventFilter(object,event)
        
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
        return super(BokehToolWindow, self).mouseMoveEvent(eventArgs)

    def mouseReleaseEvent(self, eventArgs: QtGui.QMouseEvent) -> None:
        if self.isDragging:
            self.isDragging = False
        if self.isResizing:
            self.isResizing = False
            self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
        return super(BokehToolWindow, self).mouseReleaseEvent(eventArgs)

    def mousePressEvent(self, eventArgs: QtGui.QMouseEvent) -> None:

        # Code 9 means the cursor is Qt.ArrowCursor
        if self.cursor != 9:
            self.resizingStartPos = eventArgs.scenePosition().toPoint()
            self.isResizing = True

        elif type(self.childAt(eventArgs.pos())) is QLabel:
            if self.childAt(eventArgs.pos()).text() == "Drag":
                self.isDragging = True
                self.startPos = eventArgs.scenePosition().toPoint()


        return super(BokehToolWindow, self).mousePressEvent(eventArgs)

    def paintEvent(self, eventArgs: QtGui.QPaintEvent) -> None:
        return super(BokehToolWindow, self).paintEvent(eventArgs)


#========================================================================
#===========================Over methods=================================
#========================================================================

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

    def resizeByCursor(self, eventArgs : QtGui.QMouseEvent):


        geo = self.parent().geometry()
        difference = self.startPos
        current_pos = eventArgs.scenePosition().toPoint()

        #bottom
        if self.cursor == 2:
            difference = current_pos - self.resizingStartPos
            newHeight = geo.height() + difference.y()
            newWidth = int(newHeight * (BOKEH_SUBWINDOW_MINIMUM_WIDTH / BOKEH_SUBWINDOW_MINIMUM_HEIGHT))
            print(newHeight, newWidth, self.parent().minimumWidth(), self.parent().minimumHeight())
            if newWidth > self.parent().minimumWidth() - 1 and \
                    newHeight > self.parent().minimumHeight() - 1:
                self.parent().setFixedSize(newWidth, newHeight)
                self.parent().setMinimumSize(BOKEH_SUBWINDOW_MINIMUM_WIDTH - 1, BOKEH_SUBWINDOW_MINIMUM_HEIGHT - 1)
                self.bokehWidget.setZoomFactor(newWidth / BOKEH_SUBWINDOW_MINIMUM_WIDTH)

        # bottom_right
        if self.cursor == 8:
            difference = current_pos - self.resizingStartPos
            newWidth = geo.width() + difference.x()
            newHeight = int (newWidth / (BOKEH_SUBWINDOW_MINIMUM_WIDTH / BOKEH_SUBWINDOW_MINIMUM_HEIGHT))
            if newWidth > self.parent().minimumWidth() and \
                    newHeight > self.parent().minimumHeight():
                self.parent().setFixedSize(newWidth, newHeight)
                self.parent().setMinimumSize(BOKEH_SUBWINDOW_MINIMUM_WIDTH - 1, BOKEH_SUBWINDOW_MINIMUM_HEIGHT - 1)
                self.bokehWidget.setZoomFactor(newWidth / BOKEH_SUBWINDOW_MINIMUM_WIDTH)

        # bottom_left
        if self.cursor == 6:
            difference = self.resizingStartPos - current_pos
            newWidth = geo.width() + difference.x()
            newHeight = int (newWidth / (BOKEH_SUBWINDOW_MINIMUM_WIDTH / BOKEH_SUBWINDOW_MINIMUM_HEIGHT))
            if newWidth > self.parent().minimumWidth() and \
                    newHeight > self.parent().minimumHeight():
                self.parent().setFixedSize(newWidth, newHeight)
                self.parent().setMinimumSize(BOKEH_SUBWINDOW_MINIMUM_WIDTH - 1, BOKEH_SUBWINDOW_MINIMUM_HEIGHT - 1)
                self.bokehWidget.setZoomFactor(newWidth / BOKEH_SUBWINDOW_MINIMUM_WIDTH)


        self.resizingStartPos = current_pos


class SubWindow(QMdiSubWindow):
    def __init__(self, parent : QMainWindow):
        super(SubWindow, self).__init__()
        self.setMouseTracking(True)
        self.setParent(parent)


    def mouseMoveEvent(self, mouseEvent: QtGui.QMouseEvent) -> None:
        super(SubWindow, self).mouseMoveEvent(mouseEvent)

    def close(self) -> bool:
        MainWindow.RemoveAreaFromMdi()
        super(SubWindow, self).close()



class MainWindow(QMainWindow):
    count = 0
    opened_win = []

    def __init__(self, client):
        super().__init__()
        self.pairs = []
        self.selected_pairs = []
        # self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        # self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.leftMenu = QWidget()
        self.workspace = QWidget()
        self.mdiArea = QMdiArea()
        self.client = client

        self.pushButton   = QPushButton()
        self.pushButton_2 = QPushButton()
        self.pushButton_3 = QPushButton()
        self.pushButton_4 = QPushButton()
        self.pushButton_5 = QPushButton()
        self.pushButton_6 = QPushButton()

        uic.loadUi("qt_designer/main_menu.ui", self)

        self.pushButton_6.clicked.connect(self.openGraphSelectionDialog)
        self.isDragging = False
        self.setMouseTracking(True)

        #Getting all the pairs from binance
        self.fetched_pairs = []
        self.fetch_thread = QThread()
        self.fetcher = QPairFetcher()
        self.fetcher.moveToThread(self.fetch_thread)

        self.fetch_thread.started.connect(self.fetcher.fetch)
        self.fetcher.finished.connect(self.fetch_complete)
        self.fetcher.finished.connect(self.fetch_thread.quit)
        self.fetcher.finished.connect(self.fetcher.deleteLater)
        self.fetch_thread.finished.connect(self.fetch_thread.deleteLater)
        self.fetcher.progress.connect(self.fetching)


        self.timer = t.time()
        self.fetch_thread.start()

        self.binance_connector_thr = QThread()
        self.binance_connection = QBinanceDfFetcher(self.client, self.selected_pairs)
        self.selected_pairs = self.binance_connection.get_currencies_list()
        for pair in self.selected_pairs:
            self.currencies_update(pair)

        self.binance_connection.moveToThread(self.binance_connector_thr)
        self.binance_connection.progress.connect(self.currencies_update)

        self.binance_connector_thr.started.connect(self.binance_connection.start_fetching)
        self.binance_connector_thr.start()


    # For fetching all the pairs (progress function)
    # TODO loading page
    def fetching(self, fetched):
        #print(str(fetched), end="\r")
        pass

    def fetch_complete(self, pairs):
        self.pairs = pairs
        print("Fetching pairs completed.",
              str(len(self.pairs)) +
              " pairs collected", "Elapsed time :", t.time() - self.timer)

        # self.pairs = self.fetched_pairs[0]
        # del self.fetched_pairs
        # print(self.pairs)


    def currencies_update(self, currency: tuple):
        df, ind_df = currency


    # =======================================
    # ================MDI====================
    # =======================================

    def AddAreaToMdi(self):
        MainWindow.count = MainWindow.count + 1

        sub = SubWindow(parent=self)
        sub.setParent(self)

        sub.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        sub.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        sub.setMinimumSize(
            BOKEH_SUBWINDOW_MINIMUM_WIDTH - 1,
            BOKEH_SUBWINDOW_MINIMUM_HEIGHT - 1)
        sub.setFixedSize(
            BOKEH_SUBWINDOW_MINIMUM_WIDTH,
            BOKEH_SUBWINDOW_MINIMUM_HEIGHT)

        #sub.setMaximumSize(330, 350)

        # TODO Add bokeh generation
        #bokehW = BokehToolWindow(bokeh=self.bokeh, parent=sub)
        #bokehW.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        #sub.setWidget(bokehW)
        sub.setWindowTitle("Sub Window" + str(MainWindow.count))

        self.mdiArea.addSubWindow(sub)
        self.mdiArea.tileSubWindows()

        sub.show()
        #bokehW.setupTheFilter()

    @classmethod
    def RemoveAreaFromMdi(cls):
        MainWindow.count -= 1

    # =======================================
    # ===========SelectionDialog=============
    # =======================================


    def openGraphSelectionDialog(self):
        dialog = SelectionDialog(self)

        dialog.accepted.connect(self.selectiondDialog_complete)
        dialog.setWindowTitle("Select the graph")
        dialog.setWindowFlag(QtCore.Qt.WindowType.WindowCloseButtonHint)
        dialog.setFixedSize(
            SELECTION_DIALOG_WIDTH,
            SELECTION_DIALOG_HEIGHT)
        dialog.exec()

    def selectiondDialog_complete(self, selected: str):
        self.binance_connection.add_pair(selected, "1m")
        print(self.selected_pairs)


def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("error catched!:")
    print("error message:\n", tb)
    QApplication.quit()
    # or QtWidgets.QApplication.exit(0)


def loadMain(client):
    app = QApplication(sys.argv)
    ex = MainWindow(client)
    ex.show()
    sys.excepthook = excepthook
    sys.exit(app.exec())


async def bokeh_graphs_loader():
    pass
