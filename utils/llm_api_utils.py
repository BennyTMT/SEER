from seer.utils import utils
import time 
import concurrent.futures
from copy import deepcopy

def fact_check_agent_parallelize(
                search_target , factors_extracted , model_name='', api_logger=None , prompt_domain=None  ):

    def process_single_task(search_target, item, model_name):# -> tuple[Any | Literal['gemini', 'claude'], dict[str, Any]]:
        """
        Handles a single API request for a specific item and model.
        """
        prompt_params= {
            'description':item['description'],
            'date':item['date'], 
            'entity':search_target
        }

        if not prompt_domain or 'stock' in prompt_domain:
            fact_check_prompt='factual_market'
        elif 'taxi' in prompt_domain or 'elec' in prompt_domain:
            fact_check_prompt='factual_generic'
        
        system_prompt, user_msg = utils.formating_search_prompt(\
                    search_target, prompt_params=prompt_params, agent=fact_check_prompt)
        
        # print(system_prompt)
        # print(user_msg)
        # time.sleep(100000)

        MAX_RETRIES = 10
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response_text = '' 
                if  'gemini' in model_name:
                    response_text, response_with_citations, citations = \
                        utils.query_gemini(system_prompt, user_msg, history= \
                            None, citations_need=True ,web_search = True)
                elif model_name == 'claude':
                    response_text, response_with_citations, citations = \
                            utils.query_claude(system_prompt, user_msg)
                            
                factual_status, date_val = utils.extract_tag_data(response_text)
                
                assert factual_status is not None 
                assert date_val is not None 
                
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
                    print(f'[{model_name}] waitting for {wait_time} sec!')
                    time.sleep(wait_time)
                else:
                    content = f"‼️ {MAX_RETRIES} Times Attempts, Killed the process! "
                    api_logger.error(f"[Fack-Check: {content} || {search_target}] [{model_name}]")
                    
                    return model_name, None 
                            
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        # Create a list of future tasks
        future_to_item = {}
        
        for item in factors_extracted:
            # for model_name in ['gemini_0', 'gemini_1', 'claude']:
            for model_name in ['gemini',  'claude']:
                # Submit task to the thread pool
                future = executor.submit(process_single_task, search_target, item, model_name)
                # Store the future with a reference to the item it's updating
                future_to_item[future] = item

        # As tasks complete, update the original items
        for future in concurrent.futures.as_completed(future_to_item):
            item = future_to_item[future]
            model_name, result = future.result()
            # Thread-safe update of the item dictionary
            if result is not None : 
                item[f'factual_check_{model_name}'] = result
            else:
                print('API Call is quit busy! or you have no credits')
                exit()
            
    return factors_extracted    


import os
import concurrent.futures
from functools import partial

def process_single_day(
                        cut_off_date, model_name, entity_name ,
                        prompt_domain, event_save_path, num_rounds , api_logger , question_desc=None
                       ):
    
    """处理单个日期的搜索和事实核查"""
    # 1. 检查最终结果是否已存在
    final_file = f'{event_save_path}/{model_name}-{cut_off_date}-{num_rounds}.json'
    
    if os.path.exists(final_file):
        return f"✅ {cut_off_date} already completed."
        
    print(f"🚀 Starting {model_name} for {cut_off_date} [{prompt_domain}]")
    events_pool = None 
        
    for r in range(num_rounds):
        
        round_file_save_path = f'{event_save_path}/{model_name}-{cut_off_date}-{r+1}.json'
        
        if os.path.exists(round_file_save_path):
            events_pool = utils.load_json_to_list(round_file_save_path)
            continue 
            
        ##########################################   
        # (1) Search Agent  
        ##########################################    
        if events_pool :
            events_lists , _ = utils.get_events_for_search(
                                        events_pool , 
                                        cut_off_date=cut_off_date
            )

        else:
            events_lists = None 
            
        if prompt_domain == 'economic_forecast_search' or prompt_domain == 'political_forecast_search' :
            
            assert question_desc is not None 
            
            system_prompt , user_msg = utils.formating_prompt(
                                    '',
                                    prompt_params={
                                            'target_event':question_desc , 
                                            "cut_off_date":cut_off_date,
                                            'events_lists':events_lists,
                                    },
                                    agent=prompt_domain
            )
            
        elif prompt_domain in ['stock_events_search' , 'commodities_event_search' , 'crypto_event_search' , 'weather_event_search']:
            
            system_prompt, user_msg = utils.formating_search_prompt(
                    entity_name ,
                    prompt_params={
                        'cut_off_date': cut_off_date,
                        "events_lists": events_lists,
                        'entity':entity_name
                    },
                    agent=prompt_domain
            )

        # print('system_prompt', '-------------------')
        # print(system_prompt)
        # print("--- Sending Requests.... --- Round " , r +1 , 'User Prompt:' )
        # print(user_msg)
        # print('-------------------------------------')
        # time.sleep(10000)
        
        MAX_RETRIES = 3
        factors_extracted = None
        task_label = f"{entity_name} | {cut_off_date} | R{r+1}"
        for attempt in range(1, MAX_RETRIES + 1):
            try:    
                factors_from_this_round = ''
                if model_name == 'claude':
                    factors_from_this_round , _ , _ = utils.query_claude(system_prompt , user_msg ) 
                    raise ValueError('Not Claude Yet!!!')
                elif model_name == 'gemini':
                    factors_from_this_round , _ , _ = utils.query_gemini(system_prompt , user_msg \
                        , history=None , citations_need = False , web_search=True)
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
        
        checked_facts = fact_check_agent_parallelize(entity_name,\
                            factors_extracted , model_name=model_name , api_logger=api_logger)
                        
        if events_pool is None : events_pool = checked_facts
        else: events_pool += checked_facts
            
        assert events_pool is not None 

        print(round_file_save_path , ' has done!!!')
        # utils.print_events_lists_from_pool(events_pool , r)
        utils.save_list_to_json(events_pool, round_file_save_path)

    return f"🏁 {cut_off_date} execution finished."


