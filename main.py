import extract_function_treesitter as extractor


if __name__ == '__main__':
    # project_name = "trueprint"
    # bug_file = "todelete.c"
    # target_line = 22
    # function_name, line, code = extractor.extract_function(project_name, bug_file, target_line)
    # print("name",function_name)
    # print(code)

    dataset_path = 'result/report_valid.xlsx'  # 输入数据集文件路径
    output_file = 'result/c.xlsx'  # 输出结果的文件路径
    extractor.process_dataset_with_extracted_functions(dataset_path, output_file)
