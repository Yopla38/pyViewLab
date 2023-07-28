import random

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QRubberBand, QGridLayout, QSizePolicy, \
    QLabel, QSplitter, QScrollArea, QHBoxLayout, QInputDialog


from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtCore import Qt, QRect, pyqtSlot
import time

from pyqtgraph import BarGraphItem
import pyqtgraph.opengl as gl
import random
from Axe import CustomAxis


class GraphXY:
    def __init__(self, window, autoscale=True, legend=True, accumulation=False, tools=None, realtime=False, max_points=None):

        self.window = window
        self.grid = QGridLayout()
        self.plot = pg.PlotWidget()
        self.plot.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
        self.grid.addWidget(self.plot, 0, 0)  # add the plot to the grid
        self.legend_label = QLabel()  # create a QWidget for the legend
        self.grid.addWidget(self.legend_label, 0, 1)  # add the QLabel to the grid
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.grid)
        self.autoscale = autoscale
        self.accumulation = accumulation
        self.tools = tools if tools is not None else []
        self.realtime = realtime
        self.max_points = max_points
        self.curves = []

        self.legend_layout = QVBoxLayout()
        self.grid.addLayout(self.legend_layout, 0, 1)


    def connect(self, x, y, color=(0, 0, 255), name=''):
        y_return = y()
        if isinstance(y_return, (tuple, list)):
            if isinstance(color, tuple):
                color = [color] + [tuple(map(lambda x: random.randint(0, 255), color)) for _ in
                                   range(len(y_return) - 1)]
            elif isinstance(color, str):
                color = [color for _ in range(len(y_return))]
            # Check if y() returns multiple values (tuple or list)
            return [self.connect(x, lambda y=y, i=i: y()[i], color[i], f"{name} {i + 1}") for i in range(len(y_return))]

        else:
            # Else perform the usual steps
            curve = {
                'x': x,
                'y': y,
                'color': color,
                'name': name,
                'x_data': [],
                'y_data': [],
                'plot_curve': self.plot.plot(pen=color, name=name)  # Create an empty plot curve
            }
            self.curves.append(curve)
            if self.autoscale:
                self.plot.enableAutoRange('xy', True)  # Enable auto scale
            if 'zoom' in self.tools:
                self.plot.setMouseEnabled(x=True, y=True)  # Enable manual zoom
            if 'selection' in self.tools:
                self.plot.setMouseEnabled(x=True, y=True)  # Enable mouse interaction
            self.window.legend_layout.addWidget(
                self.create_legend_item(color, name))  # add the legend to the legend layout

            # Connecte le click de souris à une slot fonction change_scale qui n'est pas défini encore
            #curve['plot_curve'].scene().sigMouseClicked.connect(self.change_scale)
            #curve['plot_curve'].setAcceptHoverEvents(True)
        return curve



    def create_legend_item(self, color, name):
        # Crée un QPixmap
        pixmap = QPixmap(12, 12)

        # Remplit la pixmap de la couleur
        if isinstance(color, tuple):
            pixmap.fill(QColor(*color))
        elif isinstance(color, str):
            color_map = {'r': Qt.GlobalColor.red,
                         'b': Qt.GlobalColor.blue,
                         'g': Qt.GlobalColor.green}
            pixmap.fill(color_map.get(color, Qt.GlobalColor.black))
        '''
        # Définit la GColor
        if color == 'r':
            gcolor = Qt.GlobalColor.red
        elif color == 'b':
            gcolor = Qt.GlobalColor.blue
        elif color == 'g':
            gcolor = Qt.GlobalColor.green
        # Ajouter plus de conditions ici pour d'autres couleurs

        # Remplit la pixmap de la couleur
        pixmap.fill(gcolor)
        '''
        # Crée une QLabel
        label = QLabel()

        # Met le QPixmap dans la QLabel
        label.setPixmap(pixmap)

        # Crée une seconde QLabel pour le texte
        label_text = QLabel()
        label_text.setText(name)

        # Prépare un layout pour la QLabel de l'icône et celle du texte
        layout = QHBoxLayout()
        layout.addWidget(label)  # Ajoute l'icône
        layout.addWidget(label_text)  # Ajoute le texte

        # Prépare un widget qui contiendra les QLabels
        container = QWidget()
        container.setLayout(layout)

        return container

    def set_labels(self, x_label, y_label):
        self.plot.setLabel('bottom', x_label)
        self.plot.setLabel('left', y_label)

    def update(self):

        for curve in self.curves:
            curve['x_data'].append(curve['x']())
            curve['y_data'].append(curve['y']())
            if self.max_points and len(curve['x_data']) > self.max_points:
                curve['x_data'] = curve['x_data'][-self.max_points:]
                curve['y_data'] = curve['y_data'][-self.max_points:]
            curve['plot_curve'].setData(curve['x_data'], curve['y_data'])  # Update the plot curve with the new data

    def get_curves_info(self):
        curves_info = []
        for curve in self.curves:
            curves_info.append({
                'x': curve['x'],
                'y': curve['y'],
                'color': curve['color'],
                'number_of_points': len(curve['x_data'])
            })
        return curves_info


