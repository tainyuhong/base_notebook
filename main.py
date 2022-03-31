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
select_filename_sql = '''select file_name from files_sort where file_name = ? '''

class MainUi(Ui_MainWindow, QMainWindow):

    def __init__(self, parent=None):
        super(MainUi, self).__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QIcon(":/icons/img/bj1.png"))
        self.db = DbHandler()       # 实例化数据库
        self.display_text.setHidden(True)       # 设置默认隐藏markdown预览窗口
        self.input_text.setReadOnly(True)       # 设置默认输入文本窗口为只读，防止没有选中目录直接编辑
        self.add_tool()  # 添加按钮工具至工具栏中

        # 连接相应信号与槽
        self.tree_file.setContextMenuPolicy(Qt.CustomContextMenu)  # 文件列表右键菜单
        self.tree_file.customContextMenuRequested.connect(self.tree_file_menu)  # 绑定右键事件

        # self.input_text.textChanged.connect(self.to_markdown)   # 输入框内容变更同步显示至预览框中
        self.action_displaylist.changed.connect(self.hide_tabview)  # 显示与隐藏tabwidget预览窗口
        self.action_to_md.changed.connect(self.hide_textbrowser)    # 显示与隐藏markdown预览窗口
        self.action_save.triggered.connect(self.save)  # 保存数据
        # self.action_clip.triggered.connect(self.display_clip)  # 显示粘贴板信息
        self.color.clicked.connect(self.chioce_color)  # 设置字体的颜色
        self.display_tree_files()  # 显示文件列表内容
        self.tree_file.clicked.connect(self.load_content_to_win)  # 文件列表点击事件连接到显示文件函数


    # 隐藏显示文件大纲tab窗口
    def hide_tabview(self):
        if self.action_displaylist.isChecked():
            self.tabWidget.setHidden(False)
        else:
            self.tabWidget.setHidden(True)

    # 转换为markdown方式预览
    def to_markdown(self):
        text = self.input_text.toPlainText()
        self.display_text.setHidden(False)
        self.display_text.setMarkdown(text)

    # 隐藏文本预览窗口
    def hide_textbrowser(self):
        if self.action_to_md.isChecked():
            self.display_text.setHidden(False)
            self.to_markdown()  # 进行预览markdown文件，当原来有内容时，将原有的内容先进行转换
            self.input_text.textChanged.connect(self.to_markdown)   # 输入框内容变更同步显示至预览框中
        else:
            self.display_text.setHidden(True)
            self.input_text.textChanged.disconnect(self.to_markdown)  # 输入框内容变更同步显示至预览框中

    # 保存文档
    def save(self):
        save_to_html_sql = '''insert into file_content (file_id,filename,content,create_date) values(?,?,?,?);'''
        content_file_id_sql = '''select file_id from file_content where file_id=? '''  # 文件内容表中file_id
        alter_content_sql = ''' update file_content set content=?,last_alter_date=? where file_id = ? '''     # 修改文件内容
        text_conntent = self.input_text.document().toHtml()
        item = self.tree_file.currentItem()  # 当前选择文件
        if item:
            file_id = self.db.select(select_fileid_sql, (item.text(0),))[0][0]  # 从文件列表中获取文件id
            print(file_id)
            time = QDateTime.currentDateTime()  # 获取系统当前时间
            timedisplay = time.toString("yyyy-MM-dd hh:mm:ss")  # 格式化一下时间
            content_file_id = self.db.select(content_file_id_sql,(file_id,))    # 查询文件内容表中的文件id
            print(content_file_id)
            # 保存至数据库,判断文件内容列表中是否有数据，有则修改，无所添加
            if len(content_file_id) == 0:
                try:
                    self.db.alter(save_to_html_sql, (file_id, item.text(0), text_conntent, timedisplay))
                except Exception as e:
                    print('错误：', e)
                else:
                    print('数据保存成功！')
            else:
                try:
                    self.db.alter(alter_content_sql, (text_conntent, timedisplay,file_id))
                except Exception as e:
                    print('错误：', e)
                else:
                    print('数据修改成功！')
        else:
            print('未选择项，不能保存')
            return

    # 显示加载显示文件内容
    def load_content_to_win(self):
        content_sql = ''' select content from file_content where filename=? '''  # 按文件名查询内容字段
        self.input_text.setReadOnly(False)    # 显示文件编辑框
        item = self.tree_file.currentItem()  # 当前选择文件
        html_content = self.db.select(content_sql, (item.text(0),))
        # print(html_content)
        if len(html_content) > 0:
            self.input_text.clear()
            self.input_text.setHtml(html_content[0][0])
            print('加载到页面成功。。。')
        else:
            self.input_text.clear()
            return

    # 显示文件树内容
    def display_tree_files(self):
        select_top_item_sql = '''select file_name,path from files_sort where parent_id is null'''
        select_second_item_sql = '''select file_name,path from files_sort where parent_id = (select id from files_sort where file_name=?);'''
        top_tree_data = self.db.select(select_top_item_sql)
        # print(top_tree_data)  # [(0, '新文件夹1', None), (1, '新文件夹2', None)]
        # 将项显示在页面上
        for item in top_tree_data:
            root_item = QTreeWidgetItem()
            root_item.setText(0, item[0])  # 显示项
            root_item.setIcon(0, QIcon(':icons/img/52.ico'))        # 一级目录添加图标
            second_item_data = self.db.select(select_second_item_sql, (item[0],))
            # print('second_item_data',second_item_data)
            # 显示二级item
            for sec_item in second_item_data:
                second_item = QTreeWidgetItem(root_item)
                second_item.setText(0, sec_item[0])
                second_item.setIcon(0, QIcon(':icons/img/2.ico'))  # 二级目录添加图标
                three_item_data = self.db.select(select_second_item_sql, (sec_item[0],))
                # print('三级',three_item_data)
                # 显示三级item
                for thr_item in three_item_data:
                    three_item = QTreeWidgetItem(second_item)
                    three_item.setText(0, thr_item[0])
            self.tree_file.addTopLevelItem(root_item)

    # 显示粘贴板内容
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

    # 快捷工具栏
    def add_tool(self):
        # 字体大小
        self.font_size = QComboBox()
        for _ in range(9, 50):
            self.font_size.addItem(str(_))
        self.font_size.setCurrentText('12')  # 设置默认字号
        self.toolBar_quick.addWidget(self.font_size)
        self.font_size.currentTextChanged.connect(self.change_font_size)    # 连接到字号大小设置槽函数

        # 定义字体类型
        fonts = ['Arial', 'Microsoft YaHei UI', 'Microsoft YaHei UI Light', 'Times New Roman', '仿宋', '仿宋_GB2312', '宋体',
                 '宋体-PUA', '微软雅黑', '微软雅黑 Light', '新宋体', '楷体', '楷体_GB2312', '等线', '黑体']
        self.font = QComboBox()
        self.font.addItems(fonts)
        self.font.setCurrentText('宋体')
        self.font.setMaximumWidth(100)  # 设置字体选择下拉框的最大宽度
        self.font.currentTextChanged.connect(self.change_font)      # 设置字体样式
        self.toolBar_quick.addWidget(self.font)     # 将字号设置控件加入到快捷栏

        # 设置颜色
        self.color = QToolButton()  # 颜色
        self.color.setIcon(QIcon(":/icons/img/font.png"))   # 颜色设置按钮图标
        # self.color.setIconSize(QSize(25, 25))
        self.color.setMaximumSize(25, 25)
        self.toolBar_quick.addWidget(self.color)        # 将颜色设置控件加入到快捷栏

        # 设置字体为粗体
        self.font_bold = QToolButton()
        self.font_bold.setIcon(QIcon(":icons/img/bold.png"))
        self.font_bold.setMaximumSize(25, 25)
        self.toolBar_quick.addWidget(self.font_bold)  # 将颜色设置控件加入到快捷栏
        self.font_bold.clicked.connect(self.change_font_bold)

        # 设置字体为斜体
        self.font_italic = QToolButton()
        self.font_italic.setIcon(QIcon(":icons/img/italic.png"))
        self.font_italic.setMaximumSize(25, 25)
        self.toolBar_quick.addWidget(self.font_italic)  # 将颜色设置控件加入到快捷栏
        self.font_italic.clicked.connect(self.change_font_italic)

    # todo 对于选取一块不同格式的文本进行改变字体及大小时，会改变为选取的第一行的格式大小。
    # 字体设置
    def change_font(self):
        select_text = self.input_text.textCursor()
        text_format = self.input_text.currentCharFormat()   # 获取当前字体的格式
        select_font = self.font.currentText()       # 获取当前选择字体
        print('选择字体：',select_font)
        text_format.setFontFamilies([select_font])      # 设置字体，需要接收列表类型格式
        select_text.mergeCharFormat(text_format)        # 将字体格式追加到原字符串格式中


    # 设置字体颜色
    def chioce_color(self):
        color = QColorDialog.getColor()
        select_text = self.input_text.textCursor()
        text_format = self.input_text.currentCharFormat()
        # print('选中内容：',color.name())
        if color.isValid():
            text_format.setForeground(QBrush(QColor(color)))
            select_text.mergeCharFormat(text_format)

    # 设置字体大小
    def change_font_size(self):
        font_size = self.font_size.currentText()
        select_text = self.input_text.textCursor()      # 游标位置
        text_format = self.input_text.currentCharFormat()                    # 定义字体格式
        text_format.setFontPointSize(float(font_size))  # 设置文档字体大小格式
        select_text.mergeCharFormat(text_format)        # 追加至文档格式中

    # 设置字体为粗体
    def change_font_bold(self):
        select_text = self.input_text.textCursor()  # 游标位置
        text_format = self.input_text.currentCharFormat()  # 定义字体格式
        current_font = text_format.font()       # 获取当前文本的字体格式
        # print('当前字体', current_font)
        current_font.setBold(True)          # 将当前文本的字体加粗
        # print('当前字体1', current_font)
        text_format.setFont(current_font)       # 设置文本格式为加粗后的格式
        select_text.mergeCharFormat(text_format)        # 追加至文档格式中

    # 设置字体为斜体
    def change_font_italic(self):
        select_text = self.input_text.textCursor()  # 游标位置
        text_format = self.input_text.currentCharFormat()
        text_format.setFontItalic(True)
        select_text.mergeCharFormat(text_format)  # 追加至文档格式中

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
            action_create_dir.setVisible(False)  # 隐藏新建目录菜单项
            action_file.setDisabled(False)
            action_alter.setDisabled(False)
        action_create_dir.triggered.connect(self.add_dirs)
        action_file.triggered.connect(self.add_files)
        action_del.triggered.connect(self.del_dirs)  # 连接删除目录信号
        action_alter.triggered.connect(self.alter_item)  # 连接修改目录信号

        self.file_menu.exec(self.mapToGlobal(pos))  # 在光标位置显示菜单

    # 文件列表添加文件夹功能
    def add_dirs(self):
        create_file_sql = ''' insert into files_sort (file_name,path) values (?,?); '''

        max_id = self.db.select(file_max_id_sql)[0][0]
        if max_id is None:
            max_id = 0
        value, ok = QInputDialog.getText(self, '文件名', '请输入文件名：', QLineEdit.Normal, '新文件夹')  # 获取输入弹出框文本
        # print(self.db.select(select_filename_sql, (value,)),ok)
        if ok and self.db.select(select_filename_sql, (value,)) == []:  # 判断文件名是否重复且点击了ok按钮
            root_dir = QTreeWidgetItem()  # 定义项，作为顶级项
            root_dir.setText(0, value)  # 设置项名称
            self.tree_file.addTopLevelItem(root_dir)  # 设置为顶级项
            root_dir.setIcon(0,QIcon(':icons/img/52.ico'))
            # index_id = self.tree_file.indexOfTopLevelItem(root_dir)
            self.db.alter(create_file_sql, (value, max_id + 1))
        else:
            QMessageBox.warning(self, '添加文件夹', '文件名输入有误或重复，请重新输入！')
            return

    # 删除文件目录
    def del_dirs(self):
        del_sql = '''delete from files_sort where file_name=?'''
        item = self.tree_file.currentItem()  # 当前选定项
        item_name = item.text(0)  # 当前项索引
        print('子项数',item.childCount())
        # 判断是否有子项
        if item.childCount() == 0:
            if QMessageBox.question(self, '删除目录', '是否确认删除当前目录', QMessageBox.Yes, QMessageBox.No) == QMessageBox.Yes:
                if self.tree_file.indexOfTopLevelItem(item) < 0:
                    item.parent().takeChildren()  # 删除当前选择的子项
                else:
                    self.tree_file.takeTopLevelItem(self.tree_file.indexOfTopLevelItem(item))  # 删除当前选择的一级目录
                try:
                    self.db.alter(del_sql, (item_name,))        # 从数据库中删除
                except Exception as e:
                    print('错误：',e)
                else:
                    print('删除成功！')
            else:
                return
        else:
            QMessageBox.warning(self,'删除目录','该目录存在下级目录，不能删除')

    # todo 未完成
    # 修改文件名
    def alter_item(self):
        # 修改文件列表中的文件名SQL
        alter_file_sort_sql = ''' update files_sort set file_name = ? where id =?; '''
        # 修改文件内容表中的文件名SQL
        alter_file_content_sql = ''' update file_content set filename = ? where file_id=? '''
        current_item = self.tree_file.currentItem()
        filename = current_item.text(0)     # 当前文件名
        current_item_id = self.db.select(select_fileid_sql,(filename,))[0][0]
        value, ok = QInputDialog.getText(self, '修改文件名', '请输入新文件名：', QLineEdit.Normal, filename)  # 获取输入弹出框文本
        if ok:
            # print(current_item_id,value)
            # 执行修改
            current_item.setText(0,value)
            self.db.alter(alter_file_sort_sql,(value,current_item_id))  # 修改文件列表中的文件名
            self.db.alter(alter_file_content_sql,(value,current_item_id))  # 修改文件内容表中的文件名
            QMessageBox.information(self,'修改文件名','文件名修改成功！',)
            print('修改成功！')
        else:
            return

    # 文件列表添加文件功能
    def add_files(self):
        add_item_sql = ''' insert into files_sort (file_name,parent_id,path) values (?,?,?); '''
        item = self.tree_file.currentItem()  # 当前选定项
        value, ok = QInputDialog.getText(self, '文件名', '请输入文件名：', QLineEdit.Normal, '新文件')  # 获取输入弹出框文本
        path = ''  # 用于记录父ITEM的ID及本ITEM的ID方便查询管理
        max_id = self.db.select(file_max_id_sql)[0][0]  # 当前最大ID
        item_name = item.text(0)  # 当前项名称
        item_id = self.db.select(select_fileid_sql, (item_name,))[0][0]  # 当前选择项id
        # 二级目录设定
        top_index = self.tree_file.indexOfTopLevelItem(item)  # 顶级目录索引
        db_item_name =self.db.select(select_filename_sql, (value,))     # 数据库中文件名
        print('数据库中',db_item_name)
        if db_item_name:
            QMessageBox.warning(self, '创建文件', '文件名重复！')
        elif top_index >= 0 and ok :
            path = item_id
            path = str(path) + '/' + str(max_id + 1)
            # print('path', path)
            # 插入数据库并添加至页面
            self.db.alter(add_item_sql, (value, item_id, path))  # 添加项的ID为最大id+1
            child_item = QTreeWidgetItem(item)  # 创建子项
            child_item.setText(0, value)  # 设置项名称
            child_item.setIcon(0, QIcon(':icons/img/2.ico'))  # 二级目录添加图标
        # 三级目录 文件创建
        elif self.tree_file.indexOfTopLevelItem(item.parent()) >= 0 and ok:  # 当前选择项的你父项为顶级项且点击了Ok按钮
            # print(item.text(0))
            select_file_path_sql = ''' select path from files_sort s where s.file_name=?'''
            item_path = self.db.select(select_file_path_sql, (item_name,))
            # print(item_path)
            child_item = QTreeWidgetItem(item)  # 创建子项
            child_item.setText(0, value)  # 设置项名称
            path = str(item_path[0][0]) + '/' + str(max_id + 1)  # 当前选择项的子项的层级位置信息
            # print(path)
            self.db.alter(add_item_sql,
                          (value, path.split('/')[1], path))  # 写入数据库 ，path.split('/')[1]：为当前选择项的id为作子项的父ID
        else:
            QMessageBox.warning(self, '创建文件', '只能创建三级目录')
            return
        self.tree_file.expandItem(item)  # 展开当前节点


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainUi()
    win.show()
    sys.exit(app.exec())
