# python -m seer.scripts.run_gemini
import os
import json
from seer.backend.backend_gemini import query as gemini_query
from seer.backend.backend_antropic_vertax import query as claude_query
from seer.events_search import domain_info 
from seer.utils import prompt, utils 
import numpy as np 

DATA_PATH='/usr/local/google/home/mingtiant/Documents/forecast_agent/nexus/seer/data/'
ERR_LOG_DIR='seer/err_log.txt'
TEST_RESP=''''''
    
def save_list_to_json(data_list, file_path):
    try:
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, indent=4, ensure_ascii=False)
        print(f"✅ Success: Data saved to {file_path}")
    except Exception as e:
        print(f"❌ Failed to save JSON: {e}")
def load_json_to_list(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)
    
    
def query_gemini(sys_msg , user_msg , history=None , citations_need = False):
    result = gemini_query(
        system_message=sys_msg,
        user_message=user_msg,
        citations_need=citations_need,
        history_messages=history,
        model="gemini-3-pro-preview", 
        temperature=0.7,         
        max_output_tokens=None,
    )
    # print("\n--- Responses From Model ---")
    # if result["response_with_citations"]:
    #     print(result["response_with_citations"])
    # else : 
    #     print(result["response_text"])
        
    # if result["citations"]:
    #     print("\n--- Citations ---")
    #     print(result["citations"])

    # print("\n--- Statistic ---")
    # print(f"Model: {result['model']}")
    # print(f"Input  Token: {result['input_tokens']}")
    # print(f"Output Token: {result['output_tokens']}")
    # print(f"TimeCost: {result['request_time']:.2f} 秒")
    return result["response_text"] , result["response_with_citations"] , result['citations']
def query_claude(sys_msg , user_msg ):
    response = claude_query(
        system_message=sys_msg,
        user_message=user_msg,
        model='claude-sonnet-4-5',
        max_tokens=2048,
        temperature=0.7,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 5
        }]
    )
    # 4. Display Results
    # print("\n[AI Response]:")
    # print(response["response_text"])
    
    # print("\n" + "="*30)
    # print(f"Request Time: {response['request_time']:.2f}s")
    # print(f"Input Tokens: {response['input_tokens']}")
    # print(f"Output Tokens: {response['output_tokens']}")
    # print(f"Stop Reason:  {response['stop_reason']}")
    # print("="*30) 
    
    return response["response_text"] , None  , response['citations'] 
    
import os
import pandas as pd
import numpy as np

def list_search_agent_events():
    # model_name = 'claude'
    model_name = 'gemini'
    
    print(f"Analyzing extraction results for model: {model_name}")
    # META NVDA GOOGL
    ticker = 'META'
    event_save_path = f'{DATA_PATH}/stock/events/{ticker}'

    # 假设你已经定义了这些工具函数和数据
    # ticker_to_name, ticker_to_company_info = domain_info.get_company_infos()
    # company_name = ticker_to_name[ticker]

    start_date = "2025-11-10"
    end_date = "2025-12-01"
    date_list = pd.date_range(start=start_date, end=end_date).strftime('%Y-%m-%d').tolist()

    # 初始化统计字典
    # 结构：{ round_index: { 'total_events': [], 'gemini_true': [], 'claude_true': [], 'both_true': [] } }
    stats = {
        r: {'total': [], 'new': [], 'gemini': [], 'claude': [], 'both': [] } for r in range(3)
    }

    for cut_off_time in date_list:
        # 检查最终轮文件是否存在
        date_events_file = f'{event_save_path}/{model_name}-{cut_off_time}-3.json'
        if not os.path.exists(date_events_file): 
            print(f"Skipping missed date: {cut_off_time}")
            continue
        
        for r in range(3):
            round_file_save_path = f'{event_save_path}/{model_name}-{cut_off_time}-{r+1}.json'
            
            if os.path.exists(round_file_save_path):
                events_pool = load_json_to_list(round_file_save_path)
                
                # 初始化当前文件的计数
                g_count = 0
                c_count = 0
                b_count = 0
                
                for event in events_pool:
                    # 安全获取 factual_status，防止 key 不存在
                    g_status = event.get('factual_check_gemini', {}).get('factual_status', False)
                    c_status = event.get('factual_check_claude', {}).get('factual_status', False)
                    
                    if g_status is None : 
                        g_status = c_status
                    if c_status is None :
                        c_status = g_status
                    
                    if g_status: g_count += 1
                    if c_status: c_count += 1
                    if g_status and c_status: b_count += 1
                
                # 记录该日期该轮次的数据
                stats[r]['total'].append(len(events_pool))
                stats[r]['gemini'].append(g_count)
                stats[r]['claude'].append(c_count)
                stats[r]['both'].append(b_count)
    
    # 打印统计结果表格
    print("\n" + ticker+"="*76)
    print(f"{'Round':<7} | {'Avg Events':<12} | {'New Events':<12} | {'Gemini True':<12} | {'Claude True':<12} | {'Both True':<10}")
    print("-" * 80)

    last_r = None 
    for r in range(3):
        avg_total = np.mean(stats[r]['total']) if stats[r]['total'] else 0
        avg_gemini = np.mean(stats[r]['gemini']) if stats[r]['gemini'] else 0
        avg_claude = np.mean(stats[r]['claude']) if stats[r]['claude'] else 0
        avg_both = np.mean(stats[r]['both']) if stats[r]['both'] else 0
        if last_r : 
            add_ = avg_total - last_r
        else:
            add_ = 0

        last_r = avg_total
            
        print(f"Round {r+1:<2} | {avg_total:<12.2f} | +{add_:<12.2f}| {avg_gemini:<12.2f} | {avg_claude:<12.2f} | {avg_both:<10.2f}")
    print("="*80 + "\n")

    return stats

