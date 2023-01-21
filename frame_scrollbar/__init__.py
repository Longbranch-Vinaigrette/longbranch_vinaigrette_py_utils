from tkinter import *


# Reference:
# https://stackoverflow.com/questions/1844995/how-to-add-a-scrollbar-to-a-window-with-tkinter
class FrameScrollbar:
    """
    # How to use class
    from tkinter import *
    obj = ScrollableFrame(master,height=300 # Total required height of canvas,width=400 # Total width of master)
    objframe = obj.frame
    # use objframe as the main window to make widget
    """
    def __init__(self, master, width, height, column, mouse_scroll=4):
        self.mouse_scroll = mouse_scroll
        self.master = master
        self.height = height
        self.width = width

        # Create mainframe
        self.main_frame = Frame(self.master)
        self.main_frame.grid(column=column, row=0, sticky="e")
        # self.scrollbar.pack(side=RIGHT, fill=Y)

        # Add a scrollbar
        self.scrollbar = Scrollbar(self.main_frame, orient=VERTICAL)
        self.scrollbar.grid(column=0, row=0, sticky="e")
        # self.scrollbar.pack(side=RIGHT, fill=Y)

        # Add a canvas
        self.canvas = Canvas(self.main_frame, yscrollcommand=self.scrollbar.set)
        self.canvas.grid(column=0, row=0, sticky="we")
        # self.canvas.pack(expand=True, fill=BOTH)
        self.scrollbar.config(command=self.canvas.yview)
        self.canvas.bind(
            '<Configure>',
            lambda e:
                self.canvas.configure(
                    scrollregion=self.canvas.bbox("all")
                )
        )

        # Frame
        self.frame = Frame(self.canvas, width=self.width, height=self.height)
        self.frame.grid(column=0, row=0, sticky="we")
        # expand=bool - expand widget if parent size grows
        # fill=NONE or X or Y or BOTH - fill widget if widget grows
        # self.frame.pack(expand=True, fill=BOTH)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        # When the mouse enters the widget
        self.frame.bind("<Enter>", self.entered)
        # When the mouse leaves the widget
        self.frame.bind("<Leave>", self.left)

    def _on_mouse_wheel(self, event):
        """When the mouse wheel is scrolling"""
        self.canvas.yview_scroll(-1 * int((event.delta / 120)), "units")

    def entered(self, event):
        """When the mouse enters bind MouseWheel"""
        if self.mouse_scroll:
            self.canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)

    def left(self, event):
        """When the mouse leaves unbind MouseWheel"""
        if self.mouse_scroll:
            self.canvas.unbind_all("<MouseWheel>")
