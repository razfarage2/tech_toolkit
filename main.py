import maya.cmds as cmds
from . import tire_rig
from . import ribbon_rig
import importlib

importlib.reload(tire_rig)
importlib.reload(ribbon_rig)


class MainToolkit:
    def __init__(self):
        self.window_id = "TechArtistToolkit"
        if cmds.window(self.window_id, exists=True):
            cmds.deleteUI(self.window_id)

        self.tire_tool = tire_rig.WheelRigUI()
        self.ribbon_tool = ribbon_rig.RibbonRigUI()
        self.show_ui()

    def show_ui(self):
        cmds.window(self.window_id, title="Tech Artist Toolkit", widthHeight=(350, 420))
        tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)

        tire_tab = cmds.columnLayout(adjustableColumn=True, p=tabs)
        self.tire_tool.build_ui(tire_tab)

        ribbon_tab = cmds.columnLayout(adjustableColumn=True, p=tabs)
        self.ribbon_tool.build_ui(ribbon_tab)

        cmds.tabLayout(
            tabs,
            edit=True,
            tabLabel=((tire_tab, "Tire Rig"), (ribbon_tab, "Ribbon Rig")),
        )
        cmds.showWindow(self.window_id)


def run():
    MainToolkit()
