from collections import Counter

import numpy as np



from AnyQt.QtCore import Qt, QSize
from AnyQt.QtWidgets import QGridLayout, QLabel
from AnyQt.QtGui import QFontMetrics

from orangewidget.settings import Setting
from orangewidget.utils.itemmodels import PyListModel

import Orange
from Orange.data import Table
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets import gui, settings
from Orange.widgets.utils.itemmodels import DomainModel

from orangecontrib.network import Network
import orangecontrib.network.widgets






class Recommendation(OWWidget):
    name = "orange3-pumice"
    description = "Recommend feature based on selected node"
    icon = "icons/recommendation.png"
    category = "Recommendation"

    class Inputs:
        network = Input("Network", Network, default=True)

    settingsHandler = settings.DomainContextHandler()
    selected_node_hint = settings.ContextSetting(None)
    node_name = settings.ContextSetting(None)
    want_control_area = False

    resizing_enabled = False

    def __init__(self):
        super().__init__()
        self.node_name_id = None
        self.network: Network = None

        self.selected_node = None

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
            model=self.nodes_model, callback=self.on_node_changed)

        align_top = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        grid.addWidget(combo, 0, 0, 1, 2)
        grid.addWidget(QLabel(self, text="<b>Features: </b"), 1, 0, alignment=align_top)
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

        #self.set_value_list()

        #nastavi node name ime ali priimek in hint
        self.openContext(self.network.nodes)
        if self.selected_node_hint \
                and self.selected_node_hint in self.nodes_model:
            self.selected_node = self.selected_node_hint
        self.set_value_list()

        #self.selected_node = (selected_node or
        #                      (self.nodes_model[0]) if self.nodes_model else None)

        self.update()

    def set_value_list(self):
        if self.node_name is None:
            self.nodes_model.clear()
        else:
            self.nodes_model[:] = self.network.nodes.get_column(self.node_name)
            self.selected_node = self.nodes_model[0]

    @property
    def selected_node_index(self):
        return self.nodes_model.indexOf(self.selected_node)

    def on_node_changed(self):
        self.selected_node_hint = self.selected_node
        self.update()

    def update(self):
        self.set_friends()
        self.set_features()
        self.set_recommendations()

    def set_friends(self):

        if self.node_name is None or self.selected_node is None:
            self.friends_list_label.setText("No friends")
            return

        sorted_data = self.sort_node_weights()
        neighbours_names = [self.nodes_model[row[1]] for row in sorted_data]

        self.friends_list_label.setText(", ".join(neighbours_names))

    def set_features(self):
        if self.node_name is None or self.selected_node is None:
            features_names = []
        else:
            node_choices = self.network.nodes.X[self.selected_node_index]
            attributes = self.network.nodes.domain.attributes
            chosen = np.flatnonzero(node_choices)
            features_names = [attributes[i].name for i in chosen]

        self.features_list_label.setText(", ".join(features_names) or "No features")

    def set_recommendations1(self):
        if self.node_name is None or self.selected_node is None:
            self.recommendations_label.setText("No recommendations")
            return

        attributes = self.network.nodes.domain.attributes

        neighbours_indices = self.network.neighbours(self.selected_node_index)

        neighbours_choices = self.network.nodes.X[neighbours_indices]

        chosen_neighbours = [np.flatnonzero(neighbour) for neighbour in neighbours_choices]

        all_features_names = [attributes[i].name for neighbours_array in chosen_neighbours for i in neighbours_array]

        counter = Counter(all_features_names)

        recommendations = counter.most_common(5)

        output = "<dl>"
        for feature, count in recommendations:
            recommending_nodes = [neighbour for i, neighbour in enumerate(neighbours) for index in chosen_neighbours[i]
                                  if attributes[index].name == feature]
            output += f"<dt>{feature}</dt>"
            output += f"<dd> {', '.join(recommending_nodes)}</dd>"
        output += "</dl>"

        self.rec.setText(output)

    def set_recommendations(self):
        # get neighbour indicises from matrix
        if self.node_name is None or self.selected_node is None:
            self.rec.setText("No recommendations")
            return

        # TODO: list(set()) je tu zato, ker se sosedje ponavljajo
        neighbours_indices = list(set(self.network.neighbours(self.selected_node_index)))
        print("neighbours_indices", neighbours_indices)
        neighbours_choices = self.network.nodes.X[neighbours_indices]
        print("neighbours_choices", neighbours_choices)

        counts = np.sum(neighbours_choices, axis=0)
        sorted_features = np.argsort(counts)[::-1]
        most_freq = sorted_features[:5]
        print("most_freq", most_freq)
        recommended_names = [self.network.nodes.domain.attributes[i].name for i in most_freq]
        print("self.netowrk.nodes.get_column(self.node_name)", self.network.nodes.get_column(self.node_name))
        recommenders_for_feature = [self.network.nodes.get_column(self.node_name)[neighbours_indices][neighbours_choices[:, i] == 1] for i in most_freq]

        print("recommended_names", recommended_names)
        print("recommenders_for_feature", recommenders_for_feature)

        output = "<dl>"
        for feature, recommenders in zip(recommended_names, recommenders_for_feature):
            output += f"<dt>{feature}</dt>"
            output += f"<dd> {', '.join(recommenders)}</dd>"
        output += "</dl>"
        self.rec.setText(output)



    def sort_node_weights(self):
        if self.node_name is None or self.selected_node is None:
            return "No node selected"

        self.weights = self.network.edges[0].edges.tocoo()
        print(self.weights)
        #print(self.weights.row, self.weights.col, self.weights.data)
        rows_for_node = [(i, j, value) for i, j, value in zip(self.weights.row, self.weights.col, self.weights.data) if

        # to je isto kot m = self.weights.row == self.selected_node_index
        # kako iz mreže uteži dobit, a se da soritrat z argmax?
                         i == self.selected_node_index]
        sorted_data = sorted(rows_for_node, key=lambda x: x[2], reverse=True)

        return sorted_data


def main():
    from Orange.widgets.utils.widgetpreview import WidgetPreview
    from orangecontrib.network.network.readwrite \
        import read_pajek
    from os.path import join, dirname


    table = Table(join(dirname(dirname(__file__)), 'networks', 'kids_cartoons_new_real_names_real_cartoons.xlsx'))
    network = read_pajek(join(dirname(dirname(__file__)), 'networks', 'real_names_real_cartoons.net'))
    network.nodes = table
    WidgetPreview(Recommendation).run(set_network=network)


if __name__ == "__main__":
    main()
