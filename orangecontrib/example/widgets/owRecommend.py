import numpy as np

import Orange
from Orange.data import Table
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets import gui
from orangecontrib.network import Network
from orangewidget.settings import Setting


class Recommendation(OWWidget):
    name = "Recommendation System 1"
    description = "Recommend cartoons for kids"
    icon = "icons/recommendation.png"
    category = "Recommendation"

    class Inputs:
        node_data = Input("Node Data", Table)
        node_subset = Input("Node Subset", Table)
        network = Input("Network", Network, default=True)
        node_distances = Input("Node Distances", Orange.misc.DistMatrix)

    kid = Setting(0)
    explanation = Setting(0)

    def __init__(self):
        super().__init__()
        self.node_data = None
        self.node_subset = None
        self.network = None
        self.node_distances = None

        gui.comboBox(self.controlArea, self, "kid", box="Kid", items=Table.get_column(self.node_data, 0))
        gui.label(self.controlArea, self, label="Cartoons list", box="Cartoons", orientation="horizontal")
        gui.label(self.controlArea, self, label="Friends list", box="Friends", orientation="horizontal")

        gui.listView(self.mainArea, self, "all_recommendations", box="Recommendations")
        gui.label(self.mainArea, self, "here we give explanations", box="Explanation", )

    @Inputs.node_data
    def set_node_data(self, node_data):
        self.node_data = node_data

    @Inputs.node_subset
    def set_node_subset(self, node_subset):
        self.node_subset = node_subset

    @Inputs.network
    def set_network(self, network):
        self.network = network

    @Inputs.node_distances
    def set_node_distances(self, node_distances):
        self.node_distances = node_distances


def main():
    from Orange.widgets.utils.widgetpreview import WidgetPreview
    from orangecontrib.network.network.readwrite \
        import read_pajek
    from os.path import join, dirname

    network = read_pajek(join(dirname(dirname(__file__)), 'networks', 'kids_cartoons.net'))
    WidgetPreview(Recommendation).run(set_network=network)


if __name__ == "__main__":
    main()
