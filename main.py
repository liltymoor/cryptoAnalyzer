from binance_imports import Client, SECRET_KEY, API_KEY
from currency_handler import CurrencyLiveCycle, LiveCycler
import asyncio

from bokeh.plotting import curdoc, figure, show
from bokeh.embed import file_html
from bokeh.resources import JS_RESOURCES, CDN, JSResources
from qt_analyzer import loadMain

client = Client(API_KEY, SECRET_KEY)

def run_live_currnecy():
    marked_pairs = [
        CurrencyLiveCycle(client, "ALICEBUSD", "1m"),
        CurrencyLiveCycle(client, "ADAUSDT", "1m")
    ]
    cycler = LiveCycler(marked_pairs)
    while True:
        cycler.live_loop()


def run_qt_ui(bokeh_obj):
    loadMain(bokeh_obj)

if __name__ == "__main__":
    x = [1, 2, 3, 4, 5]
    y = [6, 7, 6, 4, 5]
    y2 = [1, 8, 4, 1, 12]

    curdoc().theme = 'caliber'

    p = figure(title='CryptoAnalyzer', width=300, height=300)
    p.line(x, y)
    p.line(x, y2)
    html = file_html(p, CDN, "plotik")
    run_qt_ui(html)
    #show(p)
    # run_live_currnecy()





