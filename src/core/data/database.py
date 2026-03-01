"""
myStock 1.1版本 - 数据库连接模块
提供数据库连接池和基础操作
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from contextlib import contextmanager

import mysql.connector
from mysql.connector import pooling
from mysql.connector.errors import Error as MySQLError

from ..utils.helpers import Timer

logger = logging.getLogger("mystock.database")

class DatabaseManager:
    """数据库管理器"""
    
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._config = None
            self._pool = None
    
    def configure(self, config: Dict[str, Any]):
        """配置数据库连接"""
        self._config = {
            "host": config.get("host", "localhost"),
            "port": config.get("port", 3306),
            "user": config.get("user", "root"),
            "password": config.get("password", ""),
            "database": config.get("database", "mystock"),
            "charset": config.get("charset", "utf8mb4"),
            "pool_name": "mystock_pool",
            "pool_size": config.get("pool_size", 10),
            "pool_reset_session": True
        }
        
        logger.info(f"数据库配置完成: {self._config['host']}:{self._config['port']}/{self._config['database']}")
    
    def initialize_pool(self):
        """初始化连接池"""
        if self._pool is not None:
            return
        
        try:
            self._pool = mysql.connector.pooling.MySQLConnectionPool(**self._config)
            logger.info(f"数据库连接池初始化成功，大小: {self._config['pool_size']}")
        except MySQLError as e:
            logger.error(f"数据库连接池初始化失败: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接（上下文管理器）"""
        if self._pool is None:
            self.initialize_pool()
        
        connection = None
        try:
            connection = self._pool.get_connection()
            yield connection
        except MySQLError as e:
            logger.error(f"获取数据库连接失败: {e}")
            raise
        finally:
            if connection:
                connection.close()
    
    def execute_query(self, query: str, params: Tuple = None, 
                     fetch_all: bool = True) -> Optional[List[Tuple]]:
        """执行查询语句"""
        with Timer(f"执行查询: {query[:50]}..."):
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, params or ())
                    
                    if fetch_all:
                        result = cursor.fetchall()
                    else:
                        result = cursor.fetchone()
                    
                    cursor.close()
                    return result
                    
            except MySQLError as e:
                logger.error(f"查询执行失败: {e} - 查询: {query}")
                return None
    
    def execute_update(self, query: str, params: Tuple = None) -> int:
        """执行更新语句（INSERT/UPDATE/DELETE）"""
        with Timer(f"执行更新: {query[:50]}..."):
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, params or ())
                    affected_rows = cursor.rowcount
                    conn.commit()
                    cursor.close()
                    
                    logger.debug(f"更新影响行数: {affected_rows}")
                    return affected_rows
                    
            except MySQLError as e:
                logger.error(f"更新执行失败: {e} - 查询: {query}")
                return 0
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """批量执行语句"""
        with Timer(f"批量执行: {query[:50]}..."):
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.executemany(query, params_list)
                    affected_rows = cursor.rowcount
                    conn.commit()
                    cursor.close()
                    
                    logger.debug(f"批量更新影响行数: {affected_rows}")
                    return affected_rows
                    
            except MySQLError as e:
                logger.error(f"批量执行失败: {e} - 查询: {query}")
                return 0
    
    def check_connection(self) -> bool:
        """检查数据库连接"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                
                if result and result[0] == 1:
                    logger.info("数据库连接正常")
                    return True
                else:
                    logger.warning("数据库连接检查异常")
                    return False
                    
        except MySQLError as e:
            logger.error(f"数据库连接检查失败: {e}")
            return False
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """获取表结构信息"""
        query = """
        SELECT 
            COLUMN_NAME,
            DATA_TYPE,
            IS_NULLABLE,
            COLUMN_DEFAULT,
            COLUMN_KEY,
            EXTRA,
            COLUMN_COMMENT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        ORDER BY ORDINAL_POSITION
        """
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, (self._config["database"], table_name))
                columns = cursor.fetchall()
                cursor.close()
                
                logger.info(f"获取表结构: {table_name} - 列数: {len(columns)}")
                return columns
                
        except MySQLError as e:
            logger.error(f"获取表结构失败: {e} - 表名: {table_name}")
            return []
    
    def get_table_size(self, table_name: str) -> Dict[str, Any]:
        """获取表大小信息"""
        query = """
        SELECT 
            TABLE_NAME,
            TABLE_ROWS,
            DATA_LENGTH,
            INDEX_LENGTH,
            DATA_FREE,
            CREATE_TIME,
            UPDATE_TIME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        """
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, (self._config["database"], table_name))
                result = cursor.fetchone()
                cursor.close()
                
                if result:
                    # 转换为MB
                    data_mb = result.get("DATA_LENGTH", 0) / (1024 * 1024)
                    index_mb = result.get("INDEX_LENGTH", 0) / (1024 * 1024)
                    free_mb = result.get("DATA_FREE", 0) / (1024 * 1024)
                    
                    size_info = {
                        "table_name": result["TABLE_NAME"],
                        "rows": result["TABLE_ROWS"],
                        "data_mb": round(data_mb, 2),
                        "index_mb": round(index_mb, 2),
                        "total_mb": round(data_mb + index_mb, 2),
                        "free_mb": round(free_mb, 2),
                        "create_time": result["CREATE_TIME"],
                        "update_time": result["UPDATE_TIME"]
                    }
                    
                    logger.info(f"表大小信息: {table_name} - 行数: {size_info['rows']}, 大小: {size_info['total_mb']}MB")
                    return size_info
                else:
                    logger.warning(f"表不存在: {table_name}")
                    return {}
                    
        except MySQLError as e:
            logger.error(f"获取表大小失败: {e} - 表名: {table_name}")
            return {}
    
    def optimize_table(self, table_name: str) -> bool:
        """优化表（整理碎片）"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"OPTIMIZE TABLE `{table_name}`")
                result = cursor.fetchone()
                cursor.close()
                
                if result and result[1] == "OK":
                    logger.info(f"表优化成功: {table_name}")
                    return True
                else:
                    logger.warning(f"表优化失败: {table_name} - 结果: {result}")
                    return False
                    
        except MySQLError as e:
            logger.error(f"表优化执行失败: {e} - 表名: {table_name}")
            return False
    
    def backup_table(self, table_name: str, backup_suffix: str = "_backup") -> bool:
        """备份表"""
        backup_table = f"{table_name}{backup_suffix}"
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 检查备份表是否存在，如果存在则删除
                cursor.execute(f"DROP TABLE IF EXISTS `{backup_table}`")
                
                # 创建备份表
                cursor.execute(f"CREATE TABLE `{backup_table}` LIKE `{table_name}`")
                
                # 复制数据
                cursor.execute(f"INSERT INTO `{backup_table}` SELECT * FROM `{table_name}`")
                
                conn.commit()
                cursor.close()
                
                logger.info(f"表备份成功: {table_name} -> {backup_table}")
                return True
                
        except MySQLError as e:
            logger.error(f"表备份失败: {e} - 表名: {table_name}")
            return False

