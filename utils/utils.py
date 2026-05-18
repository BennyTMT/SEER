from bdb import effective
import json
import re
import pandas as pd
from seer.utils import prompt , fore_prompt , search_prompts  , retrieval_prompt
from datetime import datetime, timedelta
import argparse
import logging
import holidays
import json
import matplotlib.pyplot as plt
from datetime import datetime
import time 

def formating_stock_price_prompt(company_name , prompt_params , agent='search'):
    # ##############################################################
    # 1) Stock Price Forecasting (Infeasible❌) 
    # ##############################################################
    if 'price_forecast_cot_stock' == agent : 
        system_prompt = fore_prompt.STOCK_FORECASTING_SYSTEM_PROMPT_MERGE.format(
                prediction_days=prompt_params['prediction_horizon']
            )
        
        if prompt_params['event_strings'] == 'N/A' : 
            user_msg = fore_prompt.STOCK_FORECASTING_USER_PROMPT_WO_EVENT.format(
                company_name=company_name,
                cut_off_date=prompt_params['end_trading_date'],
                start_trading_date=prompt_params['start_trading_date'],
                prediction_days=prompt_params['prediction_horizon'],
                his_prices=prompt_params['his_prices'], 
                event_list=prompt_params['event_strings'], 
            )
        else:
            user_msg = fore_prompt.STOCK_FORECASTING_USER_PROMPT_W_EVENT.format(
                company_name=company_name,
                cut_off_date=prompt_params['end_trading_date'],
                start_trading_date=prompt_params['start_trading_date'],
                prediction_days=prompt_params['prediction_horizon'],
                his_prices=prompt_params['his_prices'], 
                event_list=prompt_params['event_strings'], 
            )


    elif  'price_forecast_cot_comm' == agent:
        system_prompt = fore_prompt.COMM_FORECASTING_SYSTEM_PROMPT_MERGE.format(
                prediction_days=prompt_params['prediction_horizon']
            )
        
        user_msg = fore_prompt.COMM_FORECASTING_USER_PROMPT.format(
            company_name=company_name,
            cut_off_date=prompt_params['end_trading_date'],
            start_trading_date=prompt_params['start_trading_date'],
            prediction_days=prompt_params['prediction_horizon'],
            his_prices=prompt_params['his_prices'], 
            event_list=prompt_params['event_strings'], 
        )
    elif  'price_forecast_ef' == agent:
        
        system_prompt = fore_prompt.PRICE_FORECASTING_SYSTEM_PROMPT_EF.format(
            prediction_days=prompt_params['prediction_horizon']
        )

        user_msg = fore_prompt.PRICE_FORECASTING_USER_PROMPT_EF.format(
            company_name=company_name,
            cut_off_date=prompt_params['end_trading_date'],
            start_trading_date=prompt_params['start_trading_date'],
            prediction_days=prompt_params['prediction_horizon'],
            his_prices=prompt_params['his_prices'], 
            event_list=prompt_params['event_strings'], 
        )
    elif  'price_forecast_cot_abl' == agent:
        system_prompt = prompt.PRICE_FORECASTING_SYSTEM_PROMPT_COT_NA.format(
            prediction_days=prompt_params['prediction_horizon']
        )
        user_msg = prompt.PRICE_PREDICT_USER_PROMPT_COT_NA.format(
            company_name=company_name,
            cut_off_date=prompt_params['end_trading_date'],
            start_trading_date=prompt_params['start_trading_date'],
            prediction_days=prompt_params['prediction_horizon'],
            his_prices=prompt_params['his_prices'], 
            event_list=prompt_params['event_strings'], 
        )

    elif   'price_forecast_base' in agent:
        # We removed this experiment (infeasible)
        system_prompt = fore_prompt.PRICE_FORECASTING_SYSTEM_PROMPT_V1 
        user_msg = fore_prompt.PRICE_FORECASTING_USER_PROMPT_V1

    elif  'price_forecast_abl' in agent:
        system_prompt = fore_prompt.PRICE_FORECASTING_SYSTEM_PROMPT_ABL
        
        if 'abl0' in agent:
            user_msg = fore_prompt.PRICE_PREDICT_USER_PROMPT_ABL0.format(
                company_name=company_name,
                cut_off_date=prompt_params['end_trading_date'],
                start_trading_date=prompt_params['start_trading_date'],
                prediction_days=prompt_params['prediction_horizon'],
                his_prices=prompt_params['his_prices'], 
                event_list=prompt_params['event_strings'], 
            )
        elif 'abl1' in agent:
            user_msg = fore_prompt.PRICE_PREDICT_USER_PROMPT_ABL1.format(
                company_name=company_name,
                cut_off_date=prompt_params['end_trading_date'],
                start_trading_date=prompt_params['start_trading_date'],
                prediction_days=prompt_params['prediction_horizon'],
                his_prices=prompt_params['his_prices'], 
                event_list=prompt_params['event_strings'], 
            )

    return system_prompt , user_msg

def formating_forecast_abl_prompt(company_name , prompt_params , agent='search'):
    if  'trend_3way_forecast_loho_living' == agent:
        system_prompt = fore_prompt.TREND_FORECASTING_SYSTEM_PROMPT_LOHO_3WAY_LIVING
        user_msg = fore_prompt.TREDN_FORECASTING_USER_PROMPT_LOHO_3WAY_LIVING.format(
            company_name=company_name,
            cut_off_date=prompt_params['end_trading_date'],
            start_trading_date=prompt_params['start_trading_date'],
            prediction_horizon=prompt_params['prediction_horizon'],
            prediction_target=prompt_params['prediction_target'],
            his_prices=prompt_params['his_prices'], 
        )
    elif  'trend_5way_forecast_loho_living' == agent:
        system_prompt = fore_prompt.TREND_FORECASTING_SYSTEM_PROMPT_LOHO_5WAY_LIVING
        user_msg = fore_prompt.TREDN_FORECASTING_USER_PROMPT_LOHO_5WAY_LIVING.format(
            company_name=company_name,
            cut_off_date=prompt_params['end_trading_date'],
            start_trading_date=prompt_params['start_trading_date'],
            prediction_horizon=prompt_params['prediction_horizon'],
            prediction_target=prompt_params['prediction_target'],
            his_prices=prompt_params['his_prices'], 
        )
    elif  'soho_trend_3way_forecast_living' == agent:
        system_prompt = fore_prompt.TREND_FORECASTING_SYSTEM_PROMPT_3WAY_SOHO_LIVING
        user_msg = fore_prompt.TREDN_FORECASTING_USER_PROMPT_3WAY_SOHO_LIVING.format(
            company_name=company_name,
            cut_off_date=prompt_params['end_trading_date'],
            start_trading_date=prompt_params['start_trading_date'],
            prediction_days=prompt_params['prediction_horizon'],
            his_prices=prompt_params['his_prices'], 
            prediction_target=prompt_params['target_forecast_date'],
        )
    elif  'soho_trend_5way_forecast_living' == agent:
        system_prompt = fore_prompt.TREND_FORECASTING_SYSTEM_PROMPT_5WAY_SOHO_LIVING
        user_msg = fore_prompt.TREDN_FORECASTING_USER_PROMPT_5WAY_SOHO_LIVING.format(
            company_name=company_name,
            cut_off_date=prompt_params['end_trading_date'],
            start_trading_date=prompt_params['start_trading_date'],
            prediction_days=prompt_params['prediction_horizon'],
            his_prices=prompt_params['his_prices'], 
            prediction_target=prompt_params['target_forecast_date'],
        )
    return system_prompt , user_msg