class ScatterGraph(GraphXY):
    def connect(self, x, y, color='b', symbol='o', name=''):
        y_return = y()
        if isinstance(y_return, (tuple, list)):
            if isinstance(color, tuple):
                color = [color] + [tuple(map(lambda x: random.randint(0, 255), color)) for _ in
                                   range(len(y_return) - 1)]
            elif isinstance(color, str):
                color = [color for _ in range(len(y_return))]
            if isinstance(name, str):
                name = [name + "_" + str(i + 1) for i in range(len(y_return))]
            # Check if y() returns multiple values (tuple or list)
            return [self.connect(x, lambda y=y, i=i: y()[i], color[i], symbol, name[i]) for i in range(len(y_return))]

        else:
            curve = {
                'x': x,
                'y': y,
                'color': QColor(*color),
                'x_data': [],
                'y_data': [],
                'symbol': 'o',  # symbol for scatter plot
                'name': name,
                'plot_curve': self.plot.plot(pen=None, name=name, symbol=symbol, symbolBrush=color)  # Create an empty plot curve
            }
        self.curves.append(curve)
        if self.autoscale:
            self.plot.enableAutoRange('xy', True)  # Enable auto scale
        if 'zoom' in self.tools:
            self.plot.setMouseEnabled(x=True, y=True)  # Enable manual zoom
        if 'selection' in self.tools:
            self.plot.setMouseEnabled(x=True, y=True)  # Enable mouse interaction
        self.window.legend_layout.addWidget(self.create_legend_item(color, name)) # add the legend to the legend layout

    def update(self):
        # and in update()
        for curve in self.curves:
            curve['x_data'].append(curve['x']())
            curve['y_data'].append(curve['y']())
            if self.max_points and len(curve['x_data']) > self.max_points:
                curve['x_data'] = curve['x_data'][-self.max_points:]
                curve['y_data'] = curve['y_data'][-self.max_points:]

            curve['plot_curve'].setData(curve['x_data'], curve['y_data'])  # Update the plot curve with the new data

class BarGraphXY(GraphXY):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bars = []

    def connect(self, x, y, color='b', name=''):
        bar = {
            'x': x,
            'y': y,
            'color': QColor(color),
            'x_data': [],
            'y_data': [],
            'name': name
        }
        self.bars.append(bar)

    def update(self):
        for bar in self.bars:
            bar['x_data'].append(bar['x']())
            bar['y_data'].append(bar['y']())
            if self.max_points and len(bar['x_data']) > self.max_points:
                bar['x_data'] = bar['x_data'][-self.max_points:]
                bar['y_data'] = bar['y_data'][-self.max_points:]
            bg1 = BarGraphItem(x=bar['x_data'], height=bar['y_data'], width=0.01, brush=bar['color'])
            self.plot.addItem(bg1)


