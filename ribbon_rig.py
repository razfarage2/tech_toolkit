import maya.cmds as cmds
import maya.mel as mel


class RibbonRigUI:
    def __init__(self):
        self.prefix = "ribbon_"

    def build_ui(self, parent_layout):
        cmds.setParent(parent_layout)
        cmds.columnLayout(
            adjustableColumn=True, rowSpacing=10, columnOffset=["left", 5]
        )

        cmds.text(l="Flexible Ribbon Settings", fn="boldLabelFont", al="left")
        self.rib_prefix = cmds.textFieldGrp(
            l="Prefix:", text=self.prefix, cl2=["left", "left"], ad2=2
        )
        self.width_field = cmds.floatFieldGrp(
            l="Total Width:", value1=2.5, cl2=["left", "left"], ad2=2
        )
        self.ratio_field = cmds.floatFieldGrp(
            l="Height/Thickness:", value1=0.2, cl2=["left", "left"], ad2=2
        )
        self.u_patches = cmds.intSliderGrp(
            l="U Patches:",
            field=True,
            min=1,
            max=50,
            v=8,
            cl3=["left", "left", "left"],
            ad3=3,
        )

        self.axis_field = cmds.radioButtonGrp(
            label="Plane Normal:",
            labelArray3=["X", "Y", "Z"],
            select=3,
            numberOfRadioButtons=3,
            cl4=["left", "left", "left", "left"],
        )

        cmds.separator(h=5)
        cmds.button(l="Generate Ribbon", c=self.build_ribbon, bgc=[0.2, 0.5, 0.8], h=40)

    def build_ribbon(self, *args):
        prefix = cmds.textFieldGrp(self.rib_prefix, q=True, text=True)
        w = cmds.floatFieldGrp(self.width_field, q=True, v1=True)
        lr = cmds.floatFieldGrp(self.ratio_field, q=True, v1=True)
        u = cmds.intSliderGrp(self.u_patches, q=True, v=True)
        ax_idx = cmds.radioButtonGrp(self.axis_field, q=True, select=True)

        axis_map = {1: (1, 0, 0), 2: (0, 1, 0), 3: (0, 0, 1)}
        plane_normal = axis_map[ax_idx]

        mesh = cmds.nurbsPlane(
            p=(0, 0, 0),
            ax=plane_normal,
            w=w,
            lr=lr,
            d=3,
            u=u,
            v=1,
            ch=1,
            n=f"{prefix}mesh",
        )[0]

        num_jnts = u + 1
        cmds.select(mesh)
        mel.eval(f"createHair {num_jnts} 1 10 0 0 1 0 5 0 1 2 1;")

        fol_grp = cmds.rename(cmds.ls("*Follicles")[-1], f"{prefix}follicle_GRP")
        follicles = cmds.listRelatives(fol_grp, c=True, f=True)

        for i, fol in enumerate(follicles):
            curves = cmds.listRelatives(fol, type="transform", f=True)
            if curves:
                cmds.delete(curves)
            cmds.select(cl=True)
            jnt = cmds.joint(n=f"{prefix}bind_{i+1:02d}_JNT", rad=lr * 0.5)
            cmds.parent(jnt, fol)
            cmds.setAttr(f"{jnt}.translate", 0, 0, 0)
            cmds.setAttr(f"{jnt}.rotate", 0, 0, 0)

        cmds.delete(cmds.ls("hairSystem*", "nucleus*", "pfxHair*", type="transform"))

        # --- ATTACH CONTROLS TO FOLLICLE JOINTS ---
        ctrl_names = ["base_CTRL", "mid_CTRL", "tip_CTRL"]
        ctrl_radius = (w * lr) * 1.5

        # Get all bind joints from follicle group
        all_bind_jnts = []
        for fol in follicles:
            bind_jnt = cmds.listRelatives(fol, type="joint", f=True)
            if bind_jnt:
                all_bind_jnts.append(bind_jnt[0])

        # Select key joints: first, middle, last
        num_bind_jnts = len(all_bind_jnts)
        mid_idx = num_bind_jnts // 2
        key_indices = [0, mid_idx, num_bind_jnts - 1]

        ctrl_jnts = []

        # Determine circle normal based on plane normal
        if ax_idx == 1:
            circle_normal = (0, 1, 0)
        elif ax_idx == 2:
            circle_normal = (1, 0, 0)
        else:
            circle_normal = (1, 0, 0)

        for i, idx in enumerate(key_indices):
            bind_jnt = all_bind_jnts[idx]

            # Get position and orientation from bind joint
            pos = cmds.xform(bind_jnt, q=True, ws=True, t=True)
            rot = cmds.xform(bind_jnt, q=True, ws=True, ro=True)

            # Create control joint at same position/orientation
            cmds.select(cl=True)
            ctrl_jnt = cmds.joint(n=f"{prefix}ctrl_JNT_{i+1:02d}", rad=lr * 0.8)
            cmds.xform(ctrl_jnt, ws=True, t=pos)
            cmds.xform(ctrl_jnt, ws=True, ro=rot)
            ctrl_jnts.append(ctrl_jnt)

            # Create control circle
            circle = cmds.circle(
                n=f"{prefix}{ctrl_names[i]}", r=ctrl_radius, nr=circle_normal
            )[0]
            cmds.xform(circle, ws=True, t=pos)
            cmds.xform(circle, ws=True, ro=rot)
            cmds.makeIdentity(circle, apply=True, t=1, r=1, s=1)

            # Parent control joint to circle
            cmds.parent(ctrl_jnt, circle)

        cmds.skinCluster(ctrl_jnts, mesh, tsb=True, mi=2)
        print(
            f"✓ {prefix} Ribbon Complete. Controls placed at joints: 1, {mid_idx+1}, {num_bind_jnts}"
        )