def formating_forecast_prompt(company_name , prompt_params , agent='search'):
    # ##############################################################
    # 0) Event Validation 
    # ##############################################################
    if agent == 'event_validation':
        system_prompt = prompt.STOCK_EVENT_VALIDATION_SYSTEM_PROMPT 
        user_msg = prompt.STOCK_EVENT_VALIDATION_USER_PROMPT.format(
            company_name=company_name,
            cut_off_date=prompt_params['end_trading_date'],
            start_trading_date=prompt_params['start_trading_date'],
            prediction_days=prompt_params['prediction_horizon'],
            his_prices=prompt_params['his_prices'], 
            event_list=prompt_params['event_strings'], 
        )
    
    elif agent == 'event_fore_validation':
        system_prompt = prompt.EVENT_FORE_VALIDATION_SYSTEM_PROPT 
        user_msg = prompt.EVENT_FORE_VALIDATION_USER_PROPT.format(
            question=prompt_params['title'],
            fore_cut_off_date=prompt_params['fore_cut_off_date'],
            result_public_date=prompt_params['q_end_str'],
            target_outcome=prompt_params['winner'], 
            list_of_evidences=prompt_params['event_list_str'], 
        )
    
    # ##############################################################
    # 1) Event Forecasting 
    # ##############################################################

    elif agent == 'forecast_events':
        system_prompt = prompt.EVENT_FORECASTING_SYSTEM_PROPT.format(
            cut_off_date=prompt_params['cut_off_date']
        )
        
        user_msg = prompt.EVENT_FORECASTING_USER_PROMPT.format(
            list_of_evidences=prompt_params['list_of_evidences'],
            cut_off_date=prompt_params['cut_off_date'],
        )
    
    
    elif agent ==  'events_filter':
        # we tried to distill information then feed then to LMs to facilitate Forecsating，not scoop ❌
        system_prompt = prompt.FILTER_SYS_PROMPT 
        user_msg = prompt.FILTER_USER_PROMPT.format(
            raw_event_list=prompt_params['event_strings'], 
        )

    # ##############################################################
    # 3) Trend Forecasting 
    # ##############################################################
    # (CoT, Does not help❌)
    # elif  'trend_forecast_cot' == agent:
    #     system_prompt = fore_prompt.TREND_FORECASTING_SYSTEM_PROMPT_COT_EVENT.format(
    #         prediction_days=prompt_params['prediction_horizon']
    #     )
    #     user_msg = fore_prompt.TREND_FORECASTING_USER_PROMPT_COT.format(
    #         company_name=company_name,
    #         cut_off_date=prompt_params['end_trading_date'],
    #         start_trading_date=prompt_params['start_trading_date'],
    #         prediction_days=prompt_params['prediction_horizon'],
    #         his_prices=prompt_params['his_prices'], 
    #         event_list=prompt_params['event_strings'], 
    #     )

    # ##############################################################
    # 3.1) Stock Trend Forecasting (High-Liq, Short-Horizon 3 5 Way) soho
    # ##############################################################
    
    elif 'soho_trend_3way_forecast_base' ==  agent:
        system_prompt = fore_prompt.TREND_FORECASTING_SYSTEM_PROMPT_3WAY_SOHO.format(
            prediction_days=prompt_params['prediction_horizon']
        )
        user_msg = fore_prompt.TREDN_FORECASTING_USER_PROMPT_3WAY_SOHO.format(
            company_name=company_name,
            cut_off_date=prompt_params['end_trading_date'],
            start_trading_date=prompt_params['start_trading_date'],
            prediction_days=prompt_params['prediction_horizon'],
            his_prices=prompt_params['his_prices'], 
            event_list=prompt_params['event_strings'], 
        )
    
    elif  'soho_trend_5way_forecast_base' == agent:

        system_prompt = fore_prompt.TREND_FORECASTING_SYSTEM_PROMPT_5WAY_SOHO.format(
            prediction_days=prompt_params['prediction_horizon']
        )
        user_msg = fore_prompt.TREDN_FORECASTING_USER_PROMPT_5WAY_SOHO.format(
            company_name=company_name,
            cut_off_date=prompt_params['end_trading_date'],
            start_trading_date=prompt_params['start_trading_date'],
            prediction_days=prompt_params['prediction_horizon'],
            his_prices=prompt_params['his_prices'], 
            event_list=prompt_params['event_strings'], 
        )

    # ##############################################################
    # 3.1) Stock Trend Forecasting (Low-Liq, Long-term 3 5 Way)     loho
    # ##############################################################
    
    # Using seperated Confidence Calibration ✅
    elif 'trend_3way_forecast_loho' == agent:
        system_prompt = fore_prompt.TREND_FORECASTING_SYSTEM_PROMPT_LOHO_3WAY_ADVOCATE
        user_msg = fore_prompt.TREDN_FORECASTING_USER_PROMPT_LOHO_3WAY_ADVOCATE.format(
            company_name=company_name,
            cut_off_date=prompt_params['end_trading_date'],
            start_trading_date=prompt_params['start_trading_date'],
            prediction_horizon=prompt_params['prediction_horizon'],
            prediction_target=prompt_params['prediction_target'],
            his_prices=prompt_params['his_prices'], 
            event_list=prompt_params['event_strings'], 
        )
    
    elif 'trend_5way_forecast_loho' == agent:
        system_prompt = fore_prompt.TREND_FORECASTING_SYSTEM_PROMPT_LOHO_5WAY_ADVOCATE
        user_msg = fore_prompt.TREDN_FORECASTING_USER_PROMPT_LOHO_5WAY_ADVOCATE.format(
            company_name=company_name,
            cut_off_date=prompt_params['end_trading_date'],
            start_trading_date=prompt_params['start_trading_date'],
            prediction_horizon=prompt_params['prediction_horizon'],
            prediction_target=prompt_params['prediction_target'],
            his_prices=prompt_params['his_prices'], 
            event_list=prompt_params['event_strings'], 
        )

    # With Confidence in output (Fail❌)
    elif  'loho_trend_3way_forecast_base' == agent:
        system_prompt = fore_prompt.TREND_FORECASTING_SYSTEM_PROMPT_CONFI_3WAY_HIGH.format(
            prediction_days=prompt_params['prediction_horizon']
        )
        user_msg = fore_prompt.TREDN_FORECASTING_USER_PROMPT_CONFI_3WAY_HIGH.format(
            company_name=company_name,
            cut_off_date=prompt_params['end_trading_date'],
            start_trading_date=prompt_params['start_trading_date'],
            prediction_days=prompt_params['prediction_horizon'],
            his_prices=prompt_params['his_prices'], 
            event_list=prompt_params['event_strings'], 
        )

    # Ratio as Confidence in output (❌, not clear)
    elif  'trend_ratio_3way_forecast_loho' == agent:
        system_prompt = fore_prompt.TREND_RATIO_FORECASTING_SYSTEM_PROMPT_LOHO_3WAY
        
        user_msg = fore_prompt.TREDN_RATIO_FORECASTING_USER_PROMPT_LOHO_3WAY.format(
            company_name=company_name,
            cut_off_date=prompt_params['end_trading_date'],
            start_trading_date=prompt_params['start_trading_date'],
            prediction_horizon=prompt_params['prediction_horizon'],
            prediction_target=prompt_params['prediction_target'],
            his_prices=prompt_params['his_prices'], 
            event_list=prompt_params['event_strings'], 
        )
    

    # ##############################################################
    # 3.2) Weather Trend Forecasting 
    # ##############################################################

    elif 'weather_forecast_trend_3way' ==  agent:
        system_prompt = fore_prompt.WEATHER_TREND_FORECASTING_SYSTEM_PROMPT.format(
            temp_type= prompt_params['forecast_type'],     
        )
        user_msg = fore_prompt.WEATHER_TREND_USER_PROMPT_3WAY.format(
            city_name=company_name,
            cut_off_time=prompt_params['end_time_str'],
            start_time=prompt_params['start_time_str'],
            prediction_days=prompt_params['prediction_horizon'],
            his_temps=prompt_params['his_time_series'], 
            event_list=prompt_params['event_strings'], 
            temp_type= prompt_params['forecast_type'],     
        )
        
    elif 'weather_forecast_trend_5way' ==  agent:
        system_prompt = fore_prompt.WEATHER_TREND_FORECASTING_SYSTEM_PROMPT.format(
            temp_type= prompt_params['forecast_type'],     
        )
        user_msg = fore_prompt.WEATHER_TREND_USER_PROMPT_5WAY.format(
            city_name=company_name,
            cut_off_time=prompt_params['end_time_str'],
            start_time=prompt_params['start_time_str'],
            prediction_days=prompt_params['prediction_horizon'],
            his_temps=prompt_params['his_time_series'], 
            event_list=prompt_params['event_strings'], 
            temp_type= prompt_params['forecast_type'],     
        )

    elif 'elec_forecast_trend_3way' ==  agent:
        system_prompt = fore_prompt.ELEC_LOAD_FORECASTING_SYSTEM_PROMPT.format(
            forecast_type= prompt_params['forecast_type']
        )
        user_msg = fore_prompt.ELEC_LOAD_USER_PROMPT_3WAY.format(
            city_name=company_name,
            cut_off_time=prompt_params['end_time_str'],
            start_time=prompt_params['start_time_str'],
            prediction_horizon=prompt_params['prediction_horizon'],
            his_time_series=prompt_params['his_time_series'], 
            event_list=prompt_params['event_strings'], 
            forecast_type= prompt_params['forecast_type']
        )

    elif 'elec_forecast_trend_5way' ==  agent:
        system_prompt = fore_prompt.ELEC_LOAD_FORECASTING_SYSTEM_PROMPT.format(
            forecast_type= prompt_params['forecast_type'],     
        )
        user_msg = fore_prompt.ELEC_LOAD_USER_PROMPT_5WAY.format(
            city_name=company_name,
            cut_off_time=prompt_params['end_time_str'],
            start_time=prompt_params['start_time_str'],
            prediction_horizon=prompt_params['prediction_horizon'],
            his_time_series=prompt_params['his_time_series'], 
            event_list=prompt_params['event_strings'], 
            forecast_type= prompt_params['forecast_type']
        )

    # ##############################################################
    # 5) Time Series Forecasting (24 hours x N horizen)
    # ##############################################################
    elif 'weather_forecast_base' ==  agent:
        system_prompt = fore_prompt.WEATHER_FORECASTING_SYSTEM_PROMPT
        user_msg = fore_prompt.WEATHER_PREDICT_USER_PROMPT.format(
            city_name= prompt_params['city_name'], 
            cut_off_time=prompt_params['end_time_str'],
            start_time=prompt_params['start_time_str'],
            prediction_days=prompt_params['prediction_horizon'],
            his_temps=prompt_params['his_time_series'], 
            event_list=prompt_params['event_strings'], 
            total_hours = prompt_params['total_hours']
        )

    # Fail: taxi data is not that event-driven, or not fit our system❌
    elif 'taxi_forecast_base' ==  agent:
        system_prompt = fore_prompt.TAXI_FORECASTING_SYSTEM_PROMPT.format(
            target_metric_name = prompt_params['target_metric_name'],
            metric_context = prompt_params['metric_context'],
            total_hours = prompt_params['total_hours']
        )
        user_msg = fore_prompt.TAXI_PREDICT_USER_PROMPT.format(
            target_metric_name=prompt_params['target_metric_name'],
            cut_off_time=prompt_params['end_time_str'],
            start_time=prompt_params['start_time_str'],
            prediction_days=prompt_params['prediction_horizon'],
            historical_values=prompt_params['his_time_series'], 
            event_list=prompt_params['event_strings'], 
            total_hours = prompt_params['total_hours'], 
        )

    elif 'elec_forecast_base' ==  agent:
        system_prompt = fore_prompt.ELEC_FORECASTING_SYSTEM_PROMPT.format(
            city_name = prompt_params['city_name'] ,
            total_hours = prompt_params['total_hours']
        )
        user_msg = fore_prompt.ELEC_PREDICT_USER_PROMPT.format(
            city_name=prompt_params['city_name'] ,
            cut_off_time=prompt_params['end_time_str'],
            start_time=prompt_params['start_time_str'],
            prediction_days=prompt_params['prediction_horizon'],
            historical_values=prompt_params['his_time_series'], 
            event_list=prompt_params['event_strings'], 
            total_hours = prompt_params['total_hours'], 
        )

    # with search (❌ not the scoop of this work)
    elif 'elec_forecast_search' ==  agent:
        system_prompt = fore_prompt.ELEC_FORECASTING_SYSTEM_PROMPT_SEARCH.format(
            city_name = prompt_params['city_name'] ,
            cut_off_time = prompt_params['end_time_str']
        )
        user_msg = fore_prompt.ELEC_PREDICT_USER_PROMPT_SEARCH.format(
            city_name=prompt_params['city_name'] ,
            cut_off_time=prompt_params['end_time_str'],
            start_time=prompt_params['start_time_str'],
            prediction_days=prompt_params['prediction_horizon'],
            historical_values=prompt_params['his_time_series'], 
            event_list=prompt_params['event_strings'], 
            total_hours = prompt_params['total_hours'], 
        )

    return system_prompt , user_msg

