"""
EMPI患者主索引
字段：
1.肾小球总数        √
2.球性硬化小球数     √
3.新月体小球数目
4.节段性硬化数目
5.内皮细胞增生
6.毛细血管管腔
7.系膜区
8.系膜细胞
9.系膜基质
10.免疫复合物
11.肾小管萎缩
12.间质纤维化
13.间质炎症细胞浸润
14.间质血管病变
15.诊断            √
16.硬化小球比例      √
17.节段硬化小球比例
18.新月体小球比例

计算指标
硬化小球比例：球性硬化小球数/肾小球总数
节段硬化小球比例：节段性硬化数目/肾小球总数
新月体小球比例：新月体小球数目/肾小球总数
"""

import pandas as pd
import numpy as np

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
# （2）“未见肾小球”18条记录，将“未见肾小球”修改为“0个肾小球”，便于后续正则提取
sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'] = sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].apply(lambda x: x.replace('未见肾小球', '0个肾小球'))
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
sz_data[['新月体1', '新月体2']] = sz_data[['新月体1', '新月体2']].astype(int)  # 排查：3703056、3658670、3616979
# （13）将“新月体1”、“新月体2”两列的数值相加
sz_data['新月体12'] = sz_data['新月体1'] + sz_data['新月体2']
# （14）查看“新月体12”不为0的记录
print(sz_data[sz_data['新月体12'] != 0][['EMPI_ID', 'DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)', '新月体12']])  # 63
# （15）排查“新月体12”不为0的记录中有错误匹配情况，若有则将其手动修改
sz_data.loc[54, '新月体小球数目'] = 13
# 皮质肾组织条，24个肾小球中8个球性废弃，10个细胞性、2个纤维细胞性、1个纤维性新月体。
sz_data.loc[74, '新月体小球数目'] = 1
# 皮髓质肾组织1条，5个肾小球中1个球性废弃，余正切球体积增大，系膜区节段中度增宽，系膜细胞增殖伴基质增多，毛细血管袢开放尚好，节段袢内皮细胞增殖、肿胀，袢内少量单个核细胞浸润，节段外周袢与囊壁粘连，1处见节段性细胞性新月体形成，囊壁节段增厚。
sz_data.loc[241, '新月体小球数目'] = 7
# 皮质肾组织2条。37个肾小球中8个球性废弃，废弃球囊内见纤维素样渗出，2个纤维细胞性新月体及5个纤维性新月体形成。
sz_data.loc[246, '新月体小球数目'] = 10
# "皮质肾组织1条，10个肾小球均见新月体形成，其中7个为细胞性、2个为纤维细胞性、1个为纤维性新月体，
sz_data.loc[378, '新月体小球数目'] = 12
# "皮质肾组织2条，36个肾小球中7个细胞性、2个纤维性及3个纤维细胞性新月体，
sz_data.loc[407, '新月体小球数目'] = 11
# "皮质肾组织1条。23个肾小球中9个球性废弃，4个球节段硬化致大部分废弃，可见6个纤维性（部分废弃球囊腔内见新月体残迹）、4个纤维细胞性及1个细胞性新月体。
sz_data.loc[604, '新月体小球数目'] = 11
# "皮质肾组织 2条，37个肾小球中1个球性废弃、4个纤维性、4个纤维细胞性及3个细胞性新月体余肾小球系膜区中到重度增宽，
sz_data.loc[626, '新月体小球数目'] = 11
# "皮质肾组织2条，34个肾小球中3个球性废弃，7个细胞性、3个纤维细胞性及1个纤维性新月体，部分为环状体，
sz_data.loc[653, '新月体小球数目'] = 2
# "皮质及皮髓质肾组织2条。10个肾小球中9个球性废弃伴囊壁纤维素样渗出，且有2个废弃球可见纤维细胞性新月体残迹。
sz_data.loc[675, '新月体小球数目'] = 6
# "皮质及皮髓质肾组织2条，26个肾小球中有3个球性废弃、2处节段硬化并与囊壁粘连，并见3个细胞性、1个纤维细胞性及2个纤维性新月体，
sz_data.loc[694, '新月体小球数目'] = 19
# 皮质及皮髓质肾组织2条，26个肾小球中有3个球性废弃、2处节段硬化并与囊壁粘连，并见3个细胞性、1个纤维细胞性及2个纤维性新月体，
sz_data.loc[695, '新月体小球数目'] = 9
# 皮质及髓质肾组织2条，22个肾小球中见12个球性废弃，废弃球中见2个细胞性新月体残留，余10个肾小球见亦见2个细胞性及5个纤维细胞性新月体，受新月体挤压，其中6个球出现明显节段硬化，
sz_data.loc[790, '新月体小球数目'] = 9
# 皮质肾组织2条，52个肾小球中见1个球性废弃及9个节段性新月体，包括5个纤维性、2个纤维细胞性及2个细胞性新月体（伴节段袢坏死），并见1处节段硬化，
sz_data.loc[844, '新月体小球数目'] = 3
# 皮髓质肾组织2条。10个肾小球中8个球已接近球性废弃，且均伴有明显的袢坏死、炎细胞浸润及囊壁断裂，其中3个球见纤维性新月体残迹。
sz_data.loc[982, '新月体小球数目'] = 15
# 皮质肾组织 2条，34个肾小球中见3个球性废弃，1个细胞性、9个纤维细胞性及5个纤维性新月体，
sz_data.loc[1084, '新月体小球数目'] = 6
# 皮质肾组织2条，44个肾小球见4个细胞性、1个纤维性及1个纤维细胞性新月体。
sz_data.loc[1114, '新月体小球数目'] = 9
# 送检皮质肾组织2条，石蜡切片见7个肾小球，冰冻组织经石蜡包埋、切片后见10个肾小球，17个肾小球中见2个球性废弃、9个纤维细胞性新月体，并见1处节段瘢痕，内皮细胞未见明显增殖，但因新月体挤压致袢腔开放欠佳；
sz_data.loc[1132, '新月体小球数目'] = 19
# 皮髓质肾组织2条，19个肾小球，16个肾小球已废弃，大部分废弃球可见新月体残迹，剩余3个肾小球，其中2个球见细胞性新月体，1个球见纤维细胞性新月体，内皮细胞未见明显增殖，因新月体挤压几乎已无袢腔开放，系膜区增宽情况不易观察；
sz_data.loc[1153, '新月体小球数目'] = 34
# 皮质及皮髓质肾组织2条，34个肾小球中仅剩3个肾小球毛细血管袢尚开放，其余31个小球周围均见环状新月体（4个为纤维细胞性新月体，27个为纤维性新月体），因环状体挤压致袢腔完全闭塞或小球废弃；剩余3个毛细血管袢尚开放的小球周围亦均见新月体（1个细胞性、1个纤维细胞性及1个纤维性新月体）
# （15）将“新月体12”列值与“新月体小球数目”列值进行对比，若“新月体12”列中的值大于“新月体小球数目”对应的值，则替换“新月体小球数目”列中的值，反之不替换。
sz_data['新月体小球数目'] = sz_data.apply(lambda x: max(x['新月体小球数目'], x['新月体12']), axis=1)
# （16）删除临时列“新月体1”、“新月体2”
sz_data = sz_data.drop(sz_data[['新月体1', '新月体2']], axis=1)
# （17）
sz_data[['新月体1', '新月体2', '新月体3']] = sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.extract('.*?(\d+)\D*[纤维|细胞]\D*(\d+)\D*[细胞|纤维]\D*(\d+)\D*[纤维|细胞]\D*新月体')


