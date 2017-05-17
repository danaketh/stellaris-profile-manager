import os
import sys
import sqlite3
import json
import subprocess
from PyQt5.uic import loadUi
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QDialog, QFileDialog
from PyQt5.QtGui import QFont
from Paradox import Mod

game_root = os.path.expanduser('~\\Documents\\Paradox Interactive\\Stellaris')

stellaris_settings_path = game_root
stellaris_mods_path = os.path.join('\\', game_root, 'mod')

db_conn = sqlite3.connect('profiles.db')
db_cursor = db_conn.cursor()
db_cursor.execute('''CREATE TABLE IF NOT EXISTS profiles
    (profile_name VARCHAR(200) PRIMARY KEY, mods TEXT, is_active INTEGER, is_default INTEGER)''')
db_cursor.execute('''CREATE TABLE IF NOT EXISTS settings
    (`key` VARCHAR(200), `value` TEXT)''')
db_cursor.execute('SELECT COUNT(*) FROM profiles')
num_of_profiles = db_cursor.fetchone()

if num_of_profiles[0] == 0:
    """
    If no record is found in the database, it was probably just created and thus we'll
    just create a default profile which has no mods.
    """
    db_cursor.execute(
        "INSERT INTO profiles (profile_name, mods, is_active, is_default) VALUES (?, ?, ?, ?)",
        ['Default', json.dumps([]), 1, 1]
    )
    db_conn.commit()


class StellarisProfilesManager(QMainWindow):
    """
    Application class
    """

    def __init__(self):
        """
        Init
        """
        self.steam_path = None

        super(StellarisProfilesManager, self).__init__()
        loadUi("ui/main.ui", self)
        self.setFixedSize(self.size())
        self.setup_ui()
        self.load_config()
        self.load_profiles()
        self.bind()
        self.show()

    def load_profiles(self):
        """
        Load profiles into the list
        :return: 
        """
        font_default = QFont()
        font_default.setItalic(True)
        db_cursor.execute("SELECT profile_name, is_active, is_default FROM profiles")
        self.listOfProfiles.clear()
        for p in db_cursor.fetchall():
            item = QListWidgetItem()
            item.setText(p[0])

            if p[2] == 1:
                item.setFont(font_default)

            self.listOfProfiles.addItem(item)

    def load_config(self):
        db_cursor.execute("SELECT `value` FROM settings WHERE `key`='steam_path'")
        steam_path = db_cursor.fetchone()

        if steam_path:
            self.steamPath.setText(steam_path[0])
            self.steam_path = steam_path[0]

    def setup_ui(self):
        self.editProfileButton.setEnabled(False)
        self.deleteProfileButton.setEnabled(False)
        self.launchButton.setEnabled(False)

    def bind(self):
        """
        Bind main window actions
        :return: 
        """
        self.newProfileButton.clicked.connect(self.editor_new_profile)
        self.editProfileButton.clicked.connect(self.editor_edit_profile)
        self.launchButton.clicked.connect(self.launch_game)
        self.pathButton.clicked.connect(self.path_finder_dialog)
        self.listOfProfiles.itemClicked.connect(self.enable_buttons)

    def editor_new_profile(self):
        """
        Open the profile editor
        :return: 
        """
        editor = ProfileEditor(app=self)
        editor.exec_()
        editor.show()

    def editor_edit_profile(self):
        """
        Open the profile editor
        :return: 
        """
        profile_item = self.listOfProfiles.currentItem()
        db_cursor.execute("SELECT profile_name, mods FROM profiles WHERE profile_name=?", [profile_item.text()])
        profile = db_cursor.fetchone()
        editor = ProfileEditor(app=self, profile=profile)
        editor.exec_()
        editor.show()

    def enable_buttons(self):
        self.editProfileButton.setEnabled(True)
        self.deleteProfileButton.setEnabled(True)

        if self.steam_path:
            self.launchButton.setEnabled(True)

    def launch_game(self):
        self.launchButton.setEnabled(False)
        profile_item = self.listOfProfiles.currentItem()
        db_cursor.execute("SELECT profile_name, mods FROM profiles WHERE profile_name=?", [profile_item.text()])
        profile = db_cursor.fetchone()
        command = list([self.steam_path.replace('/', '\\')])
        command.append("-applaunch 281990")
        command.append("-skiplauncher")
        for mod in json.loads(profile[1]):
            command.append("-mod={}".format(mod))

        command = format(" ".join(command))
        print("Executing " + command)
        return subprocess.Popen(command)

    def path_finder_dialog(self):
        fname = QFileDialog.getOpenFileName(self, 'Steam path', 'C:\\')

        if fname[0]:
            db_cursor.execute("INSERT OR IGNORE INTO settings (`key`, `value`) VALUES (?, ?)", ('steam_path', fname[0]))
            db_conn.commit()
            db_cursor.execute('UPDATE settings SET `value`=? WHERE `key`=?', (fname[0], 'steam_path'))
            db_conn.commit()
            self.load_config()


class ProfileEditor(QDialog):
    def __init__(self, app, profile=None):
        """
        Init
        """
        super(ProfileEditor, self).__init__()
        loadUi("ui/dialog.ui", self)
        self.app = app
        self.setFixedSize(self.size())
        self.bind()

        if not profile:
            self.add_mods()
        else:
            self.profileName.setText(profile[0])
            self.add_mods(profile[1])

    def bind(self):
        self.submitButton.clicked.connect(self.on_accept)
        self.cancelButton.clicked.connect(self.on_cancel)

    def add_mods(self, mods=[]):
        for m in self.get_available_mods():
            item = QListWidgetItem()
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            if m['path'] in mods:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            item.setText(m['name'])
            item.setData(Qt.UserRole, m['path'])
            self.listOfMods.addItem(item)

        self.listOfMods.sortItems(Qt.AscendingOrder)

    @staticmethod
    def get_available_mods():
        mods = []
        for m in os.listdir(stellaris_mods_path):
            p = os.path.join(stellaris_mods_path, m)
            if os.path.isfile(p):
                mod = Mod(p)
                info = mod.get_info()
                info['path'] = 'mod/' + m
                mods.append(info)

        return mods

    def on_accept(self):
        """
        Save the changes. It can be either creating a new profile
        or updating an existing one.
        :return: 
        """
        mods = []
        profile_name = self.profileName.text()
        for i in range(self.listOfMods.count()):
            item = self.listOfMods.item(i)  # type: QListWidgetItem
            if item.checkState():
                mods.append(item.data(Qt.UserRole))

        db_cursor.execute(
            'INSERT OR IGNORE INTO profiles (profile_name, mods, is_active, is_default) VALUES (?, ?, ?, ?)',
            [profile_name, json.dumps(mods), 0, 0]
        )
        db_conn.commit()
        db_cursor.execute(
            'UPDATE profiles SET mods=? WHERE profile_name=?',
            (json.dumps(mods), profile_name)
        )
        db_conn.commit()

        self.app.load_profiles()
        self.close()

    def on_cancel(self):
        """
        Just close the editor
        :param dialog: 
        :return: 
        """
        self.close()


def main():
    """
    Main app loop
    :return: 
    """
    app = QApplication(sys.argv)
    SPM = StellarisProfilesManager()
    sys.exit(app.exec_())


# Run Forrest, Run!
if __name__ == '__main__':
    main()