def formating_search_prompt(company_name , prompt_params , agent='search'):
    # ['stock_events_search' , 'commodities_event_search' , 'crypto_event_search']
    if agent=='stock_events_search':
        system_prompt = search_prompts.SYS_STOCK_EVENT_SEARCH
        
        if prompt_params['events_lists'] is not None :
            user_msg = search_prompts.STOCK_COVERAGE_SEARCH.format(
                company_name=company_name,
                cut_off_date=prompt_params['cut_off_date'],
                events_lists=prompt_params['events_lists']
            )
        else:
            user_msg = search_prompts.STOCK_USER_PROMPT.format(
            company_name=company_name,
            cut_off_date=prompt_params['cut_off_date'],
        )

    elif agent=='multi_days_stock_events_search':
        system_prompt = search_prompts.SYS_STOCK_LONG_EVENT_SEARCH
        
        if prompt_params['events_lists'] is not None :
            user_msg = search_prompts.STOCK_LONG_COVERAGE_SEARCH.format(
                company_name=company_name,
                start_date=prompt_params['start_date'],
                end_date=prompt_params['end_date'],
                events_lists=prompt_params['events_lists']
            )
        else:
            user_msg = search_prompts.STOCK_LONG_USER_PROMPT.format(
            company_name=company_name, 
            start_date=prompt_params['start_date'],
            end_date=prompt_params['end_date']
        )

    elif agent=='multi_days_taxi_events_search':
        system_prompt = search_prompts.SYS_NYCTAXI_HYBRID_SEARCH.format(
                start_date=prompt_params['start_date'],
                end_date=prompt_params['end_date'],
            )

        if prompt_params['events_lists'] is not None :
            user_msg = search_prompts.NYCTAXI_COVERAGE_PROMPT.format(
                start_date=prompt_params['start_date'],
                end_date=prompt_params['end_date'],
                events_lists=prompt_params['events_lists']
            )
        else:
            user_msg = search_prompts.NYCTAXI_USER_PROMPT.format(
            start_date=prompt_params['start_date'],
            end_date=prompt_params['end_date']
        )

    elif agent=='multi_days_elec_events_search':
        system_prompt = search_prompts.SYS_ELECTRICITY_HYBRID_SEARCH.format(
                city_name = company_name, 
                start_date=prompt_params['start_date'],
                end_date=prompt_params['end_date'],
            )

        if prompt_params['events_lists'] is not None :
            user_msg = search_prompts.ELECTRICITY_COVERAGE_PROMPT.format(
                city_name=company_name,
                start_date=prompt_params['start_date'],
                end_date=prompt_params['end_date'],
                events_lists=prompt_params['events_lists']
            )
        else:
            user_msg = search_prompts.ELECTRICITY_USER_PROMPT.format(
            city_name=company_name, 
            start_date=prompt_params['start_date'],
            end_date=prompt_params['end_date']
        )

    elif agent=='crypto_event_search':
        system_prompt = search_prompts.SYS_CRYPTO_EVENT_SEARCH
        
        if prompt_params['events_lists'] is not None :
            user_msg = search_prompts.CRYPTO_COVERAGE_SEARCH.format(
                token_name=company_name,
                cut_off_date=prompt_params['cut_off_date'],
                events_lists=prompt_params['events_lists']
            )
        else:
            user_msg = search_prompts.CRYPTO_USER_PROMPT.format(
            token_name=company_name,
            cut_off_date=prompt_params['cut_off_date'],
        )
            
    elif agent=='commodities_event_search':
        system_prompt = search_prompts.SYS_COMMODITY_EVENT_SEARCH
        
        if prompt_params['events_lists'] is not None :
            user_msg = search_prompts.COMMODITY_COVERAGE_SEARCH.format(
                commodity_name=company_name,
                cut_off_date=prompt_params['cut_off_date'],
                events_lists=prompt_params['events_lists']
            )
        else:
            user_msg = search_prompts.COMMODITY_USER_PROMPT.format(
            commodity_name=company_name,
            cut_off_date=prompt_params['cut_off_date'],
        )
    elif agent=='weather_event_search':
        system_prompt = search_prompts.SYS_WEATHER_HYBRID_SEARCH.format(
                city_name=company_name,
                cut_off_date=prompt_params['cut_off_date'],
            )
        
        if prompt_params['events_lists'] is not None :
            user_msg = search_prompts.WEATHER_COVERAGE_PROMPT.format(
                city_name=company_name,
                cut_off_date=prompt_params['cut_off_date'],
                events_lists=prompt_params['events_lists']
            )
        else:
            user_msg = search_prompts.WEATHER_USER_PROMPT.format(
            city_name=company_name,
            cut_off_date=prompt_params['cut_off_date'],
        )

    elif agent == 'forecasting_date_check':
        system_prompt = prompt.FACT_CHECK_SYSTEM_SEARCH
        user_msg = prompt.FACT_CHECK_PROMPT_SEARCH.format(
            description=prompt_params['search_results'],
            date=prompt_params['fore_cut_off_date'],
        )

    elif agent=='factual_market':
        system_prompt = prompt.FACT_CHECK_SYSTEM_MARKET
        user_msg = prompt.FACT_CHECK_PROMPT_MARKET.format(
            description=prompt_params['description'],
            date=prompt_params['date'],
        )

    elif agent=='factual_weather':
        system_prompt = prompt.FACT_CHECK_SYSTEM_WEATHER
        user_msg = prompt.FACT_CHECK_PROMPT_WEATHER.format(
            description=prompt_params['description'],
            date=prompt_params['date'],
        )
    
    elif agent=='factual_generic':
        system_prompt = prompt.FACT_CHECK_SYSTEM_GENERIC
        user_msg = prompt.FACT_CHECK_PROMPT_GENERIC.format(
            description=prompt_params['description'],
            date=prompt_params['date'],
        )

    elif agent =='covariates_cluster':
        system_prompt = prompt.COVARIATES_AGENT 
        user_msg = prompt.COVARIATES_USER_PROMPT.format(
            company_name=company_name,
            cut_off_date=prompt_params['cut_off_date'],
            events_lists=prompt_params['events_lists'],
            list_of_covariates=prompt_params['list_of_covariates'],
            num_of_events=prompt_params['num_of_events'],
        )
    elif agent =='init_covariates_merge':
        system_prompt = prompt.COVARIATES_MERGE_SYS_PROMPT
        user_msg =  prompt.COVARIATES_MERGE_INIT_PROMP
        
    elif agent =='human_expert_retriever':
        system_prompt = prompt.HUMAN_EXPERT_SYS_PROMPT
        user_msg = prompt.HUMAN_EXPERT_ARTICLE_SEARCH.format(
            company_name=company_name,
            start_date=prompt_params['start_date'],
            end_date=prompt_params['end_date'],
        )
    
    elif agent == 'economic_forecast_search':
        system_prompt = prompt.ECONOMIC_EVENT_SEARCH_SYSTEM_PROMPT
        start_date , end_date =  prompt_params['search_range']

        if prompt_params['events_lists'] is None : 
            user_msg = prompt.EVENT_FORECAST_USER_PROMPT.format(
                target_event=prompt_params['target_event'],
                start_date = start_date, 
                end_date = end_date , 
            )
        else : 
            user_msg = prompt.EVENT_FORECAST_COVERAGE_USER_PROMPT.format(
                target_event=prompt_params['target_event'],
                events_lists=prompt_params['events_lists'],
                start_date = start_date, 
                end_date = end_date , 
            )
        
    elif agent == 'political_forecast_search' : 
        system_prompt = prompt.POLITICAL_EVENT_SEARCH_SYSTEM_PROMPT
        start_date , end_date =  prompt_params['search_range']
            
        if prompt_params['events_lists'] is None : 
            user_msg = prompt.EVENT_FORECAST_USER_PROMPT.format(
                target_event=prompt_params['target_event'],
                start_date = start_date, 
                end_date = end_date , 
            )
        else : 
            user_msg = prompt.EVENT_FORECAST_COVERAGE_USER_PROMPT.format(
                target_event=prompt_params['target_event'],
                events_lists=prompt_params['events_lists'],
                start_date = start_date, 
                end_date = end_date , 
            )
    
    elif agent == 'tech_forecast_search' : 
        system_prompt = prompt.TECH_AI_EVENT_SEARCH_SYSTEM_PROMPT
        start_date , end_date =  prompt_params['search_range']
            
        if prompt_params['events_lists'] is None : 
            user_msg = prompt.EVENT_FORECAST_USER_PROMPT.format(
                target_event=prompt_params['target_event'],
                start_date = start_date, 
                end_date = end_date , 
            )
        else : 
            user_msg = prompt.EVENT_FORECAST_COVERAGE_USER_PROMPT.format(
                target_event=prompt_params['target_event'],
                events_lists=prompt_params['events_lists'],
                start_date = start_date, 
                end_date = end_date , 
            )


        
    return system_prompt , user_msg

