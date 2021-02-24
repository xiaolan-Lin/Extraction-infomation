import pandas as pd
import numpy as np
from string import digits

pd.set_option('display.max_columns', 23)  # 设置显示的最大列数参数为a
pd.set_option('display.width', 1500)  # 设置显示的宽度为500，防止输出内容被换行
pd.set_option('max_colwidth', 100)  # 设置显示列值的宽度为100
pd.set_option('display.max_rows', None)  # 设置显示的行宽为全部，将所有行显示出来

"""
1.读取扫描文件，将其以xlsx文件保存
"""
file = "/home/lxl/pythonProject/Extraction-infomation/data/肾穿病理文本文件.txt"

# pathology_data = pd.DataFrame(columns=[
#     '病理号', '姓名', '性别', '年龄', '住院号', '送检日期', '医院', '科室', '病区', '临床诊断', '送检者',
#     '肾小球总数', '球性硬化小球数', '新月体小球数目', '节段性硬化数目', '内皮细胞增生', '毛细血管管腔', '系膜区',
#     '系膜细胞', '系膜基质', '免疫复合物', '肾小管萎缩', '间质纤维化', '间质炎症细胞浸润', '间质血管病变', '诊断',
#     '硬化小球比例', '节段硬化小球比例', '新月体小球比例'
# ])

pathology_data = pd.DataFrame(columns=[
    '病理号', '姓名', '性别', '年龄', '住院号', '送检日期', '医院', '科室', '病区', '临床诊断', '送检者',
    '肾小球总数', '球性硬化小球数', '肾小球囊', '节段性硬化数目', '内皮细胞', '管腔', '系膜区',
    '嗜复红蛋白', '肾小管', '间质', '血管', '诊断'
])

