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
    description = "Recommend cartoons for kids"
    icon = "icons/recommendation.png"
    category = "Recommendation"

    class Inputs:
        network = Input("Network", Network, default=True)

    kid = settings.ContextSetting(None)
    explanation = Setting(0)
    node_name = settings.ContextSetting(None)
    want_control_area = False

    resizing_enabled = False

    def __init__(self):
        super().__init__()
        self.network: Network = None
        self.cartoons_list_label = None
        self.friends_list_label = None

        box = gui.hBox(self.mainArea)
        box2 = gui.vBox(box, "👧🏽🧒🏽Node")
        self.node_name_model = DomainModel(valid_types=Orange.data.StringVariable)
        gui.comboBox(
            box2, self, "node_name", label="Name column: ",
            model=self.node_name_model, callback=self.set_value_list, orientation=Qt.Horizontal)

        self.nodes_model = PyListModel()
        gui.comboBox(
            box2, self, "kid", label="Name ",
            model=self.nodes_model, contentsLength=10, callback=self.set_friends, orientation=Qt.Horizontal)
        gui.rubber(box2)
        fm = QFontMetrics(self.font())
        size = QSize(40 * fm.averageCharWidth(), 5 * fm.height())
        self.cartoons_list_label = gui.label(box, self, label="cartoons", box="Cartoons🦆🪿", minimumSize=size)
        self.friends_list_label = gui.label(self.mainArea, self, label="Friends list", box="Friends🤹🏼‍♀️🤹🏼",
                                            minimumSize=size)

        box3 = gui.hBox(self.mainArea, "Recommendations🏆")
        self.rec = gui.widgetLabel(box3, minimumSize=QSize(40 * fm.averageCharWidth(), 5 * fm.height()))

    @Inputs.network
    def set_network(self, network):
        self.network = network
        self.node_name_model.set_domain(network.nodes.domain)

        if self.node_name_model:
            self.node_name = self.node_name_model[0]
        self.set_value_list()
        self.set_friends()
        self.set_cartoons()

    def set_value_list(self):
        if self.node_name is None:
            self.nodes_model.clear()
        else:
            self.nodes_model[:] = self.network.nodes.get_column(self.node_name)

    def set_friends(self):
        if self.node_name is None:
            self.friends_list_label.setText("No friends")
            return
        names = self.network.nodes.get_column(self.node_name)
        idx = np.where(names == self.kid)[0]
        if len(idx) == 0:
            return
        neighbours = self.network.neighbours(idx[0])
        neighbours_names = names[neighbours]
        # print("neighbours names: ", neighbours_names)

        # self.friends_list_label.setText("<ul style='font-size: 12px; list-style-type: lower-roman;'>" + "".join([
        # "<li>" + name + "</li>" for name in neighbours_names]) + "</ul>")
        self.friends_list_label.setText(
            "<ul style='font-size: 12px; list-style-type: none;'>" +
            "".join(["<li>🍀 " + name + "</li>" for name in neighbours_names]) +
            "</ul>"
        )
        self.set_cartoons()
        # self.recommendations()
        # print("node_name", self.kid)
        # print("nodes", self.network.nodes)
        # print("nodes type", type(self.network.nodes))
        # print("nodes domain", self.network.nodes.domain)
        # get row names - cartoons from network nodes

    def set_cartoons(self):
        names = self.network.nodes.get_column(self.node_name)
        id_list = np.where(names == self.kid)[0]

        if len(id_list) == 0:
            return
        idx = id_list[0]

        if self.network.nodes.domain is None:
            self.cartoons_list_label.setText("No cartoons")
        else:
            node_string = str(self.network.nodes[idx])

            list_with_node_name = re.findall(r'{.*?}', node_string)[0][1:-1]
            enumerated_cartoons = enumerate(map(int, re.findall(r'\[.*\]', node_string)[0][1:-1].split(',')))

            all_cartoons = [idx for idx, val in enumerated_cartoons if val == 1]

            if self.kid == list_with_node_name:
                cartoons_names = [self.network.nodes.domain[i].name for i in all_cartoons]

                self.cartoons_list_label.setText(
                    "<ul style='font-size: 12px; list-style-type: none;'>" +
                    "".join(["<li>🎭 " + cartoon + "</li>" for cartoon in cartoons_names]) +
                    "</ul>"
                )

    def recommendations(self):
        names = self.network.nodes.get_column(self.node_name)
        id_list = np.where(names == self.kid)[0]
        if len(id_list) == 0:
            return
        idx = id_list[0]

        node_string = str(self.network.nodes[idx])
        list_of_cartoons = re.findall(r'\[([\d,\s]*)\]', node_string)
        cartoons_names = [self.network.nodes.domain[i].name for i in range(len(list_of_cartoons)) if
                          list_of_cartoons[i] == 1]

        list_of_cartoons = re.findall(r'\[([\d,\s]*)\]', node_string)
        list_with_node_name = re.findall(r'{.*?}', node_string)[0][1:-1]
        print("list_with_node_name: ", list_with_node_name)
        print("list_of_cartoons: ", list_of_cartoons)

        neighbours = self.network.neighbours(idx)

        all_kids = self.network.nodes.get_column(self.node_name)
        that_neighbour = all_kids[neighbours[0]]

        # Find cartoons that the neighbors have watched but the selected kid has not watched yet
        for i in range(len(neighbours)):

            that_neighbour = all_kids[neighbours[i]]

            if that_neighbour != self.kid:
                node_string = str(self.network.nodes[i])
                list_of_cartoons = re.findall(r'\[([\d,\s]*)\]', node_string)
                list_with_node_name = re.findall(r'{.*?}', node_string)[0][1:-1]
                print("node_set: ", list_with_node_name)
                print("list_of_cartoons: ", list_of_cartoons)
                if that_neighbour != list_with_node_name:
                    print("yes")
                    neighbour_cartoons_names = [self.network.nodes.domain[i].name for i in range(len(list_of_cartoons))
                                                if
                                                list_of_cartoons[i] == 1]
                    print(f"neighbour_cartoons_names: {neighbour_cartoons_names}")
                    recommendation = list(set(neighbour_cartoons_names) - set(cartoons_names))
                    print("recommendation: ", recommendation)




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