def extract_covariates(factors_from_this_round):
    covariates = re.findall(r'<covariate>(.*?)</covariate>', factors_from_this_round, flags=re.S)
    return covariates
    
import pandas as pd
import re 

def read_print_each_day_covariates_tree():
    # model_name = 'claude'
    model_name = 'gemini'
    ticker = 'META'
        
    ticker_to_name , ticker_to_company_info = domain_info.get_company_infos()
    # dates_prices = domain_info.get_time_series(ticker)
    
    company_name = ticker_to_name[ticker]
    event_save_path = f'seer/event-driven-time-series/stock/events/{ticker}'
    
    start_date =  "2025-12-01"
    end_date = "2025-12-01"
    date_list = pd.date_range(start=start_date, end=end_date).strftime('%Y-%m-%d').tolist()
    list_of_covariates = 'N/A'
    
    round_file_save_path='{DATA_PATH}/stock/events/NVDA/gemini-2025-12-01-covariates.json'
    round_file_save_path='{DATA_PATH}/stock/events/GOOGL/gemini-2025-12-01-covariates.json'
    covariates_pool = load_json_to_list(round_file_save_path ) 
    utils.plot_covariates_distribution(covariates_pool, 'GOOGL')
    exit()
    
    covariates_pool = {}
    data_list = []
    for j in range(len(date_list)):
        cut_off_time = date_list[j]

        round_file_save_path=f'{event_save_path}/{model_name}-{cut_off_time}-covariates.json'
        
        covariates_pool = load_json_to_list(round_file_save_path)    
        print(len(covariates_pool))
        data_list.append(len(covariates_pool))
        utils.format_print_covariates(covariates_pool)

def read_final_day_covs_tree():
    # round_file_save_path='{DATA_PATH}/stock/events/NVDA/gemini-2025-12-01-covariates.json'
    round_file_save_path='{DATA_PATH}/stock/events/GOOGL/gemini-2025-12-01-covariates.json'
    # round_file_save_path='{DATA_PATH}/stock/events/META/gemini-2025-12-01-covariates.json'
    covariates_pool = load_json_to_list(round_file_save_path) 
    company_name = round_file_save_path.split('/')[-2]
    print('company_name' , company_name)
    # utils.plot_covariates_distribution(covariates_pool, company_name)
    print('*'*20 + company_name +'*'*20)
    utils.format_print_covariates(covariates_pool)
    
def get_exists_covariates_names(round_file_save_path='', events_thr=None):
    model_name = 'gemini'
    ticker = 'META'
    cut_off_time = "2025-12-01"
    event_save_path = f'seer/event-driven-time-series/stock/events/{ticker}'
    round_file_save_path=f'{event_save_path}/{model_name}-{cut_off_time}-covariates.json'
    covariates_pool = load_json_to_list(round_file_save_path)   
    covariates = utils.get_exist_covariates_list(covariates_pool , events_thr = events_thr)
    list_of_covariates = "\n".join(covariates)
    # print(list_of_covariates)
    return list_of_covariates , covariates
    
