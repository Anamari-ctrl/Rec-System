import numpy as np
import re

from AnyQt.QtCore import Qt, QSize
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

    selected_node = settings.ContextSetting(None)
    node_name = settings.ContextSetting(None)
    want_control_area = False

    resizing_enabled = False

    def __init__(self):
        super().__init__()
        self.node_name_id = None
        self.network: Network = None
        self.features_list_label = None
        self.friends_list_label = None

        box = gui.hBox(self.mainArea)
        box2 = gui.vBox(box, "Node")
        self.node_name_model = DomainModel(valid_types=Orange.data.StringVariable)
        gui.comboBox(
            box2, self, "node_name", label="Name column: ",
            model=self.node_name_model, callback=self.set_value_list, orientation=Qt.Horizontal)

        self.nodes_model = PyListModel()
        gui.comboBox(
            box2, self, "selected_node", label="Name ",
            model=self.nodes_model, contentsLength=10, callback=self.set_friends, orientation=Qt.Horizontal)
        gui.rubber(box2)
        fm = QFontMetrics(self.font())
        size = QSize(40 * fm.averageCharWidth(), 5 * fm.height())
        self.features_list_label = gui.label(box, self, label="features", box="Features", minimumSize=size)
        self.friends_list_label = gui.label(self.mainArea, self, label="Friends list", box="Friends",
                                            minimumSize=size)

        box3 = gui.hBox(self.mainArea, "Recommendations")
        self.rec = gui.widgetLabel(box3, minimumSize=QSize(40 * fm.averageCharWidth(), 5 * fm.height()))

    @Inputs.network
    def set_network(self, network):
        self.network = network
        self.node_name_model.set_domain(network.nodes.domain)

        if self.node_name_model:
            self.node_name = self.node_name_model[0]

        self.node_name_id = {node: i for i, node in enumerate(self.network.nodes.get_column(self.node_name))}

        self.set_value_list()
        self.set_friends()
        self.set_features()

    def set_value_list(self):
        if self.node_name is None:
            self.nodes_model.clear()
        else:
            self.nodes_model[:] = self.network.nodes.get_column(self.node_name)

    def find_neighbours(self):
        neighbours = self.network.neighbours(self.node_name_id[self.selected_node])
        return [key for key, value in self.node_name_id.items() if value in neighbours]

    def get_features_for_node(self, node_name):
        voted_features = np.asarray(self.network.nodes[self.node_name_id[node_name]].x, dtype=int)
        return {attr.name for attr, voted in zip(self.network.nodes.domain, voted_features) if voted}

    def set_friends(self):

        if self.node_name is None or self.selected_node is None:
            self.friends_list_label.setText("No friends")
            return

        neighbours_names = self.find_neighbours()

        self.friends_list_label.setText("<ul style='font-size: 12px; list-style-type: circle;'>" + "".join([
            "<li>" + name + "</li>" for name in neighbours_names]) + "</ul>")
        self.set_features()
        self.set_recommendations()

    def set_features(self):
        if self.node_name is None or self.selected_node is None:
            self.features_list_label.setText("No features")
            return

        features_of_a_node = self.get_features_for_node(self.selected_node)

        self.features_list_label.setText("<ul style='font-size: 12px; list-style-type: disc;'>" + "".join([
            "<li>" + name + "</li>" for name in features_of_a_node]) + "</ul>")

    def set_recommendations(self):
        features_to_recommend = set()
        neighbours_names = self.find_neighbours()
        features_of_a_node = self.get_features_for_node(self.selected_node)

        for neighbour in neighbours_names:
            features_of_a_neighbour = self.get_features_for_node(neighbour)
            features_to_recommend.update(features_of_a_neighbour - features_of_a_node)

        self.rec.setText("<ul style='font-size: 12px; list-style-type: disc;'>" + "".join([
            "<li>" + name + "</li>" for name in features_to_recommend]) + "</ul>")


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
