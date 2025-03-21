import sys
import sqlite3
import json
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTextEdit, QLabel,
                             QTableWidget, QTableWidgetItem, QDialog, QFileDialog, QHeaderView, QMessageBox, QSplitter,
                             QFrame, QStyleFactory, QComboBox, QMainWindow, QToolBar, QStatusBar)
from PyQt6.QtCore import QDate, Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QColor, QAction
from persiantools.jdatetime import JalaliDate


# Resource path helper function
def resource_path(relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
                # PyInstaller creates a temp folder and stores path in _MEIPASS
                base_path = sys._MEIPASS
        except Exception:
                # If not running as bundled app, use the script's directory
                base_path = os.path.abspath(os.path.dirname(sys.argv[0]))

        return os.path.join(base_path, relative_path)


# Get the application data directory
def get_data_dir():
        """Get the appropriate data directory based on the platform"""
        if getattr(sys, 'frozen', False):
                # If the application is frozen (PyInstaller bundle)
                if sys.platform == 'darwin':  # macOS
                        # On macOS, use ~/Library/Application Support/YourAppName
                        app_name = "IT_Problem_Tracker"
                        data_dir = os.path.join(os.path.expanduser("~"), "Library", "Application Support", app_name)
                elif sys.platform == 'win32':  # Windows
                        # On Windows, use %APPDATA%\YourAppName
                        app_name = "IT_Problem_Tracker"
                        data_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser("~")), app_name)
                else:  # Linux and other platforms
                        # On Linux, use ~/.local/share/YourAppName
                        app_name = "it_problem_tracker"
                        data_dir = os.path.join(os.path.expanduser("~"), ".local", "share", app_name)
        else:
                # If running in development mode, use the current directory
                data_dir = os.path.abspath(os.path.dirname(sys.argv[0]))

        # Create the directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)

        return data_dir


# Get database path
def get_db_path():
        """Get the full path to the database file"""
        return os.path.join(get_data_dir(), "problems.db")


