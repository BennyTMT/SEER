import argparse
import pandas as pd
import json , uuid , time , os , sys
from datetime import datetime
from seer.utils import utils , io_manager , memory_tool 

from seer.utils.memory_tool import MEM_CEIL , MISSING_CEIL
from seer.events_search import  domain_info 
from collections import defaultdict
import random 
import textwrap
import concurrent.futures
from functools import partial
import re , traceback 

DATA_BASE_PATH = '.'
OUTPUT_SAVE_DIR=''
WAYS=None 
ROUND=0

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

def tee_print(msg=""):
    print(msg)
    # with open('seer/visualize/tsf_record.txt', 'a', encoding='utf-8') as log_file:
        # log_file.write(msg + "\n")
        # log_file.flush() 

def load_and_filter_events(args,  base_path=f"{DATA_BASE_PATH}/data/stock/events_soho"):

    def check_bool(val):
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            return val.lower() == 'true'
        return False

    ticker, start_date, end_date = args.ticker , args.start_date , args.end_date
    validated_events_dict = defaultdict(list)
    impact_types_to_track = ["Direct", "Indirect", "Neutral"]
    impact_stats = {k: {'total': 0, 'kept': 0} for k in impact_types_to_track}

    search_dates = pd.date_range(start=start_date, end=end_date).strftime('%Y-%m-%d').tolist()
    ticker_event_path = os.path.join(base_path, ticker)

    files_processed = 0
    total_events_kept = 0
    total_events_get  = 0 
    
    assert ROUND 

    for current_date in search_dates:
        
        filename = f"gemini-{current_date}-{ROUND}.json"

        file_path = os.path.join(ticker_event_path, filename)
        
        if not os.path.exists(file_path):
            print(f'Events Missed on {current_date}') ; continue 
            
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                events_list = json.load(f)
                
            if not isinstance(events_list, list):
                print(f"⚠️ Warning: {filename} content is not a list. Skipping."); exit() 

            files_processed += 1

            for event in events_list:
                
                raw_impact = event.get("impact_type")
                
                if raw_impact in impact_stats:
                    impact_stats[raw_impact]['total'] += 1
                
                total_events_get += 1 

                claude_check = event.get('factual_check_claude', {})
                gemini_check = event.get('factual_check_gemini', {})
                
                c_status = check_bool(claude_check.get('factual_status'))
                g_status = check_bool(gemini_check.get('factual_status'))
                
                c_date = claude_check.get('date_val')
                g_date = gemini_check.get('date_val')
                
                if c_status and g_status and c_date == g_date:
                    structured_event = {
                        "id": str(uuid.uuid4()),
                        "event": event.get("description"),
                        "sentiment": event.get("sentiment"),
                        "impact_type": raw_impact
                    }
                    validated_events_dict[c_date].append(structured_event)
                    total_events_kept += 1
                    
                    if raw_impact in impact_stats:
                        impact_stats[raw_impact]['kept'] += 1

        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            continue 
    
    assert total_events_get > 0 

    overall_r = 100 * total_events_kept / total_events_get
    print(f"✅ [{ticker}] Extracted {total_events_kept}/{total_events_get} events ({overall_r:.1f}% Kept)")
    return dict(validated_events_dict)

