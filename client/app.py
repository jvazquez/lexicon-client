# -*- coding: utf-8 -*-
"""
:mod:`module-name-here` -- Description here
===================================

.. module:: module-name-here
   :platform: Unix, Windows
   :synopsis: complete.
.. moduleauthor:: Jorge Omar Vazquez <jorgeomar.vazquez@gmail.com>
..:date: Dec 26, 2017
"""
import json
import logging
import os
import urllib.request

from os.path import abspath, dirname, join

from tkinter import Frame, Tk, BOTH, Button, Menu, Label, Text
from tkinter.constants import DISABLED, NORMAL, END
from tkinter.ttk import Entry, LabelFrame

import logconfig
from urllib.error import HTTPError

config_log = abspath(join(dirname(__file__), '../logging.json'))
logconfig.from_autodetect(config_log)
logger = logging.getLogger('debug')
LEXICON_URL = os.getenv('LEXICON', 'http://localhost:5000')
LEXICON_TERM_SAVE_URL = '{}/term/'.format(LEXICON_URL)


class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.label_check = None
        self.frame_controls = None
        self.init_window()

    # Creation of init_window
    def init_window(self):

        # changing the title of our master widget
        self.master.title("Lexicon Client")

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)

        # creating a menu instance
        menu = Menu(self.master)
        self.master.config(menu=menu)

        # create the command_menu object)
        command_menu = Menu(menu)

        # adds a command to the menu option, calling it exit, and the
        # command it runs on event is client_exit
        command_menu.add_command(
            label="Check endpoint",
            command=self.check_connection
        )

        command_menu.add_command(
            label="Add term",
            command=self.add_term
        )

        command_menu.add_command(
            label="Quit",
            command=self.client_exit
        )

        # added "command_menu" to our menu
        menu.add_cascade(label="Commands", menu=command_menu)

    def client_exit(self):
        exit()

    def we_can_write(self):
        has_connection = False
        try:
            response = urllib.request.urlopen(LEXICON_URL, timeout=1)
            has_connection = True if response.code == 200 else 400
        except Exception:
            logger.exception('Error checking the url.')
        return has_connection

    def add_label(self, message):
        return Label(self, text=message)

    def check_connection(self):
        we_can = self.we_can_write()
        if we_can:
            message = 'Has connection.'
        else:
            message = 'No connection.'

        if self.label_check is None:
            text = self.add_label(message)
            self.label_check = text
            text.pack()
        else:
            self.label_check.config(text=message)

    def add_term(self):
        if self.frame_controls is not None:
            self.frame_controls.destroy()
        self.create_frame_control()

    def create_frame_control(self):
        we_can = self.we_can_write()
        widget_state = NORMAL if we_can else DISABLED
        self.frame_controls = LabelFrame(root, text="Add term")
        self.frame_controls.pack(fill="both", expand="yes")
        term_label = Label(self.frame_controls, text='Term.')
        term_label.pack()
        self.term_entry = Entry(self.frame_controls, state=widget_state)
        self.term_entry.pack()
        definition_label = Label(self.frame_controls, text='Definition')
        definition_label.pack()
        self.text_definition = Text(self.frame_controls)
        self.text_definition.pack()
        # creating a button instance
        save_button = Button(
                             self.frame_controls,
                             text="Add",
                             command=self.save_term
                            )
        save_button.pack()

    def save_term(self):
        term = self.term_entry.get()
        definition = self.text_definition.get("1.0", END)
        data = json.dumps({'word': term, 'definition': definition})
        data_as_bytes = data.encode('utf-8')
        request = urllib.request.Request(
            LEXICON_TERM_SAVE_URL,
            data_as_bytes,
            method='POST'
        )
        request.add_header(
                           'Content-Type',
                           'application/json; charset=utf-8'
                        )
        request.add_header(
                           'Content-Length',
                           len(data_as_bytes)
                        )
        try:
            response = urllib.request.urlopen(request)
        except HTTPError:
            logger.exception('Error saving term.')


root = Tk()
# Size of the window
root.geometry("700x500")
app = Window(root)
root.mainloop()
