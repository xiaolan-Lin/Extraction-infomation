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
16.硬化小球比例     √
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
# （3）检验是否存在“未见……肾小球”的书写情况
sz_data['未见肾小球测试'] = sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.extract('(未见[\u4E00-\u9FA5]+肾小球)')
# （4）查看有无“未见……肾小球”的情况出现
print(sz_data[sz_data['未见肾小球测试'].notna()])  # 结果显示一整列为Nan值，说明没有出现“未见……肾小球”的书写情况
# （5）将测试列“未见肾小球测试”删除
del sz_data['未见肾小球测试']
# （6）提取肾小球总数
sz_data['肾小球总数'] = sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.extract('[，。？！,.?!]*(\d+|[一二三四五六七八九十]+)\D*肾小球')
# （7）查看“肾小球总数”为Nan值的记录
print(sz_data[sz_data['肾小球总数'].isna()])
# 结果：显示仅有一条记录，内容为：皮髓质肾组织1条，仅见一个完全硬化的小球。（没有关键词“肾小球”）
# （8）将“肾小球总数”为Nan值的列根据实际情况填充值
sz_data.loc[804, '肾小球总数'] = '1'
# （9）检验“肾小球总数”为1、0的数据是否提取正确
print(sz_data[sz_data['肾小球总数'] == '1'])
# 修正
sz_data.loc[523, '肾小球总数'] = '12'
sz_data.loc[737, '肾小球总数'] = '9'
print(sz_data[sz_data['肾小球总数'] == '0'])
# （10）“肾小球总数”列值转为int型数值
sz_data['肾小球总数'] = sz_data['肾小球总数'].astype(int)

"""
“球性硬化小球数”共有2种情况：
a.41个肾小球中见7个球性废弃及1处节段硬化
b.未描述球性废弃
"""
# 8.匹配--球性硬化小球数
# （1）查看共有多少条记录出现关键词“废弃”
print(len(sz_data[sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('废弃')]))  # 615
# （2）查看共有多少条记录出现“未见……废弃”
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
“新月体小球数目”共有7种出现情况：
a.皮髓质肾组织1条，5个肾小球见2个新月体。
b.皮髓质肾组织1条，5个肾小球见2个节段性纤维细胞性新月体。
c.皮质肾组织1条，12个肾小球，体积轻度增大，可见5个细胞性新月体。
d.皮质及皮髓质肾组织2条。18个肾小球中见7个纤维细胞性及2个细胞性新月体。
e.皮质和皮髓肾组织各1条，15个肾小球中3个球性废弃2个节段新月体形成。
f.未见新月体
g.未描述新月体
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
sz_data[~(sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('未见肾小球') |
          sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('个肾小球'))]  # 1089
sz_data[~sz_data['DBMS_LOB.SUBSTR(A.DIAG_DESC,4000)'].str.contains('ASM-Masson')]  # 1179






import re

s = "该通知于发布日起生效，请申请人于2017年8月30日前将材料递交到管理中心。" \
    "联系电话：（0355）3849512， (0355)39482753， 010 38492045，010-39481253， 0242—24891023，010——39281234，69384023，400-820-8820" \
    "联系人：陈先生，王小姐"
tel = re.findall(r'\d{7,8}', s)

test = pd.DataFrame({'name': [101, 102, 103, 104, 105, 106],
                     'dis': ['皮髓质肾组织1条，未见明显肾小球均已废弃。肾小管间质慢性病变重度1，大片肾小管萎缩、基膜增厚，未萎缩小管基膜亦增厚，灶性小管上皮刷状缘脱落、细胞扁平，偶见裸膜，间质纤维化+++，较多单个核细胞、浆细胞、偶见嗜酸性粒细胞浸润，并灶性聚集。偶见入球小动脉节段透明变性，部分小动脉内弹性膜分层，偶见小叶间动脉节段内膜增厚。',
                             '皮髓质肾组织1条。4肾小球均已废弃。肾小管间质慢性病变重2度',
                             '二十七个体积略增大肾小球，毛细血管袢开放',
                             '皮质肾组织1条。12小球中见1个球性废弃，余肾小球外周袢足细胞附着减少，胞浆稀少，系膜区节段轻度增宽，毛细血管袢开放尚好，',
                             '皮髓质肾组织2条，镜下大部分为髓质组织，仅在皮髓交界处见1个形态欠完整的肾小球，系膜区未见明1处肾小球',
                             '髓质肾组织1条，0个肾小球。肾小管及间质病变均轻微，小管萎缩及间质纤维化均不明显，少量小管上皮细胞粗颗粒变性，间质个别单个核细胞散在浸润。血管未见明显病变。']},
                    index=[0, 1, 2, 3, 4, 5])

test['肾小球总数'] = test['dis'].str.extract('[，。？！,.?!]*([一二三四五六七八九十]+)\D*小球')
test['未见肾小球'] = test['dis'].str.extract('(未见[\u4E00-\u9FA5]+肾小球)')

sz_data['对比结果'] = sz_data[['肾小球总数', '球性硬化小球数']].apply(lambda x: x['肾小球总数'] == x['球性硬化小球数'], axis=1)







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
