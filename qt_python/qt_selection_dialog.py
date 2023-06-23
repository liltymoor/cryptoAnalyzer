import datetime
import sys

sys.path.insert(1, "qt_python/")
from qt_python.qt_imports import *

class SelectionInformation:
    def __init__(self, currency,
                 is_live: bool,
                 date_from: datetime.datetime,
                 date_to: datetime.datetime):
        self.currency = currency
        self.is_live = is_live
        self.date_from = date_from
        self.date_to = date_to


class SelectionListView(QListView):
    selected = QtCore.pyqtSignal(int)

    def __init__(self, parent):
        super(SelectionListView, self).__init__(parent=parent)

    def currentChanged(self, current: QtCore.QModelIndex, previous: QtCore.QModelIndex) -> None:
        self.selected.emit(current.row())
        super(SelectionListView, self).currentChanged(current, previous)


class SelectionDialog(QDialog):
    accepted = QtCore.pyqtSignal(SelectionInformation)

    def accept(self) -> None:

        info_object = SelectionInformation(
            self.selected_pair.text(),
            self.isLive.checkState().value == self.isLive.checkState().Checked,
            self.fromDate.dateTime().toPyDateTime(),
            self.fromDate.dateTime().toPyDateTime()
        )

        self.accepted.emit(info_object)
        super().accept()


    def __init__(self, parent):
        super(SelectionDialog, self).__init__(parent)
        # self.setParent(parent)
        self.indicatorsList = SelectionListView(None)

        self.selected_pair = QLabel()
        self.textEdit = QTextEdit()
        self.isLive = QCheckBox()

        self.fromDate = QDateTimeEdit()
        self.toDate = QDateTimeEdit()

        self.dialogButtons = QDialogButtonBox()

        uic.loadUi("qt_python/qt_designer/graph_selection_dialog.ui", self)
        self.dialogButtons.button(self.dialogButtons.StandardButton.Ok).setEnabled(False)
        self.fromDate.setDateTime(datetime.datetime.now())
        self.toDate.setDateTime(datetime.datetime.now())
        self.indicatorsList.selected.connect(self.selectItem)

        self.model = QtGui.QStandardItemModel()
        self.indicatorsList.setModel(self.model)

        for name in parent.pairs:
            pair_name = name

            item = QtGui.QStandardItem(pair_name)
            self.model.appendRow(item)


        self.accepted.connect(self.selectionComplete)
        self.rejected.connect(self.close)


    def selectItem(self, index: int):
        if index != -1:
            self.selected_pair.setText(self.model.item(index, 0).text())
            self.dialogButtons.button(self.dialogButtons.StandardButton.Ok).setEnabled(True)


    def selectionComplete(self, selected: str):
        self.indicatorsList.deleteLater()