def formating_evoluting_prompt( prompt_params , agent='search'):

    # 1) Event Selection 
    if agent=='event_retrieval':
        system_prompt = retrieval_prompt.SYSTEM_FIN_RETRIEVAL_PROMPT
        user_msg = retrieval_prompt.USER_FIN_RETRIEVAL_PROMPT.format(
            company_name=prompt_params['company_name'],
            fore_cut_off_date=prompt_params['fore_cut_off_date'],
            prediction_horizon=prompt_params['prediction_horizon'],
            memory_info=prompt_params['memory_info'],
            event_list_str_ids=prompt_params['event_list_str_ids']
        )
    elif agent=='self_improving_retrieval':
        system_prompt = retrieval_prompt.SYSTEM_FIN_IMPROVING_PROMPT
        user_msg = retrieval_prompt.USER_FIN_IMPROVING_PROMPT.format(
            event_list_pool =prompt_params['event_list_pool'] , 
            company_name=prompt_params['company_name'],
            fore_cut_off_date=prompt_params['fore_cut_off_date'],
            prediction_horizon=prompt_params['prediction_horizon'],
            start_trading_date=prompt_params['start_trading_date'],
            his_prices=prompt_params['his_prices'],
            event_list_selected=prompt_params['event_list_selected'],
            llm_forecasting_resp=prompt_params['llm_forecasting_resp'],
            label=prompt_params['label'],
            memory_info=prompt_params['memory_info'],
            missing_info=prompt_params['missing_info'],
            sector=prompt_params['sector'] , 
            memory_cap=prompt_params['memory_cap'],
            memory_char=prompt_params['memory_char'],
            missing_cap=prompt_params['missing_cap'],
            missing_char=prompt_params['missing_char'],
        )
        
    return system_prompt , user_msg

