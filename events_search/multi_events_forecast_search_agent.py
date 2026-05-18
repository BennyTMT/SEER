# python -m seer.scripts.run_gemini
from urllib import response

from seer.utils import utils 
from seer.events_search.domain_info import DATA_BASE_PATH

import numpy as np 
import time , sys 
import traceback
import os
import json
import pandas as pd
import matplotlib.pyplot as plt

from collections import defaultdict
import random 
import argparse

'''
    /home/mingtiant_google_com/google_intern_data/data/events
'''
FORECAST_DATA_SAVE = f'{DATA_BASE_PATH}/data/events'
LOG_DIR='seer/logs'
ABLATION=True 

import concurrent.futures
from copy import deepcopy

def fact_check_agent_parallelize(search_target , factors_extracted , model_name='', api_logger=None , events_pool=None):
    
    def process_single_task(search_target, item, model_name):# -> tuple[Any | Literal['gemini', 'claude'], dict[str, Any]]:
        """
        Handles a single API request for a specific item and model.
        """
        
        system_prompt, user_msg = utils.formating_prompt(\
                    search_target, prompt_params=item, agent='factual')
        
        # description = item['description']
        # original_date = item['date']
        
        MAX_RETRIES = 5
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response_text = '' 
                
                if model_name == 'gemini':
                    response_text, response_with_citations, citations = \
                        utils.query_gemini(system_prompt, user_msg, history= \
                            None, citations_need=True ,web_search = True)
                elif model_name == 'claude':
                    response_text, response_with_citations, citations = \
                        utils.query_claude(system_prompt, user_msg)
                
                factual_status, date_val = utils.extract_tag_data(response_text)
                
                # Failed to extract effective content 
                assert factual_status is not None 
                assert date_val is not None 
                
                # num_len = len(citations) if citations else 0
                # print(f"[{model_name}] --- Event: {description} | Factual: {factual_status} | Date: {date_val} | Cites: {num_len}")
                
                result_data = {
                    'factual_status': factual_status, 
                    'date_val': date_val, 
                    'response_with_citations': response_with_citations,
                    'response_text': response_text, 
                    'citations': citations 
                }
                return model_name, result_data
                
            except Exception as e:
                response_text = utils.smart_print(response_text)
                api_logger.error(f"[Fack-Check:[{model_name}] Attempt {attempt}  {search_target}]  Resp:{response_text}")
                
                if attempt < MAX_RETRIES:
                    wait_time = 2 ** attempt 
                    time.sleep(wait_time)
                else:
                    content = f"‼️ {MAX_RETRIES} Times Attempts, Killed the process! "
                    api_logger.error(f"[Fack-Check: {content} || {search_target}] [{model_name}]")
                    
                    return model_name, None 
                            
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        # Create a list of future tasks
        future_to_item = {}
        
        for item in factors_extracted:
            for model_name in ['gemini', 'claude']:
                # Submit task to the thread pool
                future = executor.submit(process_single_task, search_target, item, model_name)
                # Store the future with a reference to the item it's updating
                future_to_item[future] = item

        # As tasks complete, update the original items
        for future in concurrent.futures.as_completed(future_to_item):
            item = future_to_item[future]
            model_name, result = future.result()
            # Thread-safe update of the item dictionary
            item[f'factual_check_{model_name}'] = result

    return factors_extracted

import os
import pandas as pd
import numpy as np
import re 
from datetime import datetime, timedelta
import concurrent.futures
from functools import partial

HISTORY_JSON_PATH = "seer/file/polymarket_history.json"
    
