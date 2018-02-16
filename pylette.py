#!/usr/bin/env python3
import logging
import re

import tkinter as tk
from tkinter import messagebox  # , ttk

columns = 0


def arrange_widgets_in_row(widgets):
    map(lambda n, w: w.grid(row=0, column=n), enumerate(widgets))


class HexRGBEntry(tk.Entry):
    """Value from clipboard is placed in it if it is recognized as RGB hex
    """
    width = 9

    def __init__(self, palette):
        self.rgb_value = tk.StringVar()
        self.rgb_value.trace('w', self.on_change)

        super().__init__(palette, textvariable=self.rgb_value)

        self.palette = palette
        self.palette.widgets.append(self)

        self.configure(justify='center', font="Helvetica 16", width=self.width)
        self.bind('<Button-1>', self.on_click)
        self.grid(row=0, column=0)

        self.log = logging.getLogger(self.__class__.__name__)

    def on_click(self, *args):
        try:
            input_from_clipboard = self.clipboard_get()
            if self._validate_rgb(input_from_clipboard):
                self.delete(0, 'end')
                self.log.info('Cleared entry')
                self.insert(0, input_from_clipboard)
                self.log.info('Inserted color from clipboard')
                # self.clipboard_clear()  # decide if it should clear or not
            else:
                messagebox.showinfo('Not RGB!',
                                    'Clipboard does not contain RGB shex code')
        except Exception:  # narrow it down to specific (_tkinter.TclError ?)
            messagebox.showinfo('Empty!', 'Clipboard is empty!')

    def on_change(self, *args):
        val = str(self.rgb_value.get())
        if self._validate_rgb(val):
            self.log.info('Content of entry changed {}'.format(val))
            self.rgb_inserted(val)

    def rgb_inserted(self, rgb_code, *args):
        self.configure(bg=rgb_code,
                       fg=self._invert_rgb(rgb_code))
        self.palette.widgets.append(ColorField(self.palette, rgb_code))

    @staticmethod
    def _validate_rgb(value):
        re_rgb = re.compile(r'#[a-fA-F0-9]{6}$')
        return bool(re_rgb.match(value))

    @staticmethod
    def _invert_rgb(value):
        hex_inv = str.maketrans(
            '0123456789ABCDEF',
            'FEDCBA9876543210')
        return value.upper().translate(hex_inv)


class ColorField(tk.Button):
    def __init__(self, palette=None, color='#ffffff'):
        super().__init__(palette)
        self.palette = palette
        self.configure(width=50, height=50, bg=color)
        self.bind('<Button-1>', lambda _: print('left'))
        self.bind('<Button-1>', lambda _: print('right'))
        self.palette.widgets.append(self)


class Palette(tk.LabelFrame):
    widgets = []
    rgb_entries = []

    def __init__(self, master=None):
        self.master = master
        self.master.widgets.append(self)
        # self.master.palettes.append(self)
        super().__init__(master)
        self.configure(text='Palette {}'.format(len(self.master.palettes) + 1),
                       bg='white', relief=tk.FLAT)
        rgb_entry = HexRGBEntry(self)




        # placing:
        rgb_entry.grid(row=0, column=0, sticky=tk.NSEW)


class AddPaletteButton(tk.Button):
    max_palettes = 5

    def __init__(self, master):
        super().__init__(master)
        self.configure(text='Add Palette', command=self.add_palette)
        master.widgets.append(self)

    def add_palette(self, *args):
        if len(self.master.palettes) < self.max_palettes:
            self.master.palettes.append(Palette(self.master).pack())
        else:
            messagebox.showinfo(
                'No more!',
                'Maximum number of palettes ({}) has been reached'.format(
                    self.max_palettes))


class App(tk.Frame):
    widgets = []
    palettes = []

    def __init__(self, master=None):
        super().__init__(master)
        self.configure(bg='white')
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        AddPaletteButton(self)
        Palette(self)
        for widget in self.widgets:
            widget.pack()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    root = tk.Tk()
    app = App(master=root)
    app.mainloop()