def generate_prediction_sample(
    fore_cut_off_date, 
    lookback_window, 
    prediction_horizon, 
    result_list, 
    validated_events_dict
):
    """
    构建单条预测样本：计算未来收益，并根据收益方向对历史事件进行有偏采样。
    已修复：包含 Lookback 窗口内的周末和节假日事件。
    """
    # --- 1. 定位日期索引 (Locate Index) ---
    try:
        # 提取所有交易日
        dates = [item['date'] for item in result_list]
        try:
            t_index = dates.index(fore_cut_off_date)
        except ValueError:
            holi = utils.check_us_holiday_or_weekend(fore_cut_off_date)
            raise ValueError(f"⚠️ Pass {fore_cut_off_date} not in price. Reason: {holi}")

        # Boundary Check 
        if t_index < lookback_window or t_index + prediction_horizon >= len(result_list):
            raise ValueError(f"⚠️ Not enough boundaries for {fore_cut_off_date}. < {lookback_window} look back days")

        
        # --- 2. 计算股价波动与打标签 (Calculate Return & Label) ---
        current_price = result_list[t_index]['close']
        future_price = result_list[t_index + prediction_horizon]['close']
        pct_change = (future_price - current_price) / current_price


        HIHG_LIQ = 1 
        if HIHG_LIQ:
            if pct_change > 0.02:               label = "Strong Up"
            elif 0.005 < pct_change <= 0.02:    label = "Up"
            elif -0.005 <= pct_change <= 0.005: label = "Neutral"
            elif -0.02 <= pct_change < -0.005:  label = "Down"
            else:                               label = "Strong Down"
        else:
            if pct_change > 0.05:               label = "Strong Up"
            elif 0.02 < pct_change <= 0.05:     label = "Up"
            elif -0.02 <= pct_change <= 0.02:   label = "Neutral"
            elif -0.05 <= pct_change < -0.02:   label = "Down"
            else:                               label = "Strong Down" 
            raise FileExistsError 
        
        # --- 3. 获取 Lookback 和 Future 价格序列 ---
        # Lookback Price List: [T-Window ... T]
        lookback_prices_objs = result_list[t_index - lookback_window : t_index + 1]
        lookback_prices = [item['close'] for item in lookback_prices_objs]
        
        # Future Price List: [T+1 ... T+Horizon]
        future_prices = [item['close'] for item in result_list[t_index + 1 : t_index + prediction_horizon + 1]]

        # --- 4. 收集 Lookback Window 内的所有事件 ---
        forecasting_cut_off_date_in_price = lookback_prices_objs[0]['date'] 
        
        # 因为周末没有价格，这里是为了涵盖节假日的事件  
        start_trading_date_event = lookback_prices_objs[-lookback_window]['date'] # Event 窗口第一天
        end_trading_date = lookback_prices_objs[-1]['date']  # 窗口最后一天 (即 cut_off_date)

        # 生成连续的日历日期范围 (包含周末、节假日)
        # 例如：如果是 周五 到 下周一，这里会生成 [周五, 周六, 周日, 周一]
        calendar_date_range = pd.date_range(start=start_trading_date_event, \
                            end=end_trading_date).strftime('%Y-%m-%d').tolist()
        
        pool_positive = []
        pool_negative = []
        pool_neutral = [] 
        
        # 使用 calendar_date_range 进行遍历，而不是 target_dates_strs
        for date_str in calendar_date_range:
            if date_str in validated_events_dict:
                daily_events = validated_events_dict[date_str]
                for evt in daily_events:
                    evt_wrapper = {'date': date_str, 'data': evt}
                    
                    sent = str(evt.get('sentiment', '')).lower()
                    if sent == 'positive':
                        pool_positive.append(evt_wrapper)
                    elif sent == 'negative':
                        pool_negative.append(evt_wrapper)
                    else:
                        pool_neutral.append(evt_wrapper)

        selected_events = pool_positive + pool_negative + pool_neutral
        selected_events.sort(key=lambda x: x['date'])

        event_lists = []
        # loc = 0 
        for idx, item in enumerate(selected_events):
            date = item['date']
            evt_data = item['data']
            desc = evt_data.get('event', evt_data.get('description', ''))
            sent = evt_data.get('sentiment', 'N/A')
            # loc +=1 
            # fmt_str = f"[{loc}] {date}: {desc}"
            fmt_str = f"{date}: {desc}"
            event_lists.append(fmt_str)

        assert end_trading_date == fore_cut_off_date 
        
        return (
            event_lists, 
            label, 
            pct_change, 
            lookback_prices, 
            future_prices, 
            forecasting_cut_off_date_in_price , end_trading_date
        )

    except Exception as e:
        print(f"❌ Error in generating sample for {fore_cut_off_date}: {e}")
        raise ValueError(f"❌ Error in generating sample for {fore_cut_off_date}: {e}")

