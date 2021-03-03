"""
EMPI患者主索引
字段：
1.肾小球总数        √
2.球性硬化小球数     √
3.新月体小球数目     √
4.节段性硬化数目     √
5.内皮细胞增生     √
6.毛细血管管腔     √
7.系膜区     √
8.系膜细胞     √
9.系膜基质     √
10.免疫复合物     ×
11.肾小管萎缩     √
12.间质纤维化
13.间质炎症细胞浸润
14.间质血管病变
15.诊断            √
16.硬化小球比例      √
17.节段硬化小球比例   √
18.新月体小球比例     √

计算指标
硬化小球比例：球性硬化小球数/肾小球总数
节段硬化小球比例：节段性硬化数目/肾小球总数
新月体小球比例：新月体小球数目/肾小球总数
"""

import pandas as pd
import numpy as np
from string import digits

pd.set_option('display.max_columns', 23)  # 设置显示的最大列数参数为a
pd.set_option('display.width', 1500)  # 设置显示的宽度为500，防止输出内容被换行
pd.set_option('max_colwidth', 100)  # 设置显示列值的宽度为100
pd.set_option('display.max_rows', None)  # 设置显示的行宽为全部，将所有行显示出来

"""
读取数据
"""
# 1.读取数据 HIS系统病理筛选.xlsx
sz_data = pd.read_excel("/home/lxl/pythonProject/Extraction-infomation/data/HIS系统病理筛选.xlsx")  # 1195
# 2.查看是否每条记录都有”光镜“字符串
is_guangjing = sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('光镜：')]  # 1195，与总记录匹配，说明每条记录都有
# 3.以”光镜“二字作为切分点，只留下存放信息的字符串
sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'] = sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].apply(lambda x: x.split('光镜：')[1])

"""
“诊断”共有3种出现情况：
a.小结：……
b.小结：1、……；\n2、……；\n3:、……；
c.医生没有写小结
"""
# 4.匹配--诊断
# （1）查看是否每条记录都有关键词“小结”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('小结')]))  # 1191，说明有4条记录没有小结
# （2）提取“诊断”
sz_data['诊断'] = sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.extract('.*?小结：([\d\D*|\D*]+)')
# （3）查看多少Nan值
print(sz_data[sz_data['诊断'].isna()])  # 4条记录为Nan，即医生有4条记录没有写小结
# （4）将Nan值填充为“无”
sz_data['诊断'] = sz_data['诊断'].fillna('无')

"""
去除“小结”部分
"""
# 5.去除DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)列中小结部分，防止总结中出现的描述与需要提取的关键词冲突
sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'] = sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].apply(lambda x: x.split('小结')[0])
# 6.再次检验DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)中是否存在小结
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('小结')]))  # 0

"""
“肾小球总数”共有8种出现情况：
a.光镜：皮髓质肾组织1条,12个肾小球均已废弃。（英文标点符号）
b.光镜：皮髓质肾组织1条，12个肾小球均已废弃。
c.光镜：皮髓质肾组织1条，8肾小球均已废弃。
d.光镜：二十七个体积略增大肾小球，毛细血管袢开放。   ?
e.光镜：17个体积略增大肾小球，毛细血管袢开放。
f.光镜：皮髓质肾组织2条，镜下大部分为髓质组织，仅在皮髓交界处见1个形态欠完整的肾小球。
g.光镜：皮质肾组织2条，镜下仅见9个废弃球。（未出现关键词“肾小球”，则按照特殊情况处理）
h.光镜：皮质肾组织1条。12小球中见1个球性废弃。
"""
# 7.匹配--肾小球总数
# （1）查看共有多少条记录出现“未见肾小球”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('未见肾小球')]))  # 18
# （2）“未见肾小球”18条记录，将“未见肾小球”修改为“0个未见肾小球”，便于后续正则提取
sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'] = sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].apply(lambda x: x.replace('未见肾小球', '0个未见肾小球'))
# （3）查看共有多少条记录出现“未见……肾小球”的书写情况
print(len(sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('(未见[\u4E00-\u9FA5]+肾小球)')))
# （4）提取肾小球总数
sz_data['肾小球总数'] = sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.extract('[，。？！,.?!]*(\d+|[一二三四五六七八九十]+)\D*肾小球')
# （5）查看“肾小球总数”为Nan值的记录
print(sz_data[sz_data['肾小球总数'].isna()])
# 结果：显示仅有一条记录，内容为：皮髓质肾组织1条，仅见一个完全硬化的小球。（没有关键词“肾小球”）
# （6）将“肾小球总数”为Nan值的列根据实际情况填充值
sz_data.loc[804, '肾小球总数'] = '1'
# （7）检验“肾小球总数”为1、0的数据是否提取正确
print(sz_data[sz_data['肾小球总数'] == '1'])
# （8）数量不多，对应更正即可
sz_data.loc[523, '肾小球总数'] = '12'
sz_data.loc[737, '肾小球总数'] = '9'
print(sz_data[sz_data['肾小球总数'] == '0'])
# （9）“肾小球总数”列值转为int型数值
sz_data['肾小球总数'] = sz_data['肾小球总数'].astype(int)

