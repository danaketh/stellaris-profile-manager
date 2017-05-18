from PyQt5.QtWidgets import QDialog, QListWidgetItem


class ProfileEditor(QDialog):
    def __init__(self, app, profile=None):
        """
        Init
        """
        super(ProfileEditor, self).__init__()
        # loadUi("ui/dialog.ui", self)
        self.app = app
        self.setFixedSize(self.size())
        #self.bind()

        """
        if not profile:
            self.add_mods()
        else:
            self.profileName.setText(profile[0])
            self.add_mods(profile[1])
        """

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