def data_loader(args):
    print(f"--- Configuration ---")
    print(f"Ticker     : {args.ticker}")
    print(f"Start Date : {args.start_date}")
    print(f"End Date   : {args.end_date}")
    print(f"Workers    : {args.workers}")
    
    if not args.ticker:
        print("❌ Error: Ticker is required!")
        sys.exit(1)

    print(f"📡 Fetching data for {args.ticker}...")
    df = domain_info.get_time_series(args.ticker , data_save_base = DATA_BASE_PATH , hori='soho')

    assert df is not None 
    
    df['date_dt'] = pd.to_datetime(df['date'])
    start_ts = pd.to_datetime(args.start_date) if args.start_date else df['date_dt'].min()
    end_ts = pd.to_datetime(args.end_date) if args.end_date else df['date_dt'].max()
    
    mask = (df['date_dt'] >= start_ts) & (df['date_dt'] <= end_ts)
    filtered_df = df.loc[mask].copy()
    filtered_df.sort_values('date_dt', inplace=True)
    
    record_count = len(filtered_df)
    print(f"✅ Price Loaded!")
    print(f"   Time Range: {start_ts.date()} to {end_ts.date()}")
    print(f"   Records   : {record_count}")
    if record_count > 0:
        print("\n--- Head (First 5) ---")
        print(filtered_df[['date', 'close', 'open']].head().to_string(index=False))
        print("\n--- Tail (Last 5) ---")
        print(filtered_df[['date', 'close', 'open']].tail().to_string(index=False))
        result_list = filtered_df[['date', 'close', 'open']].to_dict(orient='records')

    # Load Events 
    validated_events_dict = load_and_filter_events(args)
    
    # Get Company Name
    ticker_to_name , _ = domain_info.get_company_infos()
    try:
        company_name = ticker_to_name[args.ticker]
    except:
        company_name = args.ticker
    
    return result_list , validated_events_dict , company_name 

def convert_event_list_to_str(event_list):
    # Make it a str 
    event_list_str_ids = ''
    for loc in range(len(event_list)):
        event_list_str_ids += f'{loc+1}. {event_list[loc]}'
        if loc != len(event_list) -1 :
            event_list_str_ids += '\n'
    return event_list_str_ids

def convert_memeory_missing_to_str(event_list):
    return '\n§\n'.join(f"{i+1}. {event}" for i, event in enumerate(event_list))

def forecasting(prompt_params , model_name, is_debug = 0 ):
    if WAYS == '3way':
        system_prompt, user_msg = utils.formating_forecast_prompt(
                        prompt_params['company_name'], 
                        prompt_params=prompt_params, 
                        agent='soho_trend_3way_forecast_base'
        )
    elif  WAYS == '5way':
        system_prompt, user_msg = utils.formating_forecast_prompt(
                        prompt_params['company_name'], 
                        prompt_params=prompt_params, 
                        agent='soho_trend_5way_forecast_base'
        )
    if is_debug:
        tee_print(prompt_params['fore_cut_off_date'])
        tee_print('-'*20)
        tee_print(system_prompt)
        tee_print('-'*20)
        tee_print(user_msg)
    
    MAX_RETRIES = 3
    extracted_predictions = None
    task_label=''
    for attempt in range(1, MAX_RETRIES + 1):
        try:    
            forecast_res_from_llm = ''
            if 'claude' in model_name :
                forecast_res_from_llm , _ , _ = utils.query_claude(system_prompt , user_msg ,\
                                                    web_search = False , max_tokens =4096 *2  ,  
                                                    model_name=MODEL_MAP[model_name] ) 
            elif 'gemini' in model_name:
                forecast_res_from_llm , _ , _ = utils.query_gemini(system_prompt , user_msg \
                    , history=None , citations_need = False , web_search=False ,  model_name=MODEL_MAP[model_name])
            
            extracted_predictions = utils.extract_prediction_tag(forecast_res_from_llm)
            if extracted_predictions is not None:
                break
            else:
                raise ValueError("Extraction returned None (Invalid JSON format)")
                
        except Exception as e:
            if attempt < MAX_RETRIES:
                f_resp = utils.smart_print(forecast_res_from_llm)
                wait_time = 2 * attempt  
                warn_msg = f"[{model_name}] Attempt {attempt} failed: {e}. Resp:\n{f_resp}..."
                api_logger.warning(f"Forecast-Agent [{task_label}] {warn_msg}")
                time.sleep(wait_time)
            else:
                error_final_msg = f"‼️ Forecast FATAL: {model_name} failed after {MAX_RETRIES} attempts. Last Err: {e} Failed User Prompt:\n{user_msg}"
                api_logger.warning(f"\033[91m {error_final_msg} \033[0m")
                return 

    if is_debug:
        print("Forecasting Resp:")
        print(forecast_res_from_llm)
        print("Extract:")
        print(extracted_predictions)
        # time.sleep(10000)

    return forecast_res_from_llm , extracted_predictions , user_msg


