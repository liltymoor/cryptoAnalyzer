import sys
import time as t
import traceback
from qt_imports import *
from constants import INDICATORS_VOCABULARY_NAMES, \
SELECTION_DIALOG_WIDTH, SELECTION_DIALOG_HEIGHT, BOKEH_SUBWINDOW_MINIMUM_HEIGHT, \
BOKEH_SUBWINDOW_MINIMUM_WIDTH, BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM

from qt_fetcher import QPairFetcher, QBinanceDfFetcher
from qt_selection_dialog import *
from qt_mdi_windows import CurrencyBokehWindow
from currency_handler import *


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
        self.mdiArea.setMouseTracking(True)

        self.client = client

        self.pushButton   = QPushButton()
        self.pushButton_2 = QPushButton()
        self.pushButton_3 = QPushButton()
        self.pushButton_4 = QPushButton()
        self.pushButton_5 = QPushButton()
        self.pushButton_6 = QPushButton()

        uic.loadUi("qt_designer/main_menu.ui", self)

        #self.setCentralWidget(self.mdiArea)

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
        self.binance_connection = QBinanceDfFetcher(self.client)
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

    def AddAreaToMdi(self, window):
        MainWindow.count = MainWindow.count + 1
        self.mdiArea.addSubWindow(window)
        window.show()

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

    def selectiondDialog_complete(self, selected_info: SelectionInformation):
        currency = self.binance_connection.add_pair(
            selected_info.currency,
            "1m",
            date_from=selected_info.date_from,
            date_to=selected_info.date_to
        )

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
        sub.setWindowTitle(selected_info.currency)

        widget = CurrencyBokehWindow(sub, currency)
        widget.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        sub.setWidget(widget)
        sub.setMouseTracking(True)
        self.AddAreaToMdi(sub)

class SubWindow(QMdiSubWindow):
    def __init__(self, parent: QMainWindow):
        super(SubWindow, self).__init__()
        self.size_grip = QSizeGrip(self)
        self.size_grip.setVisible(False)
        #self.size_grip.setVisible(False)

        self.minimum = QtCore.QSize(
            BOKEH_SUBWINDOW_MINIMUM_WIDTH - 1,
            BOKEH_SUBWINDOW_MINIMUM_HEIGHT - 1)

        self.size_grip.installEventFilter(self)
        self.setMouseTracking(True)
        self.parent = parent

        self.prev_pos = None

    def eventFilter(self, source, event):
        if event.type() == event.Type.MouseMove and event.buttons() == Qt.MouseButton.LeftButton:
            if self.cursor() != QtCore.Qt.CursorShape.ArrowCursor:
                # Calculate the new size based on the size grip position
                new_pos = self.size_grip.mapToParent(event.pos())

                # Calculate the difference in position using previous position
                if self.prev_pos is not None:
                    diff = new_pos - self.prev_pos
                else:
                    diff = QPoint(0, 0)
                self.prev_pos = new_pos

                # Calculate the new size based on the position difference
                new_size = QtCore.QSize(self.size().width() + diff.x(), self.size().height() + diff.y())


                # Check if the new size violates the minimum size
                new_size = QtCore.QSize(
                    max(new_size.width(), self.minimum.width()),
                    max(new_size.height(), self.minimum.height()))

                # Set the new size as the fixed size of the subwindow
                self.widget().resizeWidget(new_size)
                self.setFixedSize(new_size)
                return True
        elif event.type() == event.Type.MouseButtonRelease:
            self.prev_pos = None  # Reset previous position when mouse button is released
        return super().eventFilter(source, event)

    def mouseMoveEvent(self, mouseEvent: QtGui.QMouseEvent) -> None:
        super(SubWindow, self).mouseMoveEvent(mouseEvent)

    def close(self) -> bool:
        MainWindow.RemoveAreaFromMdi()
        self.parent.binance_connection.remove_pair(self.widget().currency)
        super(SubWindow, self).close()



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
