import sys

from PyQt5.QtWidgets import QApplication,QShortcut,QMessageBox,QSpinBox,QCheckBox,QDateEdit
from PyQt5.QtWidgets import QLabel,QSizePolicy,QMenu,QMainWindow,QHBoxLayout, QAction, QToolBar
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QPushButton, QTableWidget, QTableWidgetItem
from PyQt5.QtWidgets import QLineEdit, QStackedWidget, QHeaderView ,QTimeEdit,QDateTimeEdit


from PyQt5.QtCore import Qt,QSize,QRect,QDate,QTime,QDateTime
from PyQt5.QtGui import QIcon,QFont,QKeySequence,QIntValidator, QPalette
import Setting
import sqlite3
from persiantools.jdatetime import JalaliDate


class AccountingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نرم افزار حسابداری آرنا اسپرت")
        self.setWindowIcon(QIcon("Arena.ico"))
        self.setGeometry(550, 200, 800, 600)
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.lock_check=0
        self.inventory_lock=0
        self.store_lock=0
        self.deposit_lock=0
        self.withdraw_lock=0
        self.ledger_lock=0
        self.line_Edits={"inventory":{"Num":{},"Price":{}}
                         ,"store":{"Num":{},"Price":{}}
                         ,"withdraw":{"Price":{},"Date":{},"Time":{}}
                         ,"deposit":{"Price":{},"Date":{},"Time":{}}
                         ,"ledger":{"Date":{},"Time":{},"Price":{}}
                         }
        self.line_Edit_count=1
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        self.create_toolbar()
        self.load_settings()
        self.create_pages()

    def create_toolbar(self):
        global toolbar_label,toolbar,lock_action,plus_action
        toolbar = QToolBar()
        # toolbar2 = QToolBar()
        menubar=self.menuBar()
        toolbar_label = QLabel('صفحه انبار')
        space_label = QLabel('              ')
        space_label2 = QLabel('              ')
        toolbar_label.setBackgroundRole(QPalette.ColorRole.Foreground)
        settings_button=QAction("Setting",self)
        settings_button.triggered.connect(self.open_settings_page)
        
        Help_menu=QMenu("Help",self)
        Help_Action=QAction("راهنما",Help_menu)
        Help_menu.addAction(Help_Action)
        
        settings_button.triggered.connect(self.open_settings_page)
        menubar.addAction(settings_button)
        menubar.addMenu(Help_menu)
        toolbar.addSeparator()
        # اضافه کردن دکمه‌های منو با آیکون و متن
        inventory_action = QAction(QIcon('Icons/inventory_icon.png'), 'انبار', self)
        inventory_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        inventory_action.triggered.connect(lambda: toolbar_label.setText('صفحه انبار'))
        toolbar.addAction(inventory_action)
        toolbar.addSeparator()

        store_action = QAction(QIcon('Icons/store_icon.png'), 'فروشگاه', self)
        store_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        store_action.triggered.connect(lambda: toolbar_label.setText('صفحه فروشگاه'))
        toolbar.addAction(store_action)  
        toolbar.addSeparator()
        

        deposit_action = QAction(QIcon('Icons/Deposit_icon.png'), 'واریز ها', self)
        deposit_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        deposit_action.triggered.connect(lambda: toolbar_label.setText("صفحه واریزی ها"))
        toolbar.addAction(deposit_action) 
        toolbar.addSeparator()
        
        withdraw_action = QAction(QIcon('Icons/Withdraw_icon.png'), 'برداشت ها', self)
        withdraw_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        withdraw_action.triggered.connect(lambda: toolbar_label.setText("صفحه برداشت ها"))
        toolbar.addAction(withdraw_action)
        toolbar.addSeparator()
        

        ledger_action = QAction(QIcon('Icons/ledger_icon.png'), 'حساب های دفتری', self)
        ledger_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(4))
        ledger_action.triggered.connect(lambda: toolbar_label.setText("صفحه حساب های دفتری"))
        toolbar.addAction(ledger_action)
        toolbar.addSeparator()
        
        
        toolbar.addWidget(space_label)
        
        toolbar.addWidget(toolbar_label)
       
        toolbar.addWidget(space_label2)
        toolbar.addSeparator()
       
        
        
        
        
        plus_action = QAction(QIcon('Icons/Plus_icon.png'), 'افزودن', self)
        plus_action.triggered.connect(lambda: self.AddProduct(toolbar_label))
        
        toolbar.addAction(plus_action)
        toolbar.addSeparator()
        
        minus_action = QAction(QIcon('Icons/minus_icon.png'), 'حذف', self)
        minus_action.triggered.connect(lambda: self.RemoveProduct(toolbar_label))
        
        lock_action = QAction(QIcon('Icons/unlock_icon.png'), 'قفل جدول', self)
        lock_action.triggered.connect(lambda: self.Lock_Check(toolbar_label,self.lock_check))
        
        save_action = QAction(QIcon('Icons/Save_icon.png'),  'ذخیره', self)
        save_action.triggered.connect(lambda: self.Save(inventory_table,store_table,deposit_table,withdraw_table,ledger_table))
        
        
        # minus_action..connect(lambda: self.RemoveProduct(toolbar_label))
        toolbar.addAction(minus_action)
        toolbar.addSeparator()
        toolbar.addAction(lock_action)
        toolbar.addSeparator()
        toolbar.addAction(save_action)
        toolbar.addSeparator()
        
        
        toolbar.setIconSize(QSize(40, 40))
        
        
        # اضافه کردن تولبار به پنجره
        self.addToolBar(toolbar)
        
    def open_settings_page(self):
        self.settings_page = Setting.SettingsPage()
        self.settings_page.show()
    
    def load_settings(self):
        global language
        connection = sqlite3.connect("settings.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM settings")
        settings = cursor.fetchone()
        if settings:
            # Load settings from the database and apply them
            font_name, font_size, icon_size, password_enabled, password,language = settings
            # Apply font settings
            font = QFont(font_name, int(font_size))
            self.setFont(font)
            toolbar.setIconSize(QSize(int(icon_size),int(icon_size)))
            # Apply icon size settings
            # Code to set icon size
            # Apply password settings
            if password_enabled:
                while True:
                    login_dialog = Setting.LoginDialog()
                    entered_password = login_dialog.get_password()
                    if entered_password == password:
                        break
                    else:
                        QMessageBox.warning(self,"خطا","رمز عبور را اشتباه وارد کردید")
            

        else:
            print("تنظیماتی یافت نشد. لطفا تنظیمات را انجام دهید.")
            sys.exit()

    def create_pages(self):
        global inventory_table,search_entry,store_table,ledger_table,withdraw_table,deposit_table
        self.stacked_widget = QStackedWidget()

        # validator=IntDelegate(self)
        
        inventory_page = QWidget()
        inventory_layout = QVBoxLayout()

        
        inventory_table = QTableWidget()
        inventory_table.setColumnCount(3)
        inventory_table.setObjectName("inventory_table")
        
        inventory_table.setHorizontalHeaderLabels(["نام محصول", "تعداد", "قیمت"])
        # inventory_table.setItemDelegateForColumn(1,validator)
        # inventory_table.setItemDelegateForColumn(2,validator)
        
        header = inventory_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        inventory_layout.addWidget(inventory_table)

        # add_button = QPushButton("افزودن محصول")
        # add_button.clicked.connect(lambda:self.AddProduct(inventory_table))
        
        shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        shortcut.activated.connect(lambda:self.AddProduct(toolbar_label))


        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("نام محصول")
        self.search_entry.setAlignment(Qt.AlignCenter)
        self.search_entry.textChanged.connect(lambda:self.SearchProduct(self.search_entry))

        button_layout = QHBoxLayout()

        button_layout.addWidget(self.search_entry)
        
        

        inventory_layout.addLayout(button_layout)

        inventory_page.setLayout(inventory_layout)

        store_page = QWidget()
        store_layout = QVBoxLayout()

        store_table = QTableWidget()
        store_table.setColumnCount(3)
        store_table.setObjectName("store_table")
        
        store_table.setHorizontalHeaderLabels(["نام محصول", "تعداد", "قیمت"])

        header = store_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        
        store_layout.addWidget(store_table)

        self.search_entry_store = QLineEdit()
        self.search_entry_store.setPlaceholderText("نام محصول")
        self.search_entry_store.setAlignment(Qt.AlignCenter)
        self.search_entry_store.textChanged.connect(lambda:self.SearchProduct(self.search_entry))

        button_layout = QHBoxLayout()

        button_layout.addWidget(self.search_entry_store)

        store_layout.addLayout(button_layout)

        store_page.setLayout(store_layout)

        deposit_page = QWidget()
        deposit_layout = QVBoxLayout()

        deposit_table = QTableWidget()
        deposit_table.setColumnCount(4)
        deposit_table.setObjectName("deposit_table")
        deposit_table.setHorizontalHeaderLabels(["مبلغ", "تاریخ", "ساعت", "توضیحات"])

        header = deposit_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        deposit_layout.addWidget(deposit_table)
        deposit_page.setLayout(deposit_layout)
        
        
        
        withdraw_page = QWidget()
        withdraw_layout = QVBoxLayout()

        withdraw_table = QTableWidget()
        withdraw_table.setColumnCount(4)
        withdraw_table.setObjectName("withdraw_table")
        withdraw_table.setHorizontalHeaderLabels(["مبلغ", "تاریخ", "ساعت", "توضیحات"])

        header = withdraw_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        withdraw_layout.addWidget(withdraw_table)
        withdraw_page.setLayout(withdraw_layout)


        ledger_page = QWidget()
        ledger_layout = QVBoxLayout()

        ledger_table = QTableWidget()
        ledger_table.setColumnCount(5)
        ledger_table.setObjectName("ledger_table")
        ledger_table.setHorizontalHeaderLabels(["نام و نام خانوادگی", "تاریخ", "ساعت", "مبلغ", "نام محصول"])

        header = ledger_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        ledger_layout.addWidget(ledger_table)
        ledger_page.setLayout(ledger_layout)

        self.stacked_widget.addWidget(inventory_page)
        self.stacked_widget.addWidget(store_page)
        self.stacked_widget.addWidget(deposit_page)
        self.stacked_widget.addWidget(withdraw_page)
        self.stacked_widget.addWidget(ledger_page)

        self.layout.addWidget(self.stacked_widget)
        # if language=="en":
        #         self.translate("en")
        # else:
        #         self.translate("fa")



    def translate(self,target_lan):
        
        if target_lan=="en":
            inventory_table.setHorizontalHeaderLabels(["Name", "Number", "Price"])
            store_table.setHorizontalHeaderLabels(["Name", "Number", "Price"])
            deposit_table.setHorizontalHeaderLabels(["Price", "Date","Time", "Description"])
            withdraw_table.setHorizontalHeaderLabels(["Price", "Date","Time", "Description"])
            ledger_table.setHorizontalHeaderLabels(["Name & Family", "Date","Time", "Price","Product Name"])        
            search_entry.setPlaceholderText("Product Name")
        else:
            inventory_table.setHorizontalHeaderLabels(["نام محصول", "تعداد", "قیمت"])
            store_table.setHorizontalHeaderLabels(["نام محصول", "تعداد", "قیمت"])
            deposit_table.setHorizontalHeaderLabels(["مبلغ", "تاریخ", "ساعت", "توضیحات"])
            withdraw_table.setHorizontalHeaderLabels(["مبلغ", "تاریخ", "ساعت", "توضیحات"])
            ledger_table.setHorizontalHeaderLabels(["نام و نام خانوادگی", "تاریخ", "ساعت", "مبلغ", "نام محصول"])
            search_entry.setPlaceholderText("نام محصول")

    def AddProduct(self, t_label: QLabel):
      
        if t_label.text() == 'صفحه انبار':
            table = inventory_table
            lock_variable = self.inventory_lock
            row_count = table.rowCount()
            table.insertRow(row_count)

            Line_Edit_Num = QLineEdit(self)
            Line_Edit_Price = QLineEdit(self) 
            validator = QIntValidator()
            validator2 = QIntValidator()
            
            Line_Edit_Num.setStyleSheet("border: none; font-size: 18px; font-family: 'Dubai';")
            Line_Edit_Price.setStyleSheet("border: none; font-size: 18px; font-family: 'Dubai';")

            Line_Edit_Num.setValidator(validator)
            Line_Edit_Price.setValidator(validator2)
            
            self.line_Edits["inventory"]["Num"][f"line{table.rowCount()}"] = Line_Edit_Num
            self.line_Edits["inventory"]["Price"][f"line{table.rowCount()}"] = Line_Edit_Price

            table.setCellWidget(table.rowCount() - 1, 1, Line_Edit_Num)
            table.setCellWidget(table.rowCount() - 1, 2, Line_Edit_Price)

        elif t_label.text() == 'صفحه فروشگاه':
            table = store_table
            lock_variable = self.store_lock
            
            row_count = table.rowCount()
            table.insertRow(row_count)

            Line_Edit_Num = QLineEdit(self)
            Line_Edit_Price = QLineEdit(self)
            validator = QIntValidator()
            validator2 = QIntValidator()
            Line_Edit_Num.setStyleSheet("border: none; font-size: 18px; font-family: 'Dubai';")
            Line_Edit_Price.setStyleSheet("border: none; font-size: 18px; font-family: 'Dubai';")

            Line_Edit_Num.setValidator(validator)
            Line_Edit_Price.setValidator(validator2)
            self.line_Edits["store"]["Num"][f"line{table.rowCount()}"] = Line_Edit_Num
            self.line_Edits["store"]["Price"][f"line{table.rowCount()}"] = Line_Edit_Price

            table.setCellWidget(table.rowCount() - 1, 1, Line_Edit_Num)
            table.setCellWidget(table.rowCount() - 1, 2, Line_Edit_Price)
            
        
        elif t_label.text() == "صفحه واریزی ها":
            table = deposit_table
            lock_variable = self.deposit_lock
            row_count = table.rowCount()
            table.insertRow(row_count)
            Line_Edit_Num = QLineEdit(self)
            
            
            # Date
            
            Date_Edit=QDateEdit()
            persian_today = JalaliDate.today().to_gregorian()
            qdate = QDate(persian_today.year, persian_today.month, persian_today.day)
            Date_Edit.setDate(qdate)

            
            # Time
            
            
            Time_edit = QTimeEdit()
            Time_edit.setTime(QTime.currentTime()) 
            

            validator = QIntValidator()
            Line_Edit_Num.setStyleSheet("border: none; font-size: 18px; font-family: 'Dubai';")

            Line_Edit_Num.setValidator(validator)
            self.line_Edits["deposit"]["Price"][f"line{table.rowCount()}"] = Line_Edit_Num
            self.line_Edits["deposit"]["Date"][f"line{table.rowCount()}"] = Date_Edit
            self.line_Edits["deposit"]["Time"][f"line{table.rowCount()}"] = Time_edit

            table.setCellWidget(table.rowCount() - 1, 0, Line_Edit_Num)
            table.setCellWidget(table.rowCount() - 1, 1, Date_Edit)
            table.setCellWidget(table.rowCount() - 1, 2, Time_edit)
            
        elif t_label.text() == "صفحه برداشت ها":
            table = withdraw_table
            lock_variable = self.withdraw_lock
            row_count = table.rowCount()
            table.insertRow(row_count)
            Line_Edit_Num = QLineEdit(self)
            
            validator = QIntValidator()
            Line_Edit_Num.setStyleSheet("border: none; font-size: 18px; font-family: 'Dubai';")

            Line_Edit_Num.setValidator(validator)
            
            # Date
            
            Date_Edit=QDateEdit()
            persian_today = JalaliDate.today().to_gregorian()
            
            qdate = QDate(persian_today.year, persian_today.month, persian_today.day)
            Date_Edit.setDate(qdate)
            
            # Time
            
            
            Time_edit = QTimeEdit()
            Time_edit.setTime(QTime.currentTime()) 
            self.line_Edits["withdraw"]["Price"][f"line{table.rowCount()}"] = Line_Edit_Num
            self.line_Edits["withdraw"]["Date"][f"line{table.rowCount()}"] = Date_Edit
            self.line_Edits["withdraw"]["Time"][f"line{table.rowCount()}"] = Time_edit

            table.setCellWidget(table.rowCount() - 1, 0, Line_Edit_Num)
            table.setCellWidget(table.rowCount() - 1, 1, Date_Edit)
            table.setCellWidget(table.rowCount() - 1, 2, Time_edit)
            
        elif t_label.text() == "صفحه حساب های دفتری":
            table = ledger_table
            lock_variable = self.ledger_lock
            row_count = table.rowCount()
            table.insertRow(row_count)
            
            Line_Edit_Num = QLineEdit(self)
            
            validator = QIntValidator()
            Line_Edit_Num.setStyleSheet("border: none; font-size: 18px; font-family: 'Dubai';")

            Line_Edit_Num.setValidator(validator)
            
            # Date
            
            Date_Edit=QDateEdit()
            persian_today = JalaliDate.today().to_gregorian()
            
            qdate = QDate(persian_today.year, persian_today.month, persian_today.day)
            Date_Edit.setDate(qdate)
            
            # Time
            
            
            Time_edit = QTimeEdit()
            Time_edit.setTime(QTime.currentTime())
            
            self.line_Edits["ledger"]["Price"][f"line{table.rowCount()}"] = Line_Edit_Num
            self.line_Edits["ledger"]["Date"][f"line{table.rowCount()}"] = Date_Edit
            self.line_Edits["ledger"]["Time"][f"line{table.rowCount()}"] = Time_edit
            
            table.setCellWidget(table.rowCount() - 1, 1, Date_Edit)
            table.setCellWidget(table.rowCount() - 1, 2, Time_edit)
            table.setCellWidget(table.rowCount() - 1, 3, Line_Edit_Num)

            

        # اگر قفل شده است، سطرهای جدید را نیز قفل کنید
        if lock_variable == 1:
            for i in range(table.rowCount()):
                for j in range(table.columnCount()):
                    cell_item = table.item(i, j)
                    if cell_item is not None:
                        cell_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                    else:
                        table.setItem(i, j, QTableWidgetItem(""))
                        cell_item = table.item(i, j)
                        cell_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

    def RemoveProduct(self, tlabel: QLabel):
        # متغیرهای مربوط به جداول و قفل‌ها
        if tlabel.text() == 'صفحه انبار':
            table = inventory_table
            lock_variable = self.inventory_lock
        elif tlabel.text() == 'صفحه فروشگاه':
            table = store_table
            lock_variable = self.store_lock
        elif tlabel.text() == "صفحه واریزی ها":
            table = deposit_table
            lock_variable = self.deposit_lock
        elif tlabel.text() == "صفحه برداشت ها":
            table = withdraw_table
            lock_variable = self.withdraw_lock
        elif tlabel.text() == "صفحه حساب های دفتری":
            table = ledger_table
            lock_variable = self.ledger_lock

        list_of_selected = set(table.selectedIndexes())
        num_of_selected = len(list_of_selected)
        if num_of_selected!=0:
            
            ret = QMessageBox.question(self, "آیا مطمئن هستید؟",
                                    f"آیا مطمئن هستید که می‌خواهید {num_of_selected} مورد را حذف کنید؟")

            if ret == QMessageBox.Yes:
                x = []
                for select in list_of_selected:
                    x.append(select.row())
                x_set = set(x)
                x = list(x_set)
                x.reverse()

                
                for i in x:  
                    if tlabel.text() == 'صفحه انبار':
                    
                        for key in list(self.line_Edits["inventory"]["Num"].keys()):
                            if int(key.replace('line', '')) > i + 1:
                                new_key = f'line{int(key.replace("line", "")) - 1}'
                                self.line_Edits["inventory"]["Num"][new_key] = self.line_Edits["inventory"]["Num"].pop(key)
                                
                        for key in list(self.line_Edits["inventory"]["Price"].keys()):
                            if int(key.replace('line', '')) > i + 1:
                                new_key = f'line{int(key.replace("line", "")) - 1}'
                                self.line_Edits["inventory"]["Price"][new_key] = self.line_Edits["inventory"]["Price"].pop(key)
                                
                    elif tlabel.text() == 'صفحه فروشگاه':   
                        
                        for key in list(self.line_Edits["store"]["Num"].keys()):
                            if int(key.replace('line', '')) > i + 1:
                                new_key = f'line{int(key.replace("line", "")) - 1}'
                                self.line_Edits["store"]["Num"][new_key] = self.line_Edits["store"]["Num"].pop(key)

                        for key in list(self.line_Edits["store"]["Price"].keys()):
                            if int(key.replace('line', '')) > i + 1:
                                new_key = f'line{int(key.replace("line", "")) - 1}'
                                self.line_Edits["store"]["Price"][new_key] = self.line_Edits["store"]["Price"].pop(key)
                    
                    elif tlabel.text() == "صفحه واریزی ها":   
                        
                        for key in list(self.line_Edits["deposit"]["Price"].keys()):
                            if int(key.replace('line', '')) > i + 1:
                                new_key = f'line{int(key.replace("line", "")) - 1}'
                                self.line_Edits["deposit"]["Price"][new_key] = self.line_Edits["deposit"]["Price"].pop(key)
                        
                        for key in list(self.line_Edits["deposit"]["Date"].keys()):
                            if int(key.replace('line', '')) > i + 1:
                                new_key = f'line{int(key.replace("line", "")) - 1}'
                                self.line_Edits["deposit"]["Date"][new_key] = self.line_Edits["deposit"]["Date"].pop(key)
                                
                        for key in list(self.line_Edits["deposit"]["Time"].keys()):
                            if int(key.replace('line', '')) > i + 1:
                                new_key = f'line{int(key.replace("line", "")) - 1}'
                                self.line_Edits["deposit"]["Time"][new_key] = self.line_Edits["deposit"]["Time"].pop(key)
                               
                    elif tlabel.text() == "صفحه برداشت ها":   
                        
                        for key in list(self.line_Edits["withdraw"]["Price"].keys()):
                            if int(key.replace('line', '')) > i + 1:
                                new_key = f'line{int(key.replace("line", "")) - 1}'
                                self.line_Edits["withdraw"]["Price"][new_key] = self.line_Edits["withdraw"]["Price"].pop(key)
                        
                        for key in list(self.line_Edits["withdraw"]["Date"].keys()):
                            if int(key.replace('line', '')) > i + 1:
                                new_key = f'line{int(key.replace("line", "")) - 1}'
                                self.line_Edits["withdraw"]["Date"][new_key] = self.line_Edits["withdraw"]["Date"].pop(key)
                                
                        for key in list(self.line_Edits["withdraw"]["Time"].keys()):
                            if int(key.replace('line', '')) > i + 1:
                                new_key = f'line{int(key.replace("line", "")) - 1}'
                                self.line_Edits["withdraw"]["Time"][new_key] = self.line_Edits["withdraw"]["Time"].pop(key)
                                
                    elif tlabel.text() == "صفحه حساب های دفتری":   
                        
                        for key in list(self.line_Edits["ledger"]["Price"].keys()):
                            if int(key.replace('line', '')) > i + 1:
                                new_key = f'line{int(key.replace("line", "")) - 1}'
                                self.line_Edits["ledger"]["Price"][new_key] = self.line_Edits["ledger"]["Price"].pop(key)
                        
                        for key in list(self.line_Edits["ledger"]["Date"].keys()):
                            if int(key.replace('line', '')) > i + 1:
                                new_key = f'line{int(key.replace("line", "")) - 1}'
                                self.line_Edits["ledger"]["Date"][new_key] = self.line_Edits["ledger"]["Date"].pop(key)
                                
                        for key in list(self.line_Edits["ledger"]["Time"].keys()):
                            if int(key.replace('line', '')) > i + 1:
                                new_key = f'line{int(key.replace("line", "")) - 1}'
                                self.line_Edits["ledger"]["Time"][new_key] = self.line_Edits["ledger"]["Time"].pop(key)
            
                for i in x:
                    table.removeRow(i)
                    
    def Lock_Check(self,tlabel:QLabel,check):
        
        if (tlabel.text()=='صفحه انبار'):
            table=inventory_table
            tabel_check=self.inventory_lock
            
        
        elif (tlabel.text()=='صفحه فروشگاه'):
            table=store_table
            tabel_check=self.store_lock
                       
            
        elif (tlabel.text()=="صفحه واریزی ها"):
            table=deposit_table
            tabel_check=self.deposit_lock
            
            
        elif (tlabel.text()=="صفحه برداشت ها"):
            table=withdraw_table
            tabel_check=self.withdraw_lock
            
        elif (tlabel.text()=="صفحه حساب های دفتری"):
            table=ledger_table
            tabel_check=self.ledger_lock
            
            
        if tabel_check==0:
            lock_action.setIcon(QIcon("Icons/lock_icon.png"))
            plus_action.setEnabled(False)
            for i in range(table.rowCount()):        
                for j in range(table.columnCount()):
                    cell_item = table.item(i, j)
                    if cell_item is not None: 
                        
                        if tlabel.text() == 'صفحه انبار':
                            
                            for l_e in self.line_Edits["inventory"]["Num"]:
                                if self.line_Edits["inventory"]["Num"][l_e] is not None:
                                
                                    self.line_Edits["inventory"]["Num"][l_e].setEnabled(False)
                            
                            for l_e in self.line_Edits["inventory"]["Price"]:
                                if self.line_Edits["inventory"]["Price"][l_e] is not None:
                                    print(self.line_Edits["inventory"]["Price"][l_e])
                                
                                    self.line_Edits["inventory"]["Price"][l_e].setEnabled(False)
                                            
                        elif tlabel.text() == 'صفحه فروشگاه':
                            
                            for l_e in self.line_Edits["store"]["Num"]:
                                
                                if self.line_Edits["store"]["Num"][l_e] is not None:                      
                                
                                    self.line_Edits["store"]["Num"][l_e].setEnabled(False)
                                    
                            for l_e in self.line_Edits["store"]["Price"]:
                                
                                if self.line_Edits["store"]["Price"][l_e] is not None:                      
                                
                                    self.line_Edits["store"]["Price"][l_e].setEnabled(False)
                                                                    
                        elif tlabel.text() =="صفحه واریزی ها":
                            
                            for l_e in self.line_Edits["deposit"]["Price"]:
                                
                                if self.line_Edits["deposit"]["Price"][l_e] is not None:                      
                                
                                    self.line_Edits["deposit"]["Price"][l_e].setEnabled(False)
                            
                            for l_e in self.line_Edits["deposit"]["Date"]:
                                
                                if self.line_Edits["deposit"]["Date"][l_e] is not None:                      
                                
                                    self.line_Edits["deposit"]["Date"][l_e].setEnabled(False)
                                    
                            for l_e in self.line_Edits["deposit"]["Time"]:
                                
                                if self.line_Edits["deposit"]["Time"][l_e] is not None:                      
                                
                                    self.line_Edits["deposit"]["Time"][l_e].setEnabled(False)
                                                                                
                        elif tlabel.text() == "صفحه برداشت ها":
                            
                            for l_e in self.line_Edits["withdraw"]["Price"]:
                                
                                if self.line_Edits["withdraw"]["Price"][l_e] is not None:                      
                                
                                    self.line_Edits["withdraw"]["Price"][l_e].setEnabled(False)
                            
                            for l_e in self.line_Edits["withdraw"]["Date"]:
                                
                                if self.line_Edits["withdraw"]["Date"][l_e] is not None:                      
                                
                                    self.line_Edits["withdraw"]["Date"][l_e].setEnabled(False)
                                    
                            for l_e in self.line_Edits["withdraw"]["Time"]:
                                
                                if self.line_Edits["withdraw"]["Time"][l_e] is not None:                      
                                
                                    self.line_Edits["withdraw"]["Time"][l_e].setEnabled(False)
                                                    
                        elif tlabel.text() == "صفحه حساب های دفتری":
                            
                            for l_e in self.line_Edits["ledger"]["Price"]:
                                
                                if self.line_Edits["ledger"]["Price"][l_e] is not None:                      
                                
                                    self.line_Edits["ledger"]["Price"][l_e].setEnabled(False)
                            
                            for l_e in self.line_Edits["ledger"]["Date"]:
                                
                                if self.line_Edits["ledger"]["Date"][l_e] is not None:                      
                                
                                    self.line_Edits["ledger"]["Date"][l_e].setEnabled(False)
                                    
                            for l_e in self.line_Edits["ledger"]["Time"]:
                                
                                if self.line_Edits["ledger"]["Time"][l_e] is not None:                      
                                
                                    self.line_Edits["ledger"]["Time"][l_e].setEnabled(False)
 
                        cell_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable) 
                    
                    else:
                        
                        table.setItem(i, j, QTableWidgetItem(""))
                        cell_item = table.item(i, j)
                        if tlabel.text() == 'صفحه انبار':
                            
                            for l_e in self.line_Edits["inventory"]["Num"]:
                                if self.line_Edits["inventory"]["Num"][l_e] is not None:
                                
                                    self.line_Edits["inventory"]["Num"][l_e].setEnabled(False)
                            
                            for l_e in self.line_Edits["inventory"]["Price"]:
                                if self.line_Edits["inventory"]["Price"][l_e] is not None:
                                
                                    self.line_Edits["inventory"]["Price"][l_e].setEnabled(False)
                                            
                        elif tlabel.text() == 'صفحه فروشگاه':
                            
                            for l_e in self.line_Edits["store"]["Num"]:
                                
                                if self.line_Edits["store"]["Num"][l_e] is not None:                      
                                
                                    self.line_Edits["store"]["Num"][l_e].setEnabled(False)
                                    
                            for l_e in self.line_Edits["store"]["Price"]:
                                
                                if self.line_Edits["store"]["Price"][l_e] is not None:                      
                                
                                    self.line_Edits["store"]["Price"][l_e].setEnabled(False)
                                                                    
                        elif tlabel.text() =="صفحه واریزی ها":
                            
                            for l_e in self.line_Edits["deposit"]["Price"]:
                                
                                if self.line_Edits["deposit"]["Price"][l_e] is not None:                      
                                
                                    self.line_Edits["deposit"]["Price"][l_e].setEnabled(False)
                            
                            for l_e in self.line_Edits["deposit"]["Date"]:
                                
                                if self.line_Edits["deposit"]["Date"][l_e] is not None:                      
                                
                                    self.line_Edits["deposit"]["Date"][l_e].setEnabled(False)
                                    
                            for l_e in self.line_Edits["deposit"]["Time"]:
                                
                                if self.line_Edits["deposit"]["Time"][l_e] is not None:                      
                                
                                    self.line_Edits["deposit"]["Time"][l_e].setEnabled(False)
                                                                                
                        elif tlabel.text() == "صفحه برداشت ها":
                            
                            for l_e in self.line_Edits["withdraw"]["Price"]:
                                
                                if self.line_Edits["withdraw"]["Price"][l_e] is not None:                      
                                
                                    self.line_Edits["withdraw"]["Price"][l_e].setEnabled(False)
                            
                            for l_e in self.line_Edits["withdraw"]["Date"]:
                                
                                if self.line_Edits["withdraw"]["Date"][l_e] is not None:                      
                                
                                    self.line_Edits["withdraw"]["Date"][l_e].setEnabled(False)
                                    
                            for l_e in self.line_Edits["withdraw"]["Time"]:
                                
                                if self.line_Edits["withdraw"]["Time"][l_e] is not None:                      
                                
                                    self.line_Edits["withdraw"]["Time"][l_e].setEnabled(False)
                                                    
                        elif tlabel.text() == "صفحه حساب های دفتری":
                            
                            for l_e in self.line_Edits["ledger"]["Price"]:
                                
                                if self.line_Edits["ledger"]["Price"][l_e] is not None:                      
                                
                                    self.line_Edits["ledger"]["Price"][l_e].setEnabled(False)
                            
                            for l_e in self.line_Edits["ledger"]["Date"]:
                                
                                if self.line_Edits["ledger"]["Date"][l_e] is not None:                      
                                
                                    self.line_Edits["ledger"]["Date"][l_e].setEnabled(False)
                                    
                            for l_e in self.line_Edits["ledger"]["Time"]:
                                
                                if self.line_Edits["ledger"]["Time"][l_e] is not None:                      
                                
                                    self.line_Edits["ledger"]["Time"][l_e].setEnabled(False)
                            
                        cell_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable) 
                        
                         
            if (tlabel.text()=='صفحه انبار'):
                
                self.inventory_lock=1
                
            
            elif (tlabel.text()=='صفحه فروشگاه'):
                
                self.store_lock=1
                
                
            elif (tlabel.text()=="صفحه واریزی ها"):
                
                self.deposit_lock=1
                
                
            elif (tlabel.text()=="صفحه برداشت ها"):
                
                self.withdraw_lock=1
                    
                
            elif (tlabel.text()=="صفحه حساب های دفتری"):
                
                self.ledger_lock=1
                

        else:
            lock_action.setIcon(QIcon("Icons/unlock_icon.png"))
            plus_action.setDisabled(False)
            
            for i in range(table.rowCount()):        
                for j in range(table.columnCount()):
                    cell_item = table.item(i, j)
                    if cell_item is not None: 
                        try:
                            if tlabel.text() == 'صفحه انبار':
                            
                                for l_e in self.line_Edits["inventory"]["Num"]:
                                    if self.line_Edits["inventory"]["Num"][l_e] is not None:
                                    
                                        self.line_Edits["inventory"]["Num"][l_e].setDisabled(False)
                                
                                for l_e in self.line_Edits["inventory"]["Price"]:
                                    if self.line_Edits["inventory"]["Price"][l_e] is not None:
                                    
                                        self.line_Edits["inventory"]["Price"][l_e].setDisabled(False)
                                                
                            elif tlabel.text() == 'صفحه فروشگاه':
                                
                                for l_e in self.line_Edits["store"]["Num"]:
                                    
                                    if self.line_Edits["store"]["Num"][l_e] is not None:                      
                                    
                                        self.line_Edits["store"]["Num"][l_e].setDisabled(False)
                                        
                                for l_e in self.line_Edits["store"]["Price"]:
                                    
                                    if self.line_Edits["store"]["Price"][l_e] is not None:                      
                                    
                                        self.line_Edits["store"]["Price"][l_e].setDisabled(False)
                                                                        
                            elif tlabel.text() =="صفحه واریزی ها":
                                
                                for l_e in self.line_Edits["deposit"]["Price"]:
                                    
                                    if self.line_Edits["deposit"]["Price"][l_e] is not None:                      
                                    
                                        self.line_Edits["deposit"]["Price"][l_e].setDisabled(False)
                                
                                for l_e in self.line_Edits["deposit"]["Date"]:
                                    
                                    if self.line_Edits["deposit"]["Date"][l_e] is not None:                      
                                    
                                        self.line_Edits["deposit"]["Date"][l_e].setDisabled(False)
                                        
                                for l_e in self.line_Edits["deposit"]["Time"]:
                                    
                                    if self.line_Edits["deposit"]["Time"][l_e] is not None:                      
                                    
                                        self.line_Edits["deposit"]["Time"][l_e].setDisabled(False)
                                                                                    
                            elif tlabel.text() == "صفحه برداشت ها":
                                
                                for l_e in self.line_Edits["withdraw"]["Price"]:
                                    
                                    if self.line_Edits["withdraw"]["Price"][l_e] is not None:                      
                                    
                                        self.line_Edits["withdraw"]["Price"][l_e].setDisabled(False)
                                
                                for l_e in self.line_Edits["withdraw"]["Date"]:
                                    
                                    if self.line_Edits["withdraw"]["Date"][l_e] is not None:                      
                                    
                                        self.line_Edits["withdraw"]["Date"][l_e].setDisabled(False)
                                        
                                for l_e in self.line_Edits["withdraw"]["Time"]:
                                    
                                    if self.line_Edits["withdraw"]["Time"][l_e] is not None:                      
                                    
                                        self.line_Edits["withdraw"]["Time"][l_e].setDisabled(False)
                                                        
                            elif tlabel.text() == "صفحه حساب های دفتری":
                                
                                for l_e in self.line_Edits["ledger"]["Price"]:
                                    
                                    if self.line_Edits["ledger"]["Price"][l_e] is not None:                      
                                    
                                        self.line_Edits["ledger"]["Price"][l_e].setDisabled(False)
                                
                                for l_e in self.line_Edits["ledger"]["Date"]:
                                    
                                    if self.line_Edits["ledger"]["Date"][l_e] is not None:                      
                                    
                                        self.line_Edits["ledger"]["Date"][l_e].setDisabled(False)
                                        
                                for l_e in self.line_Edits["ledger"]["Time"]:
                                    
                                    if self.line_Edits["ledger"]["Time"][l_e] is not None:                      
                                    
                                        self.line_Edits["ledger"]["Time"][l_e].setDisabled(False)

                            cell_item.setFlags(cell_item.flags() | Qt.ItemIsEditable)
                                
                        except:
                            continue
                    else:
                        table.setItem(i, j, QTableWidgetItem(""))
                        cell_item = table.item(i, j)
                        try:
                            if tlabel.text() == 'صفحه انبار':
                            
                                for l_e in self.line_Edits["inventory"]["Num"]:
                                    if self.line_Edits["inventory"]["Num"][l_e] is not None:
                                    
                                        self.line_Edits["inventory"]["Num"][l_e].setDisabled(False)
                                
                                for l_e in self.line_Edits["inventory"]["Price"]:
                                    if self.line_Edits["inventory"]["Price"][l_e] is not None:
                                    
                                        self.line_Edits["inventory"]["Price"][l_e].setDisabled(False)
                                                
                            elif tlabel.text() == 'صفحه فروشگاه':
                                
                                for l_e in self.line_Edits["store"]["Num"]:
                                    
                                    if self.line_Edits["store"]["Num"][l_e] is not None:                      
                                    
                                        self.line_Edits["store"]["Num"][l_e].setDisabled(False)
                                        
                                for l_e in self.line_Edits["store"]["Price"]:
                                    
                                    if self.line_Edits["store"]["Price"][l_e] is not None:                      
                                    
                                        self.line_Edits["store"]["Price"][l_e].setDisabled(False)
                                                                        
                            elif tlabel.text() =="صفحه واریزی ها":
                                
                                for l_e in self.line_Edits["deposit"]["Price"]:
                                    
                                    if self.line_Edits["deposit"]["Price"][l_e] is not None:                      
                                    
                                        self.line_Edits["deposit"]["Price"][l_e].setDisabled(False)
                                
                                for l_e in self.line_Edits["deposit"]["Date"]:
                                    
                                    if self.line_Edits["deposit"]["Date"][l_e] is not None:                      
                                    
                                        self.line_Edits["deposit"]["Date"][l_e].setDisabled(False)
                                        
                                for l_e in self.line_Edits["deposit"]["Time"]:
                                    
                                    if self.line_Edits["deposit"]["Time"][l_e] is not None:                      
                                    
                                        self.line_Edits["deposit"]["Time"][l_e].setDisabled(False)
                                                                                    
                            elif tlabel.text() == "صفحه برداشت ها":
                                
                                for l_e in self.line_Edits["withdraw"]["Price"]:
                                    
                                    if self.line_Edits["withdraw"]["Price"][l_e] is not None:                      
                                    
                                        self.line_Edits["withdraw"]["Price"][l_e].setDisabled(False)
                                
                                for l_e in self.line_Edits["withdraw"]["Date"]:
                                    
                                    if self.line_Edits["withdraw"]["Date"][l_e] is not None:                      
                                    
                                        self.line_Edits["withdraw"]["Date"][l_e].setDisabled(False)
                                        
                                for l_e in self.line_Edits["withdraw"]["Time"]:
                                    
                                    if self.line_Edits["withdraw"]["Time"][l_e] is not None:                      
                                    
                                        self.line_Edits["withdraw"]["Time"][l_e].setDisabled(False)
                                                        
                            elif tlabel.text() == "صفحه حساب های دفتری":
                                
                                for l_e in self.line_Edits["ledger"]["Price"]:
                                    
                                    if self.line_Edits["ledger"]["Price"][l_e] is not None:                      
                                    
                                        self.line_Edits["ledger"]["Price"][l_e].setDisabled(False)
                                
                                for l_e in self.line_Edits["ledger"]["Date"]:
                                    
                                    if self.line_Edits["ledger"]["Date"][l_e] is not None:                      
                                    
                                        self.line_Edits["ledger"]["Date"][l_e].setDisabled(False)
                                        
                                for l_e in self.line_Edits["ledger"]["Time"]:
                                    
                                    if self.line_Edits["ledger"]["Time"][l_e] is not None:                      
                                    
                                        self.line_Edits["ledger"]["Time"][l_e].setDisabled(False)

                            
                            cell_item.setFlags(cell_item.flags() | Qt.ItemIsEditable)
                        except:
                            continue
            if (tlabel.text()=='صفحه انبار'):
                
                self.inventory_lock=0
                
            
            elif (tlabel.text()=='صفحه فروشگاه'):
                
                self.store_lock=0
                
                
            elif (tlabel.text()=="صفحه واریزی ها"):
                
                self.deposit_lock=0
                
                
            elif (tlabel.text()=="صفحه برداشت ها"):
                
                self.withdraw_lock=0
                    
                
            elif (tlabel.text()=="صفحه حساب های دفتری"):
                
                self.ledger_lock=0
                
                                           
    def SearchProduct(self, entry:QLineEdit):
        text = entry.text().strip() 
        items = inventory_table.findItems(text, Qt.MatchContains)  
        if text!="":
            if items:
                for item in items:
                    item_text = item.text()
                    if text.lower() == item_text.lower():
                        item.setBackground(Qt.yellow)  
                    else:
                        if item is not None:
                            item.setBackground(Qt.white)
            else:
                for i in range(inventory_table.rowCount()):
                    for j in range(inventory_table.colorCount()) : 
                        Item=inventory_table.item(i,j)  
                        if Item is not None:           
                            Item.setBackground(Qt.white)
                        
                              


    def Save(self,*tables:QTableWidget):
        for t in tables:
            connection = sqlite3.connect("DataBase.db")
            cursor = connection.cursor()
            
            if t.objectName()=="inventory_table":
                for i in range(t.rowCount()):        
                    P_Name=t.item(i,0).text()
                    P_Num=t.cellWidget(i,1).text()    
                    P_Price=t.cellWidget(i,2).text()
                    cursor.execute("CREATE TABLE IF NOT EXISTS Inventory (PName TEXT, Num TEXT, Price TEXT)")
                    cursor.execute("INSERT INTO Inventory VALUES (?,?,?)", (P_Name,P_Num,P_Price))
                    connection.commit()
                    connection.close()
                    
            elif t.objectName()=="store_table":
                for i in range(t.rowCount()):        
                    P_Name=t.item(i,0).text()
                    P_Num=t.cellWidget(i,1).text()    
                    P_Price=t.cellWidget(i,2).text()
                    cursor.execute("CREATE TABLE IF NOT EXISTS Store (PName TEXT, Num TEXT, Price TEXT)")
                    cursor.execute("INSERT INTO Store VALUES (?,?,?)", (P_Name,P_Num,P_Price))
                    connection.commit()
                    connection.close()
                    
            elif t.objectName()=="withdraw_table":
                for i in range(t.rowCount()):        
                    W_Price=t.cellWidget(i,0).text()
                    W_Date=t.cellWidget(i,1).text()
                    W_Time=t.cellWidget(i,2).text()
                    W_Des=t.item(i,3).text()
                    cursor.execute("CREATE TABLE IF NOT EXISTS Withdraw (Price TEXT, Date TEXT, Time TEXT , Des TEXT)")
                    cursor.execute("INSERT INTO Withdraw VALUES (?,?,?,?)", (W_Price,W_Date,W_Time,W_Des))
                    connection.commit()
                    connection.close()
                
            elif t.objectName()=="deposit_table":
                for i in range(t.rowCount()):        
                    D_Price=t.cellWidget(i,0).text()
                    D_Date=t.cellWidget(i,1).text()
                    D_Time=t.cellWidget(i,2).text()
                    D_Des=t.item(i,3).text()
                    cursor.execute("CREATE TABLE IF NOT EXISTS Deposit (Price TEXT, Date TEXT, Time TEXT , Des TEXT)")
                    cursor.execute("INSERT INTO Deposit VALUES (?,?,?,?)", (D_Price,D_Date,D_Time,D_Des))
                    connection.commit()
                    connection.close()
            
            elif t.objectName()=="ledger_table":
                for i in range(t.rowCount()):        
                    L_Name=t.cellWidget(i,0).text()
                    L_Date=t.cellWidget(i,1).text()
                    L_Time=t.cellWidget(i,2).text()
                    L_Price=t.cellWidget(i,3).text()
                    L_PName=t.item(i,4).text()
                    cursor.execute("CREATE TABLE IF NOT EXISTS Ledger (Name TEXT , Date TEXT, Time TEXT, Price TEXT , PName TEXT)")
                    cursor.execute("INSERT INTO Ledger VALUES (?,?,?,?,?)", (L_Name,L_Date,L_Time,L_Price,L_PName))
                    connection.commit()
                    connection.close()
                
                
                
               
        
        
        
        
def main():
    app = QApplication(sys.argv)
    window = AccountingApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
