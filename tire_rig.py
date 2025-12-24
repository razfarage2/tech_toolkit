import maya.cmds as cmds
import math


class WheelRigUI:
    def __init__(self):
        self.prefix = "lf_fr_"
        self.rig_data = {}

    def build_ui(self, parent_layout):
        cmds.setParent(parent_layout)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=10)

        cmds.text(l="antCGI Tire Pipeline", fn="boldLabelFont")
        self.prefix_field = cmds.textFieldGrp(l="Prefix:", text=self.prefix)
        self.ground_field = cmds.textFieldGrp(l="Ground Mesh:", text="floor")

        cmds.separator(h=5)
        cmds.button(l="1. Build Skeleton", c=self.build_skeleton, bgc=[0.4, 0.5, 0.8])
        cmds.button(l="2. Add Rotation", c=self.rotation, bgc=[0.8, 0.5, 0.4])
        cmds.button(l="3. Apply antCGI Logic", c=self.apply_logic, bgc=[0.2, 0.6, 0.4])

    def get_proportions(self, mesh):
        bbox = cmds.exactWorldBoundingBox(mesh)
        center = [
            (bbox[0] + bbox[3]) / 2,
            (bbox[1] + bbox[4]) / 2,
            (bbox[2] + bbox[5]) / 2,
        ]
        radius = bbox[4] - center[1]
        return center, radius

    def build_skeleton(self, *args):
        sel = cmds.ls(sl=True)
        if not sel:
            return
        self.prefix = cmds.textFieldGrp(self.prefix_field, q=True, text=True)
        center, radius = self.get_proportions(sel[0])

        top = cmds.group(em=True, n=f"{self.prefix}rig_GRP")
        root = cmds.circle(n=f"{self.prefix}root_CTRL", r=radius * 1.3, nr=(0, 1, 0))[0]
        cmds.xform(root, ws=True, t=(center[0], 0, center[2]))
        cmds.parent(root, top)

        cmds.select(cl=True)
        hub = cmds.joint(n=f"{self.prefix}hub_JNT", p=center)
        cmds.parent(hub, top)

        for i in range(16):
            angle = (i * 22.5) * (math.pi / 180.0)
            y, z = math.cos(angle) * radius, math.sin(angle) * radius
            cmds.select(hub)
            inner = cmds.joint(
                n=f"{self.prefix}spoke_inner_{i+1:02d}_JNT",
                p=(center[0], center[1] + y, center[2] + z),
            )
            cmds.joint(
                n=f"{self.prefix}spoke_outer_{i+1:02d}_JNT",
                p=(center[0], center[1] + y * 1.05, center[2] + z * 1.05),
            )

        cmds.skinCluster(cmds.ls(f"{self.prefix}spoke_inner_*"), sel[0], tsb=True)
        self.rig_data = {"radius": radius, "prefix": self.prefix}

    def rotation(self, *args):
        p, r = self.rig_data["prefix"], self.rig_data["radius"]
        md = cmds.createNode("multiplyDivide", n=f"{p}rot_MD")
        cmds.connectAttr(f"{p}root_CTRL.translateZ", f"{md}.input1X")
        cmds.setAttr(f"{md}.input2X", 360.0 / (2.0 * math.pi * r))
        cmds.connectAttr(f"{md}.outputX", f"{p}hub_JNT.rotateX")

    def apply_logic(self, *args):
        pass
