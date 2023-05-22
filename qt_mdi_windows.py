import bokeh.plotting
from bokeh.resources import CDN

from qt_imports import *
from currency_handler import LiveCycler, CurrencyLiveCycle, IndicatorsCalculator
from constants import *
from pandas import DataFrame as DF
from pandas import to_datetime
from datetime import datetime
from bokeh.plotting import curdoc, figure, show
from bokeh.embed import file_html
from bokeh import events
from bokeh.models import WheelZoomTool, PanTool, HoverTool, ColumnDataSource, CustomJS, Div, ZoomInTool


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

    # def setupTheFilter(self):
    #     self.bokehWidget.focusProxy().installEventFilter(self)

    # def setCursorByBorder(self, object_to_check, pos):
    #     rect = object_to_check.geometry()
    #
    #     top_left, top_right, bot_left, bot_right = \
    #         (rect.topLeft(), rect.topRight(), rect.bottomLeft(), rect.bottomRight())
    #
    #     # top catch
    #     if pos in QRect(QPoint(top_left.x() + BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM,
    #                            top_left.y()),
    #                     QPoint(top_right.x() - BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM,
    #                            top_right.y() - BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM)):
    #         self.setCursor(QtCore.Qt.CursorShape.SizeVerCursor)
    #         return 1
    #
    #     # bottom catch
    #     elif pos in QRect(QPoint(bot_left.x() + BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM,
    #                              bot_left.y() + BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM),
    #                       QPoint(bot_right.x() - BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM,
    #                              bot_right.y())):
    #         self.setCursor(QtCore.Qt.CursorShape.SizeVerCursor)
    #         return 2
    #
    #     # right catch
    #     elif pos in QRect(QPoint(top_right.x() + BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM,
    #                              top_right.y() + BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM),
    #                       QPoint(bot_right.x(), bot_right.y() - BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM)):
    #         self.setCursor(QtCore.Qt.CursorShape.SizeHorCursor)
    #         return 3
    #
    #     # left catch
    #     elif pos in QRect(QPoint(top_left.x() - BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM,
    #                              top_left.y() + BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM),
    #                       QPoint(bot_left.x(),
    #                              bot_left.y() - BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM)):
    #         self.setCursor(QtCore.Qt.CursorShape.SizeHorCursor)
    #         return 4
    #
    #     # top_right catch
    #     elif pos in QRect(QPoint(top_right.x(), top_right.y()),
    #                       QPoint(top_right.x() + BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM,
    #                              top_right.y() - BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM)):
    #         self.setCursor(QtCore.Qt.CursorShape.SizeBDiagCursor)
    #         return 5
    #
    #     # bottom_left catch
    #     elif pos in QRect(QPoint(bot_left.x(), bot_left.y()),
    #                       QPoint(bot_left.x() - BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM,
    #                              bot_left.y() + BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM)):
    #         self.setCursor(QtCore.Qt.CursorShape.SizeBDiagCursor)
    #         return 6
    #
    #     # top_left catch
    #     elif pos in QRect(QPoint(top_left.x(), top_left.y()),
    #                       QPoint(top_left.x() - BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM,
    #                              top_left.y() - BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM)):
    #         self.setCursor(QtCore.Qt.CursorShape.SizeFDiagCursor)
    #         return 7
    #
    #     # bottom_right catch
    #     elif pos in QRect(QPoint(bot_right.x(), bot_right.y()),
    #                       QPoint(bot_right.x() + BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM,
    #                              bot_right.y() + BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM)):
    #         self.setCursor(QtCore.Qt.CursorShape.SizeFDiagCursor)
    #         return 8
    #
    #     if self.isResizing:
    #         return self.cursor
    #
    #     self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
    #     return 9

    # def resizeByCursor(self, eventArgs: QtGui.QMouseEvent):
    #
    #     geo = self.parent().geometry()
    #     difference = self.startPos
    #     current_pos = eventArgs.scenePosition().toPoint()
    #
    #     # bottom
    #     if self.cursor == 2:
    #         difference = current_pos - self.resizingStartPos
    #         newHeight = geo.height() + difference.y()
    #         newWidth = int(newHeight * (BOKEH_SUBWINDOW_MINIMUM_WIDTH / BOKEH_SUBWINDOW_MINIMUM_HEIGHT))
    #         print(newHeight, newWidth, self.parent().minimumWidth(), self.parent().minimumHeight())
    #         if newWidth > self.parent().minimumWidth() - 1 and \
    #                 newHeight > self.parent().minimumHeight() - 1:
    #             self.resizeWidget(newWidth, newHeight)
    #
    #     # bottom_right
    #     if self.cursor == 8:
    #         difference = current_pos - self.resizingStartPos
    #         newWidth = geo.width() + difference.x()
    #         newHeight = int(newWidth / (BOKEH_SUBWINDOW_MINIMUM_WIDTH / BOKEH_SUBWINDOW_MINIMUM_HEIGHT))
    #         if newWidth > self.parent().minimumWidth() and \
    #                 newHeight > self.parent().minimumHeight():
    #             self.resizeWidget(newWidth, newHeight)
    #
    #     # bottom_left
    #     if self.cursor == 6:
    #         difference = self.resizingStartPos - current_pos
    #         newWidth = geo.width() + difference.x()
    #         newHeight = int(newWidth / (BOKEH_SUBWINDOW_MINIMUM_WIDTH / BOKEH_SUBWINDOW_MINIMUM_HEIGHT))
    #         if newWidth > self.parent().minimumWidth() and \
    #                 newHeight > self.parent().minimumHeight():
    #             self.resizeWidget(newWidth, newHeight)
    #     self.resizingStartPos = current_pos

    def resizeWidget(self, newSize: QtCore.QSize):
        #self.parent().setFixedSize(newWidth, newHeight)
        #self.parent().setMinimumSize(BOKEH_SUBWINDOW_MINIMUM_WIDTH - 1, BOKEH_SUBWINDOW_MINIMUM_HEIGHT - 1)
        # self.bokehWidget.setZoomFactor(newWidth / BOKEH_SUBWINDOW_MINIMUM_WIDTH)
        pass


