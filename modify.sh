#!/bin/bash

# 目标目录，默认是当前目录
target_dir="${1:-.}"

# 递归查找所有文件并去除 ^L 字符
find "$target_dir" -type f | while read -r file; do
    # 检查文件是否是普通文件
    if [ -f "$file" ]; then
        echo "处理文件: $file"
        # 使用 sed 删除 ^L 字符并保存到原文件
        sed -i 's/\x0C//g' "$file"
    fi
done

echo "所有文件处理完毕。"
