from binance_imports import Client, SECRET_KEY, API_KEY

from bokeh.plotting import curdoc, figure
from bokeh.embed import file_html
from bokeh.resources import CDN
from qt_python.qt_analyzer import loadMain

global client
client = Client(API_KEY, SECRET_KEY)


def main_entry():

    x = [1, 2, 3, 4, 5]
    y = [6, 7, 6, 4, 5]
    y2 = [1, 8, 4, 1, 12]

    curdoc().theme = 'caliber'

    p = figure(title='CryptoAnalyzer', width=300, height=300)
    p.line(x, y)
    p.line(x, y2)
    html = file_html(p, CDN, "plotik")
    loadMain(client)

    # marked_pairs = [
    #     CurrencyLiveCycle(client, "ALICEBUSD", "1m"),
    #     CurrencyLiveCycle(client, "ADAUSDT", "1m")
    # ]
    # cycler = LiveCycler(client, [
    #     ("ALICEBUSD", "1m"),
    #     ("BTCBUSD", "1m"),
    #     ("ADAUSDT", "1m"),
    #     ("ADAUSDT", "1m"),
    #     ("BNBBUSD", "1m")
    # ])
    # while True:
    #     cycler.live_loop()

if __name__ == "__main__":

    main_entry()



