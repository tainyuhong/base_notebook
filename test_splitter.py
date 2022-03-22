import sys
import os
from test_Demo.doc_viewer import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from markdown2 import Markdown


class MainUi(Ui_MainWindow, QMainWindow):

    def __init__(self, parent=None):
        super(MainUi, self).__init__(parent)
        self.setupUi(self)
        self.display_text.setHidden(True)
        self.add_tool()  # 添加按钮工具至工具栏中
        self.font_size = ''
        self.tree_file.setContextMenuPolicy(Qt.CustomContextMenu)  # 文件列表右键菜单
        self.tree_file.customContextMenuRequested.connect(self.tree_file_menu)  # 绑定右键事件

        self.input_text.textChanged.connect(self.to_markdown)
        self.action_displaylist.changed.connect(self.hide_tabview)  # 显示与隐藏tabwidget预览窗口
        # self.action_to_md.changed.connect(self.hide_textbrowser)    # 显示与隐藏markdown预览窗口
        self.action_save.triggered.connect(self.save)  # 保存数据
        self.action_clip.triggered.connect(self.display_clip)  # 显示粘贴板信息
        self.color.clicked.connect(self.chioce_color)

    # 隐藏显示文件大纲tab窗口
    def hide_tabview(self):
        if self.action_displaylist.isChecked():
            self.tabWidget.setHidden(False)
        else:
            self.tabWidget.setHidden(True)

    def to_markdown(self):
        str = self.input_text.toPlainText()
        self.display_text.setHidden(False)
        # self.display_text.setMarkdown(str)
        self.display_text.setHtml(str)

    # 隐藏文本预览窗口
    def hide_textbrowser(self):
        if self.action_to_md.isChecked():
            self.display_text.setHidden(False)
        else:
            self.display_text.setHidden(True)

    # 保存文档
    def save(self):
        str = self.input_text.document().toHtml()
        # print(type(str))
        # print(str)
        os.chdir('d:\\')
        with open('test.html', 'wb+') as f:
            f.write(bytes(str, encoding='utf8'))

    def display_clip(self):
        clip = QApplication.clipboard()
        print('剪贴板内容：', clip)  # 显示剪贴板对象地址
        print(clip.mimeData().formats())  # 显示包含mime内容格式
        print(clip.mimeData().text())  # 显示mime文本
        print('是否有HTML', clip.mimeData().hasHtml(), clip.mimeData().html())  # 判断是否包含html，并打印
        print('是否有hasUrls', clip.mimeData().hasUrls(), clip.mimeData().urls())  # 判断是否包含url，并打印
        print('是否有hasImage', clip.mimeData().hasImage(), 'data', clip.mimeData().imageData())  # 判断是否包含图片，并打印
        cur = self.display_text.textCursor()  # 设定文本游标
        cur.insertImage(clip.mimeData().text())  # 根据图片地址插入图片

    def add_tool(self):
        self.font_size = QComboBox()
        for _ in range(9, 50):
            self.font_size.addItem(str(_))
        self.font_size.setCurrentText('12')  # 设置默认字号
        self.toolBar_quick.addWidget(self.font_size)
        self.font = QFontComboBox()
        self.font.setMaximumWidth(100)  # 设置字体选择下拉框的最大宽度
        self.toolBar_quick.addWidget(self.font)
        self.color = QPushButton('颜色')  # 颜色
        self.color.setMaximumSize(40, 40)
        self.toolBar_quick.addWidget(self.color)

    # 颜色选择
    def chioce_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color.setStyleSheet("background-color:{}".format(color.name()))

    # 文件列表框右键菜单
    def tree_file_menu(self, pos):
        item = self.tree_file.itemAt(pos)
        # print(item.text(0), item1.text(0))
        self.file_menu = QMenu()
        action_create_dir = QAction('新建文件夹')  # 新建文件夹菜单
        action_file = QAction('新建文件')
        action_alter = QAction('修改文件名')

        self.file_menu.addAction(action_create_dir)  # 添加到菜单
        self.file_menu.addAction(action_file)
        self.file_menu.addAction(action_alter)
        if item is None:
            # print('在空白处')
            action_file.setDisabled(True)
            action_alter.setDisabled(True)
        else:
            # print('项被选中')
            action_file.setDisabled(False)
            action_alter.setDisabled(False)
        action_create_dir.triggered.connect(self.add_dirs)
        action_file.triggered.connect(self.add_files)
        # action_alter.triggered.connect(self.quick_click)

        self.file_menu.exec(self.mapToGlobal(pos))  # 在光标位置显示菜单

    # 文件列表添加文件夹功能
    def add_dirs(self):
        value, ok = QInputDialog.getText(self, '文件名', '请输入文件名：', QLineEdit.Normal, '新文件夹')  # 获取输入弹出框文本
        # print(value)
        root_dir = QTreeWidgetItem()  # 定义项，作为顶级项
        root_dir.setText(0, value)  # 设置项名称
        self.tree_file.addTopLevelItem(root_dir)  # 设置为顶级项

    # 文件列表添加文件功能
    def add_files(self):
        parent_item = self.tree_file.currentItem()  # 当前待定项
        value, ok = QInputDialog.getText(self, '文件名', '请输入文件名：', QLineEdit.Normal, '新文件')  # 获取输入弹出框文本
        child_item = QTreeWidgetItem(parent_item)  # 创建子项
        child_item.setText(0, value)  # 设置项名称
        print('父项index',self.tree_file.indexFromItem(parent_item,0),'子项index',self.tree_file.indexFromItem(child_item,0),
              self.tree_file.indexOfTopLevelItem(parent_item),self.tree_file.indexOfTopLevelItem(child_item))
        self.tree_file.expandItem(parent_item)  # 展开当前节点


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainUi()
    win.show()
    sys.exit(app.exec())
