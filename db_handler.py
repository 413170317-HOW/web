# db_handler.py
import pyodbc

class DBHandler:
    def __init__(self, server, database):
        self.conn = pyodbc.connect(
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={server};DATABASE={database};'
            f'Trusted_Connection=yes;'
        )
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            IF OBJECT_ID('Certifications', 'U') IS NULL
            CREATE TABLE Certifications (
                ID INT IDENTITY(1,1) PRIMARY KEY,
                Title NVARCHAR(255),
                URL NVARCHAR(MAX),
                Description NVARCHAR(MAX)  -- ✅ 新增介紹欄位
            )
        ''')
        ###### coursrs ######
        self.cursor.execute('''
            IF OBJECT_ID('Courses', 'U') IS NULL
            CREATE TABLE Courses (
                ID INT IDENTITY(1,1) PRIMARY KEY,
                CertificationID INT,
                Title NVARCHAR(255),
                URL NVARCHAR(MAX),
                Description NVARCHAR(MAX),
                FOREIGN KEY (CertificationID) REFERENCES Certifications(ID)
            )
        ''')
        ###### module ######
        self.cursor.execute('''
            IF OBJECT_ID('Modules', 'U') IS NULL
            CREATE TABLE Modules (
                ID INT IDENTITY(1,1) PRIMARY KEY,
                CourseID INT,
                Title NVARCHAR(255),
                URL NVARCHAR(MAX),
                Description NVARCHAR(MAX),
                FOREIGN KEY (CourseID) REFERENCES Courses(ID)
            )
        ''')

    #	取得或建立認證，回傳 ID
    def get_or_create_certification(self, title, url):
        self.cursor.execute('SELECT ID FROM Certifications WHERE Title = ?', (title,))
        row = self.cursor.fetchone()
        if row:
            return row[0]
        else:
            self.cursor.execute('INSERT INTO Certifications (Title, URL) VALUES (?, ?)', (title, url))
            self.conn.commit()
            return self.cursor.execute('SELECT SCOPE_IDENTITY()').fetchone()[0]
    
    #   取得或建立課程，回傳 ID
    def get_or_create_course(self, title, url, cert_id):
        self.cursor.execute('SELECT ID FROM Courses WHERE Title = ? AND CertificationID = ?', (title, cert_id))
        row = self.cursor.fetchone()
        if row:
            return row[0]
        else:
            self.cursor.execute('INSERT INTO Courses (Title, URL, CertificationID) VALUES (?, ?, ?)', (title, url, cert_id))
            self.conn.commit()
            return self.cursor.execute('SELECT SCOPE_IDENTITY()').fetchone()[0]
    
    #   插入模組（僅含 title 與 course_id）
    def insert_module(self, title, course_id, url, description):
        self.cursor.execute('SELECT ID FROM Modules WHERE Title = ? AND CourseID = ?', (title, course_id))
        if not self.cursor.fetchone():
            self.cursor.execute('''
                INSERT INTO Modules (Title, CourseID, URL, Description)
                VALUES (?, ?, ?, ?)
            ''', (title, course_id, url, description))
            #print(f"✅ 新增模組：{title}")
        #else:  print(f"ℹ️ 模組已存在：{title}")
            
    # 	根據三層結構（認證→課程→模組）統一插入
    def insert_course_structure(self, certification_title, certification_url, course_title, course_url, modules):
        """
        modules: List of dicts, each with 'title', 'url', 'description'
        """
        cert_id = self.get_or_create_certification(certification_title, certification_url)
        course_id = self.get_or_create_course(course_title, course_url, cert_id)

        for module in modules:
            self.insert_module(
                title=module['title'],
                course_id=course_id,
                url=module['url'],
                description=module['description']
            )

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()