# 全局数据库管理器实例
db_manager = DatabaseManager()

def init_database(config: Dict[str, Any]):
    """初始化数据库管理器"""
    db_manager.configure(config)
    db_manager.initialize_pool()
    
    # 测试连接
    if db_manager.check_connection():
        logger.info("数据库初始化成功")
        return True
    else:
        logger.error("数据库初始化失败")
        return False

if __name__ == "__main__":
    # 测试数据库模块
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent))
    
    from config.settings import DATABASE_CONFIG
    
    print("=== 数据库模块测试 ===")
    
    # 初始化
    if init_database(DATABASE_CONFIG):
        print("数据库初始化: 成功")
        
        # 测试查询
        result = db_manager.execute_query("SELECT VERSION()")
        if result:
            print(f"MySQL版本: {result[0][0]}")
        
        # 检查连接
        if db_manager.check_connection():
            print("数据库连接: 正常")
        
        # 获取表信息（如果存在）
        tables = ["stocks", "signals", "push_history"]  # 假设的表名
        for table in tables:
            info = db_manager.get_table_info(table)
            if info:
                print(f"表 {table} 结构: {len(info)} 列")
            else:
                print(f"表 {table}: 不存在或无法访问")
    
    else:
        print("数据库初始化: 失败")
    
    print("=" * 40)