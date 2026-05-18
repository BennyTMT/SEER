# python -m seer.scripts.run_gemini
import os
import json
from urllib import response
from seer.backend.backend_gemini import query as gemini_query
from seer.backend.backend_antropic_vertax import query as claude_query
from seer.events_search import domain_info , utils
import pandas as pd
import numpy as np
from seer.utils import prompt
    
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
    return response["response_text"] , None  , response['citations'] 
    
import pandas as pd
def run_human_expert_retriever(model_name=''):
    # model_name = 'claude'
    model_name = 'gemini'
    # META NVDA GOOGL
    ticker = 'META'
        
    ticker_to_name , ticker_to_company_info = domain_info.get_company_infos()
    dates_prices = domain_info.get_time_series(ticker)
    
    company_name = ticker_to_name[ticker]
    
    start_date = "2025-11-10"
    end_date = "2025-12-01"
    date_list = pd.date_range(start=start_date, end=end_date).strftime('%Y-%m-%d').tolist()
    
    system_prompt , user_msg = utils.formating_prompt(
                                        company_name,
                                        prompt_params={
                                                'start_date':start_date , 
                                                "end_date":end_date
                                        },
                                        agent='human_expert_retriever'
                )
    print(system_prompt)
    print('---')
    print(user_msg)
    print('---')
    if model_name == 'claude':
        factors_from_this_round , _ , _ = query_claude(system_prompt , user_msg ) 
    elif model_name == 'gemini':
        factors_from_this_round ,response_with_citations , citations =\
            query_gemini(system_prompt , user_msg , history=None , citations_need = True)
    
    print('response:')
    print('+'*50)
    # print('', factors_from_this_round)
    print('', response_with_citations)
    print('+'*50)
    print('', citations)
    
if __name__ == "__main__":  
    run_human_expert_retriever()
    
'''

    python -m seer.events_search.human_expert_retriever

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

'''

"2025-11-15" - "2025-11-25"   (10 days)

Daily average of events per round.
Gemini is the search agent, Claude and Gemini is Fact-check Agent 
================================================================================
Round   | Avg Events   | Gemini True  | Claude True  | Both True  | New Events
--------------------------------------------------------------------------------
Round 1  | 3.91         | 3.91         | 3.27         | 3.27      |     NA
Round 2  | 7.00         | 6.82         | 5.36         | 5.27      |    +3.09
Round 3  | 10.45        | 9.82         | 7.18         | 7.00      |    +3.45
================================================================================


Daily average of events per round.
Claude is the search agent, Claude and Gemini is Fact-check Agent 
================================================================================
Round   | Avg Events   | Gemini True  | Claude True  | Both True   | New Events
--------------------------------------------------------------------------------
Round 1  | 4.27         | 3.91         | 3.27         | 3.09       |    NA
Round 2  | 4.64         | 4.27         | 3.64         | 3.45       |   +0.37
Round 3  | 5.27         | 4.82         | 4.18         | 4.00       |   +0.63
================================================================================

