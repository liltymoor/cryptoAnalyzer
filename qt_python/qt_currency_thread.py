from qt_imports import *
from data.currency_handler import CurrencyLiveCycle
from qt_python.qt_selection_dialog import *

class AddPairWorker(QObject):
    done = pyqtSignal(CurrencyLiveCycle, SelectionInformation)
    close_loader = pyqtSignal()
    binance_connection = None
    selected_info = None

    def calc(self):
        currency = self.binance_connection.add_pair(
            self.selected_info.currency,
            "1m",
            date_from=self.selected_info.date_from,
            date_to=self.selected_info.date_to
        )

        self.close_loader.emit()
        self.done.emit(currency, self.selected_info)


class LoadingBox(QWidget):
    def __init__(self, loading_pair, parent = None):
        super(LoadingBox, self).__init__(parent)
        self.loading_pair = QLabel()
        self.loading_gif = QLabel()

        uic.loadUi("qt_python/qt_designer/loading.ui", self)

        self.setWindowModality(QtCore.Qt.WindowModality.WindowModal)

        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)

        load_gif = QMovie("qt_python/qt_designer/giphy.gif")
        load_gif.setScaledSize(self.loading_gif.size())
        self.loading_gif.setMovie(load_gif)
        load_gif.start()
        self.loading_pair.setText("loading pair - " + loading_pair)
