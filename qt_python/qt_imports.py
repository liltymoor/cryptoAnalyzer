from PyQt6 import uic, QtGui
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QWidget, QApplication, QMainWindow, QMdiArea, QMdiSubWindow, \
    QWidgetAction, QLabel, QDialog, QListView, QTextEdit, QCheckBox, QDateTimeEdit, QDialogButtonBox, QSizeGrip
from PyQt6.QtGui import QMovie
from PyQt6.QtCore import QEvent, QObject, QRect, QPoint, QThread, pyqtSignal
from PyQt6.QtWebEngineWidgets import *
from PyQt6 import QtCore
from PyQt6.QtCore import Qt


class InfoLabels:
    def __init__(self, next_upd: QLabel, current_pair: QLabel):
        self.next_update = next_upd
        self.current_pair = current_pair