'''


'''
    
 [{'id': '1', 'domain': 'stockanalysis.com', 'title': 'stockanalysis.com', 'uri': 'https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHD6YNEQvoAVLpsgQs3XcOS8E1VgGtAF9YLqSDG0kI2VsVyNyhO_xVqgfc4zDt-9GrSJ4TbNRzY54BgI_I8vjgHU4Jx0hhFDO7_VU0bI-BLgg33AvWsMiB6XJrBv6agFSXM5e_-yrb21R_s'}, {'id': '2', 'domain': 'phemex.com', 'title': 'phemex.com', 'uri': 'https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGJPVXGnmtvSqe7B4MlOAi2U6QtyLZgg8U3m2K4RPaCp-6j2-tasLysanhbAyJn4AYqTnVGDmxxJrk5eXRZStUdU72w41wpbEqic6LuT1rjgZhYnR_dpdBwbmvpEpRKlfIN88LT7-VWIVQzB147YaU2vb_gUaJytD4QzLL7ohcwlki98ryOulOprdRCehE8_9Xe6PaMw=='}, {'id': '3', 'domain': 'ig.com', 'title': 'ig.com', 'uri': 'https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETRCtfOEQpVdcBmaR16XR-TVlGpgB_eUCx9JHmt6dzGAiHoAIsVKOhCvEZ4u5HxSQbUqzNi0AILcV_tbEj5UBR_oJOD6PVmRT0SYHmOYv2tazhsbHf1m3bEeUipAX93Ck_cyhSNaY2e0t-BoJur_yq0pHvlGsgbfsCQA3FxfWtst-sk7MqNcTNBSzPp7Eo0hdYYCgM4zGg_VAP6ZLPDcHjKNoXKGEIOpBf7dFqHw=='}, {'id': '4', 'domain': 'seekingalpha.com', 'title': 'seekingalpha.com', 'uri': 'https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFG5u9QHxArvxa1PMEw3W453HMTROEJDR7mVoJFM9rne6tIZ8_1MbFysrPVMJ3esrlcwcQ0oCnJTxNu1PFQixxP_Q3J4nDBjJE3q_uV1tR0lAlVByOyVa35ZcJhS6neREL7T_Eb2wyRKrfj7cHTzJOsJJGRfkR2i7wDZv6uuWXlR8gXbEeLu_QYRfcq0wvjJDBxaRemUdRqXOj6WD0='}, {'id': '5', 'domain': 'spglobal.com', 'title': 'spglobal.com', 'uri': 'https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0GGBjy70SU6Ce7UpU-v_OyaQ-KSzHVO5XNaRfnUIfexbs5lhvbADfkN9f66SGuuJbKXsGmPE0Aov_QH3sfRhQ-29m96N-br0ZDXWuWfjfSvOtlqfeIBfoxIdDLB5ybzHYigVAkpOL7oMFcojV6PL78nyPzuxKuzswh4tU-tnlB-ZIFu7jSB9Yk4Mg27pKWqKZ5S8upAvyJ8CVAzSwxH_RpBQHVj8C7zKSVYkCKDArlKSiqc6sLcU='}, {'id': '6', 'domain': 'morningstar.com', 'title': 'morningstar.com', 'uri': 'https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWTmtFiCGUv2lQRNHKJW1nm-udbnTMOhrMG-oy36u-IwH5OqFcEhsoi5kH8L9lvEap5cb6aiJUAdnzcPlTFUi6OZeDwVRA_vgfXsXBrpau7fP6t3N7-YYHD5VUvs8fjIGTTigdi6r6LL6RrgdZfaWrYtRBy-N0Gm16nGY-q-Nn0kOLhB-HR8hRo3ro3rr-x2bjwMUQtPICeWLycmw9UfoMV0dGX27V3A=='}, {'id': '7', 'domain': 'seekingalpha.com', 'title': 'seekingalpha.com', 'uri': 'https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENLIaeZZ1scY7wgXSkwI6imH6InQG2k_a8faFnVQbFtjjdq2ajLO9lpdqPgWLkBE4GjowPIuas0AhBN4bBg1iPVpcMJyLjGhRpI6cLP_kaf1b7ZRAoInSDXYi7ofUKXwpU5mNVk4xBBhG2So13RLArnL_oZJEWkSbbGB7ZstN5xOiMBZW5p_q6cfDb--DjBGEJhasn3Gi8gXfqOX9b-CECLRq182pZTC-gJaqfjuIQirDqoPGc7vzsVig7pcU='}, {'id': '8', 'domain': 'fool.com', 'title': 'fool.com', 'uri': 'https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF1-yHsLJtAKU0T1Dr3dNm88oO7T9iY3B_-p2imDN-KgtuPrO7cXjuheOlNN-s8-0IDJ-xpCiiFNufvV2S9L77IiZKLk6A9TL6LiPo2F8bsJNu3RpSGl9X2IDvFVK73BDr68E8zr3lepsiiJ-N3EA_tuLMsRU497kxTkFJprcLwVNwsYBYxDzmXhF2nfw6cw8CeVWFkIIZxxA=='}, {'id': '9', 'domain': 'seekingalpha.com', 'title': 'seekingalpha.com', 'uri': 'https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLGWLnYLyYUdq-oXFB0N09ur407MIobnndnmPTA6MagBPURaD3d-FmZf_yLGu7BZJx3_wqxzJV2F7VgnWYiSEXki1E9xXwiNqHkc20XL8-rVxH2Ij5EO4IdjyE0rvEBA=='}, {'id': '10', 'domain': 'marketbeat.com', 'title': 'marketbeat.com', 'uri': 'https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGueDZAniOlKOt6gwzpWfgyVlJUS1fMy5SQM-BoBbpB4LWD67AI6tl3gRzyz7WDa_LR4jmLpFKZRJKQgP8U4ek42zwp2pM3XHRSdOlM_4kqpiyu4T78Tdbui2LP6Nj-MuguphxUWPaXN593wRHJ1C_6KxkyWFfEr9kblIGbZL_xjVK5vtI3l7aPgrbSykL92t95BNQE0-5Xb2RdNk='}, {'id': '11', 'domain': 'forbes.com', 'title': 'forbes.com', 'uri': 'https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVUmuHQH_8C_DCblEKLo-CrYYKL-BiNrGogivB105CqHkJLeK1p6PtzCh9wDcSKRLTq3yh9RtbZCDG8yYMZ-iX5_-XM__dSQ99O6pWk3fw1J3fVsVLh8fXLKDv_20Y0Oi70udiBuW0kgrYvBWI4sTRfmo3APdf4IZcbLJ5XdE-hoVi0_pNOFuesaq8-eBF57uxlZf5LkgzSGkXBcSXjAIBAHB9omIIQBfmZ4Z1vDWY'}]
 
 '''