# =============================================================================
# Utils for Date and Logs 
# =============================================================================
        
def generate_id_from_title(title, max_length=50):
    # 1. 统一转为小写
    title_id = title.lower()
    # 2. 去除非字母、非数字、非空格的字符（比如问号、感叹号、逗号）
    # [^\w\s] 匹配所有非单词字符（\w 包含字母、数字和下划线）
    title_id = re.sub(r'[^\w\s]', '', title_id)
    # 3. 将空格替换为下划线
    title_id = title_id.replace(" ", "_")
    # 4. 去除多余的连续下划线（防止原标题有双空格）
    title_id = re.sub(r'_+', '_', title_id)
    # 5. 限制长度并去除末尾下划线
    return title_id[:max_length].strip("_")

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

def check_us_holiday_or_weekend(date_str):
    """
    输入日期字符串 'YYYY-MM-DD'，检测是否为周末或美国节假日。
    
    Returns:
        str: 如果是休息日，返回具体原因 (例如 "美国节假日: Christmas Day" 或 "周末: Saturday")
        None: 如果是正常工作日
    """
    try:
        # 1. 解析日期字符串
        dt = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        # 2. 获取当年的美国节假日 (包含 observed=True，即处理补休)
        # observed=True 表示如果节日落在周日，周一会被算作假期 (美股休市规则通常如此)
        us_holidays = holidays.US(years=dt.year, observed=True)
        
        # 3. 优先检查：是否是节假日
        if dt in us_holidays:
            # 获取节日名称 (e.g., "New Year's Day")
            holiday_name = us_holidays.get(dt) 
            return f"Holidays: {holiday_name}"
            
        # 4. 其次检查：是否是周末
        # weekday(): 0=周一 ... 5=周六, 6=周日
        week_num = dt.weekday()
        if week_num == 5:
            return "Saturday"
        elif week_num == 6:
            return "Sunday"
            
        # 5. 既不是节日也不是周末 -> 工作日
        return None

    except ValueError:
        return "错误: 日期格式应为 YYYY-MM-DD"

def is_string_date_format(date_str):
    try:
        if len(date_str) != 10: return False
    except:
        print('err date format !!!!!!' ,date_str )
        return False
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:  return False
  
def parse_flexible_date(date_str):
    if not date_str:
        return None
    
    date_str = date_str.strip()
    
    try:
        if len(date_str) == 4:  # 只有年份: YYYY
            dt = datetime.strptime(date_str, '%Y')
            return dt.strftime('%Y-%01-%01')

        elif len(date_str) == 7:  # 年月格式: YYYY-MM
            dt = datetime.strptime(date_str, '%Y-%m')
            return dt.strftime('%Y-%m-01')
        
        elif len(date_str) == 10:  # 完整格式: YYYY-MM-DD
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            return dt.strftime('%Y-%m-%d')
        
        else:
            raise ValueError
            
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid date format: '{date_str}'. "
            f"Please use YYYY, YYYY-MM, or YYYY-MM-DD."
        )

# =============================================================================
# Utils for Extract Results from Resp
# =============================================================================

def extract_prediction_probability(text):
    if not text:
        return None
    
    # 步骤 1：匹配所有的 <prediction> 标签内容
    # (.*?)   : 捕获标签内的所有字符，非贪婪模式
    # re.IGNORECASE | re.DOTALL : 忽略大小写，并允许内容跨越多行
    tag_pattern = r'<prediction>(.*?)</prediction>'
    tag_matches = re.findall(tag_pattern, text, flags=re.IGNORECASE | re.DOTALL)
    
    if not tag_matches:
        return None
        
    # 需求 2：如果提取到多个标签对，只取最后一个的结果
    last_tag_content = tag_matches[-1]
    
    # 步骤 2：在最后一个标签内容中提取数字
    # [-+]?     : 匹配可选的正负号
    # (?:\d*\.\d+|\d+) : 匹配浮点数 (如 .5, 10.5) 或 纯整数 (如 80)
    num_pattern = r'(?:\d*\.\d+|\d+)'
    numbers_found = re.findall(num_pattern, last_tag_content)
        
    # 需求 1：只能有一个数字出现
    if len(numbers_found) == 1:
        try:
            val = float(numbers_found[0])
            # 核心判断：数字必须在 0-100 之间
            if 0 <= val <= 100:
                return val
            else:
                # print(f"Warning: Extracted value {val} is out of range [0, 100].")
                return None
        except ValueError:
            return None
            
    else:
        # 如果没有找到数字，或者找到了多个数字 (例如 "The probability is 80 or 90%")，均视为无效
        # if len(numbers_found) > 1:
        #     print(f"Warning: Multiple numbers found in the last tag: {numbers_found}.")
        # else:
        #     print("Warning: No numbers found in the last tag.")
        return None
    
def extract_info_tag(text):
    """
    提取 <info> 和 </info> 标签之间的内容。
    如果标签不存在、内容为空或提取过程出错，则返回 None。
    """
    # 如果传入的不是字符串（例如 None 或数字），直接返回 None
    if not isinstance(text, str):
        return None

    try:
        match = re.search(r'<info>(.*?)</info>', text, flags=re.DOTALL)
        
        if match:
            content = match.group(1).strip()
            return content if content else None
        return None
        
    except Exception as e:
        return None

