from tkinter import *


class DialogBox:
    accept_command = None
    cancel_command = None

    def __init__(
            self,
            parent,
            name: str,
            description: str,
            accept_command=None,
            cancel_command=None,
        ):
        """
        description = <str> Dialog description
        """
        self.accept_command = accept_command
        self.cancel_command = cancel_command

        self.window = Toplevel(parent)
        self.window.title(name)
        self.window.option_add('*tearOff', FALSE)

        # Description
        description = Label(self.window, text=description)
        description.grid(column=0, row=0)

        # Buttons
        cancel_button = Button(
            self.window,
            text="Cancel",
            command=self.cancel)
        cancel_button.grid(column=0, row=1, sticky="sw")

        accept_button = Button(
            self.window,
            text="Accept",
            command=self.accept)
        accept_button.grid(column=1, row=1, sticky="se")

        ## Set focus
        # None of these mfs could do the work
        # window.focus_get()
        # window.focus_force()
        # window.after(1, lambda: window.focus_force())
        # window.after(2, lambda: window.focus_force())
        # window.after(3, lambda: window.focus_force())
        # This is the only one that works
        # Reference:
        # https://stackoverflow.com/questions/22751100/tkinter-main-window-focus
        # This thing didn't work for that person but for me, it does somehow)?
        self.window.wm_attributes("-topmost", -1)

    def accept(self):
        """Called when the accept button is clicked"""
        if self.accept_command is not None:
            self.accept_command()
        self.window.destroy()

    def cancel(self):
        """Called when the cancel button is clicked"""
        if self.cancel_command is not None:
            self.cancel_command()
        self.window.destroy()
