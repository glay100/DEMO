import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime, timedelta
import json
import os

class BookSharingSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("图书共享管理系统")
        self.root.geometry("1200x700")
        
        # 连接数据库
        self.conn = sqlite3.connect('book_sharing.db')
        self.cursor = self.conn.cursor()
        
        # 创建数据表
        self.create_tables()
        
        # 加载初始数据
        self.load_initial_data()
        
        # 当前用户
        self.current_user = "张三"
        
        # 创建UI
        self.create_widgets()
        
        # 加载书籍列表
        self.load_books()
        
    def create_tables(self):
        """创建数据库表"""
        # 书籍表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT,
                category TEXT,
                publisher TEXT,
                publish_year INTEGER,
                status TEXT DEFAULT '可借阅',
                owner TEXT NOT NULL,
                borrower TEXT,
                borrow_until TEXT,
                description TEXT
            )
        ''')
        
        # 共享记录表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sharing_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                book_title TEXT NOT NULL,
                borrower TEXT NOT NULL,
                borrow_date TEXT NOT NULL,
                return_date TEXT,
                status TEXT DEFAULT '借阅中',
                FOREIGN KEY (book_id) REFERENCES books (id)
            )
        ''')
        
        self.conn.commit()
    
    def load_initial_data(self):
        """加载初始数据"""
        # 检查是否有数据
        self.cursor.execute("SELECT COUNT(*) FROM books")
        count = self.cursor.fetchone()[0]
        
        if count == 0:
            # 插入示例数据
            books = [
                ("Python编程从入门到实践", "Eric Matthes", "9787115428028", "计算机", "人民邮电出版社", 2016, "可借阅", "张三", None, None, "Python编程经典入门书籍"),
                ("深入理解计算机系统", "Randal E.Bryant", "9787111544937", "计算机", "机械工业出版社", 2016, "可借阅", "李四", None, None, "计算机系统经典教材"),
                ("百年孤独", "加西亚·马尔克斯", "9787544253994", "文学", "南海出版公司", 2011, "共享中", "王五", "赵六", "2024-12-31", "魔幻现实主义文学代表作"),
                ("人类简史", "尤瓦尔·赫拉利", "9787508647357", "历史", "中信出版社", 2014, "可借阅", "李四", None, None, "从人类进化到未来的全景历史"),
                ("活着", "余华", "9787506365437", "文学", "作家出版社", 2012, "可借阅", "张三", None, None, "中国当代文学经典作品"),
                ("算法导论", "Thomas H.Cormen", "9787111187776", "计算机", "机械工业出版社", 2006, "共享中", "王五", "张三", "2024-11-30", "算法领域经典著作"),
                ("小王子", "圣埃克苏佩里", "9787020042494", "文学", "人民文学出版社", 2003, "可借阅", "赵六", None, None, "全球畅销的经典童话"),
                ("经济学原理", "曼昆", "9787300127893", "经济", "北京大学出版社", 2009, "可借阅", "李四", None, None, "经济学入门经典教材"),
            ]
            
            for book in books:
                self.cursor.execute('''
                    INSERT INTO books (title, author, isbn, category, publisher, publish_year, status, owner, borrower, borrow_until, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', book)
            
            # 插入共享记录
            records = [
                (3, "百年孤独", "赵六", "2024-10-15", None, "借阅中"),
                (6, "算法导论", "张三", "2024-10-20", None, "借阅中"),
            ]
            
            for record in records:
                self.cursor.execute('''
                    INSERT INTO sharing_records (book_id, book_title, borrower, borrow_date, return_date, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', record)
            
            self.conn.commit()
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="图书共享管理系统", font=("微软雅黑", 20, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 用户信息
        user_frame = ttk.LabelFrame(main_frame, text="用户信息", padding="5")
        user_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(user_frame, text=f"当前用户: {self.current_user}", font=("微软雅黑", 10)).grid(row=0, column=0, padx=5)
        
        # 统计信息
        self.update_stats()
        
        stats_frame = ttk.Frame(user_frame)
        stats_frame.grid(row=0, column=1, padx=20)
        
        ttk.Label(stats_frame, text=f"可借阅: {self.available_books}").grid(row=0, column=0, padx=5)
        ttk.Label(stats_frame, text=f"共享中: {self.shared_books}").grid(row=0, column=1, padx=5)
        ttk.Label(stats_frame, text=f"总书籍: {self.total_books}").grid(row=0, column=2, padx=5)
        
        # 左侧控制面板
        control_frame = ttk.LabelFrame(main_frame, text="功能控制", padding="10")
        control_frame.grid(row=2, column=0, sticky=(tk.N, tk.S), padx=(0, 10))
        
        # 按钮
        ttk.Button(control_frame, text="添加新书", command=self.add_book, width=20).pack(pady=5)
        ttk.Button(control_frame, text="编辑书籍", command=self.edit_book, width=20).pack(pady=5)
        ttk.Button(control_frame, text="删除书籍", command=self.delete_book, width=20).pack(pady=5)
        ttk.Button(control_frame, text="借阅书籍", command=self.borrow_book, width=20).pack(pady=5)
        ttk.Button(control_frame, text="归还书籍", command=self.return_book, width=20).pack(pady=5)
        ttk.Button(control_frame, text="我的共享", command=self.show_my_sharing, width=20).pack(pady=5)
        ttk.Button(control_frame, text="借阅记录", command=self.show_borrow_records, width=20).pack(pady=5)
        ttk.Button(control_frame, text="搜索书籍", command=self.search_books, width=20).pack(pady=5)
        ttk.Button(control_frame, text="刷新列表", command=self.load_books, width=20).pack(pady=5)
        
        # 书籍列表
        list_frame = ttk.LabelFrame(main_frame, text="书籍列表", padding="10")
        list_frame.grid(row=2, column=1, sticky=(tk.N, tk.S, tk.W, tk.E))
        
        # 创建表格
        columns = ("ID", "书名", "作者", "分类", "状态", "拥有者", "借阅者", "归还日期")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        # 设置列标题
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, minwidth=50)
        
        # 调整列宽
        self.tree.column("书名", width=200)
        self.tree.column("作者", width=120)
        self.tree.column("ID", width=50)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.tree.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 配置网格权重
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 右侧详细信息面板
        detail_frame = ttk.LabelFrame(main_frame, text="书籍详情", padding="10")
        detail_frame.grid(row=2, column=2, sticky=(tk.N, tk.S, tk.W, tk.E), padx=(10, 0))
        
        # 详细信息标签
        self.detail_text = tk.Text(detail_frame, height=20, width=30, wrap=tk.WORD)
        self.detail_text.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))
        
        # 配置网格权重
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(0, weight=1)
        
        # 绑定选择事件
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        # 底部状态栏
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, text="就绪")
        self.status_label.pack(side=tk.LEFT)
        
    def update_stats(self):
        """更新统计信息"""
        # 总书籍数
        self.cursor.execute("SELECT COUNT(*) FROM books")
        self.total_books = self.cursor.fetchone()[0]
        
        # 可借阅书籍数
        self.cursor.execute("SELECT COUNT(*) FROM books WHERE status = '可借阅'")
        self.available_books = self.cursor.fetchone()[0]
        
        # 共享中书籍数
        self.cursor.execute("SELECT COUNT(*) FROM books WHERE status = '共享中'")
        self.shared_books = self.cursor.fetchone()[0]
    
    def load_books(self):
        """加载书籍列表"""
        # 清空当前列表
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 从数据库获取数据
        self.cursor.execute("SELECT id, title, author, category, status, owner, borrower, borrow_until FROM books")
        books = self.cursor.fetchall()
        
        # 添加到树形视图
        for book in books:
            # 格式化日期
            borrow_until = book[7] if book[7] else ""
            self.tree.insert("", tk.END, values=book)
        
        # 更新统计信息
        self.update_stats()
        
        # 更新状态栏
        self.status_label.config(text=f"已加载 {len(books)} 本书籍")
    
    def on_tree_select(self, event):
        """当选择书籍时显示详细信息"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        book_id = item['values'][0]
        
        # 从数据库获取详细信息
        self.cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        book = self.cursor.fetchone()
        
        if book:
            # 格式化详细信息
            details = f"""书名: {book[1]}