def process_single_day(search_range , model_name, ticker, target_event, prompt_domain, event_save_path, num_rounds , api_logger):
    
    search_start_date , search_end_date = search_range
    """处理单个日期的搜索和事实核查"""
    # 1. 检查最终结果是否已存在
    final_file = f'{event_save_path}/{model_name}-{search_start_date}-{search_end_date}-{num_rounds}.json'
    
    if os.path.exists(final_file):
        return f"✅ {search_range} already completed."
        
    print(f"🚀 Starting {model_name} for {search_range}")
    events_pool = None 
    
    for r in range(num_rounds):
        
        round_file_save_path = f'{event_save_path}/{model_name}-{search_start_date}-{search_end_date}-{r+1}.json'
        print(round_file_save_path)
        
        if os.path.exists(round_file_save_path):
            events_pool = utils.load_json_to_list(round_file_save_path)
            print(round_file_save_path , 'has done')
            continue 
            
        ##########################################   
        # (1) Search Agent  
        ##########################################    
        if events_pool :
            events_lists , _ = utils.get_events_for_search(
                                        events_pool , 
                                        cut_off_date=None,
                                        search_range=search_range, 
            )
        
        else:
            events_lists = None 
            
        # try:
        system_prompt , user_msg = utils.formating_prompt(
                                '',
                                prompt_params={
                                        'target_event':target_event , 
                                        "search_range":search_range,
                                        'events_lists':events_lists
                                },
                                agent=prompt_domain
        )
        # except Exception as e:
            # api_logger.warning(f"Failed to format prompt for event: {target_event}", exc_info=True)
            
        # print('system_prompt', '-------------------')
        # print(system_prompt)
        # print("--- Sending Requests.... --- Round " , r +1 , 'User Prompt:' )
        # print(user_msg)
        # print('-------------------------------------')
        # time.sleep(1000000)

        MAX_RETRIES = 3
        factors_extracted = None
        task_label = f"{ticker} | {search_range[0]} to {search_range[1]} | R{r+1}"
        for attempt in range(1, MAX_RETRIES + 1):
            try:    
                factors_from_this_round = ''
                if model_name == 'claude':
                    factors_from_this_round , _ , _ = utils.query_claude(system_prompt , user_msg ) 
                elif model_name == 'gemini':
                    factors_from_this_round , _ , _ = utils.query_gemini(system_prompt , user_msg \
                        , history=None , citations_need = False , web_search=True)
                    
                # print('--------------')
                # print(factors_from_this_round)
                
                factors_extracted = utils.extract_json_to_list(factors_from_this_round)
                if factors_extracted is not None:
                    break
                else:
                    raise ValueError("Extraction returned None (Invalid JSON format)")

            except Exception as e:
                if attempt < MAX_RETRIES:
                    f_resp = utils.smart_print(factors_from_this_round)
                    wait_time = 2 * attempt  
                    warn_msg = f"[{model_name}] Attempt {attempt} failed: {e}. Resp:\n{f_resp}..."
                    api_logger.warning(f"Search-Agent [{task_label}] {warn_msg}")
                    time.sleep(wait_time)
                else:
                    error_final_msg = f"‼️ SEARCH FATAL: {model_name} failed after {MAX_RETRIES} attempts. Last Err: {e} Failed User Prompt:\n{user_msg}"
                    print(f"\033[91m {error_final_msg} \033[0m")
                    return None 
                    
        # print('Resp: ----------------- ' , cut_off_date)
        # print(factors_from_this_round) 

        ##########################################   
        # (2) Fact-check Agent    
        ########################################## 

        checked_facts = fact_check_agent_parallelize(target_event,\
                            factors_extracted , model_name=model_name , api_logger=api_logger)

        if events_pool is None : events_pool = checked_facts
        else: events_pool += checked_facts
            
        if events_pool is None : 
            raise ValueError(' Events Pool is None !!')

        print(round_file_save_path , ' has done!!!')
        # utils.print_events_lists_from_pool(events_pool , r)
        utils.save_list_to_json(events_pool, round_file_save_path)

    return f"🏁 {search_range} execution finished."

def split_date_range(start_date, end_date, num_splits):
    # 1. 统一转换为 datetime 对象
    if isinstance(start_date, str):
        start_dt = datetime.strptime(start_date[:10], '%Y-%m-%d')
    else:
        start_dt = start_date

    if isinstance(end_date, str):
        end_dt = datetime.strptime(end_date[:10], '%Y-%m-%d')
    else:
        end_dt = end_date

    # 2. 计算总天数
    total_days = (end_dt - start_dt).days + 1
    
    # 3. 确定实际划分份数：不能超过总天数
    actual_splits = min(num_splits, total_days)
    
    if actual_splits <= 0:
        return []
    # 4. 计算基础宽度和余数（用于平摊多出来的天数）
    base_width = total_days // actual_splits
    remainder = total_days % actual_splits
    range_list = []
    current_start = start_dt
    # 5. 分配每一份的时间
    for i in range(actual_splits):
        # 将余数里的天数逐一分配给前面的 range，保证分布均匀
        extra_day = 1 if i < remainder else 0
        current_range_days = base_width + extra_day
        # 计算当前块的结束日期
        current_end = current_start + timedelta(days=current_range_days - 1)
        # 存入列表
        range_list.append((
            current_start.strftime('%Y-%m-%d'),
            current_end.strftime('%Y-%m-%d')
        ))
        
        # 移动到下一个起点
        current_start = current_end + timedelta(days=1)
        
    return range_list , total_days , base_width

