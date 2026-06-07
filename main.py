from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

# 导入 MySQL 相关的库，请在 requirements.txt 中添加 PyMySQL==1.1.1
import pymysql

@register("astrbot_plugin_whitelist_mysql", "Lrx", "将审核通过的QQ号存入MySQL白名单", "1.0.0")
class WhitelistMysqlPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    def get_mysql_connection(self):
        # 请务必替换下面的配置信息
        return pymysql.connect(
            host='38.22.235.105',
            user='Allow',
            password='Lrx1013***',
            database='Allow',
            charset='utf8mb4'
        )

    @filter.command("save_whitelist")
    async def add_to_whitelist(self, event: AstrMessageEvent):
        """保存QQ号到白名单的命令，用法：/save_whitelist <QQ号>"""
        # 1. 解析命令，获取QQ号
        message_text = event.message_str
        parts = message_text.split()
        if len(parts) != 2:
            yield event.plain_result("用法错误，请使用 `/save_whitelist <QQ号>` 命令。")
            return

        qq_number = parts[1]
        # 这里可以增加你的审核逻辑，例如：
        # 检查用户是否已存在、是否满足某些条件等等...

        # 2. 写入MySQL数据库
        connection = None
        try:
            connection = self.get_mysql_connection()
            with connection.cursor() as cursor:
                # 假设你的白名单表名叫 user_whitelist，字段为 qq
                sql = "INSERT INTO `user_whitelist` (`qq`) VALUES (%s)"
                cursor.execute(sql, (qq_number,))
                connection.commit()
                logger.info(f"成功将QQ {qq_number} 添加到白名单。")
                yield event.plain_result(f"成功！已将QQ号 {qq_number} 添加到服务器白名单。")

        except pymysql.err.IntegrityError:
            logger.warning(f"QQ {qq_number} 已存在于白名单中。")
            yield event.plain_result(f"QQ号 {qq_number} 已经在白名单中了，无需重复添加。")
        except Exception as e:
            logger.error(f"数据库操作失败: {e}")
            yield event.plain_result(f"处理你的请求时服务器开小差了，请稍后再试。错误类型: {type(e).__name__}")
        finally:
            if connection:
                connection.close()

    async def terminate(self):
        logger.info("白名单MySQL插件已卸载。")
