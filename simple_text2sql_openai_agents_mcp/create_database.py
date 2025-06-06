import sqlite3


def create_sample_database():
    """创建一个名为 sample.db 的 SQLite 数据库文件并填充数据"""

    # 连接到（或创建）一个名为 sample.db 的数据库文件
    conn = sqlite3.connect("company_data.db")
    cursor = conn.cursor()

    # --- 创建表 ---

    # 创建员工表
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        position TEXT NOT NULL,
        salary REAL NOT NULL,
        hire_date TEXT NOT NULL
    );
    """
    )

    # 创建部门表
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        manager_id INTEGER,
        budget REAL NOT NULL,
        FOREIGN KEY (manager_id) REFERENCES employees(id)
    );
    """
    )

    # 创建项目表
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        department_id INTEGER,
        start_date TEXT NOT NULL,
        end_date TEXT,
        budget REAL NOT NULL,
        FOREIGN KEY (department_id) REFERENCES departments(id)
    );
    """
    )

    # 创建员工项目关联表
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS employee_projects (
        employee_id INTEGER,
        project_id INTEGER,
        role TEXT NOT NULL,
        hours_allocated INTEGER NOT NULL,
        PRIMARY KEY (employee_id, project_id),
        FOREIGN KEY (employee_id) REFERENCES employees(id),
        FOREIGN KEY (project_id) REFERENCES projects(id)
    );
    """
    )

    # --- 插入示例数据 (使用 INSERT OR IGNORE 防止重复插入) ---

    # 员工数据
    employees = [
        (1, "张三", "研发", "高级工程师", 15000, "2019-05-15"),
        (2, "李四", "研发", "工程师", 10000, "2020-03-10"),
        (3, "王五", "市场", "经理", 18000, "2018-07-22"),
        (4, "赵六", "销售", "销售代表", 9000, "2021-01-05"),
        (5, "钱七", "财务", "会计", 12000, "2020-11-18"),
        (6, "孙八", "研发", "主管", 20000, "2017-09-30"),
        (7, "周九", "人力资源", "经理", 16000, "2019-04-12"),
        (8, "吴十", "销售", "经理", 17000, "2018-10-25"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO employees VALUES (?, ?, ?, ?, ?, ?)", employees
    )

    # 部门数据
    departments = [
        (1, "研发部", 6, 1000000),
        (2, "市场部", 3, 500000),
        (3, "销售部", 8, 800000),
        (4, "财务部", 5, 300000),
        (5, "人力资源部", 7, 200000),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO departments VALUES (?, ?, ?, ?)", departments
    )

    # 项目数据
    projects = [
        (1, "新产品开发", 1, "2023-01-10", "2023-06-30", 500000),
        (2, "市场调研", 2, "2023-02-15", "2023-04-30", 100000),
        (3, "销售系统升级", 3, "2023-03-01", "2023-08-31", 200000),
        (4, "财务系统维护", 4, "2023-01-01", "2023-12-31", 50000),
        (5, "招聘计划", 5, "2023-04-01", "2023-07-31", 30000),
        (6, "技术研究", 1, "2023-05-01", None, 300000),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO projects VALUES (?, ?, ?, ?, ?, ?)", projects
    )

    # 员工项目关联数据
    employee_projects = [
        (1, 1, "开发者", 160),
        (2, 1, "测试员", 120),
        (6, 1, "项目经理", 80),
        (3, 2, "负责人", 100),
        (4, 3, "测试员", 60),
        (8, 3, "项目经理", 40),
        (5, 4, "主管", 20),
        (7, 5, "负责人", 50),
        (1, 6, "研究员", 100),
        (6, 6, "主管", 60),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO employee_projects VALUES (?, ?, ?, ?)", employee_projects
    )

    # 提交更改
    conn.commit()

    # 关闭连接
    conn.close()

    print("数据库 'sample.db' 已成功创建并填充数据。")


# --- 运行函数 ---
if __name__ == "__main__":
    create_sample_database()
