from PyQt5.QtWidgets import QMainWindow, QListWidget, QListWidgetItem, QPushButton, QLineEdit, QFileDialog
from PyQt5.Qt import QFont, QDesktopWidget, QSizePolicy
from .ProfileEditor import ProfileEditor
import subprocess


class StellarisProfilesManager(QMainWindow):
    """
    Main application window
    """

    def __init__(self, db):
        """
        Initialize the class
        """
        self.db = db
        self.steam_path = None

        super(StellarisProfilesManager, self).__init__()

        # define UI elements
        self.listOfProfiles = QListWidget(self)
        self.launchButton = QPushButton(self)
        self.newProfileButton = QPushButton(self)
        self.editProfileButton = QPushButton(self)
        self.deleteProfileButton = QPushButton(self)
        self.findSteamButton = QPushButton(self)
        self.pathToSteam = QLineEdit(self)

        # initialize the UI
        self.init_ui()
        self.reload_config()

        # show the main window
        self.show()

    def init_ui(self):
        """
        Initialize the actual UI
        :return: 
        """
        # Main window
        desktop = QDesktopWidget()
        screen_width = desktop.screen().width()
        screen_height = desktop.screen().height()
        app_width = 390
        app_height = 400
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
        self.create_list_of_profiles()
        self.create_launch_button()
        self.create_new_profile_button()
        self.create_edit_profile_button()
        self.create_delete_profile_button()
        self.create_find_steam_button()
        self.create_path_to_steam_input()

    def create_list_of_profiles(self):
        """
        Configure the profiles list and load profiles
        :return: 
        """
        self.listOfProfiles.setGeometry(20, 20, 350, 250)
        self.listOfProfiles.itemClicked.connect(self.enable_profile_buttons)
        self.load_profiles()

    def create_launch_button(self):
        """
        Configure the launch button
        :return: 
        """
        self.launchButton.setGeometry(19, 275, 352, 40)
        self.launchButton.setText('Launch the game')
        self.launchButton.setDisabled(True)
        font = QFont()
        font.setBold(True)
        font.setPixelSize(12)
        self.launchButton.setFont(font)
        self.launchButton.clicked.connect(self.launch_game)

    def create_new_profile_button(self):
        """
        Configure the new profile button
        :return: 
        """
        self.newProfileButton.setGeometry(19, 318, 115, 30)
        self.newProfileButton.setText('New profile')
        self.newProfileButton.clicked.connect(self.open_empty_profile)

    def create_edit_profile_button(self):
        """
        Configure the edit profile button
        :return: 
        """
        self.editProfileButton.setGeometry(137, 318, 116, 30)
        self.editProfileButton.setText('Edit profile')
        self.editProfileButton.setDisabled(True)
        self.editProfileButton.clicked.connect(self.open_existing_profile)

    def create_delete_profile_button(self):
        """
        Configure the delete profile button
        :return: 
        """
        self.deleteProfileButton.setGeometry(256, 318, 115, 30)
        self.deleteProfileButton.setText('Delete profile')
        self.deleteProfileButton.setDisabled(True)
        self.deleteProfileButton.clicked.connect(self.delete_existing_profile)

    def create_find_steam_button(self):
        """
        Configure the button for finding the Steam installation
        :return: 
        """
        self.findSteamButton.setGeometry(291, 351, 80, 30)
        self.findSteamButton.setText('Find Steam')
        self.findSteamButton.clicked.connect(self.open_path_finder_dialog)

    def create_path_to_steam_input(self):
        """
        Configure the input which holds the Steam path
        :return: 
        """
        self.pathToSteam.setGeometry(20, 352, 268, 28)
        path = self.db.get_config('steam_path')
        if path:
            self.pathToSteam.setText(path)

    def load_profiles(self):
        """
        Load profiles into the list
        :return: 
        """
        font_default = QFont()
        font_default.setItalic(True)
        self.listOfProfiles.clear()
        for p in self.db.get_profiles():
            item = QListWidgetItem()
            item.setText(p[0])

            if p[2] == 1:
                item.setFont(font_default)

            self.listOfProfiles.addItem(item)

    def reload_config(self):
        """
        Reload all configuration values
        :return: 
        """
        self.steam_path = self.db.get_config('steam_path')

    def open_empty_profile(self):
        """
        Open the profile editor, empty and ready for a new profile
        :return: 
        """
        editor = ProfileEditor(app=self)
        editor.exec_()
        editor.show()

    def open_existing_profile(self):
        """
        Open the profile editor and load in currently selected profile
        :return: 
        """
        profile_item = self.listOfProfiles.currentItem()
        profile = self.db.get_profile(profile_item.text())
        editor = ProfileEditor(app=self, profile=profile)
        editor.exec_()
        editor.show()

    def delete_existing_profile(self):
        """
        Delete an existing profile
        :return: 
        """
        profile_item = self.listOfProfiles.currentItem()
        self.db.delete_profile(profile_item.text())
        self.load_profiles()

    def enable_profile_buttons(self):
        """
        Enable profile related buttons which are disabled because
        of them requiring selected profile
        :return: 
        """
        self.editProfileButton.setEnabled(True)
        self.deleteProfileButton.setEnabled(True)

        if self.steam_path:
            self.launchButton.setEnabled(True)

    def launch_game(self):
        """
        Launch the game
        :return: 
        """
        self.launchButton.setDisabled(True)
        profile_item = self.listOfProfiles.currentItem()
        command = list([self.steam_path])
        command.append("-applaunch 281990")  # set the application ID
        command.append("-skiplauncher")  # we can skip the game launcher
        for mod in self.db.get_mods(profile_item.text()):  # build the list of mods
            command.append("-mod={}".format(mod))

        command = format(" ".join(command))
        print("Executing " + command)
        subprocess.Popen(command)

        # I guess closing the app is easier than trying to check for the process and wait for it to end
        self.close()

    def open_path_finder_dialog(self):
        """
        Open dialog for finding and choosing Steam.exe
        :return: 
        """
        file_name = QFileDialog.getOpenFileName(self, caption='Steam path', directory='C:\\')

        if file_name[0]:
            self.db.save_config('steam_path', file_name[0])
            self.reload_config()
            self.pathToSteam.setText(file_name[0])
