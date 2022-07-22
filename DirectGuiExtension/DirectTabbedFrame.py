"""This module contains the DirectTabbedFrame class.

It will create a frame with optionally closable tabs on top to switch between
multiple parented frames
"""

__all__ = ['DirectTabbedFrame']

from uuid import uuid4
from panda3d.core import *
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectRadioButton import DirectRadioButton
from . import DirectGuiHelper as DGH

class DirectTabbedFrame(DirectFrame):
    """
    A frame with tabs
    """
    def __init__(self, parent=None, **kw):
        optiondefs = (
            # Define type of DirectGuiWidget
            # The height of the area to drag the widget around
            ('tabHeight',                   0.1, None),
            ('showCloseOnTabs',            True, None),
            ('frameSize',           (-1,1,-1,1), None),
            )
        # Merge keyword options with default options
        self.defineoptions(kw, optiondefs)

        # Initialize superclasses
        DirectFrame.__init__(self, parent)

        # Call option initialization functions
        self.initialiseoptions(DirectTabbedFrame)

        pos_x = self['frameSize'][0]
        pos_z = self['frameSize'][3]-self['tabHeight']/2
        self.prevTabButton = self.createcomponent(
            'prevTabButton', (), 'prevTabButton',
            DirectButton,
            (self,),
            text='<',
            text_align=TextNode.ALeft,
            scale=self['tabHeight'],
            borderWidth=(0,0),
            pressEffect=False,
            pos=(pos_x, 0, pos_z),
            frameSize=(0,0.7,-0.5,0.5),
            text_pos=(0.1, -0.25),
            command=self.show_prev_tab,
        )

        pos_x = self['frameSize'][1]
        self.nextTabButton = self.createcomponent(
            'nextTabButton', (), 'nextTabButton',
            DirectButton,
            (self,),
            text='>',
            text_align=TextNode.ARight,
            scale=self['tabHeight'],
            borderWidth=(0,0),
            pressEffect=False,
            pos=(pos_x, 0, pos_z),
            frameSize=(-0.7,0,-0.5,0.5),
            text_pos=(-0.1, -0.25),
            command=self.show_next_tab,
        )

        self.tab_index_from = 0
        self.tab_index_to = 0

        self.tab_list = []
        self.selected_content = [None]
        self.current_content = None
        self.start_idx = 0

    def show_prev_tab(self):
        if self.start_idx > 0:
            self.start_idx -= 1
            self.reposition_tabs()

    def show_next_tab(self):
        if self.start_idx < len(self.tab_list) - 1:
            self.start_idx += 1
            self.reposition_tabs()

    def add_tab(self, tab_text, content):
        # create the new tab
        tab = self.createcomponent(
            'tab', (), 'tab',
            DirectRadioButton,
            (self,),
            text=tab_text,
            text_align=TextNode.ALeft,
            scale=self['tabHeight'],
            boxPlacement='right',
            command=self.switch_tab,
            variable=self.selected_content,
            value=[0]
            )
        # hide the radio button indicator
        tab.indicator.hide()
        tab['value'] = [content]
        # hide the tabs content by default
        content.hide()

        # get some details for the close button
        tab_height = DGH.getRealHeight(tab)
        x_pos = tab.indicator.get_pos()
        x_pos.z = (tab_height - tab['borderWidth'][1]) / 2

        # create the close button
        closeButton = self.createcomponent(
            'closeButton', (), 'closeButton',
            DirectButton,
            (tab,),
            text='x',
            pos=x_pos,
            command=self.close_tab,
            extraArgs=[tab],
        )

        # add the tab to our list
        self.tab_list.append(tab)

        # reposition all tabs
        self.reposition_tabs()

        # update all tabs with the new list
        for other_tab in self.tab_list:
            other_tab.setOthers(self.tab_list)

    def switch_tab(self):
        if self.current_content:
            self.current_content.hide()
        self.current_content = self.selected_content[0]
        if self.current_content:
            self.current_content.show()

    def close_tab(self, tab):
        # get the tabs index
        deleted_tab_idx = self.tab_list.index(tab)

        # store if it was the currently opened tab
        was_checked = tab['indicatorValue']

        # actually remove the tab from list and rendering
        del self.tab_list[deleted_tab_idx]
        if self.current_content == tab['value'][0]:
            self.current_content.hide()
            self.current_content = None
        tab.destroy()

        # update the other tabs with the new list
        for other_tab in self.tab_list:
            other_tab.setOthers(self.tab_list)

        # check tab selection
        if self.start_idx >= len(self.tab_list):
            # last tab was deleted, move forward a bit
            self.start_idx = len(self.tab_list) - 1
            if len(self.tab_list) > 0 and was_checked:
                self.select_tab(self.tab_list[-1])
        elif len(self.tab_list) >= deleted_tab_idx and was_checked:
            # select the new tab at that position, if we have any
            self.select_tab(self.tab_list[deleted_tab_idx])
        elif len(self.tab_list) > 0 and was_checked:
            # select the last available tab
            self.select_tab(self.tab_list[0])

        # reposition the existing tabs
        self.reposition_tabs()

    def reposition_tabs(self):
        # store some information we use in the repositioning
        next_x = DGH.getRealWidth(self.prevTabButton)
        show_tab = True
        next_button_width = DGH.getRealWidth(self.nextTabButton)

        # hide all tabs by default, they will be shown if they fit on the tab
        # list and are actually in the range of to be shown tabs
        for tab in self.tab_list:
            tab.hide()

        # move through all tabs, starting from the desired start index
        for tab in self.tab_list[self.start_idx:]:
            border_width = tab['borderWidth'][0]*tab['scale']
            tab_bottom = DGH.getRealBottom(tab)
            tab_width = DGH.getRealWidth(tab)

            fs = self['frameSize']

            if fs[0] + next_x + tab_width > fs[1] - next_button_width:
                # this tab doesn't fit anymore, skip it and the next
                show_tab = False

            if not show_tab:
                continue

            # show this tab
            tab.show()
            # calculate the new position and place it there
            tab_pos = (
                fs[0]+next_x+border_width,
                0,
                fs[3]-tab_bottom-self['tabHeight'])
            tab.set_pos(tab_pos)

            # calculate the X start position shift for the next tab
            next_x += tab_width

    def select_tab(self, tab):
        tab.commandFunc(None)