def extract_prediction_tag(text):
    """
    提取 <info> 和 </info> 标签之间的内容。
    如果标签不存在、内容为空或提取过程出错，则返回 None。
    """
    if not isinstance(text, str):
        return None
    try:
        pattern = r"<prediction>(.*?)</prediction>"
        match = re.search(pattern, text, flags=re.DOTALL)
        if match:
            content = match.group(1).strip()
            return content if content else None
        return None
        
    except Exception as e:
        return None


def info_leakage(forecast_res_from_llm , fore_cut_off_date):
    debug_info = 0

    def extract_search_results(text):
        if not text:
            return None
        pattern = r'<search_results>(.*?)</search_results>'
        match = re.search(pattern, text, flags=re.DOTALL)
        
        if match:
            return match.group(1).strip()
        return None
    
    def extract_date_check(text):
        # print('='*10 , 'Checking')
        # print(text)
        if not text:
            return None
        pattern = r'<date_check>(.*?)</date_check>'
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            val_str = match.group(1).strip().lower()
            if val_str == 'true':
                return True
            elif val_str == 'false':
                return False
        return None

    search_results =  extract_search_results(forecast_res_from_llm)
    if search_results : 
        system_prompt , user_msg  = formating_prompt(
                    None, 
                    prompt_params={
                        'search_results': search_results,
                        'fore_cut_off_date': fore_cut_off_date
                        }, 
                    agent='forecasting_date_check'
        )

        if debug_info:
            print('Checking... ')
            # print(system_prompt)
            print(user_msg)


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


        forecast_res_from_llm2 , _ , _ = query_claude(system_prompt , user_msg ,\
                                                    web_search = True , max_tokens =4096 *2  ,  
                                                    model_name="claude-opus-4-5" ) 
        if debug_info:
            print('forecast_res_from_llm2')
            print(forecast_res_from_llm2)
        
        if not extract_date_check(forecast_res_from_llm2):
            print('Claude Rejects!')
            return  True
        
        forecast_res_from_llm1 , _ , _ = query_gemini(system_prompt , user_msg \
                    , history=None , citations_need = False , web_search=True ,  model_name='gemini-3.1-flash-lite-preview')

        if debug_info:
            print('forecast_res_from_llm1')
            print(forecast_res_from_llm1)

        if  extract_date_check(forecast_res_from_llm1) :
            return  False
        else:
            print('Gemini Rejects!')
            return  True
        
    else:
        return True 

def extract_predict_results(text):

    if not text:
        return None
    pattern = r"<prediction>(.*?)</prediction>"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)

    if not match:
        return None

    content = match.group(1).strip()
    
    if not content:
        return None

    results = []
    
    parts = content.split(',')
    
    for part in parts:
        clean_part = part.strip()
        
        if not clean_part:
            continue
            
        try:
            val = float(clean_part)
            results.append(val)
        except ValueError:
            return None

    return results

def extract_json_to_list(text):
    json_pattern = r"```json\s*([\s\S]*?)\s*```"
    match = re.search(json_pattern, text)
    if not match:
        # print('Fail!!! no json detected !!')
        # print(match)
        return None 
        
    json_str = match.group(1).strip()

    try:
        data_list = json.loads(json_str)
        if isinstance(data_list, list):
            return data_list
        else:
            # print('Fail!!! no json detected !!')
            # print(json_str)
            return None 
    except json.JSONDecodeError as e:
        # print('Err!!! no json detected !!', e)
        # print(json_str)
        return None 

def extract_tag_data(text):
    """
    Extracts content from <factual> and <date> tags and standardizes the date format.
    
    Args:
        text (str): The raw string containing the tags.
        
    Returns:
        tuple: (factual_status, formatted_date)
               factual_status: Boolean (True/False) or None if not found.
               formatted_date: String in 'YYYY-MM-DD' format or None if invalid/NA.
    """
    # 1. Extract content from the <factual> tag
    # Uses re.IGNORECASE to handle tags like <Factual> or <FACTUAL>
    factual_match = re.search(r"<factual>(.*?)</factual>", text, re.IGNORECASE | re.DOTALL)
    factual_res = factual_match.group(1).strip() if factual_match else None
    
    # Convert the extracted string to a Boolean value
    if factual_res:
        factual_bool = factual_res.lower() == 'true'
    else:
        factual_bool = None
    
    # 2. Extract content from the <date> tag
    date_match = re.search(r"<date>(.*?)</date>", text, re.IGNORECASE | re.DOTALL)
    raw_date = date_match.group(1).strip() if date_match else None
    
    # Process the date if it is present and not explicitly "n/a"
    if raw_date and raw_date.lower() != 'n/a':
        try:
            # pd.to_datetime automatically parses various formats (e.g., "12/16/2025" or "Dec 16, 2025")
            dt = pd.to_datetime(raw_date)
            # Force the output into YYYY-MM-DD format
            formatted_date = dt.strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            # If the string is not a valid date format, return None
            if factual_bool is not None : 
                formatted_date =  'N/A'
            else:
                formatted_date = None
    else:
        formatted_date = 'N/A'
        
    return factual_bool, formatted_date


# =============================================================================
# Utils for Visilization 
# =============================================================================
def print_events_lists_from_pool(events_pool , i):
    print()
    print('Events Gathered until Round',  i+1)
    events_lists = ''
    loc = 1
    for items in events_pool:
        # dict_keys(['date', 'description', 'causality', 'sentiment', 'impact_type', 'factual_check_gemini'])
        num_cites = len(items['factual_check_gemini']['citations'])
        date_val = items['factual_check_gemini']['date_val']
        
        if items['factual_check_gemini']['factual_status']:
            if date_val == items['date']:
                events_lists += f"{loc}.{items['description']} ({date_val}) Fact-Check: ✓   cites:{num_cites}\n"
            else:
                events_lists += f"{loc}.{items['description']} ({date_val}) Fact-Check: ✓  (err_date) cites:{num_cites}\n"
        else:
            events_lists += f"{loc}.{items['description']} ({date_val}) Fact-Check: ✘  cites:{num_cites}\n"
        loc+=1 
    print(events_lists)
    
def quick_log(content,file_path=None):
    """
    Simple and fast log function.
    Appends content to the specified file with a timestamp.
    """
    assert file_path is not None 
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"[{now}] {content}\n")