def run_search_events(model_name, ticker, num_rounds, search_range=10, api_logger=None, max_workers=8):

    if not os.path.exists(HISTORY_JSON_PATH):
        raise ValueError(f"File not found: {HISTORY_JSON_PATH}")

    with open(HISTORY_JSON_PATH, 'r') as f:
        events = json.load(f)
        
    # Match Event (使用 id 匹配)
    target_event_data = next((e for e in events if e['id'] == ticker), None)
    if not target_event_data:
        raise ValueError(f"\033[91m ERROR: No event found matching ticker '{ticker}' in JSON! \033[0m")
        
    title = target_event_data['title']
    event_end_dt = datetime.strptime(target_event_data['end_date'], '%Y-%m-%d %H:%M')
    event_start_dt = datetime.strptime(target_event_data['start_date'], '%Y-%m-%d %H:%M')
    ticker_type = target_event_data['category']

    # search_range is "How many chunks do we have"
    range_list , total_days , base_width =split_date_range(event_start_dt , event_end_dt, search_range)
    
    # --- 路径设置 ---
    if ticker_type == "Economy & Business":
        base_save_path = f"{FORECAST_DATA_SAVE}/economics/{ticker}"
        prompt_domain = 'economic_forecast_search' 
    elif ticker_type == "Politics & World Affairs": 
        base_save_path = f"{FORECAST_DATA_SAVE}/political/{ticker}"
        prompt_domain = 'political_forecast_search' 
    elif ticker_type == "Tech & AI": 
        base_save_path = f"{FORECAST_DATA_SAVE}/tech/{ticker}"
        prompt_domain = 'tech_forecast_search'
        
    if not os.path.exists(base_save_path):
        os.makedirs(base_save_path)

    # --- 3) 打印信息 ---
    print(f"--- Configuration ---")
    print(f"Model        : {model_name}")
    print(f"Target Event : {title}")
    print(f"Total Period : {event_start_dt.strftime('%Y-%m-%d')} to {event_end_dt.strftime('%Y-%m-%d')} ({total_days} Days)")
    print(f"Range Width  : {base_width} Days")
    print(f"Total Ranges : {len(range_list)}")
    print(f"Save Dir     : {base_save_path}")
    
    # --- 4) 按照特定的文件名规则来检查已有的文件 ---
    tasks_to_run = []
    for r_start, r_end in range_list:
        # 严格对齐你的保存逻辑：{model_name}-{start}-{end}-{rounds}.json
        # 注意：如果 r_start 和 r_end 相同，确保格式与 process_single_day 内部一致
        file_name = f"{model_name}-{r_start}-{r_end}-{num_rounds}.json"
        save_file = os.path.join(base_save_path, file_name)
        
        should_skip = False
        if os.path.exists(save_file):
            try:
                with open(save_file, 'r') as f:
                    content = json.load(f)
                    # 只有当文件存在且内容不是 null (None) 时才跳过
                    if content is not None:
                        print(f"⏩ Skipping Range {r_start} to {r_end}, already completed.")
                        should_skip = True
            except (json.JSONDecodeError, Exception):
                pass
        if not should_skip:
            tasks_to_run.append((r_start, r_end))

    if not tasks_to_run:
        print("✅ All ranges are already processed and not null.")
        return
    
    print(f"📡 Parallelizing {len(tasks_to_run)} range-tasks with {max_workers} threads...")
        
    # --- 5) 按照 range 遍历传参 ---
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 注意：process_single_day 的第一个参数现在是 search_range (即元组)
        # 函数签名：def process_single_day(search_range, model_name, ticker, ...)
        future_to_range = {
            executor.submit(
                process_single_day,
                search_range=rng,  # 传入 (start_date, end_date) 元组
                model_name=model_name,
                ticker=ticker,
                target_event=title,
                prompt_domain=prompt_domain,
                event_save_path=base_save_path,
                num_rounds=num_rounds,
                api_logger=api_logger
            ): rng for rng in tasks_to_run
        }
        
        for future in concurrent.futures.as_completed(future_to_range):
            rng = future_to_range[future]
            try:
                result = future.result()
                print(f"✅ OK: Range {rng[0]} to {rng[1]}")
            except Exception as exc:
                # 获取完整的堆栈信息
                error_type = type(exc).__name__  # 错误类型，如 ValueError
                stack_trace = traceback.format_exc()  # 完整的堆栈跟踪字符串
                
                print(f"❌ Error at Range {rng[0]} to {rng[1]}")
                print(f"Type: {error_type}")
                print(f"Message: {exc}")
                print("-" * 20 + " Stack Trace " + "-" * 20)
                print(stack_trace)
                print("-" * 53)
                
            # try:
            #     result = future.result()
            #     print(f"OK: Range {rng[0]} to {rng[1]}")
            # except Exception as exc:
            #     print(f"❌ {rng[0]} to {rng[1]} generated an exception: {exc}")