作者: {book[2]}
ISBN: {book[3]}
分类: {book[4]}
出版社: {book[5]}
出版年份: {book[6]}
状态: {book[7]}
拥有者: {book[8]}
借阅者: {book[9] if book[9] else '无'}
归还日期: {book[10] if book[10] else '无'}

描述:
{book[11]}"""
            
            # 显示在文本框中
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(1.0, details)
    
    def add_book(self):
        """添加新书"""
        dialog = BookDialog(self.root, "添加新书")
        if dialog.result:
            # 插入数据库
            self.cursor.execute('''
                INSERT INTO books (title, author, isbn, category, publisher, publish_year, description, owner, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, '可借阅')
            ''', (
                dialog.result['title'],
                dialog.result['author'],
                dialog.result['isbn'],
                dialog.result['category'],
                dialog.result['publisher'],
                dialog.result['publish_year'],
                dialog.result['description'],
                self.current_user
            ))
            
            self.conn.commit()
            self.load_books()
            
            messagebox.showinfo("成功", f"书籍《{dialog.result['title']}》添加成功！")
            self.status_label.config(text=f"已添加书籍: {dialog.result['title']}")
    
    def edit_book(self):
        """编辑书籍"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一本书籍")
            return
        
        item = self.tree.item(selection[0])
        book_id = item['values'][0]
        
        # 从数据库获取详细信息
        self.cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        book = self.cursor.fetchone()
        
        if not book:
            messagebox.showerror("错误", "书籍不存在")
            return
        
        # 检查用户是否有权限编辑
        if book[8] != self.current_user:
            messagebox.showwarning("警告", "您只能编辑自己拥有的书籍")
            return
        
        # 创建编辑对话框
        dialog = BookDialog(
            self.root, 
            "编辑书籍",
            title=book[1],
            author=book[2],
            isbn=book[3],
            category=book[4],
            publisher=book[5],
            publish_year=book[6],
            description=book[11]
        )
        
        if dialog.result:
            # 更新数据库
            self.cursor.execute('''
                UPDATE books 
                SET title=?, author=?, isbn=?, category=?, publisher=?, publish_year=?, description=?
                WHERE id=?
            ''', (
                dialog.result['title'],
                dialog.result['author'],
                dialog.result['isbn'],
                dialog.result['category'],
                dialog.result['publisher'],
                dialog.result['publish_year'],
                dialog.result['description'],
                book_id
            ))
            
            self.conn.commit()
            self.load_books()
            
            messagebox.showinfo("成功", f"书籍《{dialog.result['title']}》编辑成功！")
            self.status_label.config(text=f"已编辑书籍: {dialog.result['title']}")
    
    def delete_book(self):
        """删除书籍"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一本书籍")
            return
        
        item = self.tree.item(selection[0])
        book_id = item['values'][0]
        book_title = item['values'][1]
        
        # 从数据库获取详细信息
        self.cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        book = self.cursor.fetchone()
        
        if not book:
            messagebox.showerror("错误", "书籍不存在")
            return
        
        # 检查用户是否有权限删除
        if book[8] != self.current_user:
            messagebox.showwarning("警告", "您只能删除自己拥有的书籍")
            return
        
        # 确认删除
        if messagebox.askyesno("确认", f"确定要删除《{book_title}》吗？"):
            # 删除数据库记录
            self.cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
            self.cursor.execute("DELETE FROM sharing_records WHERE book_id = ?", (book_id,))
            
            self.conn.commit()
            self.load_books()
            
            messagebox.showinfo("成功", f"书籍《{book_title}》删除成功！")
            self.status_label.config(text=f"已删除书籍: {book_title}")
    
    def borrow_book(self):
        """借阅书籍"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一本书籍")
            return
        
        item = self.tree.item(selection[0])
        book_id = item['values'][0]
        book_title = item['values'][1]
        status = item['values'][4]
        
        if status != "可借阅":
            messagebox.showwarning("警告", "该书籍当前不可借阅")
            return
        
        # 获取借阅天数
        days = simpledialog.askinteger("借阅天数", "请输入借阅天数（默认30天）:", minvalue=1, maxvalue=365, initialvalue=30)
        
        if days:
            # 计算归还日期
            borrow_date = datetime.now()
            return_date = borrow_date + timedelta(days=days)
            return_date_str = return_date.strftime("%Y-%m-%d")
            borrow_date_str = borrow_date.strftime("%Y-%m-%d")
            
            # 更新书籍状态
            self.cursor.execute('''
                UPDATE books 
                SET status='共享中', borrower=?, borrow_until=?
                WHERE id=?
            ''', (self.current_user, return_date_str, book_id))
            
            # 添加共享记录
            self.cursor.execute('''
                INSERT INTO sharing_records (book_id, book_title, borrower, borrow_date, status)
                VALUES (?, ?, ?, ?, '借阅中')
            ''', (book_id, book_title, self.current_user, borrow_date_str))
            
            self.conn.commit()
            self.load_books()
            
            messagebox.showinfo("成功", f"书籍《{book_title}》借阅成功！请在{return_date_str}前归还。")
            self.status_label.config(text=f"已借阅书籍: {book_title}")
    
    def return_book(self):
        """归还书籍"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一本书籍")
            return
        
        item = self.tree.item(selection[0])
        book_id = item['values'][0]
        book_title = item['values'][1]
        borrower = item['values'][6]
        status = item['values'][4]
        
        if status != "共享中":
            messagebox.showwarning("警告", "该书籍未被借阅")
            return
        
        if borrower != self.current_user:
            messagebox.showwarning("警告", "您只能归还自己借阅的书籍")
            return
        
        # 确认归还
        if messagebox.askyesno("确认", f"确定要归还《{book_title}》吗？"):
            return_date = datetime.now().strftime("%Y-%m-%d")
            
            # 更新书籍状态
            self.cursor.execute('''
                UPDATE books 
                SET status='可借阅', borrower=NULL, borrow_until=NULL
                WHERE id=?
            ''', (book_id,))
            
            # 更新共享记录
            self.cursor.execute('''
                UPDATE sharing_records 
                SET return_date=?, status='已归还'
                WHERE book_id=? AND borrower=? AND status='借阅中'
            ''', (return_date, book_id, self.current_user))
            
            self.conn.commit()
            self.load_books()
            
            messagebox.showinfo("成功", f"书籍《{book_title}》归还成功！")
            self.status_label.config(text=f"已归还书籍: {book_title}")
    
    def show_my_sharing(self):
        """显示我的共享记录"""
        # 创建新窗口
        window = tk.Toplevel(self.root)
        window.title("我的共享记录")
        window.geometry("800x500")
        
        # 创建框架
        frame = ttk.Frame(window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建表格
        columns = ("ID", "书籍ID", "书名", "借阅人", "借阅日期", "归还日期", "状态")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=20)
        
        # 设置列标题
        for col in columns:
            tree.heading(col, text=col)
        
        # 调整列宽
        tree.column("书名", width=200)
        tree.column("ID", width=50)
        tree.column("书籍ID", width=60)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 查询我的共享记录
        self.cursor.execute('''
            SELECT sr.id, b.id, b.title, sr.borrower, sr.borrow_date, sr.return_date, sr.status
            FROM sharing_records sr
            JOIN books b ON sr.book_id = b.id
            WHERE b.owner = ?
            ORDER BY sr.borrow_date DESC
        ''', (self.current_user,))
        
        records = self.cursor.fetchall()
        
        # 添加到树形视图
        for record in records:
            tree.insert("", tk.END, values=record)
        
        # 统计信息
        stats_frame = ttk.Frame(window, padding="10")
        stats_frame.pack(fill=tk.X)
        
        # 查询统计
        self.cursor.execute("SELECT COUNT(*) FROM sharing_records sr JOIN books b ON sr.book_id = b.id WHERE b.owner = ?", (self.current_user,))
        total = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM sharing_records sr JOIN books b ON sr.book_id = b.id WHERE b.owner = ? AND sr.status = '借阅中'", (self.current_user,))
        borrowing = self.cursor.fetchone()[0]
        
        ttk.Label(stats_frame, text=f"总共享次数: {total}").pack(side=tk.LEFT, padx=10)
        ttk.Label(stats_frame, text=f"借阅中: {borrowing}").pack(side=tk.LEFT, padx=10)
    
    def show_borrow_records(self):
        """显示我的借阅记录"""
        # 创建新窗口
        window = tk.Toplevel(self.root)
        window.title("我的借阅记录")
        window.geometry("800x500")
        
        # 创建框架
        frame = ttk.Frame(window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建表格
        columns = ("ID", "书籍ID", "书名", "借阅日期", "归还日期", "状态")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=20)
        
        # 设置列标题
        for col in columns:
            tree.heading(col, text=col)
        
        # 调整列宽
        tree.column("书名", width=200)
        tree.column("ID", width=50)
        tree.column("书籍ID", width=60)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 查询我的借阅记录
        self.cursor.execute('''
            SELECT sr.id, sr.book_id, sr.book_title, sr.borrow_date, sr.return_date, sr.status
            FROM sharing_records sr
            WHERE sr.borrower = ?
            ORDER BY sr.borrow_date DESC
        ''', (self.current_user,))
        
        records = self.cursor.fetchall()
        
        # 添加到树形视图
        for record in records:
            tree.insert("", tk.END, values=record)
        
        # 统计信息
        stats_frame = ttk.Frame(window, padding="10")
        stats_frame.pack(fill=tk.X)
        
        # 查询统计
        self.cursor.execute("SELECT COUNT(*) FROM sharing_records WHERE borrower = ?", (self.current_user,))
        total = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM sharing_records WHERE borrower = ? AND status = '借阅中'", (self.current_user,))
        borrowing = self.cursor.fetchone()[0]
        
        ttk.Label(stats_frame, text=f"总借阅次数: {total}").pack(side=tk.LEFT, padx=10)
        ttk.Label(stats_frame, text=f"借阅中: {borrowing}").pack(side=tk.LEFT, padx=10)
    
    def search_books(self):
        """搜索书籍"""
        # 创建搜索对话框
        search_term = simpledialog.askstring("搜索书籍", "请输入书名、作者或分类:")
        
        if search_term:
            # 清空当前列表
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # 从数据库搜索数据
            self.cursor.execute('''
                SELECT id, title, author, category, status, owner, borrower, borrow_until 
                FROM books 
                WHERE title LIKE ? OR author LIKE ? OR category LIKE ?
            ''', (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            
            books = self.cursor.fetchall()
            
            # 添加到树形视图
            for book in books:
                self.tree.insert("", tk.END, values=book)
            
            # 更新状态栏
            self.status_label.config(text=f"找到 {len(books)} 本相关书籍")
    
    def __del__(self):
        """析构函数，关闭数据库连接"""
        if hasattr(self, 'conn'):
            self.conn.close()

class BookDialog:
    """书籍信息对话框"""
    def __init__(self, parent, title, **kwargs):
        self.result = None
        
        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 创建框架
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 表单字段
        ttk.Label(frame, text="书名:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.title_entry = ttk.Entry(frame, width=30)
        self.title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        if 'title' in kwargs:
            self.title_entry.insert(0, kwargs['title'])
        
        ttk.Label(frame, text="作者:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.author_entry = ttk.Entry(frame, width=30)
        self.author_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        if 'author' in kwargs:
            self.author_entry.insert(0, kwargs['author'])
        
        ttk.Label(frame, text="ISBN:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.isbn_entry = ttk.Entry(frame, width=30)
        self.isbn_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        if 'isbn' in kwargs:
            self.isbn_entry.insert(0, kwargs['isbn'])
        
        ttk.Label(frame, text="分类:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.category_combobox = ttk.Combobox(frame, values=["计算机", "文学", "历史", "经济", "科学", "艺术", "哲学", "其他"], width=28)
        self.category_combobox.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        if 'category' in kwargs:
            self.category_combobox.set(kwargs['category'])
        else:
            self.category_combobox.set("计算机")
        
        ttk.Label(frame, text="出版社:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.publisher_entry = ttk.Entry(frame, width=30)
        self.publisher_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        if 'publisher' in kwargs:
            self.publisher_entry.insert(0, kwargs['publisher'])
        
        ttk.Label(frame, text="出版年份:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.year_entry = ttk.Entry(frame, width=30)
        self.year_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)
        if 'publish_year' in kwargs:
            self.year_entry.insert(0, kwargs['publish_year'])
        
        ttk.Label(frame, text="描述:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.description_text = tk.Text(frame, width=30, height=8)
        self.description_text.grid(row=6, column=1, sticky=(tk.W, tk.E), pady=5)
        if 'description' in kwargs:
            self.description_text.insert(1.0, kwargs['description'])
        
        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="确定", command=self.ok).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=self.cancel).pack(side=tk.LEFT, padx=10)
        
        # 配置网格权重
        frame.columnconfigure(1, weight=1)
        
        # 等待对话框关闭
        self.dialog.wait_window()
    
    def ok(self):
        """确定按钮"""
        # 验证输入
        if not self.title_entry.get():
            messagebox.showwarning("警告", "书名不能为空")
            return
        
        if not self.author_entry.get():
            messagebox.showwarning("警告", "作者不能为空")
            return
        
        try:
            year = int(self.year_entry.get()) if self.year_entry.get() else 0
        except ValueError:
            messagebox.showwarning("警告", "出版年份必须是数字")
            return
        
        # 保存结果
        self.result = {
            'title': self.title_entry.get(),
            'author': self.author_entry.get(),
            'isbn': self.isbn_entry.get(),
            'category': self.category_combobox.get(),
            'publisher': self.publisher_entry.get(),
            'publish_year': year,
            'description': self.description_text.get(1.0, tk.END).strip()
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        """取消按钮"""
        self.dialog.destroy()

def main():
    """主函数"""
    root = tk.Tk()
    app = BookSharingSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()
