import extract_function_treesitter as extractor


if __name__ == '__main__':
    # project_name = "trueprint"
    # bug_file = "todelete.c"
    # target_line = 22
    # function_name, line, code = extractor.extract_function(project_name, bug_file, target_line)
    # print("name",function_name)
    # print(code)


    dataset_path = 'result/c_raw.xlsx'  # 输入数据集文件路径
    output_file = 'result/c.xlsx'  # 输出结果的文件路径
    code_function_column = 'Code_function'
    function_column = "Function"
    extractor.process_dataset_and_extract_functions(dataset_path, output_file)
