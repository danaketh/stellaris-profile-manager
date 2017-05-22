from PyQt5.QtWidgets import QDialog, QListWidgetItem, QLineEdit, QListWidget, QPushButton
from PyQt5.Qt import Qt, QDesktopWidget, QSizePolicy
from PyQt5.QtGui import QColor
import os
from Paradox.Mod import Mod


class ProfileEditor(QDialog):
    """
    Profile editor
    """

    def __init__(self, app, profile=None):
        """
        Init
        """
        self.app = app
        self.profile = profile
        self.game_path = os.path.expanduser('~\\Documents\\Paradox Interactive\\Stellaris')
        self.game_mods_path = os.path.join('\\', self.game_path, 'mod')

        super(ProfileEditor, self).__init__()

        # define UI elements
        self.profileName = QLineEdit(self)
        self.listOfMods = QListWidget(self)
        self.saveButton = QPushButton(self)
        self.cancelButton = QPushButton(self)
        self.reloadModsButton = QPushButton(self)

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
        app_height = 420
        self.setWindowTitle('Stellaris Profile Manager')
        self.setGeometry(  # this centers the window
            (screen_width / 2) - (app_width / 2),
            (screen_height / 2) - (app_height / 2),
            app_width,
            app_height
        )
        self.setFixedSize(self.size())
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # elements
        self.create_profile_name_input()
        self.create_list_of_mods()
        self.create_save_button()
        self.create_cancel_button()
        self.create_reload_mods_button()

    def create_profile_name_input(self):
        """
        Configure the field for setting the profile name
        :return: 
        """
        self.profileName.setGeometry(20, 20, 410, 30)
        self.profileName.setPlaceholderText('Profile name')
        if self.profile:
            self.profileName.setText(self.profile[0])

    def create_list_of_mods(self):
        """
        Configure the list of mods
        :return: 
        """
        self.listOfMods.setGeometry(20, 55, 410, 300)
        if self.profile:
            self.load_mods(self.profile[1])
        else:
            self.load_mods()

    def create_save_button(self):
        """
        Configure the save button
        :return: 
        """
        self.saveButton.setGeometry(270, 360, 80, 30)
        self.saveButton.setText('Save')
        self.saveButton.clicked.connect(self.on_save)

    def create_cancel_button(self):
        """
        Configure the cancel button
        :return: 
        """
        self.cancelButton.setGeometry(351, 360, 80, 30)
        self.cancelButton.setText('Cancel')
        self.cancelButton.setDefault(True)
        self.cancelButton.clicked.connect(self.on_cancel)

    def create_reload_mods_button(self):
        """
        Configure the reload mods button
        :return: 
        """
        self.reloadModsButton.setGeometry(20, 360, 80, 30)
        self.reloadModsButton.setText('Reload mods')
        self.reloadModsButton.clicked.connect(self.reload_mods)

    def reload_mods(self):
        """
        Reload mods
        :return: 
        """
        if self.profile:
            self.load_mods(self.profile[1])
        else:
            self.load_mods()

    def load_mods(self, mods=[]):
        """
        Load mods into the list
        :param mods: 
        :return: 
        """
        self.listOfMods.clear()
        for m in self.get_available_mods():
            item = QListWidgetItem()
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            # set used mods as active
            if m['path'] in mods:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

            item.setText(m['name'])
            item.setData(Qt.UserRole, m['path'])
            # set background for the outdated mods
            if not m['version'].startswith(self.app.game_version['release']):
                item.setText('{} *OUTDATED*'.format(item.text()))
                item.setBackground(QColor('red'))

            self.listOfMods.addItem(item)

        self.listOfMods.sortItems(Qt.AscendingOrder)

    def get_available_mods(self):
        mods = []
        for m in os.listdir(self.game_mods_path):
            p = os.path.join(self.game_mods_path, m)
            if os.path.isfile(p):
                mod = Mod(p)
                info = mod.get_info()
                info['path'] = 'mod/' + m
                mods.append(info)

        return mods

    def on_save(self):
        """
        Save the changes. It can be either creating a new profile
        or updating an existing one.
        :return: 
        """
        mods = []
        for i in range(self.listOfMods.count()):
            item = self.listOfMods.item(i)  # type: QListWidgetItem
            if item.checkState():
                mods.append(item.data(Qt.UserRole))

        self.app.db.save_mods(self.profileName.text(), mods)
        self.app.load_profiles()
        self.close()

    def on_cancel(self):
        """
        Just close the editor
        :param dialog: 
        :return: 
        """
        self.close()