def event_retrieval(prompt_params  , event_list , model_name , ticker , is_debug = 0 ):

    MAX_RETRIES_REPEATE = 3

    sector, target, memory_list, missing_list , memory_cap , missing_cap =\
                    memory_tool.get_soho_stock_memorys(ticker)
    memory = convert_memeory_missing_to_str(memory_list)
    
    memory_info = f'''[SECTOR]: {sector}
[TARGET]: {target}
[MEMORY]:
{memory}
'''
    
    event_list_str_ids = convert_event_list_to_str(event_list)
    prompt_params['event_list_str_ids'] = event_list_str_ids
    prompt_params['memory_info'] = memory_info

    system_prompt, user_msg = utils.formating_evoluting_prompt(
        prompt_params=prompt_params, 
        agent='event_retrieval'
    )
    
    if is_debug : 
        print('+'*100) 
        print(system_prompt)
        print(user_msg)
        time.sleep(3)

    selected_events_ids = None
    for attempt in range(1, MAX_RETRIES_REPEATE + 1):
        try:    
            forecast_res_from_llm = ''
            if  'claude' in model_name :
                forecast_res_from_llm , _ , _ = utils.query_claude(system_prompt , user_msg ,\
                    model_name=MODEL_MAP[model_name],  web_search = False , max_tokens =4096 *2  ) 
            elif  'gemini' in model_name :
                forecast_res_from_llm , _ , _ = utils.query_gemini(system_prompt , user_msg ,\
                    model_name=MODEL_MAP[model_name] , citations_need = False , web_search=False)
            
            selected_events_ids = memory_tool.extract_single_event_numbers(forecast_res_from_llm)
            if is_debug : 
                print('+'*100) 
                print(forecast_res_from_llm)
                print('Extract:')
                print(selected_events_ids)
                time.sleep(3)
            if selected_events_ids is not None:
                break 
            else:
                continue
        except Exception as e:
            if attempt < MAX_RETRIES_REPEATE:
                api_logger.warning(f"Retrieval-Agent : [{model_name}] Attempt {attempt} failed: {e}.\nRawResp:\n{forecast_res_from_llm}")
                time.sleep(2*attempt)
            else:
                error_final_msg = f"‼️ Retrieval FATAL: {model_name} failed after {MAX_RETRIES_REPEATE} attempts. Last Err: {e} Failed User Prompt:\n{user_msg}"
                print(f"\033[91m {error_final_msg} \033[0m")
                return None 
            
    selected_events= []
    for id_ in selected_events_ids:
        selected_events.append(event_list[id_-1])

    selected_events_for_forecasting = convert_event_list_to_str(selected_events)
    if is_debug:
        print('+'*100) 
        print('Selected_events_for_forecasting:'  )
        print(selected_events_for_forecasting)
        # time.sleep(1000)

    return selected_events_for_forecasting  , event_list_str_ids 

import sys
import time
import re
# 假设 memory_tool, utils, api_logger, MODEL_MAP 等均已在外部导入