"""
计算指标
硬化小球比例：球性硬化小球数/肾小球总数
"""
# 计算硬化小球比例
# （1）硬化小球比例：球性硬化小球数/肾小球总数
sz_data['硬化小球比例'] = sz_data['球性硬化小球数'] / sz_data['肾小球总数']
# （2）解决出现分母为0计算出的结果
sz_data.replace([np.inf, -np.inf], np.nan, inplace=True)
# （3）将Nan值填充为0
sz_data['硬化小球比例'] = sz_data['硬化小球比例'].fillna(0)






len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('小结')]) + len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('未见肾小球')])  # 1089、18


sz_data['测试1'] = sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.extract('[，。？！,.?!]*(\d+|[一二三四五六七八九十]+)\D*小球')

x = 0
for i in range(len(sz_data)):
    if sz_data.iloc[i]['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].find(u'个肾小球') != -1:
        y = 0
    elif sz_data.iloc[i]['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].find(u'未见肾小球') != -1:
        x += 1
        print(sz_data[sz_data.index == i])
    else:
        y = 0


text1 = sz_data.iloc[0]['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)']
text2 = sz_data.iloc[1]['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)']

text1.split('光镜')
sz_data[~(sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('小球') |
          sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('个肾小球'))]  # 1089
sz_data[~sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('ASM-Masson')]  # 1179






import re

s = "该通知于发布日起生效，请申请人于2017年8月30日前将材料递交到管理中心。" \
    "联系电话：（0355）3849512， (0355)39482753， 010 38492045，010-39481253， 0242—24891023，010——39281234，69384023，400-820-8820" \
    "联系人：陈先生，王小姐"
tel = re.findall(r'\d{7,8}', s)

test = pd.DataFrame({'name': [101, 102, 103, 104, 105, 106, 107, 108, 109],
                     'dis': ['皮髓质肾组织1条，5个肾小球见2个新月体。',
                             '皮髓质肾组织1条。5个肾小球见2个节段性纤维细胞性新月体。',
                             '皮髓质肾组织1条。5个肾小球见2个节段纤维新月体。',
                             '皮质肾组织2条，34个肾小球中见3个球性废弃，1个细胞性、9个纤维性及5个纤维性新月体',
                             '皮髓质肾组织1条。36个肾小球中2个节段性新月体，其中1个为纤维性，另1个为细胞纤维性。',
                             '皮质肾组织1条，12个肾小球，体积轻度增大，可见5个细胞性新月体。',
                             '皮质及皮髓质肾组织2条。18个肾小球中见7个纤维细胞性及2个细胞性新月体。',
                             '皮质及皮髓质肾组织2条。18个肾小球中见5个细胞性及9个纤维细胞性新月体。',
                             '皮质和皮髓肾组织各1条，15个肾小球中3个球性废弃2个节段新月体形成。',
                             ]},
                    index=[0, 1, 2, 3, 4, 5, 6, 7, 8])


test['新月体小球数目'] = test['dis'].str.extract('.*?(\d+)\D*新月体')
test['新月体小球数目'] = test['新月体小球数目'].astype(int)
# test[['新月体1', '新月体2', '新月体3', '新月体4']] = test['dis'].str.extract('.*?(\d+)\D*[纤维|细胞]\D*(\d+)\D*[纤维|细胞]\D*(\d+)\D*[纤维|细胞]\D*(\d+)\D*[纤维|细胞]\D*新月体')
test[['新月体1', '新月体2']] = test['dis'].str.extract('.*?(\d+)\D*[纤维|细胞]\D*(\d+)\D*[纤维|细胞]\D*新月体')
test[['新月体1', '新月体2']] = test[['新月体1', '新月体2']].fillna(0)
test['新月体12'] = test['新月体1'].astype(int) + test['新月体2'].astype(int)
test = test.drop(test[['新月体1', '新月体2']], axis=1)
test['新月体小球数目'] = test.apply(lambda x: max(x['新月体小球数目'], x['新月体12']), axis=1)

# sz_data['对比结果'] = sz_data[['肾小球总数', '球性硬化小球数']].apply(lambda x: x['肾小球总数'] == x['球性硬化小球数'], axis=1)






re.findall(r'\d{1}', '皮髓质肾组织2条，18个肾小球中见3个球性废弃。'
                '余肾小球系膜区节段轻度增宽，系膜细胞增殖、基质增多，毛细血管袢开放好，内皮细胞未见明显增殖，肾小囊壁节段增厚、分层。'
                'PASM-Masson：系膜区节段少量嗜复红物沉积。肾小管间质病变尚轻，偶见肾小管萎缩，间质纤维化不明显，极少量单个核、浆细胞散在浸润。血管未见明显病变。')


ximoqu  = '光镜：皮髓质肾组织2条，18个肾小球中见3个球性废弃。余肾小球系膜区节段轻中度增宽，系膜细胞增殖、基质增多，毛细血管袢开放好，内皮细胞未见明显增殖，肾小囊壁节段增厚、分层。' \
          'PASM-Masson：系膜区节段少量嗜复红物沉积。肾小管间质病变尚轻，偶见肾小管萎缩，间质纤维化不明显，极少量单个核、浆细胞散在浸润。血管未见明显病变。'
if ximoqu.find(u'系膜区') != -1:
    regex_str = ".*?(系膜区[\u4E00-\u9FA5]+增宽)"
    ximoqu = re.match(regex_str, ximoqu).group(1)
    if ximoqu.find(u'未见') != -1:
        x = 0
        print("0")
    elif ximoqu.find(u'轻度') != -1:
        x = 1
        print("1")
    elif ximoqu.find(u'轻中度') != -1:
        x = 2
        print("2")
    else:
        print("0")
else:
    x = 0
