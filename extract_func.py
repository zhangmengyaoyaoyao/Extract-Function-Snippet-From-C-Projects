import clang.cindex

def extract_function(file_path, target_line):
    """
    使用libclang解析C/C++代码，提取包含目标行的函数
    :param file_path: C/C++ 源代码文件路径
    :param target_line: 目标行号 (从1开始)
    :return: 函数名和函数体
    """
    # 初始化Clang索引
    index = clang.cindex.Index.create()

    # 解析文件，生成AST
    translation_unit = index.parse(file_path, args=['-x', 'c++'])
    
    # 遍历AST节点
    def find_function(node):
        # 如果节点是函数定义，检查其位置是否包含目标行
        if node.kind == clang.cindex.CursorKind.FUNCTION_DECL:
            if node.location.line <= target_line <= node.location.line + len(node.spelling):
                # 提取函数名和代码体
                return node.spelling, node.extent.start.line, node.extent.end.line
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
        # 获取函数体代码
        with open(file_path, 'r') as file:
            lines = file.readlines()
            return function_name, ''.join(lines[start_line - 1:end_line])
    
    return None, None

# 使用示例
file_path = 'example.cpp'
target_line = 20
function_name, function_body = extract_function(file_path, target_line)

if function_name:
    print(f"函数名: {function_name}")
    print(f"函数代码:\n{function_body}")
else:
    print(f"未找到包含第 {target_line} 行的函数")