"""
“球性硬化小球数”共有2种情况：
a.41个肾小球中见7个球性废弃及1处节段硬化
b.未描述球性废弃
"""
# 8.匹配--球性硬化小球数
# （1）查看共有多少条记录出现关键词“废弃”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('废弃')]))  # 615
# （2）查看共有多少条记录出现“未见……废弃”的书写情况
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('未见[\u4E00-\u9FA5]+废弃')]))  # 1
# （3）由于数量仅有1条，对应更正即可
sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'] = sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].apply(lambda x: x.replace('未见球性废弃', '0个球性废弃'))
# （4）提取“球性硬化小球数”
sz_data['球性硬化小球数'] = sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.extract('.*?(\d+)\D*废弃')
# （5）将Nan值填充为0
sz_data['球性硬化小球数'] = sz_data['球性硬化小球数'].fillna(0)
# （6）“球性硬化小球数”列值转为int型数值
sz_data['球性硬化小球数'] = sz_data['球性硬化小球数'].astype(int)

"""
“新月体小球数目”共有8种出现情况：--细胞、纤维细胞、细胞纤维、纤维
a.皮髓质肾组织1条，5个肾小球见2个新月体。 （个新月体）
b.皮髓质肾组织1条，5个肾小球见2个节段性纤维细胞性新月体。  （纤维细胞）
c.皮质肾组织1条，12个肾小球，体积轻度增大，可见5个细胞性新月体。  （细胞）
d.皮质及皮髓质肾组织2条。18个肾小球中见7个纤维细胞性及2个细胞性新月体。  （纤维细胞、细胞）
e.皮质肾组织2条，34个肾小球中见3个球性废弃，1个细胞性、9个纤维细胞性及5个纤维性新月体。  （细胞、纤维细胞、纤维）
f.皮髓质肾组织1条。36个肾小球中2个节段性新月体，其中1个为纤维性，另1个为细胞纤维性。  （纤维、细胞纤维）
g.未见新月体
h.未描述新月体
"""
# 9.匹配--新月体
# （1）查看共有多少条记录出现关键词“新月体”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('新月体')]))  # 252
# （2）查看共有多少条记录出现“未见新月体”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('未见新月体')]))  # 40
# （3）“未见新月体”40条记录，将“未见新月体”修改为“0个新月体”，便于后续正则提取
sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'] = sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].apply(lambda x: x.replace('未见新月体', '0个新月体'))
# （4）查看“未见……新月体”的数量
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('未见[\u4E00-\u9FA5]+新月体')]))  # 4
# （5）由于数量仅有4条，且4种书写情况均不一致，则采用对应修正方式即可
sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'] = sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].apply(lambda x: x.replace('未见确切新月体', '0个新月体'))
sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'] = sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].apply(lambda x: x.replace('未见典型新月体', '0个新月体'))
sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'] = sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].apply(lambda x: x.replace('未见袢坏死及新月体', '0个新月体'))
# （6）提取“新月体小球数目”
sz_data['新月体小球数目'] = sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.extract('.*?(\d+)\D*新月体')
# （7）查看“新月体小球数目”列值是否有256个非空值
print(sz_data[sz_data['新月体小球数目'].notna()])  # 252
# （8）将Nan值填充为0
sz_data['新月体小球数目'] = sz_data['新月体小球数目'].fillna(0)
# （9）将“新月体小球数目”列值转为int型
sz_data['新月体小球数目'] = sz_data['新月体小球数目'].astype(int)
# 由于医生对于新月体小球数量有多种描述，其中新月体小球数量少则使用1个数值，多则使用4个数值，
# 如“皮质肾组织2条，34个肾小球中见3个球性废弃，1个细胞性、9个纤维细胞性及5个纤维性新月体”，
# 在未知医生描述患者新月体有多少个数值时，无法使用一条正则表达式提取全部信息。
# （10）由于医生对新月体存在分开描述“18个肾小球中见5个细胞性及9个纤维细胞性新月体。”的情况，因此需要将两个数字都提取出来并算出总和替代“新月体小球数目”列只提取出的那个数值
sz_data[['新月体1', '新月体2']] = sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.extract('.*?(\d+)\D*[纤维|细胞]\D*(\d+)\D*[纤维|细胞]\D*新月体')
# （11）将“新月体1”、“新月体2”两列的Nan值填充为0
sz_data[['新月体1', '新月体2']] = sz_data[['新月体1', '新月体2']].fillna(0)
# （12）将“新月体1”、“新月体2”两列的数值转换为int型
sz_data[['新月体1', '新月体2']] = sz_data[['新月体1', '新月体2']].astype(int)
# （13）将“新月体1”、“新月体2”两列的数值相加
sz_data['新月体12'] = sz_data['新月体1'] + sz_data['新月体2']
# （14）删除临时列“新月体1”、“新月体2”
sz_data = sz_data.drop(sz_data[['新月体1', '新月体2']], axis=1)
# （15）将“新月体12”列值与“新月体小球数目”列值进行对比，若“新月体12”列中的值大于“新月体小球数目”对应的值，则替换“新月体小球数目”列中的值，反之不替换。
sz_data['新月体小球数目'] = sz_data.apply(lambda x: max(x['新月体小球数目'], x['新月体12']), axis=1)
# （16）查看“新月体12”不为0的记录
print(sz_data[sz_data['新月体12'] != 0][['EMPI_ID', 'DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)', '新月体12']])  # 63
# （17）排查“新月体12”不为0的记录中有无第二次正则匹配错误的情况，若有则将其手动修改
sz_data.loc[74, '新月体小球数目'] = 1
# 皮髓质肾组织1条，5个肾小球中1个球性废弃，余正切球体积增大，系膜区节段中度增宽，系膜细胞增殖伴基质增多，毛细血管袢开放尚好，节段袢内皮细胞增殖、肿胀，袢内少量单个核细胞浸润，节段外周袢与囊壁粘连，1处见节段性细胞性新月体形成，囊壁节段增厚。
sz_data.loc[653, '新月体小球数目'] = 2
# "皮质及皮髓质肾组织2条。10个肾小球中9个球性废弃伴囊壁纤维素样渗出，且有2个废弃球可见纤维细胞性新月体残迹。
sz_data.loc[695, '新月体小球数目'] = 9
# 皮质及髓质肾组织2条，22个肾小球中见12个球性废弃，废弃球中见2个细胞性新月体残留，余10个肾小球见亦见2个细胞性及5个纤维细胞性新月体，受新月体挤压，其中6个球出现明显节段硬化，
sz_data.loc[844, '新月体小球数目'] = 3
# 皮髓质肾组织2条。10个肾小球中8个球已接近球性废弃，且均伴有明显的袢坏死、炎细胞浸润及囊壁断裂，其中3个球见纤维性新月体残迹。
sz_data.loc[1114, '新月体小球数目'] = 9
# 送检皮质肾组织2条，石蜡切片见7个肾小球，冰冻组织经石蜡包埋、切片后见10个肾小球，17个肾小球中见2个球性废弃、9个纤维细胞性新月体，并见1处节段瘢痕，内皮细胞未见明显增殖，但因新月体挤压致袢腔开放欠佳；
sz_data.loc[1132, '新月体小球数目'] = 19
# 皮髓质肾组织2条，19个肾小球，16个肾小球已废弃，大部分废弃球可见新月体残迹，剩余3个肾小球，其中2个球见细胞性新月体，1个球见纤维细胞性新月体，内皮细胞未见明显增殖，因新月体挤压几乎已无袢腔开放，系膜区增宽情况不易观察；
# （18）删除临时列“新月体12”
del sz_data['新月体12']
# （19）由于医生对新月体存在分开描述“包括5个纤维性、2个纤维细胞性及2个细胞性新月体（伴节段袢坏死），并见1处节段硬化，”，因此需要将三个数字都提取出来并算出总和替代“新月体小球数目”列只提取出的那个数值
sz_data[['新月体1', '新月体2', '新月体3']] = sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.extract('.*?(\d+)\D*[纤维|细胞]\D*(\d+)\D*[细胞|纤维]\D*(\d+)\D*[纤维|细胞]\D*新月体')
# （20）将“新月体1”、“新月体2”、“新月体3”三列的Nan值填充为0
sz_data[['新月体1', '新月体2', '新月体3']] = sz_data[['新月体1', '新月体2', '新月体3']].fillna(0)
# （21）将“新月体1”、“新月体2”、“新月体3”三列的数值转换为int型
sz_data[['新月体1', '新月体2', '新月体3']] = sz_data[['新月体1', '新月体2', '新月体3']].astype(int)
# （22）将“新月体1”、“新月体2”、“新月体3”三列的数值相加
sz_data['新月体123'] = sz_data['新月体1'] + sz_data['新月体2'] + sz_data['新月体3']
# （23）删除临时列“新月体1”、“新月体2”、“新月体3”
sz_data = sz_data.drop(sz_data[['新月体1', '新月体2', '新月体3']], axis=1)
# （24）查看“新月体123”不为0的记录
print(sz_data[sz_data['新月体123'] != 0][['EMPI_ID', 'DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)', '新月体123']])  # 14
# 检查结果都匹配第三次正则
# （25）将“新月体123”列值与“新月体小球数目”列值进行对比，若“新月体123”列中的值大于“新月体小球数目”对应的值，则替换“新月体小球数目”列中的值，反之不替换。
sz_data['新月体小球数目'] = sz_data.apply(lambda x: max(x['新月体小球数目'], x['新月体123']), axis=1)
# （26）删除临时列“新月体123”
del sz_data['新月体123']

