# Objective
Extract the function name, the code at the target line, and the full function code based on the file path and line number.

# Prerequisites
Install `tree-sitter`:

```
pip install tree-sitter
```

Clone the necessary repositories:

```bash
cd vendor/

git clone https://github.com/tree-sitter/tree-sitter-c.git

git clone https://github.com/tree-sitter/tree-sitter-cpp.git
```

# Instructions
To run the program, execute:

```
python3 -m main
```

You can modify the `main.py` to:

Use `extractor.extract_function` to extract the function name, the complete code at the target line, and the full function code for the specified line:

```python
project_name = "trueprint"  # The project is under the /projects folder
bug_file = "todelete.c"
target_line = 22
function_name, extracted_line, code = extractor.extract_function(project_name, bug_file, target_line)
```

Use `extractor.process_dataset_with_extracted_functions` to extract all specified lines from a dataset at once:

```python
process_dataset_with_extracted_functions(dataset_path, output_file, project_column='Project', bug_file_column='Bug File', target_line_column='Location')
```

This function processes each row in the dataset file, extracting the function name and function body, and saves the results in a new Excel file.

Parameters:
- `dataset_path`: The path to the dataset file (.xlsx)
- `output_file`: The path to save the results (.xlsx)
- `project_column`: The column name that contains the project name
- `bug_file_column`: The column name that contains the bug file name
- `target_line_column`: The column name that contains the target line number

For example:

```python
dataset_path = 'result/c_init.xlsx' 
output_file = 'result/c.xlsx' 
extractor.process_dataset_with_extracted_functions(dataset_path, output_file)
```

# Custom Processing
You can perform different processing based on your needs in `extract_function()`:

```c
    # Handle cases where the code is not in a function (possibly in a conditional compilation structure) or the function has too many lines.
    ## 1. Take 100 lines around the target line as context
    start_row, end_row = limit_function_range(target_line)
    function_name = ""
    extracted_line, extracted_snippet = extract_code_from_file(file_path, target_line, start_row, end_row)
    return function_name, extracted_line, extracted_snippet
```

```c
    ## 2. Store the target line as code context
    extracted_line, extracted_snippet = extract_code_from_file(file_path, target_line, target_line-1, target_line-1)
    return function_name, extracted_line, extracted_line
```

```c
    ## 3. Do not process further, print error message, and return empty values
    print("extract_function fail")
    return None, None, None
```

# Notes
In `c_init.xlsx` (with 2216 warnings), the following cases could not correctly extract the function the target line is in, and are saved in `c_manual_extract.xlsx`:

1. The function is extremely long, and the syntax tree analysis shows the function ends prematurely (it’s unclear why). It was observed that the functions that could not be extracted correctly were all over 1000 lines.
2. The target line is not in a function but inside a conditional compilation block.
3. The `bug_file` path does not exist (only 1 case), and the `warning_line` is saved as "-".

The common characteristic of cases 1 and 2 is that the syntax block is very large. Considering the purpose of the project is to extract the warning context (not necessarily the full function), special handling is performed for these cases (39 warnings in total, accounting for 1.8% of the total) as described in the "Custom Processing" section above.


# 目标
根据代码文件路径和行号，提取其所在函数的代码和函数名

# 预备备
pip install tree-sitter

cd vendor/

git clone https://github.com/tree-sitter/tree-sitter-c.git

git clone https://github.com/tree-sitter/tree-sitter-cpp.git

# 说明
运行命令
```
python3 -m main
```
可以在main.py中修改：

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

# 不同处理
可以根据不同需要，在extract_function()中进行不同处理
```c
    # 处理一些不在函数中（可能在条件编译结构中），或者函数代码行数过多的情况
    ## 1.取目标行附近100行代码作为上下文
    start_row, end_row = limit_function_range(target_line)
    function_name = ""
    extracted_line, extracted_snippet = extract_code_from_file(file_path, target_line, start_row, end_row)
    return function_name, extracted_line, extracted_snippet
```
```c
    ## 2.以代码行作为代码上下文存储
    extracted_line, extracted_snippet = extract_code_from_file(file_path, target_line, target_line-1, target_line-1)
    return function_name, extracted_line, extracted_line
```
```c
    ## 3.不额外处理 打印错误信息并保持空白
    print("extract_function fail")
    return None, None, None
```


# 注意
在 c_init.xlsx 中（共2216条警告），有以下几种情况不能正确提取所在函数，保存在 c_手动提取.xlsx ：
1. 所在函数极长，语法树分析结果中函数在中途结束（不清楚为什么），注意到不能正确提取的函数都超过了1000行
2. 目标代码行不在函数中，而是在条件编译语句中
3. bug_file路径不存在（只有1例）,warning_line保存为“-”

以上1和2情况共同的特点是所在语法块很长，考虑到项目的目的是提取警告上下文（不一定是完整函数），因此做特殊处理（共39条警告，占总数1.8%）(根据上方“不同处理”部分)