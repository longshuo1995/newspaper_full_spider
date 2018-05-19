from A1_MongoConfigs import MongoConfig
from A3_MySqlTools import MySqlTools
from B2_ExtractTool import ExtractTools
from B1_StrTools import StrTools
from C2_EmailTools import EmailToos


class Config:
    class ToolObj:
        mongo_cfg = MongoConfig()
        mysql_tool = MySqlTools()
        str_tool = StrTools()
        extract = ExtractTools()
        email_tool = EmailToos()

    @staticmethod
    def ToolCls():
        pass

