from qt_imports import *

class SelectionListView(QListView):
    selected = QtCore.pyqtSignal(int)

    def __init__(self, parent):
        super(SelectionListView, self).__init__(parent=parent)

    def currentChanged(self, current: QtCore.QModelIndex, previous: QtCore.QModelIndex) -> None:
        self.selected.emit(current.row())
        super(SelectionListView, self).currentChanged(current, previous)


class SelectionDialog(QDialog):
    accepted = QtCore.pyqtSignal(str)

    def accept(self) -> None:
        self.accepted.emit(self.selected_pair.text())
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

        uic.loadUi("qt_designer/graph_selection_dialog.ui", self)
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


    def selectionComplete(self, selected: str):
        self.indicatorsList.deleteLater()