def draw_bar_chart(stats_list , company):
    df = pd.DataFrame(stats_list)
    df = df.sort_values(by='total_events', ascending=False).reset_index(drop=True)
    df['id'] = range(1, len(df) + 1)
    df.to_csv('category_stats.csv', index=False)
    plt.figure(figsize=(10, 6))
    plt.bar(df['id'].astype(str), df['total_events'], color='skyblue', edgecolor='navy')

    plt.xlabel('Category ID')
    plt.ylabel('Total Events Count')
    plt.title('Events Distribution by Category (Sorted)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plt.savefig(f'seer/{company}_covariates.png')
    print("\n📊 [Category Mapping List]:")
    print("-" * 40)
    for _, row in df.iterrows():
        print(f"ID {row['id']:<3} | {row['category']:<20} | Total Events: {row['total_events']}")
    print("-" * 40)

def draw_bar_chart_with_fixed_covariates(stats_list, company, is_reference=False):
    """
    修改后的绘图函数：
    如果是基准文件(is_reference=True)，则进行排序；
    如果是后续文件，则保持传入的顺序。
    """
    df = pd.DataFrame(stats_list)
    
    # 只有基准文件需要在这里排序，其他的在传入前已经按基准对齐了顺序
    if is_reference:
        df = df.sort_values(by='total_events', ascending=False).reset_index(drop=True)
    
    # 分配统一的 ID
    df['id'] = range(1, len(df) + 1)
    
    plt.figure(figsize=(12, 6))
    plt.bar(df['id'].astype(str), df['total_events'], color='skyblue', edgecolor='navy')
    
    plt.xlabel('Category ID')
    plt.ylabel('Total Events Count')
    plt.title(f'Events Distribution - {company}')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # 确保保存路径存在
    plt.savefig(f'{company}_covariates.png')
    plt.close() # 绘图后关闭，防止多图重叠

    print(f"\n📊 [Category Mapping] for {company}:")
    for _, row in df.iterrows():
        print(f"ID {row['id']:<3} | {row['category']:<25} | Events: {row['total_events']}")
               
def plot_lines(data_list):
    days = list(range(1, len(data_list) + 1))
    plt.plot(days, data_list, linewidth=3, color='tab:blue', label='Categories')
    plt.xlabel(r'$\mathbf{Days}$', fontsize=12, fontweight='bold')
    plt.ylabel(r'$\mathbf{\#\ of\ covariate\ Categories}$', fontsize=12, fontewight='bold')
    plt.xticks(fontweight='bold')
    plt.yticks(fontweight='bold')
    plt.tight_layout()
    plt.savefig('covariate_plot.png', dpi=300)


# =============================================================================
# Utils for Search Task
# =============================================================================

def get_events_for_search(events_pool ,  cut_off_date=None , search_range = None):
    '''
        we only incude events released that day to the second round search!    
    '''
    events_lists = ''
    loc = 0
    for event in events_pool:
        
        # dict_keys(['date', 'description', 'causality', 'sentiment', 'impact_type', 'factual_check_gemini'])
        # [factual_status, date_val ,response_with_citations ,response_text , citations  ]
        
        g_status = event.get('factual_check_gemini', {}).get('factual_status', False)
        c_status = event.get('factual_check_claude', {}).get('factual_status', False)
        
        g_date = event.get('factual_check_gemini', {}).get('date_val', '')
        c_date = event.get('factual_check_claude', {}).get('date_val', '')
        
        # if g_status and c_status and g_date == c_date:
            
        if search_range:
            range_start, range_end = search_range
            loc += 1 
            if (g_date not in ['' , None]) and (range_start <= g_date <= range_end):
                events_lists += f"{loc}. {event['description']} ({g_date})\n"
            else:
                events_lists += f"{loc}. {event['description']}\n"
        else:
            if  c_date == cut_off_date:
                loc+=1 
                events_lists += f"{loc}.{event['description']} ({g_date})\n"

            # print('Pass ---------------------')
            # print( event['description'])
            # print(g_status  , g_date)
            # print(c_status  , c_date)
            
    if loc  == 0 :
        return None , loc 
        
    return events_lists[:-1] , loc 

def get_events_for_covariates(events_pool , model_name='gemini' , cut_off_date=None):
    '''
        we only incude events released that day to the second round search!    
    '''
    events_lists = ''
    loc = 0
    effective_events = []
    effective_dates = []
    for items in events_pool:
        # print('-'*100)
        # print(items['description'] ,  items[f'factual_check_{model_name}']['factual_status'])
        # print('-'*10)
        # print(items[f'factual_check_{model_name}']['response_text'])
        # dict_keys(['date', 'description', 'causality', 'sentiment', 'impact_type', 'factual_check_gemini'])
        # [factual_status, date_val ,response_with_citations ,response_text , citations  ]
        
        factual_check_date = items[f'factual_check_{model_name}']['date_val']
        if is_string_date_format(factual_check_date) : 
            loc+=1 
            events_lists += f"{loc}.{items['description']} ({factual_check_date})\n"
            effective_events.append(items['description'])
            effective_dates.append(factual_check_date)
    # print(events_lists)
    # exit()
    return events_lists[:-1] , effective_events ,  effective_dates


# =============================================================================
# Utils for Covariates Task (below)
# =============================================================================

def plot_covariates_distribution(covariates_pool , company):
    stats_list = []
    for cat, dates in covariates_pool.items():
        total_events = sum(len(evs) for evs in dates.values())
        stats_list.append({'category': cat, 'total_events': total_events})
    draw_bar_chart(stats_list , company)

def plot_covariates_distributions(covariates_pool , company):
    round_file_save_path1='/usr/local/google/home/mingtiant/Documents/forecast_agent/seer/event-driven-time-series/stock/events/META/gemini-2025-12-01-covariates.json'
    round_file_save_path2='/usr/local/google/home/mingtiant/Documents/forecast_agent/seer/event-driven-time-series/stock/events/NVDA/gemini-2025-12-01-covariates.json'
    round_file_save_path3='/usr/local/google/home/mingtiant/Documents/forecast_agent/seer/event-driven-time-series/stock/events/GOOGL/gemini-2025-12-01-covariates.json'
    # covariates_pool = load_json_to_list(round_file_save_path) 
    
    stats_list = []
    for cat, dates in covariates_pool.items():
        total_events = sum(len(evs) for evs in dates.values())
        stats_list.append({'category': cat, 'total_events': total_events})
    draw_bar_chart(stats_list , company)

def get_exist_covariates_list(covariates_pool , events_thr = 5):
    covariates_list = []
    for cat, dates in covariates_pool.items():
        total_events = sum(len(evs) for evs in dates.values())
        if total_events > events_thr :
            covariates_list.append(cat)
        # print(f"category:{cat} , total_events:{total_events}")
    return covariates_list
    
def format_print_covariates(covariates_pool, max_event_len=100, indent_size=4 ,domain_covariates = []  ):
    def truncate(text):
        if isinstance(text, str) and len(text) > max_event_len:
            return text[:max_event_len] + "..."
        return str(text)
    
    # print("\n" + "="*50)
    # print(f"{'COVARIATES POOL SUMMARY':^50}")
    # print("="*50)
    
    print(f"📊 [Pool Stats] Categories: {len(covariates_pool)}")
    if domain_covariates != []:
        missing_keys = set(covariates_pool.keys()) - set(domain_covariates)
        missing_keys_list = list(missing_keys)
        print(f'[# of New Covariates]:{len(missing_keys_list)}' , missing_keys_list)
        
    # for cat, dates in covariates_pool.items():
    #     total_events = sum(len(evs) for evs in dates.values())
    #     print(f"  - {cat}: {len(dates)} dates, {total_events} total events")
    
    for category, date_map in covariates_pool.items():
        print(f"📂 {category}")
        
        sorted_dates = sorted(date_map.keys())
        
        for date in sorted_dates:
            events = date_map[date]
            print(f"{' ' * indent_size}📅 {date}")

            if not events:
                print(f"{' ' * (indent_size * 2)} (No events)")
                continue
                
            for i, event in enumerate(events, 1):
                truncated_event = truncate(event)
                print(f"{' ' * (indent_size * 2)}• {truncated_event}")

    print("\n" + "="*50 + "\n")

def pretty_print_results(reasoning_dict, taxonomy_dict):
    """
    Prints the reasoning and taxonomy dictionaries.
    Feature: Taxonomy lists are printed on a SINGLE LINE per category for compactness.
    """
    
    # --- 1. 打印分类结果 (Taxonomy) - 紧凑模式 ---
    print("\n" + "="*80)
    print("📊 MASTER TAXONOMY STRUCTURE (Compact View)")
    print("="*80)
    K=1 
    for category, tags in taxonomy_dict.items():
        # 使用 json.dumps 处理列表，不加 indent 参数，它就会自动变成单行字符串
        # ensure_ascii=False 确保中文（如果有）能正常显示
        tags_line = json.dumps(tags, ensure_ascii=False)
        
        # 打印格式： 分类名: [标签1, 标签2, ...]
        print(f"🔹 {K}.{category} ({len(tags)}):")
        print(f"   {tags_line}")
        # print("-" * 40) # 弱分隔线
        K+=1

    # --- 2. 打印推理逻辑 (Reasoning) ---
    print("\n" + "="*80)
    print("🧠 REASONING LOGIC (Detailed Mapping)")
    print("="*80)
    
    sorted_keys = sorted(reasoning_dict.keys())
    
    for i, key in enumerate(sorted_keys, 1):
        reason = reasoning_dict[key]
        print(f"{i:02d}. {key}") 
        print(f"   ↳ {reason}")
        # print("-" * 40) # 这里可以选择是否保留分隔线，看你喜好
        
def get_init_master_taxonomy():
    """
    Parses the agent output to extract reasoning and taxonomy into separate dictionaries
    and saves them to JSON files.
    """
    raw_text = prompt.INIT_MASTERS
    # --- Part 1: Extract Reasoning (Convert to Dict) ---
    reasoning_dict = {}
    
    # Locate content within <reason> tags
    reason_block = re.search(r"<reason>(.*?)</reason>", raw_text, re.DOTALL)
    
    if reason_block:
        content = reason_block.group(1).strip()
        # Regex to match lines like: "1. ANALYST_RATING: Maps to..."
        # Captures Group 1 (Tag Name) and Group 2 (Reason Text)
        pattern = re.compile(r"^\d+\.\s*([A-Z_]+):\s*(.*)", re.MULTILINE)
        
        matches = pattern.findall(content)
        for tag, reason in matches:
            reasoning_dict[tag] = reason.strip()
    
    # --- Part 2: Extract Taxonomy Result (Parse JSON block) ---
    taxonomy_dict = {}
    
    # Locate content within ```json code blocks
    json_block = re.search(r"```json(.*?)```", raw_text, re.DOTALL)
    
    if json_block:
        try:
            json_str = json_block.group(1).strip()
            taxonomy_dict = json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON block: {e}")

    # --- Part 3: Save to Files ---
    
    # Save reasoning.json
    save_path = '/usr/local/google/home/mingtiant/Documents/forecast_agent/seer/event-driven-time-series/stock/'
    with open(save_path+'reasoning.json', 'w', encoding='utf-8') as f:
        json.dump(reasoning_dict, f, indent=4, ensure_ascii=False)
    
    # Save taxonomy_result.json
    with open(save_path+'taxonomy_result.json', 'w', encoding='utf-8') as f:
        json.dump(taxonomy_dict, f, indent=4, ensure_ascii=False)

    # print(len(reasoning_dict))
    # print(len(taxonomy_dict))
    # print("✅ Successfully saved 'reasoning.json' and 'taxonomy_result.json'")
    # pretty_print_results(reasoning_dict, taxonomy_dict)
    return reasoning_dict, taxonomy_dict

def get_ref_from_initiled_taxonomy():
    list_of_covariates =''
    save_path = '/usr/local/google/home/mingtiant/Documents/forecast_agent/seer/event-driven-time-series/stock/taxonomy_result.json'
    try:
        with open(save_path, 'r', encoding='utf-8') as f:
            taxonomy_dict = json.load(f)
        
        lines = []
        loc=1 
        for master_tag, sub_tags in taxonomy_dict.items():
            examples = sub_tags[:3]
            
            # "MASTER_TAG: Sub1, Sub2, Sub3, ..."
            example_str = ", ".join(examples)
            formatted_line = f"{loc}. {master_tag}: {example_str}, ..."
            loc +=1 
            lines.append(formatted_line)
            
        list_of_covariates = "\n".join(lines)

    except FileNotFoundError:
        print(f"Error: File not found at {save_path}")
        return ""
    except Exception as e:
        print(f"Error parsing taxonomy: {e}")
        return ""
    return  list_of_covariates



# =============================================================================
# Utils for Files 
# =============================================================================
import os
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
    

# =============================================================================
# API Query 
# =============================================================================
from seer.backend.backend_gemini import query as gemini_query
from seer.backend.backend_antropic_vertax import query as claude_query
def query_gemini(sys_msg , user_msg , history=None , citations_need = False ,
                     web_search = True , model_name = None , max_output_tokens = None ):
    # model="gemini-3-pro-preview", 
    
    if model_name :
        print("Assigned Model:"  , model_name)
        result = gemini_query(
            system_message=sys_msg,
            user_message=user_msg,
            citations_need=citations_need,
            history_messages=history,
            model=model_name, 
            temperature=0.7,         
            max_output_tokens=max_output_tokens,
            web_search = web_search, 
            # response_logprobs = True, 
            # logprobs=3
        )
        
    else:
        result = gemini_query(
            system_message=sys_msg,
            user_message=user_msg,
            citations_need=citations_need,
            history_messages=history,
            model="gemini-3.1-pro-preview", 
            temperature=0.7,         
            max_output_tokens=max_output_tokens,
            web_search = web_search, 
            # responseLogprobs = True, 
            # logprobs=3
        )

    return result["response_text"] , result["response_with_citations"] , result['citations']
    
def query_claude(sys_msg , user_msg , web_search = True , max_tokens =4096  ,  model_name=None):
    
    if web_search : 
        tools = [{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 5
        }]
    else:
        print('Web Search Closed!')
        tools = []
        
    if model_name:
        print(model_name)
        response = claude_query(
            system_message=sys_msg,
            user_message=user_msg,
            model=model_name,
            max_tokens=max_tokens,
            temperature=0.7,
            tools=tools
        )
    else:
        # print('Defual:' , model_name , 'claude-sonnet-4-5')
        response = claude_query(
            system_message=sys_msg,
            user_message=user_msg,
            model='claude-sonnet-4-5',
            max_tokens=max_tokens,
            temperature=0.7,
            tools=tools
        )
        
    return response["response_text"] , None  , response['citations'] 


def smart_print(text: str, max_length: int = 1500) -> None:
    """
    智能打印函数：如果文本超过 max_length，则截取“开头”和“结尾”，
    中间部分用提示信息代替。
    """
    current_length = len(text)
    
    if current_length <= max_length:
        return text

    placeholder = f"\n... [hidden {current_length - max_length} characters] ...\n"
    keep_length = (max_length - len(placeholder)) // 2

    head = text[:keep_length]
    tail = text[-keep_length:]
    
    truncated_text = f"{head}{placeholder}{tail}"
    
    return truncated_text