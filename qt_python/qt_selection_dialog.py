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


class SelectionSearchBox(QTextEdit):
    def __init__(self, parent, size, pos):
        super().__init__()
        self.move(pos)
        self.setFixedSize(size)
        self.setParent(parent)


    def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
        super(SelectionSearchBox, self).keyPressEvent(e)
        self.parent().updateList(self.toPlainText())




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
        self.setParent(parent)
        self.indicatorsList = SelectionListView(None)

        self.selected_pair = QLabel()
        self.textEdit = QTextEdit()

        self.isLive = QCheckBox()

        self.fromDate = QDateTimeEdit()
        self.toDate = QDateTimeEdit()

        self.dialogButtons = QDialogButtonBox()

        uic.loadUi("qt_python/qt_designer/graph_selection_dialog.ui", self)
        self.textEdit = SelectionSearchBox(self, self.textEdit.size(), self.textEdit.pos())
        self.dialogButtons.button(self.dialogButtons.StandardButton.Ok).setEnabled(False)
        self.fromDate.setDateTime(datetime.datetime.now())
        self.toDate.setDateTime(datetime.datetime.now())
        self.indicatorsList.selected.connect(self.selectItem)

        self.model = QtGui.QStandardItemModel()
        self.indicatorsList.setModel(self.model)

        self.updateList("")

        self.accepted.connect(self.selectionComplete)
        self.rejected.connect(self.close)


    def updateList (self, searchString:str):
        self.model.clear()

        if searchString == "":
            for name in self.parent().pairs:
                pair_name = name

                item = QtGui.QStandardItem(pair_name)
                self.model.appendRow(item)
            return


        new_list = []
        for name in self.parent().pairs:
            if searchString.lower() in name.lower():
                new_list.append(name)

        for pair in new_list:
            qitem = QtGui.QStandardItem(pair)
            self.model.appendRow(qitem)


    def eventFilter(self, a0: QtCore.QObject, a1: QtCore.QEvent) -> bool:
        print(a0, a1)
        return super(SelectionDialog, self).eventFilter(a0,a1)

    def selectItem(self, index: int):
        if index != -1:
            self.selected_pair.setText(self.model.item(index, 0).text())
            self.dialogButtons.button(self.dialogButtons.StandardButton.Ok).setEnabled(True)


    def selectionComplete(self, selected: str):
        self.indicatorsList.deleteLater()