def self_improving_retrieval(prompt_params, model_name, ticker, is_debug=0):
    MAX_RETRIES_REPEATE = 3
    
    sector, target, memory_list, missing_list , memory_cap , missing_cap =\
            memory_tool.get_soho_stock_memorys(ticker)

    memory_info = convert_memeory_missing_to_str(memory_list)
    missing_info= convert_memeory_missing_to_str(missing_list)
    prompt_params['sector'] = sector
    prompt_params['memory_info'] = memory_info
    prompt_params['missing_info'] = missing_info

    prompt_params['memory_cap'] = round(memory_cap * 100  , 1 )
    prompt_params['memory_char'] = round(memory_cap  * MEM_CEIL , 1 )
    
    prompt_params['missing_cap'] = round(missing_cap * 100 , 1 )  
    prompt_params['missing_char'] = round(missing_cap  * MISSING_CEIL , 1 )  
    
    # 获取系统级和用户级 Prompt
    system_prompt, user_msg = utils.formating_evoluting_prompt(
        prompt_params=prompt_params, 
        agent='self_improving_retrieval'
    )
    
    if is_debug:
        print('+'*100) 
        print("=== SELF IMPROVING PROMPT ===")
        print(system_prompt)
        print(user_msg)
        time.sleep(3)

    improved_res_from_llm = None
    for attempt in range(1, MAX_RETRIES_REPEATE + 1):
        try:    
            llm_res = ''
            if 'claude' in model_name:
                llm_res, _, _ = utils.query_claude(system_prompt, user_msg,
                    model_name=MODEL_MAP[model_name], web_search=False, max_tokens=4096)
            elif 'gemini' in model_name:
                llm_res, _, _ = utils.query_gemini(system_prompt, user_msg,
                    model_name=MODEL_MAP[model_name], citations_need=False, web_search=False)
            
            improved_res_from_llm = llm_res
            
            if is_debug:
                print('+'*100) 
                print("=== IMPROVED LLM RESPONSE ===")
                print(improved_res_from_llm)
                
            if improved_res_from_llm:
                break 
        except Exception as e:
            if attempt < MAX_RETRIES_REPEATE:
                api_logger.warning(f"Self-Improving-Agent: [{model_name}] Attempt {attempt} failed: {e}")
                time.sleep(2 * attempt)
            else:
                error_final_msg = f"‼️ Improving FATAL: {model_name} failed after {MAX_RETRIES_REPEATE} attempts. Last Err: {e}"
                print(f"\033[91m {error_final_msg} \033[0m")
                return False 

    memory_suggestion, delete_suggestion, missing_suggestion =\
             memory_tool.extract_suggestion_from_llm_feedback(improved_res_from_llm)
        
    if is_debug:
        print(memory_suggestion)
        print(delete_suggestion)
        print(missing_suggestion)
            
    if delete_suggestion:
        memory_tool.delete_memory(ticker , delete_suggestion)    
    if memory_suggestion:
        memory_tool.add_memory(ticker , memory_suggestion , sector , model_name)    
    if missing_suggestion:
        memory_tool.add_missing(ticker , missing_suggestion , sector , model_name)
        
    # time.sleep(30000)

def run_single_date_prediction( fore_cut_off_date , args , price_list \
        , validated_events_dict , company_name , lookback_window ,prediction_horizon , api_logger):
    
    assert WAYS in ['3way' , '5way']
    
    alpha = args.alpha
    model_name = args.pred_model_name
    model_save_dir = os.path.join(OUTPUT_SAVE_DIR + f"_{lookback_window}_{prediction_horizon}_trend_{WAYS}", f"{model_name}_{alpha}")
    os.makedirs(model_save_dir, exist_ok=True)
    
    if io_manager.is_prediction_exist(args.ticker , fore_cut_off_date , "tsf" , base_dir=model_save_dir):
        print(f"⏩ {fore_cut_off_date} already exists. Skipping.")
        return f'Skip  {fore_cut_off_date}. Already Exists.'
        
    event_lists, trend_desc , pct_change,\
        lookback_prices,future_prices, start_trading_date , end_trading_date = generate_prediction_sample(
            fore_cut_off_date,    lookback_window,     prediction_horizon,   
            price_list,   validated_events_dict
        )
    
    his_prices = ", ".join([f"{p:.1f}" for p in lookback_prices])
        
    if event_lists is None : 
        raise ValueError('Events do not exist!')

    # ####################################
    # 1) Local Retieval Based on memeory 
    prompt_params={
        'company_name': company_name , 
        'fore_cut_off_date' : fore_cut_off_date, 
        'start_trading_date':start_trading_date, 
        'end_trading_date' : end_trading_date , 
        'his_prices' : his_prices , 
        'prediction_horizon' : prediction_horizon
    } 
    retrieval_event_strings , event_list_pool = event_retrieval( prompt_params  ,\
                     event_lists , model_name , args.ticker , is_debug = 0 )

    # ####################################
    # 2) Forecasting 
    prompt_params={
        'company_name': company_name , 
        'fore_cut_off_date' : fore_cut_off_date, 
        'start_trading_date':start_trading_date, 
        'end_trading_date' : end_trading_date , 
        'event_strings' : retrieval_event_strings , 
        'his_prices' : his_prices , 
        'prediction_horizon' : prediction_horizon
    } 
    
    forecast_res_from_llm , extracted_predictions , user_msg =\
          forecasting(prompt_params , model_name=model_name,  is_debug=0)

    # ####################################
    # 3) Improving both Retrieval and Environment 
    prompt_params={
        'company_name' : company_name , 
        'event_list_pool' : event_list_pool , 
        'fore_cut_off_date' : fore_cut_off_date, 
        'prediction_horizon' : prediction_horizon , 
        'start_trading_date':start_trading_date, 
        'his_prices' : his_prices , 
        'event_list_selected': retrieval_event_strings , 
        'label': trend_desc  , 
        'llm_forecasting_resp': forecast_res_from_llm
    }
    try:
        self_improving_retrieval(prompt_params , model_name, args.ticker,  is_debug= 0 )
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"提取到的异常信息是：\n{error_trace}")
        time.sleep(1000)
    # ####################################

    if extracted_predictions is not None:
        prediction_record = {
            "fore_cut_off_date": fore_cut_off_date,
            "user_msg": user_msg , 
            "forecast_res_from_llm": forecast_res_from_llm,
            "extracted_predictions": extracted_predictions,
            "future_prices": future_prices,
            "trend_desc": trend_desc,
            "lookback_prices": lookback_prices
        }
        io_manager.save_prediction_thread_safe(args.ticker, prediction_record, 'tsf' , base_dir= model_save_dir )
            
    return 'good'
    
