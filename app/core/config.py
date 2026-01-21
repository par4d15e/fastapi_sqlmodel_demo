import warnings
from typing import Literal

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 配置来源
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # 应用信息
    app_name: str = "PAWCARE"
    debug: bool = False

    # 数据库类型 (支持 PostgreSQL 和 SQLite, 含连接池设置)
    db_type: Literal["postgres", "sqlite"] = "sqlite"

    # PostgreSQL 配置（敏感信息请通过 .env 或环境变量注入，不要在代码中硬编码）
    # 推荐在项目根目录创建 `.env` 文件，或者在部署时通过环境变量注入。
    db_host: str = "example_host"
    db_port: int = 5432
    db_user: str = "example_user"
    db_password: str = "example_password"  # 放在 .env 或环境变量中
    db_name: str = "example_db"

    # 连接池配置 (仅 PostgreSQL 有效)
    # --- 必选参数: 中等并发常用 ---
    pool_size: int = 20  # 连接池基础大小, 低: - 高: +
    max_overflow: int = 10  # 超出 pool_size 的最大连接数, 低: - 高: +
    pool_timeout: int = 30  # 获取连接超时时间 (秒), 低: + 高: -
    pool_pre_ping: bool = True  # 取连接前是否检查可用性, 低: False 高: True

    # --- 可选调优参数 (高级场景) ---
    pool_recycle: int = (
        3600  # 连接最大存活时间 (秒), 低: + 高: -, 避免长连接被数据库踢掉
    )
    pool_use_lifo: bool = (
        False  # 连接池取连接顺序, False=FIFO (默认), True=LIFO 可提高高并发命中率
    )
    echo: bool = False  # 是否打印 SQL, 开发可打开, 生产关闭

    # SQLite 配置
    sqlite_db_path: str = "./data/db.sqlite3"

    # JWT 配置（重要：请在 .env 或环境变量中设置真实的密钥，生产环境不能使用空值）
    jwt_secret: str = "example_jwt_secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Redis 配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    auth_redis_db: int = 0
    cache_redis_db: int = 1

    @computed_field
    @property
    def database_url(self) -> str:
        if self.db_type == "postgres":
            return (
                f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
                f"@{self.db_host}:{self.db_port}/{self.db_name}"
            )
        elif self.db_type == "sqlite":
            return f"sqlite+aiosqlite:///{self.sqlite_db_path}"
        else:
            raise ValueError(f"Unsupported DB_TYPE: {self.db_type}")

    @computed_field
    @property
    def engine_options(self) -> dict:
        # 统一封装 engine options, 供 create_async_engine 使用
        if self.db_type == "postgres":
            return {
                "pool_size": self.pool_size,
                "max_overflow": self.max_overflow,
                "pool_timeout": self.pool_timeout,
                "pool_recycle": self.pool_recycle,
                "pool_use_lifo": self.pool_use_lifo,
                "echo": self.echo,
            }
        # SQLite 不支持 pool 设置，返回最小参数
        return {"echo": self.echo}

    @computed_field
    @property
    def auth_redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.auth_redis_db}"

    @computed_field
    @property
    def cache_redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.cache_redis_db}"


settings = Settings()

# 运行时校验（非强制）：在非调试（生产）环境下，提示关键敏感配置未设置
# 采用警告而非抛错，避免在开发环境中因未设置 .env 导致无法运行。

if not settings.debug:
    # 如果使用 PostgreSQL，确保必要的连接信息存在
    if settings.db_type == "postgres":
        missing = [
            name
            for name in ("db_user", "db_password", "db_host", "db_name")
            if not getattr(settings, name)
        ]
        if missing:
            warnings.warn(
                f"Missing DB settings in production (.env or env vars): {', '.join(missing)}",
                RuntimeWarning,
            )
    # JWT 密钥最好存在
    if not settings.jwt_secret:
        warnings.warn(
            "Missing 'jwt_secret' in production. Please set it via .env or environment variables.",
            RuntimeWarning,
        )
