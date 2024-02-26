import numpy as np

from collections import Counter

from AnyQt.QtCore import Qt, QSize
from AnyQt.QtWidgets import QGridLayout, QLabel
from AnyQt.QtGui import QFontMetrics

import Orange
from Orange.data import Table
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets import gui, settings
from Orange.widgets.utils.itemmodels import DomainModel

from orangecontrib.network import Network

from orangewidget.settings import Setting
from orangewidget.utils.itemmodels import PyListModel


class Recommendation(OWWidget):
    name = "Recommendation System 👍"
    description = "Recommend feature based on selected node"
    icon = "icons/recommendation.png"
    category = "Recommendation"

    class Inputs:
        network = Input("Network", Network, default=True)

    settingsHandler = settings.DomainContextHandler()
    selected_node = settings.ContextSetting(None)
    node_name = settings.ContextSetting(None)
    number_of_recommendations = Setting(0)
    want_control_area = False

    resizing_enabled = False

    def __init__(self):
        super().__init__()
        self.node_name_id = None
        self.network: Network = None
        self.weights = None

        self.node_name_model = DomainModel(valid_types=Orange.data.StringVariable)
        gui.comboBox(
            self.mainArea, self, "node_name", label="Name column: ", box=True,
            model=self.node_name_model, callback=self.set_value_list,
            orientation=Qt.Horizontal)

        grid = QGridLayout()
        gui.widgetBox(self.mainArea, "Node", orientation=grid)
        self.nodes_model = PyListModel()
        combo = gui.comboBox(
            None, self, "selected_node",
            model=self.nodes_model, callback=self.set_friends)

        align_top = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        grid.addWidget(combo, 0, 0, 1, 2)
        grid.addWidget(QLabel(self, text="<b>Cartoons: </b"), 1, 0, alignment=align_top)
        self.features_list_label = QLabel(self, wordWrap=True)
        grid.addWidget(self.features_list_label, 1, 1)
        grid.addWidget(QLabel(self, text="<b>Friends: </b"), 2, 0, alignment=align_top)
        self.friends_list_label = QLabel(self, wordWrap=True)
        grid.addWidget(self.friends_list_label, 2, 1)

        fm = QFontMetrics(self.font())
        box3 = gui.hBox(self.mainArea, "Recommendations")
        self.rec = gui.widgetLabel(box3, minimumSize=QSize(40 * fm.averageCharWidth(), 5 * fm.height()), wordWrap=True)

    @Inputs.network
    def set_network(self, network):
        self.closeContext()

        self.network = network
        self.node_name_model.set_domain(network.nodes.domain)

        if self.node_name_model:
            self.node_name = self.node_name_model[0]

        self.controls.node_name.box.setHidden(len(self.node_name_model) < 2)

        self.set_value_list()

        self.openContext(self.network.nodes)
        self.weights = self.network.edges[self.selected_node_index].edges.tocoo()

        self.set_friends()
        self.set_features()

    def set_value_list(self):
        if self.node_name is None:
            self.nodes_model.clear()
        else:
            self.nodes_model[:] = self.network.nodes.get_column(self.node_name)
            self.selected_node = self.nodes_model[0]

    @property
    def selected_node_index(self):
        return self.nodes_model.indexOf(self.selected_node)

    def find_neighbours(self):
        neighbours = self.network.neighbours(self.selected_node_index)
        return self.network.nodes.get_column(self.node_name)[neighbours]

    def get_features_for_node(self):
        voted_features = np.flatnonzero(self.network.nodes.X[self.selected_node_index])
        return voted_features

    def set_friends(self):

        if self.node_name is None or self.selected_node is None:
            self.friends_list_label.setText("No friends")
            return

        sorted_data = self.sort_node_weights()
        neighbours_names_sorted = [self.nodes_model[row[1]] for row in sorted_data]

        neighbours_names = self.find_neighbours()
        neighbours_names_unsorted = [neighbour for neighbour in neighbours_names if
                                     neighbour not in neighbours_names_sorted]

        neighbours_names_combined = neighbours_names_sorted + neighbours_names_unsorted

        self.friends_list_label.setText(", ".join(neighbours_names_combined))

        self.set_features()
        self.set_recommendations()

    def set_features(self):
        if self.node_name is None or self.selected_node is None:
            self.features_list_label.setText("No features")
            return

        node_choices = self.network.nodes.X[self.selected_node_index]

        attributes = self.network.nodes.domain.attributes

        chosen = np.flatnonzero(node_choices)

        features_names = [attributes[i].name for i in chosen]

        self.features_list_label.setText(", ".join(features_names))

    def set_recommendations(self):
        if self.node_name is None or self.selected_node is None:
            self.recommendations_label.setText("No recommendations")
            return

        attributes = self.network.nodes.domain.attributes

        neighbours = self.find_neighbours()

        neighbours_indices = [self.nodes_model.indexOf(neighbour) for neighbour in neighbours]

        neighbours_choices = self.network.nodes.X[neighbours_indices]

        chosen_neighbours = [np.flatnonzero(neighbour) for neighbour in neighbours_choices]

        all_features_names = [attributes[i].name for neighbours_array in chosen_neighbours for i in neighbours_array]

        counter = Counter(all_features_names)

        recommendations = counter.most_common(5)

        output = "<dl>"
        for cartoon, count in recommendations:
            recommending_nodes = [neighbour for i, neighbour in enumerate(neighbours) for index in chosen_neighbours[i]
                                  if attributes[index].name == cartoon]
            output += f"<dt>{cartoon}</dt>"
            output += f"<dd> {', '.join(recommending_nodes)}</dd>"
        output += "</dl>"

        self.rec.setText(output)

    def sort_node_weights(self):
        if self.node_name is None or self.selected_node is None:
            return "No node selected"

        rows_for_node = [(i, j, value) for i, j, value in zip(self.weights.row, self.weights.col, self.weights.data) if
                         i == self.selected_node_index]
        sorted_data = sorted(rows_for_node, key=lambda x: x[2], reverse=True)

        return sorted_data


def main():
    from Orange.widgets.utils.widgetpreview import WidgetPreview
    from orangecontrib.network.network.readwrite \
        import read_pajek
    from os.path import join, dirname

    table = Table(join(dirname(dirname(__file__)), 'networks', 'kids_cartoons_new.xlsx'))
    network = read_pajek(join(dirname(dirname(__file__)), 'networks', 'kids_cartoons_3.net'))
    network.nodes = table
    WidgetPreview(Recommendation).run(set_network=network)


if __name__ == "__main__":
    main()
