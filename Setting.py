import sys
from PyQt5.QtWidgets import QApplication, QComboBox,QMessageBox,QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QFontComboBox, QCheckBox, QLineEdit, QDialog, QDialogButtonBox, QSpinBox
from PyQt5.QtGui import QFontDatabase, QFont
import sqlite3

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تنظیمات")
        self.setFixedWidth(300)
        self.setFixedHeight(400)
        layout = QVBoxLayout()

        # Add some content to the settings page
        self.label = QLabel("صفحه تنظیمات")
        layout.addWidget(self.label)

        self.lang_label = QLabel("انتخاب زبان:")
        self.lang_combobox = QComboBox()
        self.lang_combobox.addItems(["fa","en"])
        layout.addWidget(self.lang_label)
        layout.addWidget(self.lang_combobox)


        # Font settings
        self.font_label = QLabel("انتخاب فونت:")
        self.font_combobox = QFontComboBox()

        font_db = QFontDatabase()
        persian_fonts = [font for font in font_db.writingSystems() if QFontDatabase.writingSystemName(font) in ['Arabic', 'Persian']]
        persian_font_names = [QFontDatabase.writingSystemName(font) for font in persian_fonts]
        self.font_combobox.addItems(persian_font_names)

        layout.addWidget(self.font_label)
        layout.addWidget(self.font_combobox)

        # Font size settings
        self.font_size_label = QLabel("انتخاب اندازه فونت:")
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setMinimum(8)  # Minimum font size
        self.font_size_spinbox.setMaximum(72)  # Maximum font size
        layout.addWidget(self.font_size_label)
        layout.addWidget(self.font_size_spinbox)

        # Icon size settings
        self.icon_size_label = QLabel("انتخاب اندازه آیکن:")
        self.icon_size_spinbox = QSpinBox()
        self.icon_size_spinbox.setMinimum(16)  # Minimum icon size
        self.icon_size_spinbox.setMaximum(128)  # Maximum icon size
        layout.addWidget(self.icon_size_label)
        layout.addWidget(self.icon_size_spinbox)

        # Password settings
        self.password_checkbox = QCheckBox("فعال کردن رمز عبور")
        self.password_entry = QLineEdit()
        self.password_entry.setPlaceholderText("رمز عبور")
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.password_entry.setEnabled(False)
        self.password_checkbox.stateChanged.connect(self.toggle_password_entry)
        layout.addWidget(self.password_checkbox)
        layout.addWidget(self.password_entry)

        # Show password checkbox
        self.show_password_checkbox = QCheckBox("نمایش رمز عبور")
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_password_checkbox)

        # Save button
        self.save_button = QPushButton("ذخیره تنظیمات")
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        self.load_settings()

    def toggle_password_entry(self, state):
        if state == 2:  # Qt.Checked
            self.password_entry.setEnabled(True)
        else:
            self.password_entry.setEnabled(False)

    def toggle_password_visibility(self, state):
        if state == 2:  # Qt.Checked
            self.password_entry.setEchoMode(QLineEdit.Normal)
        else:
            self.password_entry.setEchoMode(QLineEdit.Password)

    def save_settings(self):
        font_name = self.font_combobox.currentFont().family()
        font_size = str(self.font_size_spinbox.value())
        icon_size = str(self.icon_size_spinbox.value())
        password_enabled = self.password_checkbox.isChecked()
        password = self.password_entry.text()
        language= self.lang_combobox.currentText()

        # Save settings to a database
        connection = sqlite3.connect("settings.db")
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS settings (font TEXT, font_size TEXT, icon_size TEXT, password_enabled INTEGER, password TEXT , language TEXT)")
        cursor.execute("DELETE FROM settings")
        cursor.execute("INSERT INTO settings VALUES (?, ?, ?, ?, ?, ?)", (font_name, font_size, icon_size, password_enabled, password,language))
        connection.commit()
        connection.close()
        
        QMessageBox.information(self,"توجه","برای اعمال تنظیمات لطفا برنامه را بسته و دوباره اجرا کنید")

        self.close()

    def load_settings(self):
        connection = sqlite3.connect("settings.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM settings")
        settings = cursor.fetchone()
        if settings:
            font_name, font_size, icon_size, password_enabled, password ,language= settings
            self.font_combobox.setCurrentFont(QFont(font_name))
            self.font_size_spinbox.setValue(int(font_size))
            self.icon_size_spinbox.setValue(int(icon_size))
            self.password_checkbox.setChecked(bool(password_enabled))
            if password_enabled:
                self.password_entry.setText(password)
                self.password_entry.setEnabled(True)
        connection.close()

class PasswordDialog(QDialog):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.password_label = QLabel("رمز عبور:")
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)

        layout.addWidget(self.password_label)
        layout.addWidget(self.password_entry)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        button_box = QDialogButtonBox(buttons)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_password(self):
        if self.exec_() == QDialog.Accepted:
            return self.password_entry.text()
        else:
            return ""

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setWindowTitle("Password")
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_entry)

        login_button = QPushButton("ورود")
        login_button.clicked.connect(self.accept)
        layout.addWidget(login_button)

        self.setLayout(layout)

    def get_password(self):
        if self.exec_() == QDialog.Accepted:
            return self.password_entry.text()
        else:
            return ""

def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("تنظیمات")
    window.setGeometry(100, 100, 400, 300)

    settings_page = SettingsPage()
    window.setCentralWidget(settings_page)

    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    
