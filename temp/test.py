import re

def extract_analysis_data(text):
    """
    从文本中分别提取 <MEMORY>, <delete>, <MISSING> 标签内的内容。
    - MEMORY / MISSING: 按行分割，并去除前置的各类索引 (如 1., (1), (a) 等)
    - delete: 提取由逗号分隔的整数列表
    """
    
    # ====================
    # 辅助函数：处理文本列表
    # ====================
    def clean_list_items(raw_text):
        if not raw_text:
            return []
        
        # 按换行符分割
        lines = raw_text.strip().split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 使用正则去除前置索引
            # 匹配逻辑:
            # ^\s* : 开头可能有的空格
            # \d+\.     : 数字加点，例如 "1."
            # \(\d+\)   : 括号加数字，例如 "(1)"
            # \([a-zA-Z]\): 括号加字母，例如 "(a)"
            # [a-zA-Z]\.: 字母加点，例如 "a."
            # \s* : 索引后面可能有的空格
            cleaned_line = re.sub(r'^\s*(?:\d+\.|\(\d+\)|\([a-zA-Z]\)|[a-zA-Z]\.)\s*', '', line)
            cleaned_lines.append(cleaned_line)
            
        return cleaned_lines

    # ====================
    # 1. 提取并清洗 <MEMORY>
    # ====================
    memory_match = re.search(r'<MEMORY>(.*?)</MEMORY>', text, flags=re.DOTALL | re.IGNORECASE)
    memory_list = clean_list_items(memory_match.group(1)) if memory_match else []

    # ====================
    # 2. 提取并清洗 <MISSING>
    # ====================
    missing_match = re.search(r'<MISSING>(.*?)</MISSING>', text, flags=re.DOTALL | re.IGNORECASE)
    missing_list = clean_list_items(missing_match.group(1)) if missing_match else []

    # ====================
    # 3. 提取并清洗 <delete>
    # ====================
    delete_match = re.search(r'<delete>(.*?)</delete>', text, flags=re.DOTALL | re.IGNORECASE)
    delete_list = []
    if delete_match:
        raw_delete = delete_match.group(1).strip()
        if raw_delete:
            # 按逗号分割，去除空格，并转换为整数
            delete_list = [int(num.strip()) for num in raw_delete.split(',') if num.strip()]

    return memory_list, delete_list, missing_list

# ====================
# 测试用例
# ====================
sample_text = """
[Comprehensive Analysis]
The prediction of 'Neutral' was accurate...

<MEMORY>
1. AI Infrastructure Validation: Direct partnerships between hyperscalers...
(2) The "Data Vacuum" Effect: Prolonged U.S. government shutdowns...
a. Earnings Season "Sell the News": High-momentum tech stocks...
3 Regulatory Overhang: Antitrust scrutiny...
4. Regulatory Overhang: Antitrust scrutiny...
</MEMORY>

<delete>
1,  2 ,3,    42
</delete>

<MISSING>
1. Real-time Retail Sentiment Indices: Data tracking retail investor...
2. Institutional "Positioning" Metrics: Precise data on fund...
3. Detailed Antitrust Implementation Timelines: While the events...
4. Ad-Spend Elasticity Data: While Omnicom mentions resilience...
</MISSING>
"""

memory, delete, missing = extract_analysis_data(sample_text)

print("=== MEMORY LIST ===")
print(memory)
# for item in memory:
    # print(f"- {item}")

print("\n=== DELETE LIST ===")
print(delete)

print("\n=== MISSING LIST ===")
print(missing)

# for item in missing:
    # print(f"- {item}")


'''

    python -m seer.temp.test

'''