import os
import json
import threading

# --- 全局锁 ---
# 这个锁必须是全局唯一的，所有线程共享同一个锁对象
FILE_LOCK = threading.Lock()

def _get_pred_file_path(ticker, alpha= None , base_dir=None):

    assert base_dir is not None 
    
    if not os.path.exists(base_dir):
        os.makedirs(base_dir, exist_ok=True)
        
    if alpha is not None :
        alpha = str(alpha).replace('.' , 'p')
        return os.path.join(base_dir, f"{ticker}_{alpha}.json")
    else:
        return os.path.join(base_dir, f"{ticker}.json")

import time 
def is_prediction_exist(ticker, target_date =None , alpha= None , base_dir=None):
    """
    检查某个日期的预测是否已经存在于文件中。
    用于在调用 LLM 前快速跳过。
    """
    assert base_dir is not None 
    file_path = _get_pred_file_path(ticker, alpha , base_dir)
    # print(target_date)
    # print(file_path) ; time.sleep(19999) 
    
    # 读操作也建议加锁，或者至少要处理读写冲突
    # 这里为了极致安全，读也加锁
    with FILE_LOCK:
        if not os.path.exists(file_path):
            return False
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                
            # 检查 target_date 是否在已有的记录中
            # 假设记录里的 key 是 'fore_cut_off_date'
            for record in existing_data:
                if record.get('fore_cut_off_date') == target_date:
                    
                    return True
            return False
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"⚠️ Error reading {file_path} for check: {e}")
            return False

def save_prediction_thread_safe(ticker, new_record, alpha=None, base_dir=None):
    """
    线程安全地保存预测结果。
    如果文件不存在则创建，存在则追加。会自动去重。
    """
    assert base_dir is not None 

    file_path = _get_pred_file_path(ticker, alpha , base_dir)
    
    target_date = new_record.get('fore_cut_off_date')
    
    # --- 临界区开始 (加锁) ---
    with FILE_LOCK:
        existing_data = []
        
        # 1. 读取现有数据
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except json.JSONDecodeError:
                print(f"⚠️ Warning: {file_path} corrupted. Overwriting with new data.")
                existing_data = []

        # 2. 再次检查重复 (Double Check)
        # 防止两个线程同时通过了外面的 is_prediction_exist 检查，
        # 然后都排队等着写同一个日期。
        for record in existing_data:
            if record.get('fore_cut_off_date') == target_date:
                print(f"🔄 Duplicate detected during save for {target_date}. Skipping write.")
                return # 直接返回，不保存

        # 3. 追加新数据
        existing_data.append(new_record)
        
        # 4. 排序 (可选，按日期排序让文件好看一点)
        try:
            existing_data.sort(key=lambda x: x.get('fore_cut_off_date', ''))
        except:
            pass # 如果日期格式不对就不排了

        # 5. 写入文件
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=4, ensure_ascii=False)
            print(f"💾 Saved prediction for {ticker} on {target_date}")
        except Exception as e:
            print(f"❌ Error writing to {file_path}: {e}")
    # --- 临界区结束 (自动释放锁) ---