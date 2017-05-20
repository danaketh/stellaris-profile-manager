import os
import sys
import sqlite3
import json
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore
from ui.StellarisProfileManager import StellarisProfilesManager

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"


class Database:
    """
    Just a simple object for the database connection
    """

    def __init__(self, db_name):
        """
        
        :param db_name: 
        """
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

    def init(self):
        """
        Create the basic database structure
        :return: 
        """
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS profiles
            (profile_name VARCHAR(200) PRIMARY KEY, mods TEXT, is_active INTEGER, is_default INTEGER)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS settings
            (`key` VARCHAR(200), `value` TEXT)''')
        self.cursor.execute('SELECT COUNT(*) FROM profiles')
        num_of_profiles = self.cursor.fetchone()

        if num_of_profiles[0] == 0:
            """
            If no record is found in the database, it was probably just created and thus we'll
            just create a default profile which has no mods.
            """
            self.cursor.execute(
                "INSERT INTO profiles (profile_name, mods, is_active, is_default) VALUES (?, ?, ?, ?)",
                ['Default', json.dumps([]), 1, 1]
            )
            self.connection.commit()

    def get_profiles(self):
        """
        
        :return: 
        """
        self.cursor.execute("SELECT profile_name, is_active, is_default FROM profiles")
        return self.cursor.fetchall()

    def get_profile(self, name):
        """
        
        :param name: 
        :return: 
        """
        self.cursor.execute("SELECT profile_name, mods FROM profiles WHERE profile_name=?", [name])
        return self.cursor.fetchone()

    def delete_profile(self, name):
        """
        
        :param name: 
        :return: 
        """
        self.cursor.execute("DELETE FROM profiles WHERE profile_name=?", [name])
        return self.connection.commit()

    def save_config(self, key, value):
        self.cursor.execute(
            "INSERT OR IGNORE INTO settings (`key`, `value`) VALUES (?, ?)",
            (key, value)
        )
        self.connection.commit()
        self.cursor.execute(
            'UPDATE settings SET `value`=? WHERE `key`=?',
            (value, key)
        )
        self.connection.commit()

    def get_config(self, key):
        self.cursor.execute("SELECT `value` FROM settings WHERE `key`=?", [key])
        conf = self.cursor.fetchone()

        if conf:
            return conf[0]

        return False

    def get_mods(self, profile):
        self.cursor.execute("SELECT profile_name, mods FROM profiles WHERE profile_name=?", [profile])
        profile = self.cursor.fetchone()
        return json.loads(profile[1])

    def save_mods(self, profile, mods):
        self.cursor.execute(
            'INSERT OR IGNORE INTO profiles (profile_name, mods, is_active, is_default) VALUES (?, ?, ?, ?)',
            [profile, json.dumps(mods), 0, 0]
        )
        self.connection.commit()
        self.cursor.execute(
            'UPDATE profiles SET mods=? WHERE profile_name=?',
            (json.dumps(mods), profile)
        )
        self.connection.commit()


db = Database('profiles.db')
db.init()

if not os.path.isdir('profiles'):
    os.mkdir('profiles')

def main():
    """
    Main app loop
    :return: 
    """
    app = QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    SPM = StellarisProfilesManager(db)
    sys.exit(app.exec_())


# Run Forrest, Run!
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log = open('crash.log', 'a+')
        log.write(str(e))
        log.close()