"""
“节段性硬化数目”共有10种出现情况
a.皮髓质肾组织2条，经反复深切连片，镜下见6个肾小球，其中1个球趋向硬化，
b.毛细血管袢开放尚好，其中1个球足细胞增生较明显，且毛细血管袢稍显扭曲，但未明显硬化
c.皮质肾组织1条。14个肾小球中5个球性硬化，
d.在不同切面上见6-10个肾小球，其中2个为硬化球，
e.镜下仅见2个不完整的肾小球，且1个肾小球趋向球性硬化，
f.镜下仅见1个肾小球，且在部分切片中有硬化趋势，
g.皮髓质肾组织1条，仅见一个完全硬化的小球。
h.皮髓质肾组织2条，8个肾小球中见1个节段性纤维性新月体伴节段袢粘连、硬化，
i.皮质肾组织2条，40个肾小球中3个球性硬化，
j.未描述节段性硬化
"""
# 10.匹配--节段性硬化数目
# （1）查看共有多少条记录出现关键词“硬化”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('硬化')]))  # 201
# （2）查看共有多少条记录出现关键词“节段性硬化”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('节段性硬化')]))  # 0
# （3）查看共有多少条记录出现关键词“节段硬化”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('节段硬化')]))  # 183
# （4）查看存在关键词“硬化”但非“节段硬化”的记录出现的描述
t1 = sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('硬化')]
print(t1[~t1['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('节段硬化')])  # 18
# （5）查看共有多少条记录出现关键词“无节段硬化”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('无节段硬化')]))  # 0
# （6）查看共有多少条记录出现关键词“没有节段硬化”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('没有节段硬化')]))  # 0
# （7）将“未明显硬化”1条记录，将“未明显硬化”修改为“0个硬化”，便于后续正则提取
sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'] = sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].apply(lambda x: x.replace('未明显硬化', '0个硬化'))
# （8）提取“节段性硬化数目”
sz_data['节段性硬化数目'] = sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.extract('.*?(\d+|[一二三四五六七八九十]+)\D*硬化')
# （9）查看“节段性硬化数目”为Nan值的记录
print(sz_data[sz_data['节段性硬化数目'].isna()])  # 994
# （10）将Nan值填充为0
sz_data['节段性硬化数目'] = sz_data['节段性硬化数目'].fillna(0)
# （11）“球性硬化小球数”列值转为int型数值
sz_data['节段性硬化数目'] = sz_data['节段性硬化数目'].astype(int)


"""
“内皮细胞增生”共有7种出现情况：
a.内皮细胞未见明显肿胀
b.内皮细胞肿胀
c.2个球见节段内皮细胞增殖
d.内皮细胞成对
e.内皮细胞节段成对
f.内皮细胞未见增殖
g.未描述内皮细胞增生
"""
# 11.匹配--内皮细胞增生
# （1）查看共有多少条记录出现关键词“内皮细胞”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('内皮细胞')]))  # 416
# （2）查看共有多少条记录出现关键词“内皮细胞未见”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('内皮细胞未见')]))  # 201
# （3）在所有出现“内皮细胞”的记录里增加数字1，便于后续正则提取
sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'] = sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].apply(lambda x: x.replace('内皮细胞', '1内皮细胞'))
# （4）将“内皮细胞未见”修改为“0内皮细胞”，便于后续正则提取
sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'] = sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].apply(lambda x: x.replace('1内皮细胞未见', '0内皮细胞'))
# （5）提取“内皮细胞增生”
sz_data['内皮细胞增生'] = sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.extract('.*?(\d+)内皮细胞')
# （6）查看“内皮细胞增生”不为Nan值的记录有多少
print(len(sz_data[sz_data['内皮细胞增生'].notna()]))  # 416
# （7）将Nan值填充为0
sz_data['内皮细胞增生'] = sz_data['内皮细胞增生'].fillna(0)
# （11）“球性硬化小球数”列值转为int型数值
sz_data['内皮细胞增生'] = sz_data['内皮细胞增生'].astype(int)
# 总结：（内皮细胞增生、记录数量）
# 0    980
# 1    215


"""
“毛细血管管腔”共有19种出现情况
a.未见袢坏死，（与开放性无关）
b.袢腔开放欠佳
c.袢腔开放不佳
d.袢腔狭窄，（与开放性无关）
e.毛细血管袢开放好
f.毛细血管袢尚开放，
g.毛细血管袢开放可，
h.毛细血管袢开放差，
i.毛细血管袢开放欠佳，
j.毛细血管袢开放尚佳，
k.毛细血管袢开放不佳，
l.毛细血管袢扭曲、稍显僵硬，
m.毛细血管袢开放，略显僵硬
n.毛细血管袢开放、轻度僵硬，
o.毛细血管袢皱缩易见，
p.毛细血管袢受压、开放欠佳，
q.毛细血管袢开欠佳，
r.毛细血管袢开放佳
s.未描述毛细血管管腔
"""
# 12.匹配--毛细血管管腔
# （1）查看共有多少条记录出现关键词“毛细血管袢”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('毛细血管袢')]))  # 1115
# （2）查看共有多少条记录出现关键词“毛细血管袢……开放”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('毛细血管袢[\u4E00-\u9FA5]+开放')]))  # 46
# （3）查看共有多少条记录出现关键词“毛细血管袢尚开放”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('尚开放')]))  # 46
# 注：出现关键词“毛细血管袢……开放”刚好46条记录均为“毛细血管袢尚开放”
# （4）查看共有多少条记录出现关键词“毛细血管袢……佳”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('开放[\u4E00-\u9FA5]+佳')]))  # 40
# （5）查看共有多少条记录出现关键词“毛细血管袢欠佳”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('开放欠佳')]))  # 40
# （6）查看共有多少条记录出现关键词“毛细血管袢不佳”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('开放不佳')]))  # 22
# （7）查看共有多少条记录出现关键词“毛细血管袢尚佳”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('开放尚佳')]))  # 4
# 注：出现关键词“毛细血管袢……佳”刚好40条记录包含了“毛细血管袢开放欠佳”、“毛细血管袢开放不佳”、“毛细血管袢开放尚佳”三种描述情况
# （8）将出现“开放欠佳”、“开放不佳”、“开欠佳”的记录修改为“开放差”
sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'] = sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].apply(lambda x: x.replace('开放欠佳', '开放差'))  # 40
sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'] = sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].apply(lambda x: x.replace('开放不佳', '开放差'))  # 22
sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'] = sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].apply(lambda x: x.replace('开欠佳', '开放差'))  # 2
# （9）将存在“开放差”的记录确定为“毛细血管管腔”为1
sz_data.loc[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('开放差'), '毛细血管管腔'] = 1
# （10）将“毛细血管管腔”列为Nan值的记录改为0
sz_data['毛细血管管腔'] = sz_data['毛细血管管腔'].fillna(0)
# 总结：（毛细血管管腔、记录数量）
# 0.0    1130
# 1.0      65


"""
“系膜区”提取规则：
“轻”提取1
“中”提取2
“重”提取3
其余0
"""
# 13.匹配--系膜区
# （1）查看共有多少条记录出现关键词“系膜区”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('系膜区')]))  # 1167
# （2）提取包含关键词“系膜区”的记录，创建ximoqu表
ximoqu = sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('系膜区')][['EMPI_ID', 'DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)']]
# （3）在ximoqu表中增加“系膜区”一列，内容即提取系膜区所在句子
ximoqu['系膜区1'] = "系膜区" + ximoqu['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].apply(lambda x: x.split('系膜区')[1].split('，')[0])
# （4）去除系膜区中出现的数字，以免对后续提取造成干扰
ximoqu['系膜区1'] = ximoqu['系膜区1'].apply(lambda x: x.translate(str.maketrans('', '', digits)))
# （5）在ximoqu表中“系膜区”列中找到关键词“轻”、“中”、“重”，对应替换成需要提取的数字
ximoqu['系膜区1'] = ximoqu['系膜区1'].apply(lambda x: x.replace('轻', '1轻'))
ximoqu['系膜区1'] = ximoqu['系膜区1'].apply(lambda x: x.replace('中', '2中'))
ximoqu['系膜区1'] = ximoqu['系膜区1'].apply(lambda x: x.replace('重', '3重'))
# （6）提取出ximoqu表中“系膜区”列的数字
ximoqu['系膜区'] = ximoqu['系膜区1'].str.extract('(\d+)')
# （7）检验纠错
ximoqu.loc[1189, '系膜区'] = 0
# （8）将ximoqu表与sz_data表进行“EMPI_ID”、“DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)”列外连接合并
sz_data = pd.merge(sz_data, ximoqu, on=['EMPI_ID', 'DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'], how='left')
# （9）“系膜区”的Nan值填充为0
sz_data['系膜区'] = sz_data['系膜区'].fillna(0)
# （10）删除“系膜区1”列
del sz_data['系膜区1']
# （11）“未见肾小球”无法提取系膜区信息，标记为“999”
sz_data.loc[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('未见肾小球'), '系膜区'] = 999
# 总结：（系膜区、记录数量）
# 1      650
# 0      395
# 2       95
# 3       38
# 999     17（未见肾小球）

"""
“系膜细胞”
a.系膜细胞增殖
b.系膜细胞增生
c.系膜细胞及基质增殖
d.未描述系膜细胞
"""
# （1）查看共有多少条记录出现关键词“系膜细胞”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('系膜细胞')]))  # 608
# （2）将存在“系膜细胞”的记录确定为“系膜细胞”为1
sz_data.loc[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('系膜细胞'), '系膜细胞'] = 1
# （3）将“系膜细胞”列为Nan值的记录改为0
sz_data['系膜细胞'] = sz_data['系膜细胞'].fillna(0)
# 总结：（系膜细胞、记录数量）
# 1.0    608
# 0.0    587

"""
“系膜基质”
a.基质增多
b.系膜基质稍增多
c.系膜细胞及基质增殖
d.基质稍增多
e.基质明显增多
f.基质增加为主
g.未描述系膜细胞
"""
# （1）查看共有多少条记录出现关键词“系膜细胞”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('基质')]))  # 643
# （2）将存在“基质”的记录确定为“系膜基质”为1
sz_data.loc[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('基质'), '系膜基质'] = 1
# （3）将“系膜基质”列为Nan值的记录改为0
sz_data['系膜基质'] = sz_data['系膜基质'].fillna(0)
# 总结：（系膜基质、记录数量）
# 1.0    643
# 0.0    552

"""
“免疫复合物”共有13种出现情况：（医生对其定义不清晰，不予提取）
a.PASM-Masson：毛细血管袢腔内见嗜复红物。
b.PASM-Masson：肾小球节段袢分层、嗜银强弱不一。
c.PASM-Masson：偶见上皮侧毛刺状嗜银物。
d.PASM-Masson：肾小球内皮下及系膜区少量嗜复红物沉积。
e.PASM-Masson：阴性。
f.PASM-Masson：嗜红物沉积不明显。
g.PASM-Masson：不确切。
h.PASM-Masson：。
i.PASM-Masson：系膜区节段少量嗜复红物沉积。
j.PASM-Masson：系膜区似见嗜复红物沉积。
k.PASM-Masson：系膜区较多嗜复红物沉积。
l.PASM-Masson：肾小球上皮侧较多嗜复红物沉积。
m.未描述嗜复红物沉积
n.PASM-Masson：内皮下及系膜区少量、上皮侧偶见嗜复红物沉积，
o.PASM-Masson：上皮侧及系膜区节段嗜复红物沉积。
p.PASM-Masson：肾小球上皮侧及系膜区少量嗜复红物沉积，
"""
# 匹配--嗜复红物沉积
# （1）查看共有多少条记录出现关键词“嗜复红物沉积”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('嗜复红物沉积')]))  # 805
# （2）查看共有多少条记录出现关键词“阴性”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('阴性')]))  # 354
# （3）查看共有多少条记录出现关键词“不确切”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('不确切')]))  # 1
# （4）查看共有多少记录出现关键词“嗜红物沉积”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('嗜红物沉积')]))  # 2
# （6）查看共有多少记录出现关键词“嗜复红物”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('嗜复红物')]))  # 813
# （7）查看共有多少记录出现关键词“嗜银”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('嗜银')]))  # 7
# （8）将出现关键词“阴性”的记录修改为“0免疫复合物”
sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'] = sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].apply(lambda x: x.replace('阴性', '0免疫复合物，阴性'))
# （9）将出现内容为“大量嗜复红物沉积”的记录修改为“1免疫复合物”
sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'] = sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].apply(lambda x: x.replace('大量嗜复红物沉积', '0免疫复合物'))

print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('上皮侧[\u4E00-\u9FA5]+嗜复红物沉积')]))  # 380
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('上皮侧大量嗜复红物沉积')]))  # 66
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('上皮侧少量嗜复红物沉积')]))  # 125
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('上皮侧较多嗜复红物沉积')]))  # 113
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('上皮侧较少嗜复红物沉积')]))  # 0
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('上皮侧偶见嗜复红物沉积')]))  # 23
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('上皮侧及系膜区节段嗜复红物沉积')]))  # 2
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('上皮侧及系膜区少量嗜复红物沉积')]))  # 11
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('上皮侧及系膜区大量嗜复红物沉积')]))  # 1
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('上皮侧及系膜区较多嗜复红物沉积')]))  # 3
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('上皮侧及系膜区较少嗜复红物沉积')]))  # 0
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('上皮侧节段嗜复红物沉积')]))  # 15
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('上皮侧送检嗜复红物沉积')]))  # 1
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('上皮侧疑似少量嗜复红物沉积')]))  # 2
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('上皮侧及基膜内少量嗜复红物沉积')]))  # 1
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('上皮侧及基膜内大量嗜复红物沉积')]))  # 2
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('上皮侧弥漫嗜复红物沉积')]))  # 3
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('上皮侧似见节段嗜复红物沉积')]))  # 1
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('上皮侧及内皮下少量嗜复红物沉积')]))  # 1