# --- 4. 启动入口 ---
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Stock Data Backtest Loader")
    parser.add_argument("-t", "--ticker", type=str, required=True, help="Stock ticker symbol (e.g., META)")
    parser.add_argument("-s", "--start_date", type=utils.parse_flexible_date, default=None, 
                        help="Start date (YYYY, YYYY-MM, or YYYY-MM-DD)")
    parser.add_argument("-e", "--end_date", type=utils.parse_flexible_date, default=None, 
                        help="End date (YYYY, YYYY-MM, or YYYY-MM-DD)")
    
    parser.add_argument("-w", "--workers", type=int, default=12, help="Number of parallel threads")
    parser.add_argument("-a", "--alpha", type=str, default='', help="Ratios")

    parser.add_argument("-b", "--lookback", type=int, default=14, help="lookback_window")
    parser.add_argument("-p", "--pred_horizon", type=int, default=3, help="prediction_horizon")

    parser.add_argument("-m", "--pred_model_name", type=str, default='', help="prediction Models")
    
    parser.add_argument("-d", "--dom", type=str, default='other', help="prediction Models")
    parser.add_argument("-y", "--way", type=str, default='3way', help="prediction Models")

    parser.add_argument("-r", "--repeat", type=str, default='', choices=['' , 'v0' , 'v1' , 'v2'] , 
                                 help="This is to help replicate the experiments.")
    
    args = parser.parse_args()  
    
    WAYS = args.way 

    if args.dom =='stock':
        if  args.repeat != '':
            OUTPUT_SAVE_DIR=f'seer/result/stock-soho-{args.repeat}/pred'
        else:
            OUTPUT_SAVE_DIR=f'seer/result/stock-soho/pred'
    else:
        OUTPUT_SAVE_DIR='seer/result/market/pred'

    match = re.search(r'r(\d+)', args.alpha )
    ROUND = 2 
    GAP_DAY = 2
    
    api_logger = utils.setup_custom_logger('stock_pred_api', f'seer/logs/price_predict_err.log')
    
    price_list , validated_events_dict , company_name  = data_loader(args)
    lookback_window = args.lookback
    prediction_horizon = args.pred_horizon
    
    # 4. 生成日期列表，间隔为 GAP_DAY
    if args.start_date and args.end_date:
        date_range = pd.date_range(start=args.start_date, end=args.end_date, freq=f'{GAP_DAY}D')
        print(f'Total Forecasting Days :  {len(date_range)}')
        target_dates = date_range.strftime('%Y-%m-%d').tolist()
    else:
        print("❌ Start/End date required for parallel run.") ; sys.exit(1)

    print(f"🚀 Starting Parallel Prediction: {len(target_dates)} dates | {args.workers} workers | Gap: {GAP_DAY}d")

    count = 0   

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        worker_func = partial(
            run_single_date_prediction,
            args=args,
            price_list=price_list,
            validated_events_dict=validated_events_dict,
            company_name=company_name,
            lookback_window=lookback_window,
            prediction_horizon=prediction_horizon,
            api_logger=api_logger
        )
        future_to_date = {executor.submit(worker_func, date): date for date in target_dates}
        for future in concurrent.futures.as_completed(future_to_date):
            date = future_to_date[future]
            try:
                result = future.result()
                if result == 'good':
                    count +=1 
            except Exception as exc:
                full_traceback = traceback.format_exc()
                if 'Not enough boundaries' not in full_traceback and 'Reason:' not in full_traceback:
                    api_logger.error(f"Critical failure {date}: {exc}\nTraceback details:\n{full_traceback}")

    print("🎉 All predictions completed." , count)
    