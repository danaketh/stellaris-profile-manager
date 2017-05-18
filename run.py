import os
import sys
import sqlite3
import json
from PyQt5.QtWidgets import QApplication
from ui.StellarisProfileManager import StellarisProfilesManager

game_root = os.path.expanduser('~\\Documents\\Paradox Interactive\\Stellaris')

stellaris_settings_path = game_root
stellaris_mods_path = os.path.join('\\', game_root, 'mod')


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


db = Database('profiles.db')
db.init()


def main():
    """
    Main app loop
    :return: 
    """
    app = QApplication(sys.argv)
    SPM = StellarisProfilesManager(db)
    sys.exit(app.exec_())


# Run Forrest, Run!
if __name__ == '__main__':
    main()
