from direct.showbase.ShowBase import ShowBase
from DirectGuiExtension.DirectTreeView import DirectTreeView
import BetterDirectGui

ShowBase()
BetterDirectGui.init(do_keyboard_navigation=False)

DirectTreeView(
    frameSize=[-0.5,0.5, -0.5,0.5],
    autoUpdateFrameSize=False,
    tree={
        "A":{"1":None,"2":None},
        "B":"C"
    })

base.run()
