import numpy as np
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets import gui
from orangecontrib.network import Network
from orangewidget.settings import Setting
import numpy as np


class Recommendation(OWWidget):
    name = "Recommendation System 1"
    description = "Recommend cartoons for kids"
    icon = "icons/recommendation.png"
    category = "Recommendation"

    class Inputs:
        image = Input("Network", Network)

    kid = Setting(0)
    explanation = Setting(0)
    def __init__(self):
        super().__init__()

        gui.comboBox(self.controlArea, self, "kid", box="Kid",
                     items=["kid1", "kid2", "kid3", "kid4", "kid5", "kid6", "kid7", "kid8", "kid9", "kid10"],
                     callback=self.update_recommendation)
        gui.label(self.controlArea, self, label="Cartoons list", box="Cartoons", orientation="horizontal")
        gui.label(self.controlArea, self, label="Friends list", box="Friends", orientation="horizontal")

        gui.listView(self.mainArea, self, "all_recommendations", box="Recommendations", callback=self.update_recommendation)
        gui.label(self.mainArea, self, "here we give explanations", box="Explanation",)


    def all_kids(self):
        return "abc"
        # lines = open("cartoons_table/kids_cartoons.csv").readlines()
        # self.kids = np.array([row.split(';')[0] for row in lines[1:]])


    def update_recommendation(self):
        return "abc"


if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview
    WidgetPreview(Recommendation).run()

