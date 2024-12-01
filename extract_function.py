import clang.cindex
import os
import pandas as pd

def extract_function(file_path, target_line):
    """
    使用libclang解析C/C++代码，提取包含目标行的函数
    :param file_path: C/C++ 源代码文件路径
    :param target_line: 目标行号 (从1开始)
    :return: 函数名和函数体
    """
    # 初始化Clang索引
    index = clang.cindex.Index.create()

    # 根据文件类型设置解析语言
    if file_path.endswith('.c'):
        pl = 'c'
    elif file_path.endswith('.cpp'):
        pl = 'c++'
    else:
        pl = 'unknown'
        print(file_path, "find pl fail")
    
    # 解析文件，生成AST
    translation_unit = index.parse(file_path, args=['-x', pl])

    # 遍历AST节点
    def find_function(node):
        # 如果节点是函数定义，检查其位置是否包含目标行
        if node.kind == clang.cindex.CursorKind.FUNCTION_DECL:
            # 获取文件路径
            node_path = node.location.file.name if node.location.file else None
            
            # 判断是否为库函数（假设库函数在系统路径下，路径包含 'include' 或 'sys'）
            if node_path and ('include' in node_path or 'sys' in node_path):
                # 如果是库函数，跳过或者进行其他处理
                print(f"Library function detected: {node.spelling} in {node_path}")
                return None
            
            print("decl: ",node.spelling, node.extent.start.line+1, node.extent.end.line+1)
            start_line = node.extent.start.line
            end_line = node.extent.end.line
            # 如果目标行在函数的范围内
            if start_line <= target_line <= end_line:
                # 提取函数名和代码体
                print("info: ",node.spelling, node.extent.start.line, node.extent.end.line+1)
                return node.spelling, node.extent.start.line, node.extent.end.line+1
        # 递归遍历子节点
        for child in node.get_children():
            result = find_function(child)
            if result:
                return result
        return None
    
    # 查找包含目标行的函数
    function_info = find_function(translation_unit.cursor)
    
    if function_info:
        function_name, start_line, end_line = function_info
        start_line -= 1
        end_line -= 1
        
        # 获取函数体代码
        with open(file_path, 'r') as file:
            lines = file.readlines()
            print("llllllllllllllllllllllllllllllllll")
            # index = 0
            # for l in lines:
            #     print(index,": " , lines[index])
            #     index += 1
            print("llllllllllllllllllllllllllllllllll")

            
            # 使用 start_line 和 end_line 提取代码段
            function_body = ''.join(lines[start_line : end_line])
            print("取行号",start_line, end_line)
            
            # 继续提取，确保函数体内容完整
            if lines[end_line-1].strip() != "}":
                while end_line < len(lines):
                    line = lines[end_line]
                    # print(end_line, " : ", line)
                    if line.strip() == "}":  # 如果是函数体的结束标志
                        function_body += line
                        break
                    function_body += line
                    end_line += 1
            
            return function_name, function_body
    
    return None, None



def extract_function_from_project(project_name, bug_file, target_line):
    file_path = os.path.join("projects", project_name, bug_file)
    # read_and_print_file(file_path)
    function_name, function_body = extract_function(file_path, target_line)

    if function_name:
        print(f"函数名: {function_name}")
        print(f"函数代码:\n{function_body}")
        return function_name, function_body
    else:
        print(f"未找到包含第 {target_line} 行的函数")
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
        function_name, function_body = extract_function_from_project(project_name, bug_file, target_line)
        
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


#test
def read_and_print_file(file_path):
    try:
        with open(file_path, 'r') as file:
            # 读取文件内容
            file_content = file.read()
            # 打印文件内容
            print(file_content)
    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 未找到.")
    except IOError as e:
        print(f"错误: 无法读取文件 '{file_path}'. 错误详情: {e}")