class CurrencyBokehWindow(MdiWidget):
    def __init__(self, parent, currency: CurrencyLiveCycle):
        super(CurrencyBokehWindow, self).__init__(parent)
        self.plot_x = parent.size().height() - BOKEH_X_PADDING_BETWEEN_SUBWINDOW
        self.plot_y = parent.size().width() - BOKEH_Y_PADDING_BETWEEN_SUBWINDOW

        self.setParent(parent)
        self.currency = currency
        currency.updated.connect(self.BOKEH_update)

        self.bokehWidget = QWebEngineView()
        self.bokehWidget.setMouseTracking(True)
        uic.loadUi("qt_designer/bokeh_tool.ui", self)

        #self.bokehWidget.setHtml(bokeh)

        self.close.clicked.connect(parent.close)
        self.setMouseTracking(True)

        self.currentBokehObject: bokeh.plotting.Figure = None
        currency.window_created()


    # ========================================================================
    # ===================Overloaded events of widget==========================
    # ========================================================================



    # ========================================================================
    # ===========================Over methods=================================
    # ========================================================================

    def BOKEH_update(self, df: DF):
        print()
        MdiWidget.debug_msg(self.currency.currency_pair, "Redraw were forced.")
        self.drawBokeh(df)

    def drawBokeh(self, df: DF):
        curdoc().theme = 'caliber'

        src = ColumnDataSource(data=dict(
            x=df.index.values.tolist(),
            y=df["Close"].values.tolist(),
            date=[to_datetime(date, unit='ns') for date in df.index.values.tolist()])
        )

        #tools
        hoverTool = HoverTool(
            tooltips=[
                ('date',   '@date{%F %T}'),
                ('close',  '$@y{%0.4f}')
            ],

            formatters={
                '@date': 'datetime',
                '@y': 'printf',
            },

            mode='vline'
        )


        self.currentBokehObject = figure (
                title=self.currency.currency_pair,
                plot_width=self.plot_y, plot_height=self.plot_x,
                x_axis_label='Time', y_axis_label='Value',
                tools=["pan", "wheel_zoom", hoverTool, "reset"],
                active_drag="pan",
                active_scroll="wheel_zoom",
                y_range=(min(df["Close"].values.tolist()),max(df["Close"].values.tolist())),
                output_backend='webgl'
        )
        curdoc().add_root(self.currentBokehObject)
        self.currentBokehObject.line('x', 'y', source=src)

        #circle = p.circle(x, y, fill_color="gray", size=2)

        #p.axis.minor_tick_in = -3
        #p.axis.minor_tick_out = 6

        self.updateWidget_html()

    def resizeWidget(self, newSize: QtCore.QSize):
        super(CurrencyBokehWindow, self).resizeWidget(newSize)

        self.plot_x = newSize.height() - BOKEH_X_PADDING_BETWEEN_SUBWINDOW
        self.plot_y = newSize.width() - BOKEH_Y_PADDING_BETWEEN_SUBWINDOW

        self.currentBokehObject.plot_height = self.plot_x
        self.currentBokehObject.plot_width = self.plot_y

        self.updateWidget_html()

    def updateWidget_html(self):
        html = file_html(self.currentBokehObject, CDN, "plotik")
        self.bokehWidget.setHtml(html)
        #self.bokehWidget.setZoomFactor(newWidth / BOKEH_SUBWINDOW_MINIMUM_WIDTH)




