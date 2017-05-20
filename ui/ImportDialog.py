from PyQt5.QtWidgets import QDialog, QListWidgetItem, QLineEdit, QListWidget, QPushButton
from PyQt5.Qt import Qt, QFont, QDesktopWidget, QSizePolicy
import os
import json
import datetime


class ImportDialog(QDialog):
    def __init__(self, app):
        """
        Init
        """
        self.app = app

        super(ImportDialog, self).__init__()

        # define UI elements
        self.listOfProfiles = QListWidget(self)
        self.importButton = QPushButton(self)

        # initialize the UI
        self.init_ui()

    def init_ui(self):
        """
        Initialize the actual UI
        :return: 
        """
        # Main window
        desktop = QDesktopWidget()
        screen_width = desktop.screen().width()
        screen_height = desktop.screen().height()
        app_width = 450
        app_height = 375
        self.setWindowTitle('Import profile')
        self.setGeometry(  # this centers the window
            (screen_width / 2) - (app_width / 2),
            (screen_height / 2) - (app_height / 2),
            app_width,
            app_height
        )
        self.setFixedSize(self.size())
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # elements
        self.create_list_of_profiles()
        self.create_import_button()

    def create_list_of_profiles(self):
        """
        Configure the list of profiles
        :return: 
        """
        self.listOfProfiles.setGeometry(20, 20, 410, 300)
        self.listOfProfiles.itemClicked.connect(self.enable_buttons)
        self.load_profiles()

    def create_import_button(self):
        """
        Configure the save button
        :return: 
        """
        self.importButton.setGeometry(351, 325, 80, 30)
        self.importButton.setText('Import')
        self.importButton.setDisabled(True)
        self.importButton.clicked.connect(self.on_import)

    def load_profiles(self):
        """
        Load mods into the list
        :param mods: 
        :return: 
        """
        self.listOfProfiles.clear()
        for m in self.get_available_profiles():
            # change the name to avoid conflicts - overwriting might cause problems
            if self.app.db.profile_exists(m[0]):
                m[0] = '{} ({})'.format(m[0], datetime.datetime.now())

            item = QListWidgetItem()
            item.setText(m[0])
            item.setData(Qt.UserRole, m[1])
            self.listOfProfiles.addItem(item)

        self.listOfProfiles.sortItems(Qt.AscendingOrder)

    @staticmethod
    def get_available_profiles():
        profiles = []
        for p in os.listdir('profiles'):
            f = open('profiles/' + p, 'r')
            profiles.append(
                json.loads(f.read())
            )
            f.close()

        return profiles

    def enable_buttons(self):
        self.importButton.setEnabled(True)

    def on_import(self):
        """
        Insert the profile into database
        :return: 
        """
        item = self.listOfProfiles.currentItem() # type: QListWidgetItem
        mods = json.dumps(item.data(Qt.UserRole))
        self.app.db.save_mods(item.text(), mods)
        item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
        item.setText(item.text() + ' *IMPORTED*')
        self.app.load_profiles()
