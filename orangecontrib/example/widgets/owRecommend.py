import numpy as np

import Orange
from Orange.data import Table
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets import gui, settings
from orangecontrib.network import Network
from orangewidget.settings import Setting
from orangewidget.utils.itemmodels import PyListModel


class Recommendation(OWWidget):
    name = "Recommendation System 1"
    description = "Recommend cartoons for kids"
    icon = "icons/recommendation.png"
    category = "Recommendation"

    class Inputs:
        network = Input("Network", Network, default=True)

    kid = settings.ContextSetting(None)
    explanation = Setting(0)

    def __init__(self):
        super().__init__()
        self.network: Network  = None
        self.cartoons_list_label = None
        self.friends_list_label = None

        self.nodes_model = PyListModel()
        value_combo = gui.comboBox(
            self.controlArea, self, "kid", label="Kid: ",
            model=self.nodes_model, contentsLength=10, callback=self.set_friends)

        gui.label(self.controlArea, self, label="Cartoons asdf", box="Cartoons", orientation="horizontal")
        self.friends_list_label =gui.label(self.controlArea, self, label="Friends list", box="Friends", orientation="horizontal")

        gui.listView(self.mainArea, self, "all_recommendations", box="Recommendations")
        gui.label(self.mainArea, self, "here we give explanations", box="Explanation", )

    @Inputs.network
    def set_network(self, network):
        self.network = network
        self.set_value_list()
        self.set_friends()

    def set_value_list(self):
        self.nodes_model[:] = self.network.nodes
    def set_friends(self):
        idx = np.where(self.network.nodes == self.kid)[0]
        if len(idx) == 0:
            return
        neighbours = self.network.neighbours(idx[0])
        neighbours_names = [self.network.nodes[i] for i in neighbours]
        self.friends_list_label.setText("\n".join(neighbours_names))


def main():
    from Orange.widgets.utils.widgetpreview import WidgetPreview
    from orangecontrib.network.network.readwrite \
        import read_pajek
    from os.path import join, dirname

    network = read_pajek(join(dirname(dirname(__file__)), 'networks', 'kids_cartoons.net'))
    WidgetPreview(Recommendation).run(set_network=network)


if __name__ == "__main__":
    main()
