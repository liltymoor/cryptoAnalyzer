from binance_imports import Client, SECRET_KEY, API_KEY

from bokeh.plotting import curdoc, figure
from bokeh.embed import file_html
from bokeh.resources import CDN
from qt_python.qt_analyzer import loadMain
import subprocess

global client
client = Client(API_KEY, SECRET_KEY)


def main_entry():
    subprocess.Popen(
        ['python', '-u', 'flask_controller.py'])
    loadMain(client)


if __name__ == "__main__":
    main_entry()



