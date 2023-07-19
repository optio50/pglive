import pglive.examples_pyside2 as examples
import signal
import time
from math import sin
from threading import Thread
from time import sleep

import pyqtgraph as pg  # type: ignore

from pglive.kwargs import Axis
from pglive.sources.data_connector import DataConnector
from pglive.sources.live_axis import LiveAxis
from pglive.sources.live_plot import LiveLinePlot
from pglive.sources.live_plot_widget import LivePlotWidget

"""
Line plot is displayed in this example.
"""
connectors = []

layout = pg.LayoutWidget()
# Define Time plot
left_axis = LiveAxis("left", axisPen="red", textPen="red")
bottom_axis = LiveAxis("bottom", axisPen="green", textPen="green", **{Axis.TICK_FORMAT: Axis.TIME})
time_axis_plot_widget = LivePlotWidget(title="Time Line Plot @ 100Hz",
                                       axisItems={'bottom': bottom_axis, 'left': left_axis})
plot = LiveLinePlot()
time_axis_plot_widget.addItem(plot)
connectors.append(DataConnector(plot, max_points=600))
layout.addWidget(time_axis_plot_widget)

# Define DateTime plot
left_axis = LiveAxis("left", axisPen="purple", textPen="purple")
bottom_axis = LiveAxis("bottom", axisPen="yellow", textPen="yellow", **{Axis.TICK_FORMAT: Axis.DATETIME})
datetime_axis_plot_widget = LivePlotWidget(title="DateTime Line Plot @ 100Hz",
                                           axisItems={'bottom': bottom_axis, 'left': left_axis})
plot = LiveLinePlot()
datetime_axis_plot_widget.addItem(plot)

layout.addWidget(datetime_axis_plot_widget)
connectors.append(DataConnector(plot, max_points=600))

layout.show()


def sin_wave_generator(*data_connectors):
    """Sinus wave generator"""
    x = 0
    while examples.running:
        x += 1
        for data_connector in data_connectors:
            data_connector.cb_append_data_point(sin(x * 0.01), time.time())
        sleep(0.01)


Thread(target=sin_wave_generator, args=connectors).start()
signal.signal(signal.SIGINT, lambda sig, frame: examples.stop())
examples.app.exec_()
examples.stop()