with open(file, encoding='utf8') as f:
    for i, line in enumerate(f.readlines()):
        if line != '\n':
            content = line.split(':')[0].replace(' ', '')
            if content == '病理号':
                pathology_data = pathology_data.append({'病理号': line.split(':')[1].split(' ')[0]}, ignore_index=True)
                print(line.split(':')[1].split(' ')[0])
            if content == '姓名':
                pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '姓名'] = \
                    line.split(':')[1].split(' ')[0].replace('\n', '')
                pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '性别'] = \
                    line.split(':')[2].split(' ')[0].replace('\n', '')
                pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '年龄'] = \
                    line.split(':')[3].split(' ')[0].replace('\n', '')
                pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '住院号'] = \
                    line.split(':')[4].split(' ')[0].replace('\n', '')
                pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '送检日期'] = \
                    line.split(':')[5].split(' ')[0].replace('\n', '')
            if content == '医院':
                if len(line.split(':')) == 6:
                    pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '医院'] = \
                        line.split(':')[1].split(' ')[0]
                    pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '科室'] = \
                        line.split(':')[2].split(' ')[0]
                    pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '病区'] = \
                        line.split(':')[3].split(' ')[0]
                    pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '临床诊断'] = \
                        line.split(':')[4].split(' ')[0]
                    pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '送检者'] = \
                        line.split(':')[5].split(' ')[0]
                if len(line.split(':')) == 5:
                    pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '医院'] = \
                        line.split(':')[1].split(' ')[0]
                    pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '科室'] = \
                        line.split(':')[2].split(' ')[0]
                    pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '病区'] = \
                        line.split(':')[3].split(' ')[0].replace('\n', '')
                    pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '临床诊断'] = \
                        line.split(':')[4].split(' ')[0].replace('\n', '')
            if content == '肾小球':
                if pathology_data.iloc[len(pathology_data) - 1]['肾小球总数'] is np.nan:
                    if '节段性硬化' in line:
                        pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '肾小球总数'] = \
                            line.split('数量 ')[1].split(' ')[0].replace('\n', '')
                        pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '球性硬化小球数'] = \
                            line.split('球性硬化 ')[1].split(' ')[0].replace('\n', '')
                        pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '节段性硬化数目'] = \
                            line.split('节段性硬化 ')[1].split(' ')[0].replace('\n', '')
                    else:
                        pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '肾小球总数'] = \
                            line.split('数量 ')[1].split(' ')[0].replace('\n', '')
                        pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '球性硬化小球数'] = \
                            line.split('球性硬化 ')[1].split(' ')[0].replace('\n', '')
            if content == '肾小球囊':
                if pathology_data.iloc[len(pathology_data) - 1]['肾小球囊'] is np.nan:
                    if '肾小球囊: ' in line:
                        pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '肾小球囊'] = \
                            line.split('肾小球囊: ')[1].replace('\n', '')  # 新月体小球数目，此处将描述全部取出
            if content == '内皮细胞':
                if pathology_data.iloc[len(pathology_data) - 1]['内皮细胞'] is np.nan:
                    pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '内皮细胞'] = \
                        line.split('内皮细胞:')[1].replace('\n', '')  # 内皮细胞增生，此处将描述全部取出
            if content == '管腔':
                if pathology_data.iloc[len(pathology_data) - 1]['管腔'] is np.nan:
                    pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '管腔'] = \
                        line.split('管腔:')[1].replace('\n', '')  # 毛细血管管腔，此处将描述全部取出
            if content == '系膜区':
                if pathology_data.iloc[len(pathology_data) - 1]['系膜区'] is np.nan:
                    pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '系膜区'] = \
                        line.split('系膜区:')[1].replace('\n', '')  # 系膜区、系膜细胞、系膜基质，此处将描述全部取出
            if content == '嗜复红蛋白':
                if pathology_data.iloc[len(pathology_data) - 1]['嗜复红蛋白'] is np.nan:
                    pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '嗜复红蛋白'] = \
                        line.split('嗜复红蛋白:')[1].replace('\n', '')  # 免疫复合物，此处将描述全部取出
            if content == '肾小管':
                if pathology_data.iloc[len(pathology_data) - 1]['肾小管'] is np.nan:
                    pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '肾小管'] = \
                        line.split('肾小管:')[1].replace('\n', '')  # 肾小管萎缩，此处将描述全部取出
            if content == '间质':
                if pathology_data.iloc[len(pathology_data) - 1]['间质'] is np.nan:
                    pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '间质'] = \
                        line.split('间质:')[1].replace('\n', '')  # 间质纤维化、间质炎症细胞浸润，此处将描述全部取出
            if content == '血管':
                if pathology_data.iloc[len(pathology_data) - 1]['血管'] is np.nan:
                    pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '血管'] = \
                        line.split('血管:')[1].replace('\n', '')  # 间质血管病变，此处将描述全部取出
            if content == '诊断':
                if pathology_data.iloc[len(pathology_data) - 1]['诊断'] is np.nan:
                    pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '诊断'] = \
                        line.split('诊断:')[1].split('诊断系数:')[0].replace(' ', '').replace('\n', '')  # 诊断，此处将描述全部取出

pathology_data.head()
# 将从txt文件提取到的信息保存为xlsx文件
pathology_data.to_excel("/home/lxl/pythonProject/Extraction-infomation/after_data/肾穿病理文本文件.xlsx",
                        encoding='utf8', index=False)

"""
2.数据提取
"""
# 1.读取xlsx文件
pathology_data = pd.read_excel("/home/lxl/pythonProject/Extraction-infomation/after_data/肾穿病理文本文件.xlsx",
                        encoding='utf8')
