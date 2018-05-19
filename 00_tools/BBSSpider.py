import Configs

detail_url = '''
http://news.qq.com/
'''
save_field = {
    't': "span[id='echoData']",
}

res = Configs.ToolsObjManager.extract_tool.extract_by_bs4(detail_url, save_field)
print(res[0])
