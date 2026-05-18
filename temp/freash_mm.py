import os
import json
import glob

def refresh_memory_files(directory="seer/memory"):
    """
    清理指定目录下的所有 .lock 文件，
    并将所有 .json 文件中的 MEMORY 和 MISSING 模块重置为空，容量清零。
    """
    if not os.path.exists(directory):
        print(f"[-] 错误: 目录 '{directory}' 不存在。")
        return

    # ==========================================
    # 1. 批量删除 .lock 文件
    # ==========================================
    lock_files = glob.glob(os.path.join(directory, "*.lock"))
    lock_count = 0
    for lock_file in lock_files:
        try:
            os.remove(lock_file)
            lock_count += 1
        except Exception as e:
            print(f"[-] 无法删除锁文件 {lock_file}: {e}")
            
    if lock_count > 0:
        print(f"[+] 成功清理了 {lock_count} 个 .lock 文件。")
    else:
        print("[*] 没有发现需要清理的 .lock 文件。")

    # ==========================================
    # 2. 批量重置 .json 文件的记忆与容量
    # ==========================================
    json_files = glob.glob(os.path.join(directory, "*.json"))
    json_count = 0
    
    if not json_files:
        print(f"[-] 在 '{directory}' 下未找到任何 JSON 文件。")
        return

    for json_path in json_files:
        try:
            # 读取原始数据
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 重置指定字段，保留 SECTOR 和 TARGET
            data['MEMORY'] = []
            data['MISSING'] = []
            data['MEMORY_CAP'] = 0
            data['MISSING_CAP'] = 0
            
            # 写回文件
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                
            json_count += 1
            print(f"  -> 重置成功: {os.path.basename(json_path)}")
            
        except json.JSONDecodeError:
            print(f"[-] 格式错误，跳过文件: {json_path}")
        except Exception as e:
            print(f"[-] 处理 {json_path} 时发生未知错误: {e}")

    print("-" * 50)
    print(f"✅ 任务完成！共重置了 {json_count} 个 JSON 记忆文件。")

if __name__ == "__main__":
    refresh_memory_files()

'''
    
    python -m seer.temp.freash_mm
'''