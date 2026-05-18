import os
import re
import json
import glob

def batch_convert_md_to_json(directory="seer/memory"):
    """
    遍历指定目录下的所有 Markdown 文件，提取 SECTOR 和 TARGET 内容，
    并将其转换为带有初始化配置的 JSON 格式文件。
    """
    # 检查目录是否存在
    if not os.path.exists(directory):
        print(f"[-] 目录不存在: {directory}")
        return

    # 获取目录下所有的 .md 文件
    md_files = glob.glob(os.path.join(directory, "*.md"))
    
    if not md_files:
        print(f"[-] 在 '{directory}' 目录下没有找到任何 markdown 文件。")
        return

    print(f"[*] 开始转换 '{directory}' 目录下的文件...\n")
    
    success_count = 0
    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as file:
                content = file.read()

            # 1. 使用正则表达式匹配 SECTOR 和 TARGET
            # (.*?)(?=════) 意味着匹配任意字符直到遇到下一个 "════" 分隔符
            sector_match = re.search(r"SECTOR:\s*(.*?)(?=════)", content, re.DOTALL)
            target_match = re.search(r"TARGET:\s*(.*?)(?=════)", content, re.DOTALL)

            # 提取内容并去除首尾多余的空白字符和换行符
            sector_text = sector_match.group(1).strip() if sector_match else ""
            target_text = target_match.group(1).strip() if target_match else ""

            # 2. 构建符合要求的 JSON 字典结构
            json_data = {
                "SECTOR": sector_text,
                "TARGET": target_text,
                "MEMORY": [],
                "MISSING": [],
                "MEMORY_CAP": 0,
                "MISSING_CAP": 0
            }

            # 3. 生成新的 JSON 文件路径 (替换原有的 .md 后缀)
            json_file_path = os.path.splitext(md_file)[0] + ".json"

            # 4. 写入 JSON 文件
            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                # ensure_ascii=False 保证中文字符正常显示，indent=4 保证 JSON 格式美观
                json.dump(json_data, json_file, ensure_ascii=False, indent=4)
            
            print(f"[+] 成功转换: {os.path.basename(md_file)} -> {os.path.basename(json_file_path)}")
            success_count += 1
            
        except Exception as e:
            print(f"[-] 转换 {md_file} 时发生错误: {e}")
                
    print("-" * 50)
    print(f"✅ 转换完成! 共处理了 {success_count} 个文件。")

# ====================
# 执行函数
# ====================
if __name__ == "__main__":
    batch_convert_md_to_json(directory="seer/memory")



'''
    python -m seer.temp.cov
'''