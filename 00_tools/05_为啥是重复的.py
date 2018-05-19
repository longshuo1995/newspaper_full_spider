from Extract_Tools import ExtractTools
from lxml import etree
# from bs4 import BeautifulSoup

tool = ExtractTools()
html = tool.extract_html(url='https://bbs.51credit.com/thread-3966704-2-1.html')[0]
xhtml = etree.HTML(html)
res = xhtml.xpath("//div[@id='postlist']/div")
print(len(res))
a = res[2].xpath("/table//div[@class='authi']/a")
print(len(a))
print(a.xpath('string(.)'))
# for i in range(len(res)):
#     username = res[i].xpath("//div[@class='pi']/div[@class='authi']/a[1]")[0].xpath('string(.)')
#     print(username)

# print(dir(res[0]))
# for item in res:
#     print(item.getchildren()[0].xpath("//div[@class='pi']/div[@class='authi']/a[1]")[0].xpath('string(.)'))


# soup = BeautifulSoup(html)
# soup.find()
# parrent = soup.select("div[id='postlist'] > div")
# print(len(parrent))
# for item in parrent:
#     try:
#         print(item.select("div[class='authi'] > a")[0].text)
#         print(item.select("td .t_f")[0].text)
#     except:
#         pass
