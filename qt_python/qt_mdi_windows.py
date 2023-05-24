import bokeh.plotting
from bokeh.resources import CDN

from qt_python.qt_imports import *
from data.currency_handler import LiveCycler, CurrencyLiveCycle, IndicatorsCalculator
from constants import *
from pandas import DataFrame as DF
from pandas import to_datetime
from bokeh.plotting import curdoc, figure
from datetime import datetime
from bokeh.embed import file_html
from bokeh.models import HoverTool, ColumnDataSource


class MdiWidget(QWidget):
    def __init__(self, parent, isInherit=False):
        super(MdiWidget, self).__init__()
        self.setParent(parent)

        self.close = QPushButton()
        self.mainLayout = QVBoxLayout()
        self.bokehWidget = QWidget()
        self.bokehWidget.setMouseTracking(True)

        if not isInherit:
            uic.loadUi("qt_python/qt_designer/mdi_widget.ui")


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

    def resizeWidget(self, newSize: QtCore.QSize):
        #self.parent().setFixedSize(newWidth, newHeight)
        #self.parent().setMinimumSize(BOKEH_SUBWINDOW_MINIMUM_WIDTH - 1, BOKEH_SUBWINDOW_MINIMUM_HEIGHT - 1)
        # self.bokehWidget.setZoomFactor(newWidth / BOKEH_SUBWINDOW_MINIMUM_WIDTH)
        pass


class CurrencyBokehWindow(MdiWidget):
    def __init__(self, parent, currency: CurrencyLiveCycle):
        super(CurrencyBokehWindow, self).__init__(parent, isInherit=True)
        self.plot_x = parent.size().height() - BOKEH_X_PADDING_BETWEEN_SUBWINDOW
        self.plot_y = parent.size().width() - BOKEH_Y_PADDING_BETWEEN_SUBWINDOW

        self.setParent(parent)
        self.currency = currency
        currency.updated.connect(self.BOKEH_update)

        self.bokehWidget = QWebEngineView()
        self.bokehWidget.setMouseTracking(True)
        uic.loadUi("qt_python/qt_designer/bokeh_tool.ui", self)

        #self.bokehWidget.setHtml(bokeh)

        self.close.clicked.connect(parent.close)
        self.setMouseTracking(True)

        self.currentBokehObject: bokeh.plotting.Figure = None
        self.xmax = None
        self.xmin = None
        self.ymax = None
        self.ymin = None
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
            x=df.index,
            y=df["Close"],
            date=[to_datetime(date, unit='ns') for date in df.index.values.tolist()])
        )

        #tools
        hoverTool = HoverTool(
            tooltips=[
                ('date',   '@date{%F %T}'),
                ('close',   self.currency.currency_pair + ' @y{%0.4f}')
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
                x_axis_type='datetime',
                tools=["pan", "wheel_zoom", hoverTool, "reset"],
                active_drag="pan",
                active_scroll="wheel_zoom",
                x_range=(min(df.index), max(df.index)),
                y_range=(min(df["Close"].values.tolist()), max(df["Close"].values.tolist())),
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




