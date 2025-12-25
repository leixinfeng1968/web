import pandas as pd

# 读取Markdown文件
with open('课件统计表格.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到表格开始的位置
start_index = None
for i, line in enumerate(lines):
    if '| 序号 | 年级 | 册数 | 章节 | 课件名称 | 作者 |' in line:
        start_index = i
        break

if start_index is None:
    print("未找到表格")
    exit()

# 提取表格数据
header = lines[start_index].strip().split('|')[1:-1]  # 去除首尾空字符串
header = [h.strip() for h in header]

data = []
for line in lines[start_index + 2:]:  # 跳过表头和分隔线
    if line.strip() and '|' in line:
        cells = line.strip().split('|')[1:-1]  # 去除首尾空字符串
        cells = [c.strip() for c in cells]
        data.append(cells)

# 创建DataFrame
df = pd.DataFrame(data, columns=header)

# 保存为Excel文件
with pd.ExcelWriter('课件统计表格.xlsx', engine='openpyxl') as writer:
    df.to_excel(writer, index=False)
    
    # 获取工作表
    worksheet = writer.sheets['Sheet1']
    
    # 设置列宽：22个汉字，每个汉字大约需要2个宽度单位
    worksheet.column_dimensions['E'].width = 22 * 2

print('转换完成！Excel文件已保存为：课件统计表格.xlsx')
