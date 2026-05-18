import argparse
import pandas as pd
import json , uuid , time , os , sys

from collections import defaultdict
import pandas as pd
import re 

def check_bool(val):
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() == 'true'
    return False
    
def load_and_filter_events(args, ticker, start_date, end_date, base_data_path , search_round):

    ticker = ticker.replace(" ", "_")

    base_path = f"{base_data_path}/{args.domain}/events"

    validated_events_dict = defaultdict(list)

    if 'taxi' in args.domain:
        ticker_event_path = os.path.join(base_path, 'NYC')
    else:
        ticker_event_path = os.path.join(base_path, ticker) 

    impact_types_to_track = ["Direct", "Indirect", "Neutral"]
    impact_stats = {k: {'total': 0, 'kept': 0} for k in impact_types_to_track}

    if not os.path.exists(ticker_event_path):
        print(f"⚠️ Warning: Events path does not exist: {ticker_event_path}")
        return dict(validated_events_dict)

    if 'weather' in  args.domain:
        search_pattern = os.path.join(ticker_event_path, f"gemini-*-{search_round}.json")
    else:
        search_pattern = os.path.join(ticker_event_path, f"gemini-*_to_*-{search_round}.json")

    files = glob.glob(search_pattern)
    
    assert len(files) > 1 

    total_events_kept = 0
    total_events_get = 0 

    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                events_list = json.load(f)
                
            if not isinstance(events_list, list):
                continue
                
            for event in events_list:
                raw_impact = event.get("impact_type", "Unknown")
                date_val = event.get("date", "Unknown")

                    

                if raw_impact in impact_stats:
                    impact_stats[raw_impact]['total'] += 1
                total_events_get += 1 
                
                is_3_check_agent = ('factual_check_gemini_0' in event) and ('factual_check_gemini_1' in event)
                if not is_3_check_agent :
                    fc_g = event.get("factual_check_gemini", {})
                    fc_c  = event.get("factual_check_claude", {})
                    
                    status_g0 = check_bool(fc_g.get("factual_status"))
                    status_c  = check_bool(fc_c.get("factual_status"))
                    
                    date_g0 = fc_g.get("date_val")
                    date_c  = fc_c.get("date_val")
                    
                    # Filtering Condition: Statuses and Dates must match
                    statuses_match = (status_g0  == status_c) and (status_g0 is not None)
                    dates_match = (date_g0  == date_c) and (date_g0 is not None)
                    
                    if statuses_match and dates_match:
                        date_val = date_g0
                    else:
                        continue 
                else:
                    gemini_check = event.get('factual_check_gemini_0', {})
                    claude_check = event.get('factual_check_gemini_1', {})
                    
                    c_status = check_bool(claude_check.get('factual_status'))
                    g_status = check_bool(gemini_check.get('factual_status'))
                    
                    c_date = claude_check.get('date_val')
                    g_date = gemini_check.get('date_val')
                    
                    if c_status and g_status and c_date == g_date:
                        date_val = c_date
                    else:
                        continue 

                if not date_val: continue
                # event_dt = pd.to_datetime(date_val, errors='coerce')
                # if pd.isna(event_dt) or event_dt < global_start_dt or event_dt > global_end_dt:
                    # continue

                structured_event = {
                    "id": str(uuid.uuid4()),
                    "event": event.get("description", ""),
                    "sentiment": event.get("sentiment", "N/A"),
                    "impact_type": raw_impact
                }
                
                validated_events_dict[date_val].append(structured_event)
                total_events_kept += 1
                if raw_impact in impact_stats:
                    impact_stats[raw_impact]['kept'] += 1

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            continue 
                
    if total_events_get > 0:
        overall_r = 100 * total_events_kept / total_events_get
        print(f"✅ [{ticker}] Extracted {total_events_kept}/{total_events_get} events ({overall_r:.1f}% Kept)")
    else:
        print(f"⚠️ No events found for {ticker}")

    return dict(validated_events_dict)
        
