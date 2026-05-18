# python -m seer.scripts.run_gemini
import os
from seer.events_search import  domain_info 
from seer.events_search.domain_info import DATA_BASE_PATH
from seer.utils import utils , llm_api_utils 
from datetime import datetime
import os
import pandas as pd
import argparse
import concurrent.futures
from functools import partial
import logging
from copy import deepcopy
import traceback 
    
# --- 3. Logging Helper ---
def setup_custom_logger(name, log_file):
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
    # 确保日志目录存在
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
         
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    # 避免重复添加 handler
    if not logger.handlers:
        logger.addHandler(handler)
    return logger
    
from seer.utils.llm_api_utils import process_single_day , process_multi_days

def run_search_stock_parallel(model_name, ticker, start_date, end_date, 
                              num_rounds, agent_domain, api_logger=None, max_workers=12):
    
    print(f"--- Stock Search Configuration ---")
    print(f"Model      : {model_name}")
    print(f"Ticker     : {ticker}")
    print(f"Agent      : {agent_domain}")
    print(f"Rounds     : {num_rounds}")
    print(f"Workers    : {max_workers}")
    
    event_save_path = f'{DATA_BASE_PATH}/data/stock/events_loho/{ticker}'
    if not os.path.exists(event_save_path):
        os.makedirs(event_save_path)
        
    try:
        entity_name = domain_info.get_completed_name(ticker)
        print(f"Target Company: {entity_name} [{ticker}]")
    except Exception as e:
        print(f"\033[91m ERROR: Failed to fetch domain info: {e} \033[0m")
        return
    
    today_str = datetime.today().strftime('%Y-%m-%d')
    if str(end_date) > today_str:
        end_date = today_str
    print(f"Range      : {start_date} to {end_date}")
    
    # 1. 生成所有日期，并按设定的天数（如 7 天）进行切片
    date_list = pd.date_range(start=start_date, end=end_date)
    chunk_size = 7
    date_chunks = []
    
    for i in range(0, len(date_list), chunk_size):
        chunk = date_list[i:i + chunk_size]
        # 保存每个 chunk 的开始和结束日期
        chunk_start = chunk[0].strftime('%Y-%m-%d')
        chunk_end = chunk[-1].strftime('%Y-%m-%d')
        date_chunks.append((chunk_start, chunk_end))

    print(f"📡 Parallelizing {len(date_chunks)} date chunks (size {chunk_size} days)... to {max_workers} workers!")
     
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        
        # 2. 绑定新的 process_multi_days 函数
        worker_func = partial(
            process_multi_days,
            model_name=model_name,
            entity_name=entity_name,
            prompt_domain=agent_domain,
            event_save_path=event_save_path,
            num_rounds=num_rounds,
            api_logger=api_logger
        )
        
        # 3. 提交任务：传入 start_date 和 end_date
        future_to_chunk = {
            executor.submit(worker_func, start_d, end_d): (start_d, end_d) 
            for start_d, end_d in date_chunks
        }
        
        # 4. 获取结果
        for future in concurrent.futures.as_completed(future_to_chunk):
            start_d, end_d = future_to_chunk[future]
            try:
                result = future.result()
                print(result)
            except Exception as exc:
                print(f"❌ {start_d} to {end_d} generated an exception: {exc}")
                full_traceback = traceback.format_exc()
                if api_logger:
                    api_logger.error(f"Thread Exception for {start_d} to {end_d}:\n{full_traceback}")

# --- 4. CLI Entry Point ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stock Events Search Agent")

    parser.add_argument("-m", "--model_name", type=str, choices=["gemini", "claude"], default="gemini", help="Model name")
    parser.add_argument("-t", "--ticker", type=str, required=True, help="Stock ticker symbol (e.g., NVDA)")
    parser.add_argument("-d", "--domain", type=str, required=True, help="Price Search Domain (e.g., stock_events_search)")
    
    parser.add_argument("-s", "--start_date", type=utils.parse_flexible_date, default=None, 
                        help="Start date (YYYY, YYYY-MM, or YYYY-MM-DD)")
    parser.add_argument("-e", "--end_date", type=utils.parse_flexible_date, default=None, 
                        help="End date (YYYY, YYYY-MM, or YYYY-MM-DD)")
    
    parser.add_argument("-n", "--num_rounds", type=int, default=3, help="Search rounds per day")
    parser.add_argument("-w", "--workers", type=int, default=12, help="Number of parallel threads")

    args = parser.parse_args()

    LOG_DIR = 'seer/logs' 
    api_logger = setup_custom_logger('stock_api_checker', f'{LOG_DIR}/stock_API_errors.log')
    
    run_search_stock_parallel(
        model_name=args.model_name,
        ticker=args.ticker,
        start_date=args.start_date,
        end_date=args.end_date,
        num_rounds=args.num_rounds,
        max_workers=args.workers,
        agent_domain=args.domain,
        api_logger=api_logger
    )
    
'''

Data Format:
    [
        {
            "date": "YYYY-MM-DD",
            "description": "The key entity and the nature of the event.",
            "causality": "Why and how it impacted the stock.",
            "sentiment": "Positive" | "Negative" | "Neutral",
            "impact_type": "Direct" | "Indirect" | "Neutral", 
            "factual_check_gemini":{
                'factual_status': True|False, 
                'date_val': "YYYY-MM-DD",
                'response_with_citations': '...', 
                'response_text': '...', 
                'citations': [...],
            },
            "factual_check_claude":{
                'factual_status': True|False, 
                'date_val': "YYYY-MM-DD",
                'response_with_citations': '...', 
                'response_text': '...', 
                'citations': [...],
            }    
        },
        (... List of events for that day)
    ]

'''
