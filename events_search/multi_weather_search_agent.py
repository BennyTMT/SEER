# python -m seer.scripts.run_gemini
import os
import json
from seer.events_search import  domain_info 
from seer.events_search.domain_info import DATA_BASE_PATH
import numpy as np 
import time , sys 
from seer.utils import utils , llm_api_utils 

import os
import sys
import pandas as pd
import argparse
import concurrent.futures
from functools import partial
import logging
from copy import deepcopy

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
    
from seer.utils.llm_api_utils import process_single_day

'''

    /home/mingtiant_google_com/google_intern_data/data/weather/events/

'''
# --- 2. Main Runner: 负责设置和调度 ---
def run_search_stock_parallel(model_name, ticker, start_date, end_date, 
                              num_rounds, agent_domain, api_logger=None, max_workers=12):
    
    print(f"--- Stock Search Configuration ---")
    print(f"Model      : {model_name}")
    print(f"Ticker     : {ticker}")
    print(f"Agent      : {agent_domain}")
    print(f"Range      : {start_date} to {end_date}")
    print(f"Rounds     : {num_rounds}")
    print(f"Workers    : {max_workers}")
    
    safe_ticker = ticker.replace(" ", "_")
    event_save_path = f'{DATA_BASE_PATH}/data/weather/events/{safe_ticker}'
    if not os.path.exists(event_save_path):
        os.makedirs(event_save_path)
        
    # 2. 获取公司信息 (Stock 特有的逻辑)
    print("Fetching CITY info...")
    try:
        entity_name =  domain_info.get_completed_name(ticker)
        print(f"Target CITY: {entity_name} [{ticker}]")
        
    except Exception as e:
        print(f"\033[91m ERROR: Failed to fetch domain info: {e} \033[0m")
        return
        
    # 3. 生成日期列表
    date_list = pd.date_range(start=start_date, end=end_date).strftime('%Y-%m-%d').tolist()
    print(f"📡 Parallelizing {len(date_list)} days... to {max_workers} workers!")
     
    # 4. 多线程执行
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 使用 partial 锁定那些不变的参数
        worker_func = partial(
            process_single_day,
            model_name=model_name, 
            entity_name=entity_name,
            prompt_domain=agent_domain,
            event_save_path=event_save_path,
            num_rounds=num_rounds,
            api_logger=api_logger
        )
        
        # 提交任务
        future_to_date = {executor.submit(worker_func, date): date for date in date_list}
            
        # 获取结果并打印进度
        for future in concurrent.futures.as_completed(future_to_date):
            date = future_to_date[future]
            try:
                result = future.result()
                print(result)
            except Exception as exc:
                print(f"❌ {date} generated an exception: {exc}")
                if api_logger:
                    api_logger.error(f"Thread Exception for {date}: {exc}")

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

    # 设置日志
    LOG_DIR = 'seer/logs' # 假设的日志目录
    api_logger = setup_custom_logger('stock_api_checker', f'{LOG_DIR}/stock_API_errors.log')
    
    # 运行主程序
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
Format:
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