# 2.匹配“肾小球囊”，提取出“新月体小球数目”
# （1）将“肾小球囊”列转换为str类型
pathology_data['肾小球囊'] = pathology_data['肾小球囊'].astype(str)
# （2）查看“肾小球囊”列出现的可能情况
print(pathology_data['肾小球囊'].value_counts())  # 144种，1种为Nan
# （3）去除空格
pathology_data['肾小球囊'] = pathology_data['肾小球囊'].apply(lambda x: x.replace(' ', ''))
# （4）将“肾小球囊”列出现的“未见明显改变 1”修改为“未见明显改变”
pathology_data.loc[585, '肾小球囊'] = '未见明显改变'
# （5）提取出“肾小球囊”列的存在两个数字的列值
pathology_data[['肾小球囊1', '肾小球囊2']] = pathology_data['肾小球囊'].str.extract('(\d+)\D*(\d+)')
# （6）将“肾小球囊1”、“肾小球囊2”两列的Nan值填充为0
pathology_data[['肾小球囊1', '肾小球囊2']] = pathology_data[['肾小球囊1', '肾小球囊2']].fillna(0)
# （7）将“肾小球囊1”、“肾小球囊2”两列的数值转换为int型
pathology_data[['肾小球囊1', '肾小球囊2']] = pathology_data[['肾小球囊1', '肾小球囊2']].astype(int)
# （8）将“肾小球囊1”、“肾小球囊2”两列的数值相加
pathology_data['肾小球囊12'] = pathology_data['肾小球囊1'] + pathology_data['肾小球囊2']
# （9）删除临时列“肾小球囊1”、“肾小球囊2”
pathology_data = pathology_data.drop(pathology_data[['肾小球囊1', '肾小球囊2']], axis=1)
# （10）提取出“肾小球囊”列的存在一个数字的列值
pathology_data['新月体小球数目'] = pathology_data['肾小球囊'].str.extract('(\d+)')
# （11）将“新月体小球数目”列的Nan值填充为0
pathology_data['新月体小球数目'] = pathology_data['新月体小球数目'].fillna(0)
# （12）将“新月体小球数目”列的数值转换为int型
pathology_data['新月体小球数目'] = pathology_data['新月体小球数目'].astype(int)
# （13）将“新月体小球数目”与“肾小球囊12”列值进行对比，若“新月体小球数目”列中的值大于“肾小球囊12”对应的值，则替换“新月体小球数目”列中的值，反之不替换。
pathology_data['新月体小球数目'] = pathology_data.apply(lambda x: max(x['新月体小球数目'], x['肾小球囊12']), axis=1)
# （14）删除临时列“肾小球囊12”
del pathology_data['肾小球囊12']

# 3.匹配“内皮细胞”，提取出“内皮细胞增生”
# （1）将“内皮细胞”列转换为str类型
pathology_data['内皮细胞'] = pathology_data['内皮细胞'].astype(str)
# （2）查看“内皮细胞”列出现的可能情况
print(pathology_data['内皮细胞'].value_counts())  # 17种，1种为Nan
# （3）去除空格
pathology_data['内皮细胞'] = pathology_data['内皮细胞'].apply(lambda x: x.replace(' ', ''))
# （4）去除内皮细胞中出现的数字，以免对后续提取造成干扰
pathology_data['内皮细胞'] = pathology_data['内皮细胞'].apply(lambda x: x.translate(str.maketrans('', '', digits)))
# （5）在“内皮细胞”列中找到“轻”、“中”、“重”，对应替换成需要提取的数字
pathology_data['内皮细胞'] = pathology_data['内皮细胞'].apply(lambda x: x.replace('增生', '1增生'))
pathology_data['内皮细胞'] = pathology_data['内皮细胞'].apply(lambda x: x.replace('轻', '0轻'))
pathology_data['内皮细胞'] = pathology_data['内皮细胞'].apply(lambda x: x.replace('中', '1中'))
pathology_data['内皮细胞'] = pathology_data['内皮细胞'].apply(lambda x: x.replace('重', '2重'))
# （6）提取出“内皮细胞”列的存在两个数字的列值
pathology_data[['内皮细胞1', '内皮细胞2']] = pathology_data['内皮细胞'].str.extract('(\d+)\D*(\d+)')
# （7）将“内皮细胞1”、“内皮细胞2”两列的Nan值填充为0
pathology_data[['内皮细胞1', '内皮细胞2']] = pathology_data[['内皮细胞1', '内皮细胞2']].fillna(0)
# （8）将“内皮细胞1”、“内皮细胞2”两列的数值转换为int型
pathology_data[['内皮细胞1', '内皮细胞2']] = pathology_data[['内皮细胞1', '内皮细胞2']].astype(int)
# （9）将“内皮细胞1”、“肾小球囊2”两列的数值相加
pathology_data['内皮细胞12'] = pathology_data['内皮细胞1'] + pathology_data['内皮细胞2']
# （10）删除临时列“内皮细胞1”、“内皮细胞2”
pathology_data = pathology_data.drop(pathology_data[['内皮细胞1', '内皮细胞2']], axis=1)
# （11）提取出“内皮细胞”列的存在一个数字的列值
pathology_data['内皮细胞增生'] = pathology_data['内皮细胞'].str.extract('(\d+)')
# （12）将“内皮细胞增生”列的Nan值填充为0
pathology_data['内皮细胞增生'] = pathology_data['内皮细胞增生'].fillna(0)
# （13）将“内皮细胞增生”列的数值转换为int型
pathology_data['内皮细胞增生'] = pathology_data['内皮细胞增生'].astype(int)
# （14）将“内皮细胞增生”与“内皮细胞12”列值进行对比，若“内皮细胞增生”列中的值大于“内皮细胞12”对应的值，则替换“内皮细胞增生”列中的值，反之不替换。
pathology_data['内皮细胞增生'] = pathology_data.apply(lambda x: max(x['内皮细胞增生'], x['内皮细胞12']), axis=1)
# （15）删除临时列“内皮细胞12”
del pathology_data['内皮细胞12']

