# 目标
根据代码文件路径和行号，提取其所在函数的代码和函数名

# 预备备
pip install tree-sitter

cd vendor/

git clone https://github.com/tree-sitter/tree-sitter-c.git

git clone https://github.com/tree-sitter/tree-sitter-cpp.git

# 说明
在main.py中编写内容并运行
```
python3 -m main
```
通过extractor.extract_function提取指定代码行**所在函数的函数名、所在代码行完整代码、所在函数完整代码**
```python
project_name = "trueprint"  # 项目在/projects文件夹下
bug_file = "todelete.c"
target_line = 22
function_name, extracted_line, code = extractor.extract_function(project_name, bug_file, target_line)
```
通过extractor.process_dataset_with_extracted_functions一次性提取数据集中的所有指定代码行
```python
process_dataset_with_extracted_functions(dataset_path, output_file, project_column='Project', bug_file_column='Bug File', target_line_column='Location')
"""
遍历数据集文件中的每一行，提取函数名和函数体，并保存到新的 Excel 文件中。
:param dataset_path: 数据集文件路径（.xlsx）
:param output_file: 保存结果的输出文件路径（.xlsx）
:param project_column: 存储项目名的列名
:param bug_file_column: 存储 bug 文件的列名
:param target_line_column: 存储目标行号的列名
"""
```
例如，
```python
dataset_path = 'result/c_init.xlsx' 
output_file = 'result/c.xlsx' 
extractor.process_dataset_with_extracted_functions(dataset_path, output_file)
```

# 注意
在 c_init.xlsx 中（共2216条警告），有以下几种情况不能正确提取所在函数，保存在 c_手动提取.xlsx ：
1. 所在函数极长，语法树分析结果中函数在中途结束（不清楚为什么），注意到不能正确提取的函数都超过了1000行
2. 目标代码行不在函数中，而是在条件编译语句中
3. bug_file路径不存在（只有1例）,warning_line保存为“-”

以上1和2情况共同的特点是所在语法块很长，考虑到项目的目的是提取警告上下文（不一定是完整函数），因此做特殊处理（共39条警告，占总数1.8%）：

提取[target_line-14, target_line+6)作为上下文，函数名为空字符串。