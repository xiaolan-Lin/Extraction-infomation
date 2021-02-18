import pandas as pd
import numpy as np

file = "/home/lxl/pythonProject/Extraction-infomation/data/肾穿病理文本文件.txt"

pathology_data = pd.DataFrame(columns=[
    '病理号', '姓名', '性别', '年龄', '住院号', '送检日期', '医院', '科室', '病区', '临床诊断', '送检者',
    '肾小球总数', '球性硬化小球数', '新月体小球数目', '节段性硬化数目', '内皮细胞增生', '毛细血管管腔', '系膜区',
    '系膜细胞', '系膜基质', '免疫复合物', '肾小管萎缩', '间质纤维化', '间质炎症细胞浸润', '间质血管病变', '诊断',
    '硬化小球比例', '节段硬化小球比例', '新月体小球比例'
])

with open(file, encoding='utf8') as f:
    for i, line in enumerate(f.readlines()):
        if line != '\n':
            content = line.split(':')[0].replace(' ', '')
            if content == '病理号':
                pathology_data = pathology_data.append({'病理号': line.split(':')[1].split(' ')[0]}, ignore_index=True)
            if content == '姓名':
                pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '姓名'] = \
                    line.split(':')[1].split(' ')[0]
                pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '性别'] = \
                    line.split(':')[2].split(' ')[0]
                pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '年龄'] = \
                    line.split(':')[3].split(' ')[0]
                pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '住院号'] = \
                    line.split(':')[4].split(' ')[0]
                pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '送检日期'] = \
                    line.split(':')[5].split(' ')[0]
            if content == '医院':
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
            if content == '肾小球':
                pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '肾小球总数'] = \
                    line.split('数量 ')[1].split(' ')[0]
                pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '球性硬化小球数'] = \
                    line.split('球性硬化 ')[1].split(' ')[0]
                pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '节段性硬化数目'] = \
                    line.split('节段性硬化 ')[1].split(' ')[0]
            if content == '肾小球囊':
                pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '新月体小球数目'] = \
                    line.split('肾小球囊: ')[1]  # 新月体小球数目，此处将描述全部取出
            if content == '内皮细胞':
                pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '内皮细胞增生'] = \
                    line.split('内皮细胞:')[1]  # 内皮细胞增生，此处将描述全部取出
            if content == '管腔':
                if pathology_data.iloc[len(pathology_data) - 1]['毛细血管管腔'] is np.nan:
                    pathology_data.loc[pathology_data.index == (len(pathology_data) - 1), '毛细血管管腔'] = \
                    line.split('管腔:')[1]  # 毛细血管管腔，此处将描述全部取出


管腔:    未见明显改变
管腔:      未见明显改变













x = 0
if (x != 1) | (x != 2):
    print(x)