import os
import concurrent.futures
from functools import partial
import time

def process_multi_days(
                        start_date, end_date, model_name, entity_name,
                        prompt_domain, event_save_path, num_rounds, api_logger, question_desc=None
                       ):
    
    """处理日期范围（多天）的搜索和事实核查"""
    
    # 使用日期范围作为文件名标识
    date_range_label = f"{start_date}_to_{end_date}"
    
    # 1. 检查最终结果是否已存在
    final_file = f'{event_save_path}/{model_name}-{date_range_label}-{num_rounds}.json'
    
    if os.path.exists(final_file):
        return f"✅ {date_range_label} already completed."
        
    print(f"🚀 Starting {model_name} for {date_range_label} [{prompt_domain}]")
    events_pool = None 
        
    for r in range(num_rounds):
        
        round_file_save_path = f'{event_save_path}/{model_name}-{date_range_label}-{r+1}.json'
        
        if os.path.exists(round_file_save_path):
            events_pool = utils.load_json_to_list(round_file_save_path)
            continue 
            
        ##########################################   
        # (1) Search Agent 
        ##########################################    
        if events_pool:
            events_lists, _ = utils.get_events_for_search(
                                        events_pool, 
                                        search_range = (start_date,end_date)
            )
        else:
            events_lists = None 
            
        # print(events_lists)
        # ---------------------------------------------------------
        system_prompt, user_msg = utils.formating_search_prompt(
                entity_name,
                prompt_params={
                    'start_date': start_date,
                    'end_date': end_date,
                    "events_lists": events_lists,
                    'entity': entity_name
                },
                agent=prompt_domain
        )
        
        # print('system_prompt', '-------------------')
        # print(system_prompt)
        # print("--- Sending Requests.... --- Round " , r +1 , 'User Prompt:' )
        # print(user_msg)
        # print('-------------------------------------')
        # time.sleep(10000)
        
        MAX_RETRIES = 3
        factors_extracted = None
        task_label = f"{entity_name} | {date_range_label} | R{r+1}"
        for attempt in range(1, MAX_RETRIES + 1):
            try:    
                factors_from_this_round = ''
                if model_name == 'claude':
                    raise ValueError('Not Claude Yet!!!')
                elif model_name == 'gemini':
                    factors_from_this_round , _ , _ = utils.query_gemini(system_prompt , user_msg \
                        , history=None , citations_need = False , web_search=True)
                factors_extracted = utils.extract_json_to_list(factors_from_this_round)
                # print(factors_from_this_round)
                # time.sleep(10000)
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
                    
        ##########################################   
        # (2) Fact-check Agent    
        ########################################## 
        
        checked_facts = fact_check_agent_parallelize(entity_name,\
                            factors_extracted , model_name=model_name , api_logger=api_logger , prompt_domain=prompt_domain)
                        
        if events_pool is None : events_pool = checked_facts
        else: events_pool += checked_facts
            
        assert events_pool is not None 

        print(round_file_save_path , ' has done!!!')
        # utils.print_events_lists_from_pool(events_pool , r)
        utils.save_list_to_json(events_pool, round_file_save_path)

    return f"🏁 {date_range_label} execution finished."
    