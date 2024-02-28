import sysconfig
from orangecontrib.network import Network
from orangewidget.utils.signals import summarize, PartialSummary

# Category metadata.

# Category icon show in the menu
ICON = "icons/category.svg"

# Background color for category background in menu
# and widget icon background in workflow.
BACKGROUND = "light-blue"

# Location of widget help files.
WIDGET_HELP_PATH = (
    # Development documentation
    # You need to build help pages manually using
    # make htmlhelp
    # inside doc folder
    ("{DEVELOP_ROOT}/doc/_build/htmlhelp/index.html", None),

    # Documentation included in wheel
    # Correct DATA_FILES entry is needed in setup.py and documentation has to be built
    # before the wheel is created.
    ("{}/help/orange3-example/index.html".format(sysconfig.get_path("data")), None),

    # Online documentation url, used when the local documentation is not available.
    # Url should point to a page with a section Widgets. This section should
    # includes links to documentation pages of each widget. Matching is
    # performed by comparing link caption to widget name.
    ("http://orange3-example-addon.readthedocs.io/en/latest/", "")
)

@summarize.register
def summarize_(net: Network):
    n = net.number_of_nodes()
    e = net.number_of_edges()
    if len(net.edges) == 1:
        directed = net.edges[0].directed
        direct = "➝" if directed else "–"
        nettype = ['Network', 'Directed network'][directed]
        details = f"<nobr>{nettype} with {n} nodes " \
                  f"and {net.number_of_edges()} edges</nobr>."
    else:
        direct = "–"
        details = f"<nobr>Network with {n} nodes"
        if net.edges:
            details += " and {len(net.edges)} edge types:</nobr><ul>" + "".join(
                f"<li>{len(edges)} edges, "
                f"{['undirected', 'directed'][edges.directed]}</li>"
                for edges in net.edges) + "."

    return PartialSummary(f"•{n} {direct}{e}", details)
