import sys
import traceback
from constants import INDICATORS_VOCABULARY_NAMES, \
SELECTION_DIALOG_WIDTH, SELECTION_DIALOG_HEIGHT, BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM, BOKEH_SUBWINDOW_MINIMUM_HEIGHT, BOKEH_SUBWINDOW_MINIMUM_WIDTH
from PyQt6 import uic, QtGui
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QWidget, QApplication, QMainWindow, QMdiArea, QMdiSubWindow, \
    QWidgetAction, QLabel, QDialog, QListView, QTextEdit, QCheckBox, QDateTimeEdit, QDialogButtonBox

from PyQt6.QtCore import QEvent, QObject, QRect, QPoint
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtWebEngineCore import QWebEngineSettings
#from PyQt6.QtGui import QPainter, QColor
from PyQt6 import QtCore





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

    def __init__(self, bokeh):
        super().__init__()

        # self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        # self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.leftMenu = QWidget()
        self.workspace = QWidget()
        self.mdiArea = QMdiArea()
        self.bokeh = bokeh

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

    def WindowTrig(self, p):

        if p.text() == "New":
            MainWindow.count = MainWindow.count + 1
            sub = QMdiSubWindow()

            sub.setWidget(MainWindow())
            sub.setWindowTitle("Sub Window" + str(MainWindow.count))
            self.mdiArea.addSubWindow(sub)
            sub.show()

        if p.text() == "cascade":
            self.mdiArea.cascadeSubWindows()

        if p.text() == "Tiled":
            self.mdiArea.tileSubWindows()

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

        bokehW = BokehToolWindow(bokeh=self.bokeh, parent=sub)

        sub.setWidget(bokehW)
        sub.setWindowTitle("Sub Window" + str(MainWindow.count))

        self.mdiArea.addSubWindow(sub)
        self.mdiArea.tileSubWindows()

        sub.show()
        bokehW.setupTheFilter()

    def openGraphSelectionDialog(self):
        dialog = SelectionDialog()
        dialog.setWindowTitle("Select the graph")
        dialog.setWindowFlag(QtCore.Qt.WindowType.WindowCloseButtonHint)
        dialog.setFixedSize(
            SELECTION_DIALOG_WIDTH,
            SELECTION_DIALOG_HEIGHT)
        dialog.exec()

    @classmethod
    def RemoveAreaFromMdi(cls):
        MainWindow.count -= 1


class SelectionDialog(QDialog):
    def __init__(self):
        super(SelectionDialog, self).__init__()
        self.indicatorsList = QListView()
        self.textEdit = QTextEdit()
        self.isLive = QCheckBox()

        self.fromDate = QDateTimeEdit()
        self.toDate = QDateTimeEdit()

        self.dialogButtons = QDialogButtonBox()
        uic.loadUi("qt_designer/graph_selection_dialog.ui", self)

        model = QtGui.QStandardItemModel()
        self.indicatorsList.setModel(model)

        for name, lines in INDICATORS_VOCABULARY_NAMES.items():
            for line in range(len(lines)):
                if type(lines[line]) is list:
                    lines[line] = ", ".join(lines[line])

            string_item = "[" + ", ".join(lines) + "] "
            string_item += name

            item = QtGui.QStandardItem(string_item)
            model.appendRow(item)


        self.accepted.connect(self.selectionComplete)
        self.rejected.connect(self.close)

    def selectionComplete(self):
        pass

def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("error catched!:")
    print("error message:\n", tb)
    QApplication.quit()
    # or QtWidgets.QApplication.exit(0)


def loadMain(bokeh_obj):
    app = QApplication(sys.argv)
    ex = MainWindow(bokeh_obj)
    ex.show()
    sys.excepthook = excepthook
    sys.exit(app.exec())


async def bokeh_graphs_loader():
    pass
