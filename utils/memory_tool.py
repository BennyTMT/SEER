import json , re  ,sys 
import logging
import time
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
import os 
from seer.utils import utils 
from seer.utils import retrieval_prompt 

MODEL_MAP = {
    'gemini': "gemini-3.1-pro-preview",
    'gemini-flash-3p0': 'gemini-3-flash-preview',
    'gemini-flash-3p1' : 'gemini-3.1-flash-lite-preview',
    'claude': "claude-sonnet-4-5",
    'claude-opus-4p5' : 'claude-opus-4-5', 
    'claude-opus-4p6' : 'claude-opus-4-6' , 
    'claude-sonnet-4p6': 'claude-sonnet-4-6',
    'qwen3p5' : "Qwen3.5-397B-A17B", 
    'mm2p5' : 'minimax-m2.5' , 
}

def extract_single_event_numbers(text):
    raw_blocks = re.findall(r'<events>(.*?)</events>', text, flags=re.DOTALL)
    if len(raw_blocks) != 1:
        return None
    block = raw_blocks[0]
    validation_pattern = re.compile(r'^\s*\d+(?:\s*,\s*\d+)*\s*$')
    if validation_pattern.match(block):
        extract_numbers = [int(num.strip()) for num in block.split(',')]
        return sorted(extract_numbers)
    else:
        return None
    
def convert_memeory_missing_to_str(event_list):
    return '\n§\n'.join(f"{i+1}. {event}" for i, event in enumerate(event_list))


##############################################################################################
# Memory Blocks 
##############################################################################################
import fcntl
    
import fcntl

def extract_memory_blocks(file_path: str):
    """
    JSON read function with fcntl process shared lock (read lock).
    """
    if not os.path.exists(file_path):
        print(f"[-] Error: File not found at {file_path}")
        return "MATCH_ERROR", "MATCH_ERROR", [], [], 0, 0

    lock_path = f"{file_path}.lock"
    lock_file = open(lock_path, 'a')
    
    try:
        # 1. Acquire shared lock (read lock) -> allows multiple processes to read simultaneously, but waits for write lock to be released
        fcntl.flock(lock_file, fcntl.LOCK_SH)
        
        # 2. Safely read data
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
    except json.JSONDecodeError as e:
        print(f"[-] Error: Failed to parse JSON file {file_path} - {e}")
        return "MATCH_ERROR", "MATCH_ERROR", [], [], 0, 0
    except Exception as e:
        print(f"[-] Unexpected error reading {file_path}: {e}")
        return "MATCH_ERROR", "MATCH_ERROR", [], [], 0, 0
    finally:
        # 3. After reading, release the read lock as early as possible so other processes wanting to write can proceed
        fcntl.flock(lock_file, fcntl.LOCK_UN)
        lock_file.close()

    # 4. Data is already in the 'data' variable in memory, the following operations do not need lock protection
    # Extract values using .get() with safe default fallbacks
    sector = data.get("SECTOR", "MATCH_ERROR")
    target = data.get("TARGET", "MATCH_ERROR")
    
    # Lists default to empty if not found
    memory = data.get("MEMORY", [])
    missing = data.get("MISSING", [])
    
    # Capacities default to 0 if not found
    memory_cap = data.get("MEMORY_CAP", 0)
    missing_cap = data.get("MISSING_CAP", 0)
    
    return sector, target, memory, missing, memory_cap, missing_cap


def save_memory_to_file(file_path: str, data: dict):
    """
    Safe JSON save function with fcntl process exclusive lock (write lock).
    """
    # Ensure target directory exists
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    
    # Define independent lock file path
    lock_path = f"{file_path}.lock"
    
    # Open lock file (use 'a' append mode to prevent accidental clearing of content, even though it is empty)
    lock_file = open(lock_path, 'a')
    
    try:
        # 1. Attempt to acquire exclusive lock (write lock) -> block until successful
        fcntl.flock(lock_file, fcntl.LOCK_EX)
        
        # 2. After acquiring the lock, safely overwrite the original file using 'w' mode
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
            # 3. Ultimate crash prevention: force flush memory buffer data into physical hard drive sectors
            f.flush()
            os.fsync(f.fileno())
        
    except Exception as e:
        print(f"[-] Error writing memory to {file_path}: {e}")
        raise e
    finally:
        # 4. Whether successful or error occurs, be sure to release the lock and close the lock file
        fcntl.flock(lock_file, fcntl.LOCK_UN)
        lock_file.close()
    