# 4.匹配“管腔”，提取出“毛细血管管腔”
# （1）将“内皮细胞”列转换为str类型
pathology_data['管腔'] = pathology_data['管腔'].astype(str)
# （2）查看“内皮细胞”列出现的可能情况
print(pathology_data['管腔'].value_counts())  # 48种，1种为Nan
# （3）去除空格
pathology_data['管腔'] = pathology_data['管腔'].apply(lambda x: x.replace(' ', ''))

# 5.匹配“系膜区”，提取出“系膜区”
# （1）将“系膜区”列转换为str类型
pathology_data['系膜区'] = pathology_data['系膜区'].astype(str)
# （2）查看“内皮细胞”列出现的可能情况
print(pathology_data['系膜区'].value_counts())  # 137种，1种为Nan
# （3）去除空格
pathology_data['系膜区'] = pathology_data['系膜区'].apply(lambda x: x.replace(' ', ''))

# 6.匹配“嗜复红蛋白”，提取出“免疫复合物”
# （1）将“嗜复红蛋白”列转换为str类型
pathology_data['嗜复红蛋白'] = pathology_data['嗜复红蛋白'].astype(str)
# （2）查看“内皮细胞”列出现的可能情况
print(pathology_data['嗜复红蛋白'].value_counts())  # 28种，1种为Nan
# （3）去除空格
pathology_data['嗜复红蛋白'] = pathology_data['嗜复红蛋白'].apply(lambda x: x.replace(' ', ''))

# 7.匹配“肾小管”，提取出“肾小管萎缩”
# （1）将“肾小管”列转换为str类型
pathology_data['肾小管'] = pathology_data['肾小管'].astype(str)
# （2）查看“内皮细胞”列出现的可能情况
print(pathology_data['肾小管'].value_counts())  # 87种，1种为Nan
# （3）去除空格
pathology_data['肾小管'] = pathology_data['肾小管'].apply(lambda x: x.replace(' ', ''))

# 8.匹配“间质”，提取出“间质纤维化”
# （1）将“间质”列转换为str类型
pathology_data['间质'] = pathology_data['间质'].astype(str)
# （2）查看“内皮细胞”列出现的可能情况
print(pathology_data['间质'].value_counts())  # 76种，1种为Nan
# （3）去除空格
pathology_data['间质'] = pathology_data['间质'].apply(lambda x: x.replace(' ', ''))

# 9.匹配“血管”，提取出“间质血管病变”
# （1）将“血管”列转换为str类型
pathology_data['血管'] = pathology_data['血管'].astype(str)
# （2）查看“内皮细胞”列出现的可能情况
print(pathology_data['血管'].value_counts())  # 45种，1种为Nan
# （3）去除空格
pathology_data['血管'] = pathology_data['血管'].apply(lambda x: x.replace(' ', ''))




pathology_data[(pathology_data['肾小球囊'].str.contains('未见明显改变') & pathology_data['肾小球囊'].str.contains('1'))]