"""
“肾小管萎缩”
"""
# 匹配--肾小管萎缩
# （1）查看共有多少条记录出现“小管萎缩”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('小管萎缩')]))  # 1150
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('萎缩')]))  # 1158
# （2）提取包含关键词“萎缩”的记录，创建weisuo表
weisuo = sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('萎缩')][['EMPI_ID', 'DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)']]
# （3）在ximoqu表中增加“萎缩”一列，内容即提取萎缩所在句子
weisuo['萎缩'] = weisuo['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].apply(lambda x: x.split('萎缩')[0].split('，')[-1]) + '萎缩'
# （4）去除萎缩中出现的数字，以免对后续提取造成干扰
weisuo['萎缩'] = weisuo['萎缩'].apply(lambda x: x.translate(str.maketrans('', '', digits)))
# （5）在ximoqu表中“系膜区”列中找到关键词“轻”、“中”、“重”，对应替换成需要提取的数字
weisuo['萎缩'] = weisuo['萎缩'].apply(lambda x: x.replace('多灶', '多灶2'))
weisuo['萎缩'] = weisuo['萎缩'].apply(lambda x: x.replace('灶性', '1灶性'))
weisuo['萎缩'] = weisuo['萎缩'].apply(lambda x: x.replace('小片状', '小片2状'))
weisuo['萎缩'] = weisuo['萎缩'].apply(lambda x: x.replace('片状', '3片状'))
weisuo['萎缩'] = weisuo['萎缩'].apply(lambda x: x.replace('大量', '3大量'))
# （6）提取出weisuo表中“萎缩”列的数字
weisuo['肾小管萎缩'] = weisuo['萎缩'].str.extract('(\d+)')
# （7）将weisuo表中的Nan中填充为1
weisuo['肾小管萎缩'] = weisuo['肾小管萎缩'].fillna(1)
# （8）将weisuo表中的“肾小管萎缩”列值转换为int类型
weisuo['肾小管萎缩'] = weisuo['肾小管萎缩'].astype(int)
# （9）将出现的“未见肾小管萎缩”、“肾小管未见萎缩”、“肾小管未见明显萎缩”等的“肾小管萎缩”列值均改为0
weisuo.loc[weisuo['萎缩'].str.contains('未见'), '肾小管萎缩'] = 0
# （10）删除weisuo表中的“萎缩”列
del weisuo['萎缩']
# （11）将weisuo表与sz_data表进行“EMPI_ID”、“DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)”列外连接合并
sz_data = pd.merge(sz_data, weisuo, on=['EMPI_ID', 'DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'], how='left')
# （12）将“萎缩不明显”记录的“肾小管萎缩”列值更改为0
sz_data.loc[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('萎缩不明显'), '肾小管萎缩'] = 0
# （13）将“肾小管萎缩”列值填充为0
sz_data['肾小管萎缩'] = sz_data['肾小管萎缩'].fillna(0)
# 总结：（神小管萎缩、记录数量）
# 1.0    963
# 3.0    105
# 2.0     66
# 0.0     61

"""
‘间质纤维化“共有种出现情况：
a.间质纤维化均不明显
b.纤维化不明显
c.
d.
e.
f.
g.未描述间质纤维化
"""
# 匹配--间质纤维化
# （1）查看共有多少条记录出现“纤维化”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('纤维化')]))  # 1173
# （2）提取包含关键词“纤维化”的记录，创建xianweihua表
xianweihua = sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('纤维化')][['EMPI_ID', 'DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)']]
# （3）在xianweihua表中增加“纤维化”一列，内容即提取纤维化所在句子
xianweihua['纤维化'] = '纤维化' + xianweihua['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].apply(lambda x: x.split('纤维化')[1].split('，')[0])
# （4）去除纤维化中出现的数字，以免对后续提取造成干扰
xianweihua['纤维化'] = xianweihua['纤维化'].apply(lambda x: x.translate(str.maketrans('', '', digits)))
# （5）在xianweihua表中“系膜区”列中找到关键词“轻”、“中”、“重”，对应替换成需要提取的数字
xianweihua['纤维化'] = xianweihua['纤维化'].apply(lambda x: x.replace('+++', '3'))
xianweihua['纤维化'] = xianweihua['纤维化'].apply(lambda x: x.replace('++', '2'))
xianweihua['纤维化'] = xianweihua['纤维化'].apply(lambda x: x.replace('+', '1'))
# （6）提取出xianweihua表中“纤维化”列的数字
xianweihua['间质纤维化'] = xianweihua['纤维化'].str.extract('(\d+)')
# （7）将xianweihua表中的Nan中填充为1
xianweihua['间质纤维化'] = xianweihua['间质纤维化'].fillna(1)
# （8）将xianweihua表中的“肾小管萎缩”列值转换为int类型
xianweihua['间质纤维化'] = xianweihua['间质纤维化'].astype(int)
# （9）将出现的“纤维化不明显”、“肾小管未见萎缩”等的“间质纤维化”列值均改为0
xianweihua.loc[xianweihua['纤维化'].str.contains('不明显'), '间质纤维化'] = 0
# （10）删除xianweihua表中的“纤维化”列
del xianweihua['纤维化']
# （11）将xianweihua表与sz_data表进行“EMPI_ID”、“DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)”列外连接合并
sz_data = pd.merge(sz_data, xianweihua, on=['EMPI_ID', 'DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'], how='left')
# （12）将“肾小管萎缩”列值填充为0
sz_data['间质纤维化'] = sz_data['间质纤维化'].fillna(0)
# 总结：（间质纤维化、记录数量）
# 0.0    538
# 1.0    530
# 3.0     66
# 2.0     61

"""
”间质炎症细胞浸润“共有种出现情况：
a.细胞散在浸润
b.细胞浸润
c.少量单个核细胞
d.散在极少量单个核细胞分布
"""




"""
计算指标
硬化小球比例：球性硬化小球数/肾小球总数
节段硬化小球比例：节段性硬化数目/肾小球总数
新月体小球比例：新月体小球数目/肾小球总数
"""
# # 计算硬化小球比例
# # （1）硬化小球比例：球性硬化小球数/肾小球总数
# sz_data['硬化小球比例'] = sz_data['球性硬化小球数'] / sz_data['肾小球总数']
# # （2）解决出现分母为0计算出的结果
# sz_data.replace([np.inf, -np.inf], np.nan, inplace=True)
# # （3）将Nan值填充为0
# sz_data['硬化小球比例'] = sz_data['硬化小球比例'].fillna(0)
#
# # 计算节段硬化小球比例
# # （1）节段硬化小球比例：节段性硬化数目/肾小球总数
# sz_data['节段硬化小球比例'] = sz_data['节段性硬化数目'] / sz_data['肾小球总数']
# # （2）解决出现分母为0计算出的结果
# sz_data.replace([np.inf, -np.inf], np.nan, inplace=True)
# # （3）将Nan值填充为0
# sz_data['节段硬化小球比例'] = sz_data['节段硬化小球比例'].fillna(0)
#
# # 计算新月体小球比例
# # （1）新月体小球比例：新月体小球数目/肾小球总数
# sz_data['新月体小球比例'] = sz_data['新月体小球数目'] / sz_data['肾小球总数']
# # （2）解决出现分母为0计算出的结果
# sz_data.replace([np.inf, -np.inf], np.nan, inplace=True)
# # （3）将Nan值填充为0
# sz_data['新月体小球比例'] = sz_data['新月体小球比例'].fillna(0)



# sz_data.to_excel("/home/lxl/pythonProject/Extraction-infomation/after_data/after_HIS.xlsx", encoding='utf8', index=False)