def get_soho_stock_domain_file(ticker: str) -> str:
    domain_mapping = {
        'tech.json': {'META', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NFLX', 'DIS', 'ADBE', 'CRM', 'ORCL'},
        'semi.json': {'NVDA', 'AMD', 'INTC', 'TSM', 'AVGO', 'QCOM'},
        'fin.json': {'JPM', 'BAC', 'V', 'MA'},
        'consumer.json': {'WMT', 'COST', 'KO', 'PEP', 'PG'},
        'health.json': {'JNJ', 'PFE', 'LLY', 'UNH'}
    }
    formatted_ticker = ticker.upper().strip()
    for filename, tickers in domain_mapping.items():
        if formatted_ticker in tickers:
            return filename
    raise FileExistsError 
    
def get_soho_stock_memorys(ticker , memory_dir = None):
    assert memory_dir
    file_name = get_soho_stock_domain_file(ticker)
    memory_path = f'seer/memory/{memory_dir}/{file_name}'
    memory_items = extract_memory_blocks(memory_path)
    if "MATCH_ERROR" in memory_items:
        raise ValueError(f'Error reading memory file for improving: {memory_path}\n')
    return memory_items

def get_memeory_by_ticker(ticker):
    try:
        file_name = get_soho_stock_domain_file(ticker)
        file_path = os.path.join('seer', 'memory', file_name)
    except NameError:
        raise FileExistsError 

    if not os.path.exists(file_path):
        print(f"[-] Error: Memory file for {ticker} not found at {file_path}")
        raise FileExistsError 

    # 2. Load the JSON data
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[-] Error: Failed to parse JSON file {file_path} - {e}")
        return False

    return data , file_path


# MEM_CEIL = 10000
MEM_CEIL = 12000
MISSING_CEIL = 8000

def condense_memory(ticker, sector , model_name, memory_list, is_debug=0 , mm='missing'):

    memory_str = convert_memeory_missing_to_str(memory_list)
    
    if mm =='memory':
        system_prompt = retrieval_prompt.CONDENSE_MEM_SYSTEM_PROMPT.format(sector = sector)
        user_msg = retrieval_prompt.CONDENSE_MEM_USER_PROMPT.format(memory_str = memory_str)
    elif mm =='missing':
        system_prompt = retrieval_prompt.CONDENSE_MISS_SYSTEM_PROMPT.format(sector = sector)
        user_msg = retrieval_prompt.CONDENSE_MISS_USER_PROMPT.format(memory_str = memory_str)
    else : 
        raise FileExistsError 
    
    MAX_RETRIES_REPEATE = 3 
    new_memory_list = []
    for attempt in range(1, MAX_RETRIES_REPEATE + 1):
        try:    
            llm_res = ''
            if 'claude' in model_name:
                llm_res, _, _ = utils.query_claude(system_prompt, user_msg,
                    model_name=MODEL_MAP[model_name], web_search=False, max_tokens=4096)
            elif 'gemini' in model_name:
                llm_res, _, _ = utils.query_gemini(system_prompt, user_msg,
                    model_name=MODEL_MAP[model_name], citations_need=False, web_search=False)
            
            match = re.search(r'<CONDENSED_MEMORY>(.*?)</CONDENSED_MEMORY>', llm_res, flags=re.DOTALL | re.IGNORECASE)
            if not match:
                print(f"[-] Error: LLM did not return <CONDENSED_MEMORY> tags for {ticker}.")
                continue 
            else:
                raw_text = match.group(1).strip()
                lines = raw_text.split('\n')
                new_memory_list = []
                for line in lines:
                    line = line.replace('§', '').strip()
                    if not line:    continue
                    cleaned_line = re.sub(r'^[-*0-9.]+\s*', '', line)
                    if cleaned_line:
                        new_memory_list.append(cleaned_line)
                if not new_memory_list:
                    print(f"[-] Error: Extracted condensed memory is empty for {ticker}. Funtion: condense_memory")
                    print(llm_res)
                    continue
                if is_debug:
                    print('+'*100) 
                    print("=== Condensing LLM Memory ===")
                    print(system_prompt)
                    print(user_msg)
                    print("=== Condensed ===")
                    print(llm_res)
                break 
                
        except Exception as e:
            if attempt < MAX_RETRIES_REPEATE:
                time.sleep(2 * attempt)
            else:
                error_final_msg = f"‼️ Improving FATAL: {model_name} failed after {MAX_RETRIES_REPEATE} attempts. Last Err: {e}"
                print(f"\033[91m {error_final_msg} \033[0m")
                return False 

    return new_memory_list

def delete_memory(ticker, delete_suggestion):
    """
    Reads the JSON memory file for the specified ticker, deletes the Memory 
    items corresponding to the 1-based indices in delete_suggestion, recalculates 
    the total character count (CAP), and saves the updated JSON back to the file.
    """

    data  , file_path = get_memeory_by_ticker(ticker)
    memory_list = data.get('MEMORY', [])
    ori_memory_len = len(memory_list)
    # 3. Sort the indices in descending order
    # This is critical! Deleting from the end of the list first ensures that 
    # the indices of the remaining items do not shift during the loop.
    # We also filter out invalid indices (< 1).
    valid_indices = sorted([i for i in delete_suggestion if i >= 1], reverse=True)

    # 4. Delete the items
    for idx in valid_indices:
        list_idx = idx - 1  # Convert 1-based index to 0-based index
        if 0 <= list_idx < len(memory_list):
            memory_list.pop(list_idx)
        else:
            print(f"[!] Warning: Index {idx} is out of bounds. Skipping deletion.")

    assert len(delete_suggestion) + len(memory_list) == ori_memory_len
    
    # 5. Recalculate the MEMORY_CAP (total character count of all memory items)
    total_chars = sum(len(str(item)) for item in memory_list)

    # 6. Update the dictionary
    data['MEMORY'] = memory_list
    data['MEMORY_CAP'] = float(total_chars) / MEM_CEIL 
    save_memory_to_file(file_path , data)
    print(f"[+] Successfully deleted memory {delete_suggestion}. Remaining items: {len(memory_list)} (Ori:{ori_memory_len}), CAP: {total_chars}/{MEM_CEIL} chars.")
    
def add_memory(ticker, memory_suggestion , sector , model_name ):

    data  , file_path = get_memeory_by_ticker(ticker)
    memory_list = data.get('MEMORY', [])

    # a. Add the new memory suggestions to the list
    if isinstance(memory_suggestion, list):
        # Clean up the suggestions (strip whitespace and ignore completely empty strings)
        clean_suggestions = [str(item).strip() for item in memory_suggestion if str(item).strip()]
        memory_list.extend(clean_suggestions)
    else:
        print("[-] Error: memory_suggestion must be a list.")
        return False

    # b. Recalculate the MEMORY_CAP (total character count of all memory items)
    total_chars = sum(len(str(item)) for item in memory_list)
    is_condensed = 0 
    # Warn if the ceiling is exceeded
    if total_chars > MEM_CEIL * 0.75:
        print(f"[!] Warning: Memory capacity ({total_chars}) exceeds the ceiling of {MEM_CEIL}.")
        memory_list =  condense_memory(ticker , sector , model_name, memory_list, is_debug= 0 , mm='memory')
        total_chars = sum(len(str(item)) for item in memory_list)
        is_condensed = 1 

    # c. Update the dictionary
    data['MEMORY'] = memory_list
    data['MEMORY_CAP'] = float(total_chars) / MEM_CEIL 

    save_memory_to_file(file_path , data)

    if is_condensed:
        print(f"[+] Successfully condense Memory. Total items: {len(memory_list)}. CAP: {total_chars}/{MISSING_CEIL} chars.")
    else:
        print(f"[+] Successfully added {len(clean_suggestions)} items. Total items: {len(memory_list)}, CAP: {total_chars}/{MEM_CEIL} chars.")
        

def add_missing(ticker , missing_suggestion , sector , model_name):
    data  , file_path = get_memeory_by_ticker(ticker)
    missing_list = data.get('MISSING', [])
        
    if isinstance(missing_suggestion, list):
        clean_suggestions = [str(item).strip() for item in missing_suggestion if str(item).strip()]
        missing_list.extend(clean_suggestions)
    else:
        print("[-] Error: missing_suggestion must be a list.")
        return False

    total_chars = sum(len(str(item)) for item in missing_list)
    is_condensed = 0 
    if total_chars > MISSING_CEIL * 0.75:
        print(f"[!] Warning: MISSING capacity ({total_chars}) exceeds the ceiling of {MISSING_CEIL}.")
        missing_list =  condense_memory(ticker , sector , model_name, missing_list, is_debug= 0, mm='missing')
        total_chars = sum(len(str(item)) for item in missing_list)
        is_condensed = 1

    data['MISSING'] = missing_list
    data['MISSING_CAP'] = float(total_chars) / MISSING_CEIL 

    save_memory_to_file(file_path , data)

    if is_condensed:
        print(f"[+] Successfully condense MISSING. Total items: {len(missing_list)}, CAP: {total_chars}/{MISSING_CEIL} chars.")
    else:
        print(f"[+] Successfully added {len(clean_suggestions)} items to MISSING. Total items: {len(missing_list)}, CAP: {total_chars}/{MISSING_CEIL} chars.")
        

def extract_suggestion_from_llm_feedback(text):
    """
    从文本中分别提取 <MEMORY>, <delete>, <MISSING> 标签内的内容。
    - MEMORY / MISSING: 按行分割，并去除前置的各类索引 (如 1., (1), (a) 等)
    - delete: 提取由逗号分隔的整数列表
    """
    def clean_list_items(raw_text):
        if not raw_text:
            return []
        
        # 按换行符分割
        lines = raw_text.strip().split('\n')
        cleaned_lines = []
        
        for line in lines:

            line = line.replace('§', '').strip()
            # 如果这一行全是空格或者原本就只有一个 '§'，处理后会变成空字符串，直接跳过
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
            try:
                cleaned_line = re.sub(r'^\s*(?:\d+\.|\(\d+\)|\([a-zA-Z]\)|[a-zA-Z]\.)\s*', '', line)
                cleaned_lines.append(cleaned_line)
            except:
                print('! Failed to extract information from:')
                print(raw_text)
                continue 

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
            try:
                delete_list = [int(num.strip()) for num in raw_delete.split(',') if num.strip()]
            except:
                print('WARNING: Delete extraction failed:' , raw_delete)
                pass 
    return memory_list, delete_list, missing_list








'''
    
def extract_memory_blocks(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    sector_match = re.search(r"SECTOR:\s*(.*?)(?=════)", content, re.DOTALL)
    sector = sector_match.group(1).strip() if sector_match else "MATCH_ERROR"

    target_match = re.search(r"TARGET:\s*(.*?)(?=════)", content, re.DOTALL)
    target = target_match.group(1).strip() if target_match else "MATCH_ERROR"

    memory_match = re.search(r"MEMORY[^\n]*\n(.*?)(?=════)", content, re.DOTALL)
    if memory_match:
        memory_raw = memory_match.group(1)
        memory = [item.strip() for item in memory_raw.split('§') if item.strip()]
    else:
        memory = "MATCH_ERROR"
    
    missing_match = re.search(r"MISSING[^\n]*\n(.*?)(?=════)", content, re.DOTALL)
    if missing_match:
        missing_raw = missing_match.group(1)
        missing = [item.strip() for item in missing_raw.split('§') if item.strip()]
    else:
        missing = "MATCH_ERROR"

    return sector, target, memory, missing
'''