class Graph3D:
    def __init__(self, window):
        self.window = window
        self.plot = gl.GLViewWidget()
        #self.plot.setBackgroundColor('white')
        self.plot.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.plot.setWindowTitle('pyqtgraph example: GLViewWidget')
        self.vx, self.vy, self.vz = 0, 0, 0 # to store last vertex
        self.window.layout.addWidget(self.plot)
        self.plots = []
        self.count = 0
        self.color = ('r','g','b','y')

    def connect(self, x, y, z):
        plot = {
          'x': x,
          'y': y,
          'z': z,
          'color': None,
          'gl_item': None,
          'x_data': [],
          'y_data': [],
          'z_data': []
         }

        self.plots.append(plot)
        return plot

    def set_plot(self, plot_type, plot, **kwargs):
        color = kwargs.get('color')
        if color:
            if isinstance(color, str):
                color = pg.glColor(color)
            elif isinstance(color, (tuple, list)):
                color = pg.glColor(*color)
        else:
            color = pg.glColor(self.color[self.count % len(self.color)])

        plot['color'] = color

        if plot_type == 'scatter':
            size = kwargs.get('size', 2)
            gl_item = gl.GLScatterPlotItem(pos=np.empty((0, 3)), size=size, color=pg.glColor(color))
        elif plot_type == 'line':
            width = kwargs.get('width', 1)
            gl_item = gl.GLLinePlotItem(pos=np.empty((0, 3)), width=width, color=pg.glColor(color))

        self.count += 1
        plot['gl_item'] = gl_item
        self.plot.addItem(gl_item)

    def update(self):
        for plot in self.plots:
            if plot['gl_item'] is None:
                return
            plot['x_data'].append(plot['x']())
            plot['y_data'].append(plot['y']())
            plot['z_data'].append(plot['z']())

            color = plot['color']
            pos = np.array([plot['x_data'], plot['y_data'], plot['z_data']]).T
            if isinstance(plot['gl_item'], gl.GLScatterPlotItem):
                plot['gl_item'].setData(pos=pos, color=color)
            elif isinstance(plot['gl_item'], gl.GLLinePlotItem):
                plot['gl_item'].setData(pos=pos, color=color, width=3, antialias=True)
class Window:
    instances = []

    @classmethod
    def new(cls):
        instance = cls()
        cls.instances.append(instance)
        return instance

    def __init__(self):
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication([])
        self.window = QMainWindow()
        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        self.window.setCentralWidget(self.widget)
        self.window.setGeometry(QRect(100, 100, 800, 600))
        self.window.show()
        self.graphs = []

        self.splitter = QSplitter(Qt.Orientation.Horizontal, self.window)  # change to Vertical if you prefer
        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        self.splitter.addWidget(self.widget)
        self.legend_widget = QWidget()
        self.legend_layout = QVBoxLayout()
        self.legend_widget.setLayout(self.legend_layout)
        self.legend_scroll_area = QScrollArea()
        self.legend_scroll_area.setWidgetResizable(True)  # make the legend scrollable
        self.legend_scroll_area.setWidget(self.legend_widget)
        self.splitter.addWidget(self.legend_scroll_area)
        self.window.setCentralWidget(self.splitter)

    def add_XYGraph(self, **kwargs):
        graph = GraphXY(self, **kwargs)
        self.layout.addWidget(graph.plot)
        self.graphs.append(graph)
        return graph

    def add_ScatterGraph(self, **kwargs):
        graph = ScatterGraph(self, **kwargs)
        self.layout.addWidget(graph.plot)
        self.graphs.append(graph)
        return graph

    def add_BarGraphXY(self, **kwargs):
        graph = BarGraphXY(self, **kwargs)
        self.layout.addWidget(graph.plot)
        self.graphs.append(graph)
        return graph

    def add_3DGraph(self):
        graph = Graph3D(self)
        return graph

    def update(self):
        for graph in self.graphs:
            graph.update()
        self.app.processEvents()


def update_data_y():
    y_data = random.randint(1, 20)
    x_data = random.randint(1, 20)
    return x_data, y_data


def update_data_x():
    x_data = time.time()
    return x_data


# HOW TO
# create new window -->  fenetre = Window.new()
# Add XY graph to your window --> graph1 = fenetre.add_XYGraph(autoscale=True, tools=["zoom", "selection"])
# possible parameter for graph : max_points=50 : stock only 50 points. If max_point is None, graph stock all points
# To connect your graph with a function : graph.connect(x=[your_function], y=[your_other_function], name=[name_of], color=([red], [green], [blue]))
# [your_other_function] can return a simple int, float but can be a tuple or list (float, int, float) for example (In the last case, graph have 3 traces)
# If your graph have 3 traces, the first one use color and other a random color, but you can specify all by color=[([red1], [green1], [blue1]), ([red2], [green2], [blue2]), ...]
# It's same for the name. pass a list or just name who the program add number.
#
# Each time you update your window, the connected function is called and graph is refresh.
# For update : fenetre.update()



fenetre_tension = Window.new()
U_de_t = fenetre_tension.add_XYGraph(autoscale=True, tools=["zoom", "selection"])
U_de_I = fenetre_tension.add_ScatterGraph(autoscale=True, max_points=50, tools=["zoom"])
U_de_t.connect(x=time.time, y=update_data_y, name="Tension")
#U_de_t.connect(x=time.time, y=update_data_x, name="Tension 2", color='r')
U_de_I.connect(x=update_data_x, y=update_data_y, name="Courant", color=[(0, 255, 0), (255, 0, 0)])

while True:
    fenetre_tension.update()
