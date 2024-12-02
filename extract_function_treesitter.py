from tree_sitter import Language, Parser
import os
import pandas as pd

def get_function_name(node, code):
    # 打印节点类型，调试用
    # print("node-", node.type)
    
    # 如果当前节点是 identifier 类型，直接返回其文本
    if node.type == "identifier":
        return code[node.start_byte:node.end_byte]
    
    # 直接查找 declarator 节点中的 identifier
    identifier_node = node.child_by_field_name("declarator")
    # print("enter children")
    if identifier_node and identifier_node.type == "identifier":
        return code[identifier_node.start_byte:identifier_node.end_byte]
    for child in node.children:
        # print("childnode of", node.type,"---" ,child.type, child.text)
        function_name = get_function_name(child, code)
        if function_name:
            return function_name
    # print("leave children")
    
    # 如果没有找到名称，返回 None
    return None


def extract_code_from_file(file_path, start_row, end_row):
    # 打开文件并读取所有行
    with open(file_path, "r") as file:
        lines = file.readlines()

    # 注意：start_row 和 end_row 是从 0 开始的，所以我们需要加 1 来适配
    extracted_code = lines[start_row:end_row + 1]  # 提取起始和结束行之间的代码

    # 返回提取的代码
    return ''.join(extracted_code)


# 定义一个递归函数来遍历所有节点
def traverse_node_get_function(node, code, target_line):
    print("into tra node:", node.type, node.text)
    if node.type == "function_definition":
        start_row, start_col = node.start_point  # 起始行号和列号
        end_row, end_col = node.end_point        # 结束行号和列号
        # 如果目标行在当前函数的范围内
        if target_line >= start_row and target_line <= end_row:
            print(f"Function definition starts at line {start_row + 1}, ends at line {end_row + 1}")
            # 获取函数名，假设函数名是第一个子节点，通常是 'identifier' 类型
            function_name = get_function_name(node, code)
            print(f"Function name: {function_name}", "end_name")
            print("return: ",start_row, end_row, function_name)
            return start_row, end_row, function_name

    # 遍历子节点
    for child in node.children:
        function_name = None
        start_row = None
        start_row, end_row, function_name = traverse_node_get_function(child, code, target_line)
        if start_row:  # 如果找到匹配的函数定义，则返回
            return start_row, end_row, function_name

    return None, None, None  # 如果没有找到匹配的函数，返回 None



def extract_function(project_name, bug_file, target_line):
    file_path = os.path.join("projects", project_name, bug_file)

    # 加载 C 或 C++ 语法
    C_LANG = Language('build/my-languages.so', 'c')

    # 初始化解析器
    parser = Parser()
    parser.set_language(C_LANG)  # 使用 C++ 语法，如果是 C 代码，使用 C_LANG

    # 读取文件内容
    with open(file_path, "r") as file:
        code = file.read()

    # 解析代码，生成语法树
    tree = parser.parse(bytes(code, "utf8"))

    # 获取语法树的根节点并开始遍历
    function_name = None
    start_row, end_row, function_name = traverse_node_get_function(tree.root_node, code, target_line)
    if function_name:
        extracted_code = extract_code_from_file(file_path, start_row, end_row)
        return function_name, extracted_code

    print("extract_function fail")
    return None, None


def process_dataset_and_extract_functions(dataset_path, project_column, bug_file_column, target_line_column, output_file):
    """
    遍历数据集文件中的每一行，提取函数名和函数体，并保存到新的 Excel 文件中。
    :param dataset_path: 数据集文件路径（.xlsx）
    :param project_column: 存储项目名的列名
    :param bug_file_column: 存储 bug 文件的列名
    :param target_line_column: 存储目标行号的列名
    :param output_file: 保存结果的输出文件路径（.xlsx）
    """
    # 读取 Excel 文件
    try:
        df = pd.read_excel(dataset_path)
    except Exception as e:
        print(f"错误: 无法读取文件 {dataset_path}. 错误详情: {e}")
        return
    
    # 创建一个列表来保存结果
    result_data = []

    # 遍历数据集中的每一行
    for index, row in df.iterrows():
        project_name = row[project_column]
        bug_file = row[bug_file_column]
        target_line = row[target_line_column]
        
        # 调用 extract_function_from_project 提取函数名和函数体
        function_name, function_body = extract_function(project_name, bug_file, target_line)
        
        # 如果成功提取到函数，添加到结果数据
        if function_name and function_body:
            result_data.append([project_name, bug_file, target_line, function_name, function_body])
        else:
            result_data.append([project_name, bug_file, target_line, None, None])
            print(f"未能提取 {project_name} 的函数: {bug_file} 第 {target_line} 行")
    
    # 将结果数据保存到新的 Excel 文件
    try:
        result_df = pd.DataFrame(result_data, columns=["Project", "BugFile", "TargetLine", "FunctionName", "FunctionBody"])
        result_df.to_excel(output_file, index=False)
        print(f"提取完成，结果已保存到 {output_file}")
    except Exception as e:
        print(f"错误: 无法保存结果到 {output_file}. 错误详情: {e}")