import extract_function_treesitter as extractor


if __name__ == '__main__':
    # project_name = "trueprint"
    # bug_file = "todelete.c"
    # target_line = 5
    # code, function_name = extractor.extract_function(project_name, bug_file, target_line)
    # print(code)
    # print(function_name)



    dataset_path = 'result/c_raw.xlsx'  # 输入数据集文件路径
    project_column = 'Project'  # 存储项目名的列名
    bug_file_column = 'Bug File'  # 存储 bug 文件的列名
    target_line_column = 'Location'  # 存储目标行号的列名
    output_file = 'result/c.xlsx'  # 输出结果的文件路径
    extractor.process_dataset_and_extract_functions(dataset_path, project_column, bug_file_column, target_line_column, output_file)