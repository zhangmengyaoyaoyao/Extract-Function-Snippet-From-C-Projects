from tree_sitter import Language, Parser
import os
import pandas as pd

def get_function_name(node, code, root):
    # 打印节点类型，调试用
    # print("node-", node.type)
    if node.type == "function_declarator":
        for child in node.children:
            if child.type == "identifier":
                return code[child.start_byte:child.end_byte]
    

    for child in node.children:
        function_name = get_function_name(child, code, root)
        if function_name:
            return function_name
    
    if node is not root:
        # 如果没有找到名称，返回 None
        return None
    
    for child in node.children:
        if "identifier" in child.type:
            return code[child.start_byte:child.end_byte]

def extract_code_from_file(file_path, target_line, start_row, end_row):
    # 打开文件并读取所有行
    with open(file_path, "r") as file:
        lines = file.readlines()

    extracted_function = lines[start_row:end_row + 1]  # 提取起始和结束行之间的代码
    extracted_line = lines[target_line-1]

    # 返回提取的代码
    return extracted_line.strip(), ''.join(extracted_function)

# 定义一个递归函数来遍历所有节点
def get_functioninfo(node, code, target_line):
    if node.type == "function_definition":
        start_row, start_col = node.start_point  # 起始行号和列号
        end_row, end_col = node.end_point        # 结束行号和列号
        # print("find function_definition in", start_row, end_row)

        # 如果目标行在当前函数的范围内
        if target_line >= start_row and target_line <= end_row:
            # print(target_line, start_row, end_row)
            # 获取函数名，假设函数名是第一个子节点，通常是 'identifier' 类型
            function_name = get_function_name(node, code, node)
            # print("ret1", start_row, end_row, function_name)
            return start_row, end_row, function_name

    # 遍历子节点
    for child in node.children:
        function_name = None
        start_row = None
        start_row, end_row, function_name = get_functioninfo(child, code, target_line)
        if start_row is not None:  # 如果找到匹配的函数定义，则返回
            # print("ret2")
            return start_row, end_row, function_name

    return None, None, None  # 如果没有找到匹配的函数，返回 None

def get_functioninfo_outerparam(node, code, target_line, fathernode, grandfathernode, grandgrandfathernode):
    # function_definition中必然含有function_declarator，如果第一轮的get_function没有成功，就说明目标行不存在与function_definition中
    if node.type == "function_definition":
        return None, None, None

    if node.type == "function_declarator":
        start_row, start_col = fathernode.start_point
        end_row, end_col = fathernode.end_point
        # print("find function_declarator in", start_row, end_row)

        lastnode = None
        for senior in grandgrandfathernode.children:
            # print("-senior is:", senior.type, senior.text)
            if senior.start_point == fathernode.start_point:
                # print("--find start:", senior.start_point)
                if lastnode is not None:
                    start_row, start_col = lastnode.start_point

            if senior.type == "compound_statement" and senior.start_point >= fathernode.start_point:
                end_row, end_col = senior.end_point
                break
            lastnode = senior
    

        if target_line >= start_row and target_line <= end_row:
            function_name = get_function_name(node, code, node)
            # print(target_line, start_row, end_row, "so ret")
            return start_row, end_row, function_name

    for child in node.children:
        function_name = None
        start_row = None
        start_row, end_row, function_name = get_functioninfo_outerparam(child, code, target_line, node, fathernode, grandfathernode)
        if start_row is not None:  # 如果找到匹配的函数定义，则返回
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
    try:
        with open(file_path, "r") as file:
            code = file.read()
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到，跳过该文件。")
        print("extract_function fail", file_path)
        return None, '-', None
    except IOError as e:
        print(f"打开文件 {file_path} 时发生错误: {e}")
        print("extract_function fail", file_path)
        return None, '-', None
    
    # 解析代码，生成语法树
    tree = parser.parse(bytes(code, "utf8"))

    # 获取语法树的根节点并开始遍历
    start_row = None
    start_row, end_row, function_name = get_functioninfo(tree.root_node, code, target_line)
    # 利用function_definiton提取
    # print("1:",start_row, end_row, function_name)
    if start_row is not None:
        extracted_line, extracted_function = extract_code_from_file(file_path, target_line, start_row, end_row)
        return function_name, extracted_line, extracted_function
    
    # 利用function_declarator提取（有些函数有括号外参数）
    start_row, end_row, function_name = get_functioninfo_outerparam(tree.root_node, code, target_line, tree.root_node, tree.root_node, tree.root_node)
    # print("2:",start_row, end_row, function_name)
    if start_row is not None:
        extracted_line, extracted_function = extract_code_from_file(file_path, target_line, start_row, end_row)
        return function_name, extracted_line, extracted_function

    # 处理一些不在函数中（可能在条件编译结构中），或者函数代码行数过多的情况
    front = 14
    back = 6
    start_row = target_line - front
    end_row = target_line + back
    function_name = ""
    extracted_line, extracted_snippet = extract_code_from_file(file_path, target_line, start_row, end_row)
    print("extract_function fail")
    return function_name, extracted_line, extracted_snippet

def process_dataset_with_extracted_functions(dataset_path, output_file, project_column='Project', bug_file_column='Bug File', target_line_column='Location'):
    """
    遍历数据集文件中的每一行，提取函数名和函数体，并保存到新的 Excel 文件中。
    :param dataset_path: 数据集文件路径（.xlsx）
    :param output_file: 保存结果的输出文件路径（.xlsx）
    :param project_column: 存储项目名的列名
    :param bug_file_column: 存储 bug 文件的列名
    :param target_line_column: 存储目标行号的列名
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
        id, groundTruth, tool, bugType, message = row['Id'], row['GroundTruth'], row['Tool'], row['Bug Type'], row['Message']
        project_name = row[project_column]
        bug_file = row[bug_file_column]
        target_line = row[target_line_column]
        
        # 调用 extract_function_from_project 提取函数名和函数体
        function_name = None
        extracted_line = None
        extracted_function = None
        function_name, extracted_line, extracted_function = extract_function(project_name, bug_file, target_line)
        result_data.append([id, groundTruth, project_name, tool, bugType, bug_file, target_line, function_name, extracted_line, extracted_function, message])

        if function_name is None or extracted_function is None:
            print(f"未能提取 {project_name} 的函数: {bug_file} 第 {target_line} 行")
    
        del function_name, extracted_function # 清理中间结果（删除不再需要的变量以释放内存）
    # 将结果数据保存到新的 Excel 文件
    try:
        result_df = pd.DataFrame(result_data, columns=["id", "final_lable", "project", "tool", "category", "file", "targetLine", "warning_function_name", "warning_line", "warning_function", "message"])
        result_df.to_excel(output_file, index=False)
        print(f"提取完成，结果已保存到 {output_file}")
    except Exception as e:
        print(f"错误: 无法保存结果到 {output_file}. 错误详情: {e}")
