# This Python file uses the following encoding: utf-8
import sys
import os
import time
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTextBrowser
from PySide6.QtCore import QDateTime
import datetime
import winreg

error_log_file = "error_log.txt"

class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        file_path = None
        if len(sys.argv) > 1:
            file_path = sys.argv[1]

        if file_path:
            file_time = os.path.getmtime(file_path)
            dt = datetime.datetime.fromtimestamp(file_time)
            formatted_time = dt.strftime('%Y-%m-%d %H:%M')
            self.label = QLabel(f"文件修改时间：{formatted_time}")
            self.time_edit = QLineEdit(formatted_time)
            self.original_time = file_time
        else:
            if file_path:
                with open(error_log_file, "a") as f:
                    f.write(f"不是有效的文件路径：{file_path}\n")
                QMessageBox.critical(self, "错误", "不是有效的文件路径。")
            else:
                with open(error_log_file, "a") as f:
                    f.write("未提供文件路径。\n")
                QMessageBox.critical(self, "错误", "未提供文件路径。")
            self.label = QLabel("文件修改时间：")
            self.time_edit = QLineEdit()

        self.save_button = QPushButton("保存修改时间")
        self.register_button = QPushButton("更新注册表")
        self.help_button = QPushButton("说明")

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.time_edit)
        self.layout.addWidget(self.save_button)
        self.layout.addWidget(self.register_button)
        self.layout.addWidget(self.help_button)

        self.save_button.clicked.connect(self.save_time)
        self.register_button.clicked.connect(self.update_registry)
        self.help_button.clicked.connect(self.show_help)

    def save_time(self):
        new_time_str = self.time_edit.text()
        try:
            new_dt = datetime.datetime.strptime(new_time_str, '%Y-%m-%d %H:%M')
            new_time = new_dt.timestamp()
            if len(sys.argv) > 1:
                file_path = sys.argv[1]
                os.utime(file_path, (os.path.getatime(file_path), new_time))
                QMessageBox.information(self, "成功", "文件修改时间已成功修改。")
            else:
                with open(error_log_file, "a") as f:
                    f.write("没有文件路径可用。\n")
                QMessageBox.critical(self, "错误", "没有文件路径可用。")
        except Exception as e:
            with open(error_log_file, "a") as f:
                f.write(f"修改时间失败：{str(e)}\n")
            QMessageBox.critical(self, "错误", f"修改时间失败：{str(e)}")

    def update_registry(self):
        exe_path = os.path.abspath(sys.argv[0])
        dir_key_path = r"Directory\shell\Dirtinmer"
        dir_command_key_path = r"Directory\shell\Dirtinmer\command"
        file_key_path = r"*\shell\Dirtinmer"
        file_command_key_path = r"*\shell\Dirtinmer\command"
        dir_registry_updated = False
        file_registry_updated = False

        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, dir_key_path, 0, winreg.KEY_READ) as key:
                winreg.SetValueEx(key, "MUIVerb", 0, winreg.REG_SZ, "修改时间")
                with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, dir_command_key_path, 0, winreg.KEY_READ) as command_key:
                    winreg.SetValueEx(command_key, None, 0, winreg.REG_SZ, f'"{exe_path}" %1')
        except FileNotFoundError as e:
            with open(error_log_file, "a") as f:
                f.write(f"尝试打开注册表项 {dir_key_path} 失败，创建该项。错误信息：{str(e)}\n")
            dir_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, dir_key_path)
            winreg.SetValueEx(dir_key, "MUIVerb", 0, winreg.REG_SZ, "修改时间")
            dir_command_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, dir_command_key_path)
            winreg.SetValueEx(dir_command_key, None, 0, winreg.REG_SZ, f'"{exe_path}" %1')
            dir_registry_updated = True
        except Exception as e:
            with open(error_log_file, "a") as f:
                f.write(f"处理注册表项 {dir_key_path} 时发生未知错误。错误信息：{str(e)}\n")

        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, file_key_path, 0, winreg.KEY_READ) as key:
                winreg.SetValueEx(key, "MUIVerb", 0, winreg.REG_SZ, "修改时间")
        except FileNotFoundError as e:
            with open(error_log_file, "a") as f:
                f.write(f"尝试打开注册表项 {file_key_path} 失败，创建该项。错误信息：{str(e)}\n")
            file_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, file_key_path)
            winreg.SetValueEx(file_key, "MUIVerb", 0, winreg.REG_SZ, "修改时间")
            file_registry_updated = True
        except Exception as e:
            with open(error_log_file, "a") as f:
                f.write(f"处理注册表项 {file_key_path} 时发生未知错误。错误信息：{str(e)}\n")

        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, file_command_key_path, 0, winreg.KEY_READ) as key:
                winreg.SetValueEx(key, None, 0, winreg.REG_SZ, f'"{exe_path}" %1')
        except FileNotFoundError as e:
            with open(error_log_file, "a") as f:
                f.write(f"尝试打开注册表项 {file_command_key_path} 失败，创建该项。错误信息：{str(e)}\n")
            file_command_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, file_command_key_path)
            winreg.SetValueEx(file_command_key, None, 0, winreg.REG_SZ, f'"{exe_path}" %1')
            file_registry_updated = True
        except Exception as e:
            with open(error_log_file, "a") as f:
                f.write(f"处理注册表项 {file_command_key_path} 时发生未知错误。错误信息：{str(e)}\n")

        message = "注册表更新成功。"
        if dir_registry_updated:
            message += " 目录注册表项已创建或更新。"
        if file_registry_updated:
            message += " 文件注册表项已创建或更新。"
        QMessageBox.information(self, "成功", message)

    def show_help(self):
        help_text = """
        本程序功能说明：
        - 可以修改文件的修改时间。
        - 提供更新注册表的功能，在注册表中创建相关项，以便在文件或目录右键菜单中添加“修改时间”选项，方便快速修改文件时间。
        """
        help_dialog = QMessageBox(QMessageBox.Information, "说明", help_text)
        help_dialog.exec()

if __name__ == "__main__":
    # 检查错误日志文件
    if os.path.exists(error_log_file):
        if os.path.getsize(error_log_file) > 100 * 1024:
            with open(error_log_file, "w") as f:
                f.write("")
    app = QApplication([])
    window = Widget()
    window.show()
    sys.exit(app.exec())