import logging

def setup_custom_logger(name, log_file):
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger


if __name__ == "__main__":  
    parser = argparse.ArgumentParser(description="Events Search Agent Parameters")

    parser.add_argument(
        "-m", 
        "--model_name", 
        type=str, 
        choices=["gemini", "claude"], 
        default="gemini", 
        help="Name of the model (choices: gemini, claude, default: gemini)"
    )
    
    parser.add_argument("-t", "--ticker", type=str, default=None, help="Stock ticker symbol")
    parser.add_argument("-r", "--ranges", type=int, default=30 )
    parser.add_argument("-n", "--num_rounds", type=int, default=5, help="Number of search rounds")
    parser.add_argument("-w", "--workers", type=int, default=12, help="Number of parallel threads")
    args = parser.parse_args()
    
    print(f"Running {args.model_name} [{args.ticker}] For {args.ranges} ranges!")
    print(f"Total rounds: {args.num_rounds}")
    
    api_logger = setup_custom_logger('api_checker', f'{LOG_DIR}/event_API_errors.log')

    run_search_events(
        args.model_name, 
        args.ticker,
        args.num_rounds, 
        search_range=args.ranges, 
        api_logger=api_logger, 
        max_workers=args.workers
    )
         
    
'''
{
    "id": "0x7c6c69d91b21cbbea08a13d0ad51c0e96a956045aaadc77bce507c6b0475b66e",
    "source": "polymarket",
    "question": "Fed increases interest rates by 25+ bps after January 2026 meeting?",
    "resolution_criteria": "Resolves to the outcome of the question found at https://polymarket.com/market/fed-increases-interest-rates-by-25-bps-after-january-2026-meeting.",
    
    "background": "The FED interest rates are defined in this market by the upper bound of the target federal funds range. The decisions on the target federal fund range are made by the Federal Open Market Committee (FOMC) meetings.\n\nThis market will resolve to the amount of basis points the upper bound of the target federal funds rate is changed by versus the level it was prior to the Federal Reserve's January 2026 meeting.\n\nIf the target federal funds rate is changed to a level not expressed in the displayed options, the change will be rounded up to the nearest 25 and will resolve to the relevant bracket. (e.g. if there's a cut/increase of 12.5 bps it will be considered to be 25 bps)\n\nThe resolution source for this market is the FOMC\u2019s statement after its meeting scheduled for January 27 - 28, 2026 according to the official calendar: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm.\n\nThe level and change of the target federal funds rate is also published at the official website of the Federal Reserve at https://www.federalreserve.gov/monetarypolicy/openmarket.htm.\n\nThis market may resolve as soon as the FOMC\u2019s statement for their January meeting with relevant data is issued. If no statement is released by the end date of the next scheduled meeting, this market will resolve to the \"No change\" bracket.",
    
    "market_info_open_datetime": "2025-09-17",
    "market_info_close_datetime": "2026-01-28T00:00:00+00:00",
    "market_info_resolution_criteria": "N/A",
    "url": "https://polymarket.com/market/fed-increases-interest-rates-by-25-bps-after-january-2026-meeting",
    "freeze_datetime": "2026-01-08T00:00:00+00:00",
    "freeze_datetime_value": "0.0035",
    "freeze_datetime_value_explanation": "The market price.",
    "source_intro": "We would like you to predict the outcome of a prediction market. A prediction market, in this context, is the aggregate of predictions submitted by users on the website Polymarket. You're going to predict the probability that the market will resolve as 'Yes'.",
    "resolution_dates": "N/A"
},
        
'''


'''

[
   {
    "date": "YYYY-MM-DD",
    "description": "The specific data point, quote, or market metric.",
    "causality": "Brief reasoning on why this shifts the probability in that direction.",
    "category": "Hard Data" | "Signal" | "Market Pricing",
    "impact_type": "Increases Likelihood" | "Decreases Likelihood" | "Neutral",
    "source": "Source Name",
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
  }
  ... (List of events)
]

'''