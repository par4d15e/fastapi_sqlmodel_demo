from sqlmodel import create_engine

# 使用项目目录下的 SQLite 文件（相对路径 ./database.db）
DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(
    DATABASE_URL,
    echo=True,  # 可选：打印 SQL 日志，调试时有用
)