def run_stock_covs(model_name=''):
    # model_name = 'claude'
    model_name = 'gemini'
    # META NVDA GOOGL
    ticker = 'GOOGL'
    
    ticker_to_name , ticker_to_company_info = domain_info.get_company_infos()
    # dates_prices = domain_info.get_time_series(ticker)
    
    company_name = ticker_to_name[ticker]
    event_save_path = f'seer/event-driven-time-series/stock/events/{ticker}'
    
    start_date =  "2025-11-10"
    end_date = "2025-12-01"
    date_list = pd.date_range(start=start_date, end=end_date).strftime('%Y-%m-%d').tolist()
    
    list_of_covariates = 'N/A'
    domain_covariates = []

    # if ticker != 'META':
        # list_of_covariates , domain_covariates = get_exists_covariates_names(events_thr=5)
    
    list_of_covariates = utils.get_ref_from_initiled_taxonomy()
    # print(list_of_covariates)
    # exit()
    # factors_from_this_round='''
    # 1. <covariate>INSIDER_TRADING</covariate>
    # 11. <covariate>INVESTOR_SENTIMENT</covariate>
    # '''
    # covariates = extract_covariates(factors_from_this_round)
    # list_of_covariates = "\n".join(covariates)

    covariates_pool = {}
    date_processed = []
    for j in range(len(date_list)):
        cut_off_time = date_list[j]
        date_processed.append(cut_off_time)

        date_events_file = f'{event_save_path}/{model_name}-{cut_off_time}-3.json'
        if not os.path.exists(date_events_file): 
            print(f"Skipping missed date: {cut_off_time}")
            continue

        events_pool = load_json_to_list(date_events_file)
        
        events_lists , effective_events ,  effective_dates = utils.get_events_for_covariates(events_pool, model_name='gemini' , cut_off_time=cut_off_time)
        system_prompt , user_msg = utils.formating_prompt(
                                company_name,
                                prompt_params={
                                        'cut_off_time':cut_off_time , 
                                        "events_lists":events_lists,
                                        'list_of_covariates': list_of_covariates,
                                        'num_of_events': len(effective_events),
                                },
                                agent='covariates_cluster'
        )
        
        # print(system_prompt)
        print('='*80)
        print(user_msg)
        print('='*80)
        exit()
        
        if model_name == 'claude':
            factors_from_this_round , _ , _ = query_claude(system_prompt , user_msg ) 
        elif model_name == 'gemini':
            factors_from_this_round , _ , _ = query_gemini(system_prompt , user_msg , history=None , citations_need = False)
        print(factors_from_this_round)

        covariates = re.findall(r'<covariate>(.*?)</covariate>', factors_from_this_round, flags=re.S)
        assert len(covariates) == len(effective_events) ==  len(effective_dates)
        
        for covs , event , date_val in zip(covariates,effective_events , effective_dates ):
            if covs in covariates_pool:
                if date_val not in covariates_pool[covs]:
                    covariates_pool[covs][date_val] = [event]
                else:
                    covariates_pool[covs][date_val].append(event)
            else:
                covariates_pool[covs] = {
                    date_val:[event]
                }
        
        cur_covariates_cates = list(covariates_pool.keys()) + domain_covariates
        cur_covariates_cates = list(set(cur_covariates_cates))
        list_of_covariates = "\n".join(cur_covariates_cates)
        
        round_file_save_path=f'{event_save_path}/{model_name}-{cut_off_time}-covariates.json'
        
        utils.format_print_covariates(covariates_pool , domain_covariates = domain_covariates)
        save_list_to_json(covariates_pool, round_file_save_path)

def plot_from_META_covs():
    def get_stats_dict(covariates_pool):
        """辅助函数：将原始 pool 转换为 {category: total_count} 的字典"""
        stats_dict = {}
        for cat, dates in covariates_pool.items():
            total_events = sum(len(evs) for evs in dates.values())
            stats_dict[cat] = total_events
        return stats_dict

    # 1. 定义文件路径
    files = {
        'META': '{DATA_PATH}/stock/events/META/gemini-2025-12-01-covariates.json',
        'NVDA': '{DATA_PATH}/stock/events/NVDA/gemini-2025-12-01-covariates.json',
        'GOOGL': '{DATA_PATH}/stock/events/GOOGL/gemini-2025-12-01-covariates.json'
    }

    # 2. 处理第一个文件 (META) 作为基准
    with open(files['META'], 'r') as f:
        meta_pool = json.load(f)
    
    meta_stats = get_stats_dict(meta_pool)
    
    # 核心：过滤 > 5 并排序，确定唯一的基准顺序
    reference_categories = [
        cat for cat, count in sorted(meta_stats.items(), key=lambda x: x[1], reverse=True)
        if count > 5
    ]
    
    print(f"✅ 基准已确立，共 {len(reference_categories)} 个类别 (Events > 5)")

    # 3. 遍历所有公司（包括第一个），按照基准顺序生成数据
    for company, path in files.items():
        with open(path, 'r') as f:
            current_pool = json.load(f)
        
        current_stats_dict = get_stats_dict(current_pool)
        
        # 按照基准列表对齐数据
        aligned_stats_list = []
        for cat in reference_categories:
            # 如果当前公司没有这个类，给 0
            count = current_stats_dict.get(cat, 0)
            aligned_stats_list.append({'category': cat, 'total_events': count})

        # 绘图（此时 aligned_stats_list 的顺序已经和 reference_categories 一致了）
        utils.draw_bar_chart_with_fixed_covariates(aligned_stats_list, company, is_reference=False)
        