# Database Setup
def init_db():
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                subject TEXT,
                problem TEXT,
                solution TEXT
            )''')
        conn.commit()
        conn.close()
        print(f"Database initialized at: {db_path}")


# Backup Functionality
def export_backup():
        options = QFileDialog.Option.DontUseNativeDialog
        file_path, _ = QFileDialog.getSaveFileName(None, "Save Backup", "backup.bak", "Backup Files (*.bak)",
                                                   options=options)
        if file_path:
                conn = sqlite3.connect(get_db_path())
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM problems")
                data = cursor.fetchall()

                with open(file_path, "w", encoding="utf-8") as file:
                        json.dump(data, file, ensure_ascii=False, indent=4)

                conn.close()
                QMessageBox.information(None, "Backup Complete", f"Backup saved as {file_path}")


def import_backup():
        options = QFileDialog.Option.DontUseNativeDialog
        file_path, _ = QFileDialog.getOpenFileName(None, "Open Backup", "", "Backup Files (*.bak)", options=options)
        if file_path:
                try:
                        conn = sqlite3.connect(get_db_path())
                        cursor = conn.cursor()

                        with open(file_path, "r", encoding="utf-8") as file:
                                data = json.load(file)

                        cursor.execute("DELETE FROM problems")
                        for record in data:
                                cursor.execute("INSERT INTO problems VALUES (?, ?, ?, ?, ?)", record)

                        conn.commit()
                        conn.close()
                        QMessageBox.information(None, "Restore Complete", f"Database restored from {file_path}")
                        return True
                except Exception as e:
                        QMessageBox.critical(None, "Error", f"Failed to restore backup: {str(e)}")
                        return False


# Entry Dialog (for both New and Edit operations)
class EntryDialog(QDialog):
        def __init__(self, parent=None, record_id=None):
                super().__init__(parent)
                self.record_id = record_id
                self.is_edit_mode = record_id is not None

                title = "Edit Problem Entry" if self.is_edit_mode else "New Problem Entry"
                self.setWindowTitle(title)
                self.setGeometry(400, 200, 800, 700)
                self.setStyleSheet("""
            QDialog {
                background-color: #30302E;
                color: #FFFFFF;
            }
            QLabel { 
                font-weight: bold; 
                color: #FFFFFF;
                background: transparent;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #4A4A48;
                border-radius: 4px;
                padding: 8px;
                background-color: #3A3A38;
                color: #FFFFFF;
            }
            QPushButton {
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                background-color: #4A4A48;
                color: #FFFFFF;
            }
            QPushButton:hover {
                background-color: #5A5A58;
            }
            """)

                layout = QVBoxLayout()

                # Fields
                date_layout = QHBoxLayout()
                date_label = QLabel("Date:")
                self.date = QLabel(str(JalaliDate.today()))
                date_layout.addWidget(date_label)
                date_layout.addWidget(self.date)
                date_layout.addStretch()
                layout.addLayout(date_layout)

                subject_label = QLabel("Subject:")
                layout.addWidget(subject_label)
                self.subject = QLineEdit()
                self.subject.setPlaceholderText("Enter a descriptive subject for the problem")
                self.subject.setLayoutDirection(Qt.LayoutDirection.RightToLeft)  # Right-to-left for Persian
                layout.addWidget(self.subject)
                subject_label.setStyleSheet(
                        "font-weight: bold; color: #FFFFFF; margin-top: 10px; background: transparent;")

                problem_label = QLabel("Problem Description:")
                layout.addWidget(problem_label)
                self.problem = QTextEdit()
                self.problem.setPlaceholderText("Describe the problem in detail...")
                self.problem.setMinimumHeight(150)
                self.problem.setLayoutDirection(Qt.LayoutDirection.RightToLeft)  # Right-to-left for Persian
                layout.addWidget(self.problem)
                problem_label.setStyleSheet(
                        "font-weight: bold; color: #FFFFFF; margin-top: 10px; background: transparent;")

                solution_label = QLabel("Solution:")
                layout.addWidget(solution_label)
                self.solution = QTextEdit()
                self.solution.setPlaceholderText("Describe the solution or workaround...")
                self.solution.setMinimumHeight(300)
                self.solution.setLayoutDirection(Qt.LayoutDirection.RightToLeft)  # Right-to-left for Persian
                layout.addWidget(self.solution)
                solution_label.setStyleSheet(
                        "font-weight: bold; color: #FFFFFF; margin-top: 10px; background: transparent;")

                # Buttons
                button_layout = QHBoxLayout()
                self.save_btn = QPushButton("Save Changes" if self.is_edit_mode else "Save")
                self.save_btn.setStyleSheet("background-color: #296F62; color: #000000;")
                self.save_btn.clicked.connect(self.save_entry)

                self.cancel_btn = QPushButton("Cancel")
                self.cancel_btn.setStyleSheet("background-color: #7A1818; color: #000000;")
                self.cancel_btn.clicked.connect(self.reject)

                button_layout.addWidget(self.cancel_btn)
                button_layout.addWidget(self.save_btn)
                layout.addLayout(button_layout)

                self.setLayout(layout)

                # If in edit mode, load the existing data
                if self.is_edit_mode:
                        self.load_data()

        def load_data(self):
                conn = sqlite3.connect(get_db_path())
                cursor = conn.cursor()
                cursor.execute("SELECT date, subject, problem, solution FROM problems WHERE id = ?", (self.record_id,))
                record = cursor.fetchone()
                conn.close()

                if record:
                        self.date.setText(record[0])
                        self.subject.setText(record[1])
                        self.problem.setPlainText(record[2])
                        self.solution.setPlainText(record[3])

        def save_entry(self):
                # Validate inputs
                if not self.subject.text().strip():
                        QMessageBox.warning(self, "Validation Error", "Subject cannot be empty!")
                        return

                conn = sqlite3.connect(get_db_path())
                cursor = conn.cursor()

                try:
                        if self.is_edit_mode:
                                cursor.execute(
                                        "UPDATE problems SET date=?, subject=?, problem=?, solution=? WHERE id=?",
                                        (self.date.text(), self.subject.text(), self.problem.toPlainText(),
                                         self.solution.toPlainText(), self.record_id))
                        else:
                                cursor.execute(
                                        "INSERT INTO problems (date, subject, problem, solution) VALUES (?, ?, ?, ?)",
                                        (str(JalaliDate.today()), self.subject.text(), self.problem.toPlainText(),
                                         self.solution.toPlainText()))

                        conn.commit()
                        conn.close()
                        self.accept()
                except Exception as e:
                        QMessageBox.critical(self, "Error", f"Failed to save entry: {str(e)}")
                        conn.close()


# Problem Detail View Dialog
class ProblemDetailDialog(QDialog):
        def __init__(self, parent=None, record_id=None):
                super().__init__(parent)
                self.record_id = record_id
                self.setWindowTitle("Problem Details")
                self.setGeometry(400, 200, 900, 600)
                self.setStyleSheet("""
            QDialog {
                background-color: #30302E;
                color: #FFFFFF;
            }
            QLabel { 
                color: #FFFFFF;
                background: transparent;
            }
            QTextEdit {
                border: 1px solid #4A4A48;
                border-radius: 4px;
                padding: 8px;
                background-color: #3A3A38;
                color: #FFFFFF;
            }
            QPushButton {
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                opacity: 0.8;
            }
            """)

                # Get data
                conn = sqlite3.connect(get_db_path())
                cursor = conn.cursor()
                cursor.execute("SELECT date, subject, problem, solution FROM problems WHERE id = ?", (self.record_id,))
                self.record = cursor.fetchone()
                conn.close()

                if not self.record:
                        QMessageBox.critical(self, "Error", "Record not found!")
                        self.reject()
                        return

                layout = QVBoxLayout()

                # Date
                date_label = QLabel(f"Date: {self.record[0]}")
                date_label.setStyleSheet("font-weight: bold; color: #CCCCCC; background: transparent;")
                layout.addWidget(date_label)

                # Problem
                problem_header = QLabel("Problem Description:")
                problem_header.setStyleSheet(
                        "font-weight: bold; color: #FFFFFF; margin-top: 10px; background: transparent;")
                layout.addWidget(problem_header)

                problem_text = QTextEdit()
                problem_text.setPlainText(self.record[2])
                problem_text.setReadOnly(True)
                problem_text.setLayoutDirection(Qt.LayoutDirection.RightToLeft)  # Right-to-left for Persian
                layout.addWidget(problem_text)

                # Solution
                solution_header = QLabel("Solution:")
                solution_header.setStyleSheet(
                        "font-weight: bold; color: #FFFFFF; margin-top: 10px; background: transparent;")
                layout.addWidget(solution_header)

                solution_text = QTextEdit()
                solution_text.setPlainText(self.record[3])
                solution_text.setReadOnly(True)
                solution_text.setLayoutDirection(Qt.LayoutDirection.RightToLeft)  # Right-to-left for Persian
                layout.addWidget(solution_text)

                # Buttons
                button_layout = QHBoxLayout()

                edit_btn = QPushButton("Edit")
                edit_btn.setStyleSheet("background-color: #296F62; color: #000000;")
                edit_btn.clicked.connect(self.edit_record)

                delete_btn = QPushButton("Delete")
                delete_btn.setStyleSheet("background-color: #7A1818; color: #000000;")
                delete_btn.clicked.connect(self.delete_record)

                button_layout.addWidget(edit_btn)
                button_layout.addWidget(delete_btn)
                layout.addLayout(button_layout)

                self.setLayout(layout)

        def edit_record(self):
                self.close()
                dialog = EntryDialog(self.parent(), self.record_id)
                if dialog.exec():
                        self.parent().load_entries()

        def delete_record(self):
                reply = QMessageBox.question(self, "Confirm Deletion",
                                             "Are you sure you want to delete this record?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                             QMessageBox.StandardButton.No)

                if reply == QMessageBox.StandardButton.Yes:
                        conn = sqlite3.connect(get_db_path())
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM problems WHERE id = ?", (self.record_id,))
                        conn.commit()
                        conn.close()
                        self.accept()  # Close and signal success


# Custom RTL Text Delegate for Table Items
from PyQt6.QtWidgets import QStyledItemDelegate
from PyQt6.QtGui import QTextDocument
from PyQt6.QtCore import QRectF


class RTLTextDelegate(QStyledItemDelegate):
        def paint(self, painter, option, index):
                text = index.data(Qt.ItemDataRole.DisplayRole)
                if text:
                        painter.save()

                        doc = QTextDocument()
                        doc.setHtml(f'<div dir="rtl" style="text-align:right;">{text}</div>')

                        option.rect.adjust(5, 5, -5, -5)  # Add some padding
                        painter.translate(option.rect.topLeft())

                        ctx = QRectF(0, 0, option.rect.width(), option.rect.height())
                        doc.drawContents(painter, ctx)

                        painter.restore()
                else:
                        super().paint(painter, option, index)


# Main Application Window
class MainApp(QMainWindow):
        def __init__(self):
                super().__init__()
                self.setWindowTitle("IT Problem Tracker")
                self.setGeometry(300, 100, 1200, 800)
                self.setStyleSheet("""
        QMainWindow {
            background-color: #30302E;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 10pt;
            color: #FFFFFF;
        }
        QWidget {
            background-color: #30302E;
            color: #FFFFFF;
        }
        QPushButton {
            padding: 8px 16px;
            border-radius: 4px;
            border: none;
            font-weight: bold;
            background-color: #4A4A48;
            color: #FFFFFF;
        }
        QPushButton:hover {
            background-color: #5A5A58;
        }
        QLineEdit, QTextEdit {
            padding: 8px;
            border: 1px solid #4A4A48;
            border-radius: 4px;
            background-color: #3A3A38;
            color: #FFFFFF;
            selection-background-color: #5E9CF9;
            selection-color: #30302E;
        }
        QComboBox {
            padding: 8px;
            border: 1px solid #4A4A48;
            border-radius: 4px;
            background-color: #3A3A38;
            color: #FFFFFF;
            selection-background-color: #5E9CF9;
        }
        QComboBox QAbstractItemView {
            background-color: #3A3A38;
            color: #FFFFFF;
            selection-background-color: #5E9CF9;
            selection-color: #30302E;
        }
        QTableWidget {
            gridline-color: #4A4A48;
            background-color: #3A3A38;
            color: #FFFFFF;
            selection-background-color: #5E9CF9;
            selection-color: #30302E;
            alternate-background-color: #454543;
            border: 1px solid #4A4A48;
            border-radius: 4px;
        }
        QHeaderView::section {
            background-color: #252523;
            color: #FFFFFF;
            padding: 8px;
            font-weight: bold;
            border: none;
            border-right: 1px solid #4A4A48;
        }
        QScrollBar:vertical {
            background-color: #3A3A38;
            width: 14px;
            margin: 15px 3px 15px 3px;
            border: 1px solid #4A4A48;
            border-radius: 4px;
        }
        QScrollBar::handle:vertical {
            background-color: #4A4A48;
            min-height: 20px;
            border-radius: 2px;
        }
        QScrollBar::add-line:vertical {
            background: none;
            height: 0px;
        }
        QScrollBar::sub-line:vertical {
            background: none;
            height: 0px;
        }
        QStatusBar {
            background-color: #252523;
            color: #FFFFFF;
        }
        QLabel {
            color: #FFFFFF;
            background: transparent;
        }
        QFrame {
            background-color: #4A4A48;
        }
        QMenu {
            background-color: #3A3A38;
            color: #FFFFFF;
            border: 1px solid #4A4A48;
        }
        QMenu::item:selected {
            background-color: #5E9CF9;
            color: #30302E;
        }
        QToolTip {
            background-color: #3A3A38;
            color: #FFFFFF;
            border: 1px solid #4A4A48;
        }
        QTableWidget::item {
            direction: rtl;
            text-align: right;
        }
    """)

                # Create central widget
                central_widget = QWidget()
                self.setCentralWidget(central_widget)
                main_layout = QVBoxLayout(central_widget)

                # Set application layout direction to RTL
                self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

                # Create toolbar
                self.create_toolbar()

                # Create status bar
                self.statusBar = QStatusBar()
                self.setStatusBar(self.statusBar)
                self.status_label = QLabel("Ready")
                self.status_label.setStyleSheet("background: transparent;")
                self.statusBar.addPermanentWidget(self.status_label)

                # Top controls
                top_layout = QHBoxLayout()

                # Search
                search_layout = QVBoxLayout()
                self.search_bar = QLineEdit()
                self.search_bar.setPlaceholderText("Search by subject, problem, or solution...")
                self.search_bar.textChanged.connect(self.search)
                self.search_bar.setLayoutDirection(Qt.LayoutDirection.RightToLeft)  # Right-to-left for Persian
                search_layout.addWidget(self.search_bar)
                top_layout.addLayout(search_layout, 3)

                # Filter dropdown
                filter_layout = QVBoxLayout()
                self.filter_combo = QComboBox()
                self.filter_combo.addItems(["All", "Subject", "Problem", "Solution"])
                self.filter_combo.currentTextChanged.connect(self.search)
                self.filter_combo.setLayoutDirection(Qt.LayoutDirection.RightToLeft)  # Right-to-left for Persian
                filter_layout.addWidget(self.filter_combo)
                top_layout.addLayout(filter_layout, 1)

                # Actions panel
                actions_layout = QVBoxLayout()
                actions_panel = QHBoxLayout()

                self.new_btn = QPushButton("New")
                self.new_btn.setStyleSheet("background-color: #296F62; color: #000000;")
                self.new_btn.clicked.connect(self.add_new_entry)
                actions_panel.addWidget(self.new_btn)

                actions_layout.addLayout(actions_panel)
                top_layout.addLayout(actions_layout, 2)

                main_layout.addLayout(top_layout)

                # Add separator
                separator = QFrame()
                separator.setFrameShape(QFrame.Shape.HLine)
                separator.setFrameShadow(QFrame.Shadow.Sunken)
                separator.setStyleSheet("background-color: #4A4A48; margin: 10px 0;")
                main_layout.addWidget(separator)

                # Table view
                table_label = QLabel("Problems List:")
                table_label.setStyleSheet(
                        "font-weight: bold; font-size: 14px; margin-top: 5px; background: transparent;")
                main_layout.addWidget(table_label)

                # Double-click instruction
                instruction_label = QLabel("Double-click on any row to view details, edit or delete")
                instruction_label.setStyleSheet(
                        "color: #CCCCCC; font-style: italic; margin-bottom: 5px; background: transparent;")
                main_layout.addWidget(instruction_label)

                self.table = QTableWidget()
                self.table.setColumnCount(4)

                # Set table to RTL layout direction
                self.table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

                # Reverse the column order for better RTL experience
                self.table.setHorizontalHeaderLabels(["Solution", "Problem", "Subject", "Date"])

                # Set RTL alignment for header
                self.table.horizontalHeader().setLayoutDirection(Qt.LayoutDirection.RightToLeft)

                # Add custom delegate for RTL text direction
                rtl_delegate = RTLTextDelegate()
                self.table.setItemDelegate(rtl_delegate)

                self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Disable direct editing
                self.table.setAlternatingRowColors(True)
                self.table.verticalHeader().setVisible(False)  # Hide row numbers
                self.table.verticalHeader().setDefaultSectionSize(60)  # Increase row height
                self.table.setShowGrid(True)

                # Set column widths
                self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Date
                self.table.horizontalHeader().setSectionResizeMode(2,
                                                                   QHeaderView.ResizeMode.ResizeToContents)  # Subject
                self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Problem
                self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Solution

                self.table.doubleClicked.connect(self.show_details)  # Double-click to view details

                # Additional stylesheet for table items to ensure RTL text flow
                self.table.setStyleSheet("""
            QTableWidget::item {
                direction: rtl;
                text-align: right;
            }
            """)

                main_layout.addWidget(self.table)

                # Display application data directory in status bar temporarily
                self.status_label.setText(f"Data directory: {get_data_dir()}")
                # Load entries after a short delay
                self.load_entries()

        def create_toolbar(self):
                toolbar = QToolBar("Main Toolbar")
                toolbar.setIconSize(QSize(24, 24))
                toolbar.setMovable(False)
                toolbar.setStyleSheet("""
            QToolBar {
                background-color: #252523;
                spacing: 5px;
                padding: 5px;
                border-bottom: 1px solid #4A4A48;
            }
            QToolButton {
                background-color: transparent;
                color: #FFFFFF;
                padding: 8px;
                border-radius: 4px;
            }
            QToolButton:hover {
                background-color: #3A3A38;
            }
            QToolBar::separator {
                background-color: #4A4A48;
                width: 1px;
                margin: 0px 10px;
            }
            """)

                # Export backup action
                export_action = QAction("Export Backup", self)
                export_action.triggered.connect(export_backup)
                toolbar.addAction(export_action)

                # Import backup action
                import_action = QAction("Import Backup", self)
                import_action.triggered.connect(self.import_and_refresh)
                toolbar.addAction(import_action)

                self.addToolBar(toolbar)

        def load_entries(self, limit=20):
                """Load entries from database with optional limit"""
                conn = sqlite3.connect(get_db_path())
                cursor = conn.cursor()
                cursor.execute("SELECT id, date, subject, problem, solution FROM problems ORDER BY id DESC LIMIT ?",
                               (limit,))
                records = cursor.fetchall()
                conn.close()

                self.display_records(records)
                self.status_label.setText(f"Showing {len(records)} records")
                self.status_label.setStyleSheet("background: transparent;")

        def display_records(self, records):
                """Display the given records in the table"""
                self.table.setRowCount(len(records))
                for row_idx, row_data in enumerate(records):
                        record_id = row_data[0]

                        # Truncate long text for display
                        truncate_length = 100

                        # Date (column index changed for RTL)
                        date_item = QTableWidgetItem(str(row_data[1]))
                        date_item.setTextAlignment(int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter))
                        self.table.setItem(row_idx, 3, date_item)  # Changed column index for RTL

                        # Subject (column index changed for RTL)
                        subject_item = QTableWidgetItem(row_data[2])
                        subject_item.setTextAlignment(int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter))
                        subject_item.setToolTip(row_data[2])
                        self.table.setItem(row_idx, 2, subject_item)  # Changed column index for RTL

                        # Problem (truncated) (column index changed for RTL)
                        problem_text = row_data[3]
                        problem_display = problem_text[:truncate_length] + "..." if len(
                                problem_text) > truncate_length else problem_text
                        problem_item = QTableWidgetItem(problem_display)
                        problem_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                        problem_item.setToolTip(problem_text)
                        self.table.setItem(row_idx, 1, problem_item)  # Changed column index for RTL

                        # Solution (truncated) (column index changed for RTL)
                        solution_text = row_data[4]
                        solution_display = solution_text[:truncate_length] + "..." if len(
                                solution_text) > truncate_length else solution_text
                        solution_item = QTableWidgetItem(solution_display)
                        solution_item.setTextAlignment(int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter))
                        solution_item.setToolTip(solution_text)
                        self.table.setItem(row_idx, 0, solution_item)  # Changed column index for RTL

                        # Store record ID in each item for future reference
                        for col in range(4):
                                item = self.table.item(row_idx, col)
                                item.setData(Qt.ItemDataRole.UserRole, record_id)

        def search(self):
                """Search database based on keyword and filter"""
                keyword = self.search_bar.text()
                filter_by = self.filter_combo.currentText()

                conn = sqlite3.connect("problems.db")
                cursor = conn.cursor()

                if not keyword:
                        # If search is empty, show recent entries
                        self.load_entries()
                        return

                # Build query based on filter
                if filter_by == "All":
                        query = """SELECT id, date, subject, problem, solution FROM problems 
                    WHERE subject LIKE ? OR problem LIKE ? OR solution LIKE ? 
                    ORDER BY id DESC"""
                        params = (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
                elif filter_by == "Subject":
                        query = """SELECT id, date, subject, problem, solution FROM problems 
                    WHERE subject LIKE ? ORDER BY id DESC"""
                        params = (f"%{keyword}%",)
                elif filter_by == "Problem":
                        query = """SELECT id, date, subject, problem, solution FROM problems 
                    WHERE problem LIKE ? ORDER BY id DESC"""
                        params = (f"%{keyword}%",)
                elif filter_by == "Solution":
                        query = """SELECT id, date, subject, problem, solution FROM problems 
                    WHERE solution LIKE ? ORDER BY id DESC"""
                        params = (f"%{keyword}%",)

                cursor.execute(query, params)
                records = cursor.fetchall()
                conn.close()

                self.display_records(records)
                self.status_label.setText(f"Found {len(records)} matching records")

        def add_new_entry(self):
                """Open dialog to add a new entry"""
                dialog = EntryDialog(self)
                if dialog.exec():
                        self.load_entries()
                        self.status_label.setText("New problem added successfully")

        def show_details(self, index):
                """Show detailed view of a problem when double-clicked"""
                record_id = self.table.item(index.row(), index.column()).data(Qt.ItemDataRole.UserRole)
                if record_id:
                        dialog = ProblemDetailDialog(self, record_id)
                        if dialog.exec():  # This will be true if delete was successful
                                self.load_entries()
                                self.status_label.setText("Problem deleted successfully")

        def import_and_refresh(self):
                """Import backup and refresh the view if successful"""
                if import_backup():
                        self.load_entries()
                        self.status_label.setText("Database restored from backup")


if __name__ == "__main__":
        init_db()
        app = QApplication(sys.argv)

        # In PyQt6, we use setStyle differently
        app.setStyle("Fusion")  # More modern look

        window = MainApp()
        window.show()
        sys.exit(app.exec())