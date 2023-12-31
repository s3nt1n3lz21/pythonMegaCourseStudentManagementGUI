from PyQt6.QtWidgets import (QApplication, QVBoxLayout, QLabel,
                             QWidget, QGridLayout, QLineEdit,
                             QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QComboBox, QToolBar,
                             QStatusBar, QMessageBox
                             )
from PyQt6.QtGui import QAction, QIcon
import sys
import sqlite3
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

# class DatabaseConnection:
#     def __init__(self, database_file="database.db"):
#         self.database_file = database_file
#
#     def connect(self):
#         connection = sqlite3.connect(self.database_file)
#         return connection

class DatabaseConnection:
    def __init__(self, host="localhost", user="root", password=os.environ.get("DATABASE_PASSWORD"), database="school"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        connection = mysql.connector.connect(host=self.host, user=self.user, password=self.password, database=self.database)
        return connection

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 800)

        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.about)
        help_menu_item.addAction(about_action)
        # Fix to show help menu on MAC OS
        about_action.setMenuRole(QAction.MenuRole.NoRole)

        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        search_action.triggered.connect(self.search)
        edit_menu_item.addAction(search_action)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        # Hide index column
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Create shortcut toolbar
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Detect a user clicking on a table cell
        self.table.cellClicked.connect(self.cell_clicked)

        # hello = QLabel("Hello World")
        # self.status_bar.addWidget(hello)

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        # Remove existing buttons from bottom status bar
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.status_bar.removeWidget(child)

        # Add edit and delete button to bottom status bar
        self.status_bar.addWidget(edit_button)
        self.status_bar.addWidget(delete_button)

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def load_data(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students")
        result = cursor.fetchall()
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        dialog = AddStudentDialog()
        dialog.exec()

    def search(self):
        dialog = SearchStudentDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()

    def search_student(self, search_text):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students WHERE name = %s", (search_text,))
        result = cursor.fetchall()
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        self.setText("A Student Management App.")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Get selected student name
        index = main_window.table.currentRow()
        student_name = main_window.table.item(index, 1).text()

        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText(student_name)
        self.student_name.setText(student_name)
        layout.addWidget(self.student_name)

        # Get selected course
        course = main_window.table.item(index, 2).text()

        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        course_index = courses.index(course)
        self.course_name.setCurrentIndex(course_index)
        layout.addWidget(self.course_name)

        # Get student number
        mobile_number = main_window.table.item(index, 3).text()

        self.mobile_number = QLineEdit()
        self.mobile_number.setPlaceholderText(mobile_number)
        self.mobile_number.setText(mobile_number)
        layout.addWidget(self.mobile_number)

        button = QPushButton("Update Student")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile_number.text()
        row_index = main_window.table.currentRow()
        id = main_window.table.item(row_index, 0).text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = %s, course = %s, mobile = %s WHERE id = %s", (name, course, mobile, id))
        connection.commit()

        cursor.close()
        connection.close()

        main_window.load_data()

        # Close the edit window
        self.close()

class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student")

        layout = QGridLayout()
        confirmation_label = QLabel("Are you sure you want to delete this student data?")
        yes_button = QPushButton("Yes")
        no_button = QPushButton("No")

        layout.addWidget(confirmation_label, 0, 0, 1, 2)
        layout.addWidget(yes_button, 1, 0)
        layout.addWidget(no_button, 1, 1)

        self.setLayout(layout)

        yes_button.clicked.connect(self.delete_student)
        no_button.clicked.connect(self.close)

    def delete_student(self):
        # Delete student
        row_index = main_window.table.currentRow()
        id = main_window.table.item(row_index, 0).text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM students WHERE id = %s", (id))
        connection.commit()

        cursor.close()
        connection.close()

        main_window.load_data()

        # Close window
        self.close()

        # Show Delete Success Message
        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The student data was successfully deleted")
        confirmation_widget.exec()

class SearchStudentDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.student_search = QLineEdit()
        self.student_search.setPlaceholderText("Name")
        layout.addWidget(self.student_search)

        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        search_text = self.student_search.text()
        main_window.search_student(search_text)

class AddStudentDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        self.mobile_number = QLineEdit()
        self.mobile_number.setPlaceholderText("Number")
        layout.addWidget(self.mobile_number)

        button = QPushButton("Add Student")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile_number.text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (%s, %s, %s)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()

app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())