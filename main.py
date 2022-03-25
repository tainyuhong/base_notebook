import sys
import os
from ui.doc_viewer import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from sqlite_handler import *
from markdown2 import Markdown


# 公用SQL
file_max_id_sql = ''' select max(id) from files_sort s '''
select_fileid_sql = '''select id from files_sort s where s.file_name=? '''
add_item_sql = ''' insert into files_sort (file_name,parent_id,path) values (?,?,?); '''


class MainUi(Ui_MainWindow, QMainWindow):

    def __init__(self, parent=None):
        super(MainUi, self).__init__(parent)
        self.setupUi(self)
        self.db = DbHandler()
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
        self.display_tree_files()

    # 隐藏显示文件大纲tab窗口
    def hide_tabview(self):
        if self.action_displaylist.isChecked():
            self.tabWidget.setHidden(False)
        else:
            self.tabWidget.setHidden(True)

    def to_markdown(self):
        text = self.input_text.toPlainText()
        self.display_text.setHidden(False)
        # self.display_text.setMarkdown(str)
        self.display_text.setHtml(text)

    # 隐藏文本预览窗口
    def hide_textbrowser(self):
        if self.action_to_md.isChecked():
            self.display_text.setHidden(False)
        else:
            self.display_text.setHidden(True)

    # 保存文档
    def save(self):
        text = self.input_text.document().toHtml()
        # print(type(str))
        # print(str)
        os.chdir('d:\\')
        with open('test.html', 'wb+') as f:
            f.write(bytes(text, encoding='utf8'))

    # todo
    # 显示文件树内容
    def display_tree_files(self):
        select_top_item_sql = '''select file_name,path from files_sort where parent_id is null'''
        select_second_item_sql = '''select file_name,path from files_sort where parent_id is not null'''
        select_three_item_sql = '''select file_name,path from files_sort where parent_id is null'''
        tree_file_data = self.db.select(select_top_item_sql)
        print(tree_file_data)  # [(0, '新文件夹1', None), (1, '新文件夹2', None)]
        # 将项显示在页面上
        for item in tree_file_data:
            root_item = QTreeWidgetItem()
            # second_item = QTreeWidgetItem(root_item)
            # three_item = QTreeWidgetItem(second_item)
            if len(item[1])==1:
                root_item.setText(0, item[0])  # 显示项
            # elif len(item[1])==2:
            #     print('item项', item)
            #     second_item.setText(0, item[0])
            print('item项', item)
            self.tree_file.addTopLevelItem(root_item)

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
        action_create_dir = QAction('新建目录')  # 新建文件夹菜单
        action_file = QAction('新建文件')
        action_alter = QAction('重命名')
        action_del = QAction('删除文件')

        self.file_menu.addAction(action_create_dir)  # 添加到菜单
        self.file_menu.addAction(action_file)
        self.file_menu.addAction(action_alter)
        self.file_menu.addAction(action_del)
        if item is None:
            # print('在空白处')
            action_file.setVisible(False)
            action_alter.setVisible(False)
            action_del.setVisible(False)
        else:
            # print('项被选中')
            action_create_dir.setVisible(False)     # 隐藏新建目录菜单项
            action_file.setDisabled(False)
            action_alter.setDisabled(False)
        action_create_dir.triggered.connect(self.add_dirs)
        action_file.triggered.connect(self.add_files)
        action_del.triggered.connect(self.del_dirs)     # 连接删除目录信号

        self.file_menu.exec(self.mapToGlobal(pos))  # 在光标位置显示菜单

    # 文件列表添加文件夹功能
    def add_dirs(self):
        create_file_sql = ''' insert into files_sort (file_name,path) values (?,?); '''
        select_filename_sql = '''select file_name from files_sort where file_name = ? '''
        max_id = self.db.select(file_max_id_sql)[0][0]
        if max_id is None:
            max_id = 0
        value, ok = QInputDialog.getText(self, '文件名', '请输入文件名：', QLineEdit.Normal, '新文件夹')  # 获取输入弹出框文本
        # print(self.db.select(select_filename_sql, (value,)),ok)
        if ok is True and self.db.select(select_filename_sql, (value,)) == []:  # 判断文件名是否重复且点击了ok按钮
            root_dir = QTreeWidgetItem()  # 定义项，作为顶级项
            root_dir.setText(0, value)  # 设置项名称
            self.tree_file.addTopLevelItem(root_dir)  # 设置为顶级项
            # index_id = self.tree_file.indexOfTopLevelItem(root_dir)
            self.db.alter(create_file_sql, (value,max_id +1))
        else:
            QMessageBox.warning(self,'添加文件夹','文件名输入有误或重复，请重新输入！')
            return

    # 删除目录
    def del_dirs(self):
        del_sql = '''delete from files_sort where file_name=?'''
        item = self.tree_file.currentItem()  # 当前选定项
        item_name = item.text(0)        # 当前项索引
        print(item_name)
        if QMessageBox.question(self,'删除目录','是否确认删除当前目录',QMessageBox.Yes,QMessageBox.No) == QMessageBox.Yes:
            self.tree_file.takeTopLevelItem(self.tree_file.indexOfTopLevelItem(item))   # 删除当前选择的一级目录
            self.db.alter(del_sql,(item_name,))
        else:
            return

    # 文件列表添加文件功能
    def add_files(self):
        add_item_sql = ''' insert into files_sort (file_name,parent_id,path) values (?,?,?); '''
        item = self.tree_file.currentItem()  # 当前选定项
        value, ok = QInputDialog.getText(self, '文件名', '请输入文件名：', QLineEdit.Normal, '新文件')  # 获取输入弹出框文本
        path = ''   # 用于记录父ITEM的ID及本ITEM的ID方便查询管理
        max_id = self.db.select(file_max_id_sql)[0][0]      # 当前最大ID
        item_name = item.text(0)        # 当前项名称
        item_id = self.db.select(select_fileid_sql, (item_name,))[0][0]  # 当前选择项id
        # 二级目录设定
        top_index = self.tree_file.indexOfTopLevelItem(item)    # 顶级目录索引
        if top_index >= 0 and ok:
            path = item_id
            path = str(path) + '/'+ str(max_id+1)
            print('path', path)
            # 插入数据库并添加至页面
            self.db.alter(add_item_sql,(value,item_id,path))   # 添加项的ID为最大id+1
            child_item = QTreeWidgetItem(item)  # 创建子项
            child_item.setText(0, value)  # 设置项名称
        # 三级目录 文件创建
        elif self.tree_file.indexOfTopLevelItem(item.parent()) >= 0 and ok:     # 当前选择项的你父项为顶级项且点击了Ok按钮
            print(item.text(0))
            select_file_path_sql = ''' select path from files_sort s where s.file_name=?'''
            item_path = self.db.select(select_file_path_sql,(item_name,))
            print(item_path)
            child_item = QTreeWidgetItem(item)  # 创建子项
            child_item.setText(0, value)  # 设置项名称
            # path.append(self.tree_file.indexOfTopLevelItem(item.parent()))  # 顶级项的索引加入序列表（一级目录）
            # path.append(item.parent().indexOfChild(item))  # 当前选择项索引加入序列表（二级目录）
            # path.append(item.indexOfChild(child_item))  # 当前选择项的子项的索引加入序列表 （三级目录）
            path = str(item_path[0][0]) + '/' + str(max_id+1)       # 当前选择项的子项的层级位置信息
            print(path)
            self.db.alter(add_item_sql,(value,path.split('/')[1],path))  # 写入数据库 ，path.split('/')[1]：为当前选择项的id为作子项的父ID
            # print(self.tree_file.itemFromIndex(child_item))
        # print('父项index', self.tree_file.indexOfTopLevelItem(item), item, item.parent(), item.indexOfChild(child_item))
        else :
            QMessageBox.warning(self,'创建文件','只能创建三级目录')
            return
        self.tree_file.expandItem(item)  # 展开当前节点


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainUi()
    win.show()
    sys.exit(app.exec())