def prt_time_series(args , result_list):
    if not result_list:
        print("❌ 获取数据失败或数据为空，程序退出。")
        time.sleep(10000)
    else:
        # 2. 将列表转换回 DataFrame 用于后续过滤与打印
        df = pd.DataFrame(result_list)
        df['date_dt'] = pd.to_datetime(df['date'])
        start_ts = pd.to_datetime(args.start_date) if args.start_date else df['date_dt'].min()
        end_ts = pd.to_datetime(args.end_date) if args.end_date else df['date_dt'].max()
        
        # 根据时间范围过滤数据
        mask = (df['date_dt'] >= start_ts) & (df['date_dt'] <= end_ts)
        filtered_df = df.loc[mask].copy()

        filtered_df.sort_values('date_dt', inplace=True)
        record_count = len(filtered_df)
        print(f"\n✅ Data Loaded Successfully!")
        print(f"   Time Range: {start_ts.date()} to {end_ts.date()}")
        print(f"   Records   : {record_count}")
        if record_count > 0:
            print("\n--- Head (First 5) ---")
            print(filtered_df[['date', 'value']].head().to_string(index=False))
            print("\n--- Tail (Last 5) ---")
            print(filtered_df[['date', 'value']].tail().to_string(index=False))


import glob
def get_time_series(args , base_data_path):
    """
    根据给定的 args.domain 和 args.ticker 获取并处理时间序列数据。
    返回格式为: [{'date': 'YYYY-MM-DD HH:MM:SS', 'value': float}, ...] (按小时聚合)
    """
    domain = str(args.domain).lower()
    ticker = str(args.ticker)
    
    # ==========================================
    # 1. Elec Demand time series 
    # ==========================================
    if "elec" in domain:
        elec_dir = os.path.join(base_data_path, "elec", "values")
        search_pattern = os.path.join(elec_dir, f"{ticker}_Load_*.csv")
        files = glob.glob(search_pattern)
        
        if not files:
            raise ValueError(f"❌ No {ticker} data in {search_pattern}")

        target_file = files[0]
        try:
            df = pd.read_csv(target_file, usecols=["Time", "Load"])
            # 🌟 修复时区错位UTC：截取前 19 个字符 (YYYY-MM-DD HH:MM:SS) 
            # 强行剥离时区偏移，100% 锁死当地的表盘时间
            df['Time'] = df['Time'].str[:19]
            
            # 此时转换 datetime，就是单纯的当地时间 (Naive Datetime)
            df['Time'] = pd.to_datetime(df['Time'])
            df.set_index('Time', inplace=True)
            
            # 现在的 resample 是完全按照当地的 0点、1点、2点 进行精确聚合的
            df_hourly = df['Load'].resample('1h').mean().dropna().reset_index()
            
            # 格式化回字符串
            df_hourly['Time'] = df_hourly['Time'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            df_hourly.rename(columns={'Time': 'date', 'Load': 'value'}, inplace=True)
            
            return df_hourly.to_dict(orient='records')
            
        except Exception as e:
            print(f"❌ 读取 elec 数据失败 ({ticker}): {e}")
            time.sleep(100000)

    elif "weather" in domain:
        ticker = ticker.replace(" ", "_")
        weather_dir = os.path.join(base_data_path, "weather", "values")
        target_file = os.path.join(weather_dir, f"{ticker}.csv")
        
        if not os.path.exists(target_file):
            print(f"❌ Weather data file not found: {target_file}")
            sys.exit(1) 
        try:
            time_col = "time" # Update if your CSV uses 'datetime' or 'date'
            df = pd.read_csv(target_file, usecols=[time_col, "temp"])
            df[time_col] = pd.to_datetime(df[time_col])
            df.set_index(time_col, inplace=True)
            df_hourly = df['temp'].resample('1h').mean().dropna().reset_index()
            df_hourly[time_col] = df_hourly[time_col].dt.strftime('%Y-%m-%d %H:%M:%S')
            df_hourly.rename(columns={time_col: 'date', 'temp': 'value'}, inplace=True)
            return df_hourly.to_dict(orient='records')
        except Exception as e:
            print(f"❌ Failed to read weather data ({ticker}): {e}")
            sys.exit(1)
    # ==========================================
    # 2. taxi 
    # domain: taxi
    # ticker : "green_passenger_count"
    # ==========================================
    elif "taxi" in domain:
        parts = ticker.split('_', 1)
        if len(parts) != 2:
            print(f"❌ 无效的 taxi ticker 格式: {ticker}")
            time.sleep(100000)
            
        taxi_type = parts[0]
        target_col = parts[1]
        taxi_dir = os.path.join(base_data_path, "taxi/values")
        
        search_pattern = os.path.join(taxi_dir, f"{taxi_type}_tripdata_*.parquet")
        files = glob.glob(search_pattern)
        
        if not files:
            print(f"❌ 未找到 {taxi_type} 的出租车数据文件 ")
            print(taxi_dir , f"{taxi_type}_tripdata_*.parquet")
            time.sleep(100000)
            
        # 提取月份并排序
        months_found = []
        for f in files:
            basename = os.path.basename(f)
            # 正则提取 YYYY-MM
            match = re.search(r'(\d{4}-\d{2})', basename)
            if match:
                months_found.append(match.group(1))
                
        months_found = sorted(list(set(months_found)))
        if not months_found:
            print("❌ 未能从文件名中解析出任何有效月份。")
            time.sleep(100000)

        # 🌟 检查月份连续性
        start_month = pd.to_datetime(months_found[0])
        end_month = pd.to_datetime(months_found[-1])
        
        # 生成期望的连续月份列表 (freq='MS' 代表月初)
        expected_months_dt = pd.date_range(start=start_month, end=end_month, freq='MS')
        expected_months = expected_months_dt.strftime('%Y-%m').tolist()
        
        missing_months = set(expected_months) - set(months_found)
        if missing_months:
            print(f"⚠️ 警告：检测到缺失的月份数据: {sorted(list(missing_months))}")
        else:
            print(f"✅ 月份连续性检查通过: {months_found[0]} 至 {months_found[-1]}")
            
        # 根据动态识别出的最小和最大月份，计算合法的边界时间（用于过滤脏数据）
        valid_start_time = start_month
        valid_end_time = end_month + pd.DateOffset(months=1) # 包含最后那个月的全月
        
        resampled_dfs = []
        for month in months_found:
            filename = f"{taxi_type}_tripdata_{month}.parquet"
            file_path = os.path.join(taxi_dir, filename)
            
            try:
                df = pd.read_parquet(file_path, engine='pyarrow')
                
                time_cols = [col for col in df.columns if 'pickup_datetime' in col.lower()]
                time_col = time_cols[0]
                
                if target_col not in df.columns:
                    print(f"⚠️ 列 '{target_col}' 不在文件 {filename} 中")
                    time.sleep(100000)
                
                df[time_col] = pd.to_datetime(df[time_col])
                
                # 🌟 使用动态生成的边界时间过滤脏数据
                mask = (df[time_col] >= valid_start_time) & (df[time_col] < valid_end_time)
                df = df[mask].copy()
                
                df.set_index(time_col, inplace=True)

                df_hourly = df[[target_col]].resample('1h').mean()
                resampled_dfs.append(df_hourly)
                
            except Exception as e:
                print(f"⚠️ 处理 {filename} 时出错: {e}")
                
        if not resampled_dfs:
            print(f"❌ 没有成功处理 {ticker} 的任何 taxi 数据。")
            time.sleep(1000000)
        
        # final_df = pd.concat(resampled_dfs).groupby(level=0).mean().dropna().reset_index()

        final_df = pd.concat(resampled_dfs).sort_index().dropna().reset_index()
        # duplicates = final_df[final_df.index.duplicated(keep=False)].sort_index()
        # if not duplicates.empty:
        #     print("\n🚨 发现跨月重叠（重复）的时间数据！详细如下：")
        #     print(duplicates)
        #     print("-" * 50)

        time_col = final_df.columns[0]
        final_df[time_col] = final_df[time_col].dt.strftime('%Y-%m-%d %H:%M:%S')
        final_df.rename(columns={time_col: 'date', target_col: 'value'}, inplace=True)
        return final_df.to_dict(orient='records')

    else:
        print(f"❌ 不支持的 domain 类型: {domain}")
        return []

def data_loader(args , base_data_path , search_round):
    print(f"--- Configuration ---")
    print(f"City (Ticker) : {args.ticker}")
    print(f"Start Date    : {args.start_date}")
    print(f"End Date      : {args.end_date}")
    print(f"Workers       : {args.workers}")
    print(f"PATH          : {base_data_path}")

    if not args.ticker:
        print("❌ Error: Ticker (City name) is required!")
        sys.exit(1)
    
    print(f"📡 Fetching valueerature data for {args.ticker}...")
    result_list = get_time_series(args , base_data_path)
    prt_time_series(args , result_list)
    validated_events_dict = load_and_filter_events(args, \
                args.ticker , args.start_date , args.end_date , base_data_path , search_round)
    return result_list, validated_events_dict
    