def analyze_covariates_overlap():
    # 1. Define file paths
    paths = {
        'META': f'{DATA_PATH}/stock/events/META/gemini-2025-12-01-covariates.json',
        'NVDA': f'{DATA_PATH}/stock/events/NVDA/gemini-2025-12-01-covariates.json',
        'GOOGL': f'{DATA_PATH}/stock/events/GOOGL/gemini-2025-12-01-covariates.json'
    }
    # 2. Load data and extract keys into sets
    sets = {}
    for name, path in paths.items():
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                sets[name] = set(data.keys())
        except FileNotFoundError:
            print(f"Error: File not found at {path}")
            return
        except Exception as e:
            print(f"Error loading {name}: {e}")
            return

    s1, s2, s3 = sets['META'], sets['NVDA'], sets['GOOGL']
    union_set = s1 | s2 | s3
    master_covariates_list = sorted(list(set(union_set)))
    print(master_covariates_list)
    print(len(master_covariates_list))

    # 3. Calculate metrics
    # Common to all three
    common_all = sorted(list(s1 & s2 & s3))

    # Unique to each company
    unique_meta = sorted(list(s1 - s2 - s3))
    unique_nvda = sorted(list(s2 - s1 - s3))
    unique_googl = sorted(list(s3 - s1 - s2))

    # 4. Print Results
    print("=" * 60)
    print("      📊 COVARIATES OVERLAP ANALYSIS REPORT")
    print("=" * 60)

    # Section 1: Total Counts
    print("\n[SECTION 1: TOTAL COVARIATE COUNTS]")
    print("-" * 40)
    for name, key_set in sets.items():
        print(f"🔹 {name:<6}: {len(key_set)} total covariates")

    # Section 2: Shared Covariates
    print(f"\n[SECTION 2: SHARED BY ALL THREE COMPANIES ({len(common_all)})]")
    print("-" * 40)
    if common_all:
        print(" | ".join(common_all))
        # for item in common_all:
            # print(f" • {item}")
    else:
        print(" (No common categories found across all three)")

    # Section 3: Unique Covariates
    # print("\n[SECTION 3: UNIQUE COVARIATES (EXCLUSIVELY IN ONE FILE)]")

    unique_data = [
        ('META', unique_meta),
        ('NVDA', unique_nvda),
        ('GOOGL', unique_googl)
    ]

    for company, items in unique_data:
        print(f"📍 UNIQUE TO {company} ({len(items)}):")
        print("-" * 25)
        if items:
            print(" | ".join(items))
        else:
            print(" (None)")

    # Section 4: Pairwise Overlaps (Exclude those in all three)
    print("\n[SECTION 4: PAIRWISE OVERLAP (EXCLUDING TRIPLE-SHARED)]")
    print("-" * 40)
    print(f"🤝 META & NVDA only  : {len((s1 & s2) - set(common_all))}")
    print(f"🤝 META & GOOGL only : {len((s1 & s3) - set(common_all))}")
    print(f"🤝 NVDA & GOOGL only : {len((s2 & s3) - set(common_all))}")
    print("=" * 60)

def init_merge_covariates():
    utils.get_init_master_taxonomy()
    
if __name__ == "__main__":  
    run_stock_covs()
    # analyze_covariates_overlap()
    # plot_from_META_covs()
    # read_final_day_covs_tree()
    # init_merge_covariates()
    # list_search_agent_events()
    # get_exists_covariates_names()
    
'''
    
    python -m seer.events_search.covariates_agent
    
'''


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


