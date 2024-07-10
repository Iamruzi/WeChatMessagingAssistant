import sys
from datetime import datetime

from wxauto import *

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,QWidget, QTextEdit, QMessageBox,QMenuBar, QAction,QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap,QIcon
from PyQt5.QtCore import QFile


class MainWindow(QMainWindow):
    def __init__(self):
        """
        初始化微信群发工具自动化版界面和设置。
        
        Args:
            无参数。
        
        Returns:
            无返回值。
        
        """
        super().__init__()
        
        # UI 初始化全局变量  # 
        self.users_list = []
        self.send_text_flag = False
        self.send_image_flag = False
        self.send_file_flag = False

        # 初始化UI  # 
        self.setWindowTitle("微信群发工具 自动化版 v0.02 by Iamruzi")
        QMessageBox.warning(self, "注意", "使用前请先登录微信客户端，并确保微信处于运行状态。脚本不要放在中文路径下，否则可能无法正常运行。")
        self.resize(400, 300)
        
        # 创建主窗口 witget类
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # 创建主布局
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # 创建菜单栏
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        # 创建帮助菜单
        self.help_menu = self.menu_bar.addMenu("菜单")

        # 创建帮助选项
        self.help_action = QAction("用法说明", self)
        self.help_action.triggered.connect(self.show_help_dialog)
        self.help_menu.addAction(self.help_action)

        # 1. 创建群组文件
        self.file_button = QPushButton("1.📂选择群组信息文件")
        self.file_button.clicked.connect(self.open_file_dialog)
        self.layout.addWidget(self.file_button)

        self.file_content_label = QLabel("群组信息:")
        self.layout.addWidget(self.file_content_label)

        self.file_content_text = QTextEdit()
        self.file_content_text.setReadOnly(True)
        self.layout.addWidget(self.file_content_text)

        # 2. 输入内如：包括文字，图片，文件
        self.message_label = QLabel("2.📜输入群发内容:")
        self.layout.addWidget(self.message_label)

        self.text_layout = QHBoxLayout()
        self.message_label = QLabel("🔗文字（可选）:")
        self.message_label.setFixedWidth(200)
        self.text_layout.addWidget(self.message_label)

        self.message_text = QTextEdit()
        self.text_layout.addWidget(self.message_text)
        self.message_text.textChanged.connect(self.send_text)
        self.layout.addLayout(self.text_layout)

        self.image_layout = QHBoxLayout()
        self.image_button = QPushButton("🔗图片（可选）")
        self.image_button.setFixedWidth(200)
        self.image_button.clicked.connect(self.send_image)
        self.image_layout.addWidget(self.image_button)
        self.image_label = QLabel("图片预览")
        self.image_layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        self.layout.addLayout(self.image_layout)

        self.file_layout = QHBoxLayout()
        self.file_button = QPushButton("🔗文件（可选）")
        self.file_button.setFixedWidth(200)
        self.file_button.clicked.connect(self.send_file)
        self.file_layout.addWidget(self.file_button)
        self.file_label = QLabel("文件路径")
        self.file_layout.addWidget(self.file_label, alignment=Qt.AlignCenter)
        self.layout.addLayout(self.file_layout)

        # 获取当前页面用户会话
        self.wx_users_get_button = QPushButton("获取当前页面用户会话(可选)")
        self.wx_users_get_button.clicked.connect(self.get_weixin_session)
        self.layout.addWidget(self.wx_users_get_button)
        
        # 3. 开始群发
        self.send_button = QPushButton("3.📤开始群发（点击后，等待操作，不要操作键鼠）")
        self.send_button.clicked.connect(self.start_broadcast)
        self.layout.addWidget(self.send_button)

        # 输出日志
        self.log_label = QLabel("📝日志输出:")
        self.layout.addWidget(self.log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.layout.addWidget(self.log_text)

        # 设置底部版权信息文本
        self.copyright_text_label = QLabel()
        self.layout.addWidget(self.copyright_text_label)
        copyright_text = "🖥版权所有 © 2024，作者：Iamruzi"
        self.copyright_text_label.setText(copyright_text)

        # UI 结束后，初始化其他功能  # 
        # 初始化微信 
        self.init_weixin()

        # 默认打开default.txt文件
        default_file_path = "default.txt"
        if QFile.exists(default_file_path):
            self.log(f"为您加载默认群组文件: {default_file_path}")
            self.load_file(default_file_path)

    def show_help_dialog(self):
        """
        显示软件使用说明。
        Args:
            无参数。
        Returns:
            无返回值。
        """
        QMessageBox.information(self, "用法说明", '''前提 使用前先登陆微信（不要含中文路径，且微信语言要是中文）\n 
                                1. 准备群发用户文件\n
                                将需要群发的群名 按一行一个 放入一个文件（如果不想手动，可以使用软件里获取当前页面用户会话按钮，慢慢那获取，然后复制-排版）\n
                                2. 打开软件\n
                                选择群组信息文件（选择好后，会加载到群组信息文本框），如果default在，会加载默认\n
                                3. 输入你需要群发的消息或者图片或者文件\n
                                4. 开始群发\n
                                注意：当前版本版本可能会有一些bug，欢迎反馈''')
        
    def send_text(self):
        """
        发送文本消息的函数。
        Args:
            无参数。
        Returns:
            无返回值。
        """
        self.message = self.message_text.toPlainText()
        if self.message:
            self.send_text_flag = True
        else:
            self.send_text_flag = False
            QMessageBox.warning(self, "警告", "请输入群发内容")

    def send_image(self):
        """
        发送图片消息的函数。
        Args:
            无参数。
        Returns:
            无返回值。
        """
        self.image_path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Image Files (*.png *.jpg *.jpeg)")
        if self.image_path:
            self.send_image_flag = True
            # 显示图片
            pixmap = QPixmap(self.image_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaledToWidth(100)  # 调整图片宽度为200像素
                image_label = QLabel("预览")
                image_label.setPixmap(pixmap)
                self.image_layout.addWidget(image_label)
            # 实现发送图片的逻辑
            self.log(f"已加载图片：{ self.image_path}")
        else:
            self.send_image_flag = False
            QMessageBox.warning(self, "警告", "请选择图片")


    def send_file(self):
        """
        发送文件消息的函数。
        Args:
            无参数。
        Returns:
            无返回值。
        """
        self.file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "All Files (*)")
        if self.file_path:
            self.send_file_flag = True
            self.file_label.setText(self.file_path)
            self.file_layout.addWidget(self.file_label)
            # 实现发送文件的逻辑
            self.log(f"已加载文件：{self.file_path}")
        else:
            self.send_file_flag = False
            QMessageBox.warning(self, "警告", "请选择文件")

    def open_file_dialog(self):
        """
        打开文件选择对话框。
        Args:
            无参数。
        Returns:
            无返回值。
        """
        file_dialog = QFileDialog.getOpenFileName(self, "选择文件", "", "Text Files (*.txt)")
        if file_dialog[0]:
            file_path = file_dialog[0]
            self.log(f"您打开了群组信息文件{file_path}")
            self.load_file(file_path)

    def load_file(self, file_path):
        """
        加载文件内容。
        Args:
            file_path (str): 文件路径。
        Returns:
            无返回值。
        """
        file_path = file_path.encode('utf-8').decode('gbk')  # 解决中文路径编码问题
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
            self.users_list = file_content.splitlines()  # 读取文件内容，并拆分为行，以列表的形式返回
            self.log(f"已加载等待发送用户：\n{self.users_list}")
            self.file_content_text.setText(file_content)
            if self.users_list == []:
                QMessageBox.warning(self, "警告", "接收群组信息为空")
                
    def init_weixin(self):
        """
        初始化微信客户端。
        Args:
            无参数。
        Returns:
            无返回值。
        """
        self.wx = WeChat()
        self.log("微信客户端初始化完成")

    def get_weixin_session(self):
        """
        获取当前微信用户会话。
        Args:
            无参数。
        Returns:
            无返回值。
        """
        self.log("正在获取微信用户会话")
        sessions_dict =  self.wx.GetSessionList().keys()
        sessions_list = list(sessions_dict)
        self.log(f"当前界面微信用户会话为：\n{sessions_list}")

    def send_weixin_msg(self,message,user):
        """
        发送微信消息。
        Args:
            message (str): 发送的消息内容。
            user (str): 接收者的用户名。
        Returns:
            无返回值。
        """
        self.log(f"正在发送消息给{user}：{message}")
        self.wx.ChatWith(user)
        self.wx.SendMsg(message)
        self.log(f"已发送文字给{user}：{message}")

    def send_weixin_file(self,file,user):
        """
        发送微信文件。
        Args:
            file (str): 发送的文件路径。
            user (str): 接收者的用户名。
        Returns:
            无返回值。
        """
        self.log(f"正在发送文件给{user}：{file}")
        message = self.message_text.toPlainText()
        self.wx.ChatWith(user)
        self.wx.SendFiles(file)
        self.log(f"已发送文件给{user}：{file}")

    def start_broadcast(self):
        """
        开始群发消息。
        Args:
            无参数。
        Returns:
            无返回值。
        """
        try:
            if self.wx and self.users_list: 
                self.log("开始任务")
                print(self.send_file_flag,self.send_image_flag,self.send_text_flag)
                if self.message!="":
                    self.send_text_flag = True
                if self.send_text_flag:
                    self.log("文本转发中")
                    self.send_text_flag = False
                    for i, user in enumerate(self.users_list):
                        self.log(f"【共{len(self.users_list)}个】【第{i+1}个】用户：【{user}】")
                        self.send_weixin_msg(self.message,user)
                if self.send_image_flag:
                    self.log("图片转发中")
                    self.send_image_flag = False
                    for i, user in enumerate(self.users_list):
                        self.log(f"【共{len(self.users_list)}个】【第{i+1}个】用户：【{user}】")
                        self.send_weixin_file(self.image_path,user)
                if self.send_file_flag:
                    self.log("文件转发中")
                    self.send_file_flag = False
                    for i, user in enumerate(self.users_list):
                        self.log(f"【共{len(self.users_list)}个】【第{i+1}个】用户：【{user}】")
                        self.send_weixin_file(self.file_path,user)

                self.log("任务已结束") 
                QMessageBox.information(self, "信息", "任务已结束")

        except Exception as e:
            self.log(f"发送失败：{e}")

    def log(self, message):
        """
        记录日志。
        Args:
            message (str): 记录的消息内容。
        Returns:
            无返回值。
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{current_time}] {message}"
        self.log_text.append(log_message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("wx.png"))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())