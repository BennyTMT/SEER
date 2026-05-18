import json
import numpy as np 
import pandas as pd
import os
import glob

# DATA_BASE_PATH = '/home/mingtiant_google_com/google_intern_data'
DATA_BASE_PATH = '.'


'''

Could you help with the following updates for the uploaded python code:
Translate all Chinese comments and print statements into English.
Remove all "python -m" execution comments
Change all "seer" to "leaf" in the code 
Keep the rest of the original code strictly unchanged.
Remove all personal information comments or dir include "mingtian"
Code:





    /home/mingtiant_google_com/google_intern_data/data/stock/events
    
'''

TICKER_MAPING={
    'fed_interest_Jan_2026':
        {   
            'type':'ECON',
            'event': "Fed increases interest rates by 25+ bps after January 2026 meeting?",
            'cut_off_date': '2026-01-28'
        },
    "us_gov_shutdown_jan_30_2026":
        {   
            'type': 'POL', 
            'event': 'US Government Shutdown',
            'cut_off_date': '2026-01-30',
            'start_date': "2026-01-10", 
            'end_date': "2026-01-30", 
        },
    "nominate_fed_chair":
        {
            'type': 'POL', 
            'event': "Who will Trump nominate as Fed Chair?",
            'cut_off_date': '2026-01-30',
            'start_date': "2025-12-25", 
            'end_date': "2026-01-30", 
        },
    "khamenei_out_iran_leader":
        {
            'type': 'POL', 
            'event': "Khamenei out as Supreme Leader of Iran by March 31?",
            'cut_off_date': '2026-03-31',
            'start_date': "2026-01-01", 
            'end_date': "2026-02-02", 
        }
}

def get_company_infos():
    
    # Ticker 到 公司官方全名 的映射字典
    ticker_to_name = {
        # --- Magnificent Seven (Tech Giants) ---
        "META": "Meta Platforms, Inc.",
        "AAPL": "Apple Inc.",
        "NVDA": "NVIDIA Corporation",
        "MSFT": "Microsoft Corporation",
        "GOOGL": "Alphabet Inc.",
        "AMZN": "Amazon.com, Inc.",
        "TSLA": "Tesla, Inc.",

        # --- Semiconductors ---
        "AMD": "Advanced Micro Devices, Inc.",
        "INTC": "Intel Corporation",
        "TSM": "Taiwan Semiconductor Manufacturing Company Limited",
        "AVGO": "Broadcom Inc.",
        "QCOM": "Qualcomm Incorporated",

        # --- Software / Media ---
        "NFLX": "Netflix, Inc.",
        "DIS": "The Walt Disney Company",
        "ADBE": "Adobe Inc.",
        "CRM": "Salesforce, Inc.",
        "ORCL": "Oracle Corporation",

        # --- Finance / Payments ---
        "JPM": "JPMorgan Chase & Co.",
        "BAC": "Bank of America Corporation",
        "V": "Visa Inc.",
        "MA": "Mastercard Incorporated",

        # --- Consumer / Retail ---
        "WMT": "Walmart Inc.",
        "COST": "Costco Wholesale Corporation",
        "KO": "The Coca-Cola Company",
        "PEP": "PepsiCo, Inc.",
        "PG": "The Procter & Gamble Company",

        # --- Healthcare ---
        "JNJ": "Johnson & Johnson",
        "PFE": "Pfizer Inc.",
        "LLY": "Eli Lilly and Company",

        # --- Space ---
        "RDW": "Redwire Corporation",
        "RKLB": "Rocket Lab USA, Inc.", 

        # ==========================================
        # 阵营一：多巴胺与新金融 (高波动、加密货币与投机属性)
        # 适合策略：监控加密周期、政策放开预期、极端情绪逼空
        # ==========================================
        "DKNG": "DraftKings Inc.",
        "SOFI": "SoFi Technologies, Inc.",
        "SQ": "Block, Inc.",
        "COIN": "Coinbase Global, Inc.",
        "HOOD": "Robinhood Markets, Inc.",
        # --- 补充新增 ---
        "MSTR": "MicroStrategy Incorporated", # 纯粹的比特币高倍杠杆
        "AFRM": "Affirm Holdings, Inc.",      # 消费降级与信贷坏账周期的放大器

        # ==========================================
        # 阵营二：数字原生与注意力经济 (社交、游戏与年轻流量)
        # 适合策略：财报日内剧烈波动(IV Crush)、用户数据突发异动
        # ==========================================
        "RDDT": "Reddit, Inc.",
        "RBLX": "Roblox Corporation",
        "DUOL": "Duolingo, Inc.",
        "U": "Unity Software Inc.",
        # --- 补充新增 ---
        "SE": "Sea Limited",                  # 东南亚“腾讯+阿里”，游戏与电商流量变现

        # ==========================================
        # 阵营三：新世代消费信仰 (狂热的品牌忠诚度与高速扩张)
        # 适合策略：强劲动量(Momentum)追踪、打破传统华尔街估值偏见
        # ==========================================
        "CELH": "Celsius Holdings, Inc.",
        "CAVA": "CAVA Group, Inc.",
        "ONON": "On Holding AG",
        "ELF": "e.l.f. Beauty, Inc.",
        # --- 补充新增 ---
        "CVNA": "Carvana Co.",                # 二手车电商，困境反转与散户逼空的极致体现
        "CPNG": "Coupang, Inc.",              # 亚洲亚马逊，自由现金流收割期的消费巨头
        "TOST": "Toast, Inc.",                # 餐饮SaaS，美国线下餐饮消费与通胀的晴雨表

        # ==========================================
        # 阵营四：散户的“硬核科幻浪漫” (太空、机器人与高分歧标的)
        # 适合策略：大订单/政府合同事件驱动、两极分化带来的定价错位
        # ==========================================
        "PLTR": "Palantir Technologies Inc.",
        "RIVN": "Rivian Automotive, Inc.",
        "RKLB": "Rocket Lab USA, Inc.",
        "SYM": "Symbotic Inc.",
        # --- 补充新增 ---
        "ASTS": "AST SpaceMobile, Inc.",      # 低轨卫星直连手机，长线看组网商业化里程碑
        "JOBY": "Joby Aviation, Inc.",        # eVTOL飞行汽车，长线紧盯FAA适航认证节点
        "FSLR": "First Solar, Inc.",          # 本土太阳能，科技巨头清洁能源订单的直接受益者

        # ==========================================
        # 阵营五：AI 周期里的“卖水人”与“边缘颠覆者”
        # 适合策略：监控大厂资本支出(CapEx)溢出效应、技术落地反转
        # ==========================================
        "ALAB": "Astera Labs, Inc.",
        "APP": "AppLovin Corporation",
        "MDB": "MongoDB, Inc.",
        "NET": "Cloudflare, Inc.",
        # --- 补充新增 (AI基建、液冷、网络与软件深水区) ---
        "VST": "Vistra Corp.",                # AI数据中心核电供应商
        "CEG": "Constellation Energy Corporation", # AI清洁能源底座
        "VRT": "Vertiv Holdings Co",          # 数据中心液冷与温控核心标的
        "SMCI": "Super Micro Computer, Inc.", # 高波动服务器集成商
        "MRVL": "Marvell Technology, Inc.",   # 定制化ASIC芯片与高速光通信
        "COHR": "Coherent Corp.",             # AI光模块与底层材料
        "SNOW": "Snowflake Inc.",             # 云数据仓库，多空博弈最剧烈的SaaS之一
        "DDOG": "Datadog, Inc.",              # 云监控龙头，企业IT支出复苏风向标
        "ZS": "Zscaler, Inc.",                # 零信任网络安全龙头
        "S": "SentinelOne, Inc.",             # 高弹性AI驱动网络安全平台
        "PATH": "UiPath Inc.",                # RPA自动化，AI智能体时代的边缘颠覆/被颠覆者

        # ==========================================
        # 阵营六：颠覆性生物医药 (纯粹的结构性数据驱动) [新增阵营]
        # 适合策略：围绕FDA审批节点和三期临床数据公布日进行事件驱动交易
        # ==========================================
        "VKTX": "Viking Therapeutics, Inc.",  # GLP-1减肥药赛道的高倍弹性妖股
        "CRSP": "CRISPR Therapeutics AG" ,     # 基因编辑商业化先驱，长线逻辑纯看临床数据

        'UNH': 'UnitedHealth Group Incorporated',
        'HD': 'The Home Depot, Inc.', 
        'BRK-B': 'Berkshire Hathaway Inc.',
        'XOM': 'Exxon Mobil Corporation'

}
    
   
    ticker_to_company_info = {
        # --- Magnificent Seven (Tech Giants) ---
        "META": "Meta Platforms, Inc. (formerly Facebook) is the world's largest social media company, owning Facebook, Instagram, WhatsApp, and Threads. It generates revenue primarily through digital advertising. The company is currently heavily investing in Artificial Intelligence (Llama models) and the Metaverse (Reality Labs).",
        "AAPL": "Apple Inc. designs, manufactures, and markets smartphones (iPhone), personal computers (Mac), tablets (iPad), and wearables (Apple Watch). It has a massive services business (App Store, iCloud, Apple Music). Apple is known for its premium brand ecosystem and high profit margins.",
        "NVDA": "NVIDIA Corporation is the dominant global supplier of Artificial Intelligence hardware and software. Its GPUs (Graphics Processing Units) are the industry standard for gaming, professional visualization, and most importantly, data centers training Large Language Models (LLMs).",
        "MSFT": "Microsoft Corporation is a global technology leader providing software (Windows, Office/365), cloud computing (Azure), and gaming (Xbox). It is a major investor in OpenAI (ChatGPT) and is integrating AI Copilots across its entire product suite.",
        "GOOGL": "Alphabet Inc. is the parent company of Google. It dominates global search, digital advertising, and mobile operating systems (Android). It owns YouTube and Google Cloud. The company is a pioneer in AI research (DeepMind, Gemini) and autonomous driving (Waymo).",
        "AMZN": "Amazon.com, Inc. is the world's largest e-commerce retailer and cloud computing provider (AWS). It operates a massive logistics network, subscription services (Prime), and advertising business. AWS is a critical profit driver, powering a vast portion of the internet.",
        "TSLA": "Tesla, Inc. designs and manufactures electric vehicles (EVs), battery energy storage systems, and solar products. Led by Elon Musk, the company is also heavily focused on autonomous driving technology (FSD) and robotics (Optimus).",

        # --- Semiconductors ---
        "AMD": "Advanced Micro Devices (AMD) designs high-performance computing, graphics, and visualization technologies. It competes directly with Intel in CPUs (Ryzen/EPYC) and with NVIDIA in GPUs (MI300 series), positioning itself as a key player in the AI hardware market.",
        "INTC": "Intel Corporation is one of the world's largest semiconductor chip manufacturers. Unlike many competitors who are fabless, Intel designs and manufactures its own chips (IDM). It is currently undergoing a massive transformation to expand its foundry services (IFS) to manufacture chips for others.",
        "TSM": "Taiwan Semiconductor Manufacturing Company (TSMC) is the world's largest dedicated semiconductor foundry. It manufactures chips for Apple, NVIDIA, AMD, and Qualcomm. It possesses the most advanced process technology (3nm, 5nm) and is the bottleneck of the global AI supply chain.",
        "AVGO": "Broadcom Inc. is a global technology leader in semiconductor and infrastructure software solutions. It focuses on networking, broadband, and wireless connectivity. It recently acquired VMware, expanding its footprint in enterprise software and cloud infrastructure.",
        "QCOM": "Qualcomm Incorporated is a global leader in wireless technology and the driving force behind the development of 5G. It designs processors (Snapdragon) for the vast majority of Android smartphones and owns essential patents for mobile communications.",

        # --- Software / Media ---
        "NFLX": "Netflix, Inc. is the world's leading streaming entertainment service. It offers TV series, documentaries, feature films, and mobile games. It pioneered the subscription streaming model and invests heavily in original content production globally.",
        "DIS": "The Walt Disney Company is a diversified international family entertainment and media enterprise. It owns theme parks (Disney World), film studios (Marvel, Pixar, Star Wars, Disney Animation), TV networks (ESPN, ABC), and streaming services (Disney+, Hulu).",
        "ADBE": "Adobe Inc. is the global leader in digital media and digital marketing software. Its Creative Cloud (Photoshop, Premiere, Illustrator) is the industry standard for creatives. It is aggressively integrating Generative AI (Firefly) into its tools.",
        "CRM": "Salesforce, Inc. is the world's #1 Customer Relationship Management (CRM) platform. It provides cloud-based software for sales, service, marketing, and analytics (Tableau). It is focused on integrating AI (Einstein) into enterprise workflows.",
        "ORCL": "Oracle Corporation provides products and services that address enterprise information technology environments. It is known for its database software, ERP systems, and increasingly, Oracle Cloud Infrastructure (OCI), which is gaining traction in AI training workloads.",

        # --- Finance / Payments ---
        "JPM": "JPMorgan Chase & Co. is the largest bank in the United States and a global leader in financial services. Its businesses include investment banking, commercial banking, financial transaction processing, and asset management.",
        "BAC": "Bank of America Corporation is one of the world's leading financial institutions, serving individual consumers, small and middle-market businesses, and large corporations with a full range of banking, investing, and asset management products.",
        "V": "Visa Inc. is a global payments technology company that connects consumers, businesses, banks, and governments. It does not issue cards or extend credit but operates the payment processing network (VisaNet) that facilitates transactions.",
        "MA": "Mastercard Incorporated is a global technology company in the payments industry. Like Visa, it operates a payment processing network connecting financial institutions, merchants, and consumers worldwide.",

        # --- Consumer / Retail ---
        "WMT": "Walmart Inc. is the world's largest retailer by revenue. It operates a chain of hypermarkets, discount department stores, and grocery stores. It is known for its massive scale, supply chain efficiency, and 'Everyday Low Prices' strategy.",
        "COST": "Costco Wholesale Corporation operates an international chain of membership warehouses. It is known for selling high-quality products in bulk at low prices. Its membership model creates high customer loyalty and recurring revenue.",
        "KO": "The Coca-Cola Company is a total beverage company. It owns and markets some of the world's most famous non-alcoholic beverage brands, including Coca-Cola, Sprite, Fanta, and Dasani. It is a classic 'value' stock with a long history of dividends.",
        "PEP": "PepsiCo, Inc. is a global food and beverage leader. Unlike Coca-Cola, it has a massive snack food business (Frito-Lay, Cheetos, Doritos) in addition to its beverages (Pepsi, Gatorade, Mountain Dew), offering more diversification.",
        "PG": "The Procter & Gamble Company (P&G) is a multinational consumer goods corporation. It owns household name brands like Tide, Pampers, Gillette, Crest, and Head & Shoulders. It is considered a defensive stock due to stable demand for daily necessities.",

        # --- Healthcare ---
        "JNJ": "Johnson & Johnson is a diversified healthcare giant. It focuses on Innovative Medicine (Pharmaceuticals) and MedTech (Medical Devices). It recently spun off its consumer health division (Kenvue, maker of Tylenol/Band-Aid) to focus on higher-growth areas.",
        "PFE": "Pfizer Inc. is a major global pharmaceutical company. It is known for developing vaccines (including the COVID-19 mRNA vaccine) and drugs for oncology, inflammation, and rare diseases. It is currently navigating a post-pandemic transition.",
        "LLY": "Eli Lilly and Company is a global pharmaceutical leader. It has recently become the most valuable healthcare company in the world, driven largely by the massive success of its GLP-1 drugs (Mounjaro/Zepbound) for diabetes and weight loss treatment.",

        "RDW": "Redwire Corporation is a leading provider of mission-critical space infrastructure. It specializes in solar power generation (iROSA), deployable structures, and in-space manufacturing technology. The company serves as a key hardware supplier for NASA's Artemis program and commercial space stations, focusing on the foundational 'building blocks' of the orbital economy.",
        "RKLB": "Rocket Lab USA, Inc. is a leading end-to-end space company, best known for its Electron small launch vehicle. It is the only commercial launcher besides SpaceX with a proven, high-frequency flight heritage. Beyond rockets, its Space Systems division provides satellite buses and components, and the company is currently developing the Neutron medium-lift reusable rocket to compete for large-scale constellation launches."
        
    }
    
    return ticker_to_name , ticker_to_company_info

def get_completed_name(ticker):
    inc_to_name = {
        # --- Magnificent Seven (Tech Giants) ---
        "META": "Meta Platforms, Inc.",
        "AAPL": "Apple Inc.",
        "NVDA": "NVIDIA Corporation",
        "MSFT": "Microsoft Corporation",
        "GOOGL": "Alphabet Inc.",
        "AMZN": "Amazon.com, Inc.",
        "TSLA": "Tesla, Inc.",

        # --- Semiconductors ---
        "AMD": "Advanced Micro Devices, Inc.",
        "INTC": "Intel Corporation",
        "TSM": "Taiwan Semiconductor Manufacturing Company Limited",
        "AVGO": "Broadcom Inc.",
        "QCOM": "Qualcomm Incorporated",

        # --- Software / Media ---
        "NFLX": "Netflix, Inc.",
        "DIS": "The Walt Disney Company",
        "ADBE": "Adobe Inc.",
        "CRM": "Salesforce, Inc.",
        "ORCL": "Oracle Corporation",

        # --- Finance / Payments ---
        "JPM": "JPMorgan Chase & Co.",
        "BAC": "Bank of America Corporation",
        "V": "Visa Inc.",
        "MA": "Mastercard Incorporated",

        # --- Consumer / Retail ---
        "WMT": "Walmart Inc.",
        "COST": "Costco Wholesale Corporation",
        "KO": "The Coca-Cola Company",
        "PEP": "PepsiCo, Inc.",
        "PG": "The Procter & Gamble Company",

        # --- Healthcare ---
        "JNJ": "Johnson & Johnson",
        "PFE": "Pfizer Inc.",
        "LLY": "Eli Lilly and Company",

        # --- Space ---
        "RDW": "Redwire Corporation",
        "RKLB": "Rocket Lab USA, Inc.",

        # ==========================================
        # 阵营一：多巴胺与新金融 (高波动、加密货币与投机属性)
        # 适合策略：监控加密周期、政策放开预期、极端情绪逼空
        # ==========================================
        "DKNG": "DraftKings Inc.",
        "SOFI": "SoFi Technologies, Inc.",
        "SQ": "Block, Inc.",
        "COIN": "Coinbase Global, Inc.",
        "HOOD": "Robinhood Markets, Inc.",
        # --- 补充新增 ---
        "MSTR": "MicroStrategy Incorporated", # 纯粹的比特币高倍杠杆
        "AFRM": "Affirm Holdings, Inc.",      # 消费降级与信贷坏账周期的放大器

        # ==========================================
        # 阵营二：数字原生与注意力经济 (社交、游戏与年轻流量)
        # 适合策略：财报日内剧烈波动(IV Crush)、用户数据突发异动
        # ==========================================
        "RDDT": "Reddit, Inc.",
        "RBLX": "Roblox Corporation",
        "DUOL": "Duolingo, Inc.",
        "U": "Unity Software Inc.",
        # --- 补充新增 ---
        "SE": "Sea Limited",                  # 东南亚“腾讯+阿里”，游戏与电商流量变现

        # ==========================================
        # 阵营三：新世代消费信仰 (狂热的品牌忠诚度与高速扩张)
        # 适合策略：强劲动量(Momentum)追踪、打破传统华尔街估值偏见
        # ==========================================
        "CELH": "Celsius Holdings, Inc.",
        "CAVA": "CAVA Group, Inc.",
        "ONON": "On Holding AG",
        "ELF": "e.l.f. Beauty, Inc.",
        # --- 补充新增 ---
        "CVNA": "Carvana Co.",                # 二手车电商，困境反转与散户逼空的极致体现
        "CPNG": "Coupang, Inc.",              # 亚洲亚马逊，自由现金流收割期的消费巨头
        "TOST": "Toast, Inc.",                # 餐饮SaaS，美国线下餐饮消费与通胀的晴雨表

        # ==========================================
        # 阵营四：散户的“硬核科幻浪漫” (太空、机器人与高分歧标的)
        # 适合策略：大订单/政府合同事件驱动、两极分化带来的定价错位
        # ==========================================
        "PLTR": "Palantir Technologies Inc.",
        "RIVN": "Rivian Automotive, Inc.",
        "RKLB": "Rocket Lab USA, Inc.",
        "SYM": "Symbotic Inc.",
        # --- 补充新增 ---
        "ASTS": "AST SpaceMobile, Inc.",      # 低轨卫星直连手机，长线看组网商业化里程碑
        "JOBY": "Joby Aviation, Inc.",        # eVTOL飞行汽车，长线紧盯FAA适航认证节点
        "FSLR": "First Solar, Inc.",          # 本土太阳能，科技巨头清洁能源订单的直接受益者

        # ==========================================
        # 阵营五：AI 周期里的“卖水人”与“边缘颠覆者”
        # 适合策略：监控大厂资本支出(CapEx)溢出效应、技术落地反转
        # ==========================================
        "ALAB": "Astera Labs, Inc.",
        "APP": "AppLovin Corporation",
        "MDB": "MongoDB, Inc.",
        "NET": "Cloudflare, Inc.",
        # --- 补充新增 (AI基建、液冷、网络与软件深水区) ---
        "VST": "Vistra Corp.",                # AI数据中心核电供应商
        "CEG": "Constellation Energy Corporation", # AI清洁能源底座
        "VRT": "Vertiv Holdings Co",          # 数据中心液冷与温控核心标的
        "SMCI": "Super Micro Computer, Inc.", # 高波动服务器集成商
        "MRVL": "Marvell Technology, Inc.",   # 定制化ASIC芯片与高速光通信
        "COHR": "Coherent Corp.",             # AI光模块与底层材料
        "SNOW": "Snowflake Inc.",             # 云数据仓库，多空博弈最剧烈的SaaS之一
        "DDOG": "Datadog, Inc.",              # 云监控龙头，企业IT支出复苏风向标
        "ZS": "Zscaler, Inc.",                # 零信任网络安全龙头
        "S": "SentinelOne, Inc.",             # 高弹性AI驱动网络安全平台
        "PATH": "UiPath Inc.",                # RPA自动化，AI智能体时代的边缘颠覆/被颠覆者

        # ==========================================
        # 阵营六：颠覆性生物医药 (纯粹的结构性数据驱动) [新增阵营]
        # 适合策略：围绕FDA审批节点和三期临床数据公布日进行事件驱动交易
        # ==========================================
        "VKTX": "Viking Therapeutics, Inc.",  # GLP-1减肥药赛道的高倍弹性妖股
        "CRSP": "CRISPR Therapeutics AG" ,     # 基因编辑商业化先驱，长线逻辑纯看临床数据

        # ==========================================
        # Four new 
        # ==========================================
        'UNH': 'UnitedHealth Group Incorporated',
        'HD': 'The Home Depot, Inc.', 
        'BRK-B': 'Berkshire Hathaway Inc.',
        'XOM': 'Exxon Mobil Corporation'
    }

    crypto_mapping = {
        "BTC": "Bitcoin",
        "ETH": "Ethereum",
        "BNB": "Binance Coin",
        "SOL": "Solana",
        "XRP": "XRP",
        "DOGE": "Dogecoin",
        "ADA": "Cardano",
        "AVAX": "Avalanche",
        "SHIB": "Shiba Inu",
        "DOT": "Polkadot",
        "TRX": "TRON",
        "BCH": "Bitcoin Cash",
        "LINK": "Chainlink",
        "LTC": "Litecoin",
        "NEAR": "NEAR Protocol"
    }

    '''
        "BTC ETH BNB SOL XRP DOGE ADA AVAX SHIB DOT TRX BCH LINK LTC NEAR"
    '''
    
    commodities_map = {
        "GC=F": "Gold",              # 
        "SI=F": "Silver",            # 
        "CL=F": "Crude_Oil_WTI",     # 
        "BZ=F": "Brent_Crude",       # 
        "NG=F": "Natural_Gas",       # 
        "HG=F": "Copper",            # 
        "ZC=F": "Corn",              # 
        "ZS=F": "Soybeans",          # 
        "ZW=F": "Wheat",             # 
        "KC=F": "Coffee"             # 
    }
    
    location_city = {
        "Chicago":  "Chicago (41.8781, -87.6298)",
        "New York": "New York (40.7128, -74.0060)",
        "San Francisco": "San Francisco (37.7749, -122.4194)",
        "Washington DC": "Washington D.C. (38.9072, -77.0369)",
        "Miami": "Miami (25.7617, -80.1918)",
        "Los Angeles": "Los Angeles (34.0522, -118.2437)",
        "Houston": "Houston (29.7604, -95.3698)",
        "Seattle": "Seattle (47.6062, -122.3321)",
        "Boston": "Boston (42.3601, -71.0589)",
        "Denver": "Denver (39.7392, -104.9903)"
    }
    
    major_city = {
        "Chicago":  "Chicago (41.8781, -87.6298)",
        "New York": "New York (40.7128, -74.0060)",
        "San Francisco": "San Francisco (37.7749, -122.4194)",
        "Washington DC": "Washington D.C. (38.9072, -77.0369)",
        "Miami": "Miami (25.7617, -80.1918)",
        "Los Angeles": "Los Angeles (34.0522, -118.2437)",
        "Houston": "Houston (29.7604, -95.3698)",
        "Seattle": "Seattle (47.6062, -122.3321)",
        "Boston": "Boston (42.3601, -71.0589)",
        "Denver": "Denver (39.7392, -104.9903)"
    }

    
    if ticker in inc_to_name:
        return inc_to_name[ticker]
    elif ticker in crypto_mapping:
        return crypto_mapping[ticker]
    elif ticker in commodities_map:
        return commodities_map[ticker]
    elif ticker in location_city:
        return location_city[ticker]
    else : 
        raise FileNotFoundError 
    
def get_time_series(ticker_name , freq ='day', data_save_base = None ,\
                     hori ='loho'  , data_name='stock'):
    """
    Reads the daily CSV file for a specified ticker and returns a list of dictionaries sorted by time.
    
    Args:
        ticker_name (str): The stock ticker symbol, e.g., "META", "AAPL".
        freq (str): Data frequency, defaults to 'day'.
        base_path (str): The directory path where CSV files are stored.

    Returns:
        list: A list containing dictionaries, for example:
              [
                  {'date': '2024-01-02', 'close': 346.29, 'open': 342.30},
                  {'date': '2024-01-03', 'close': 344.47, 'open': 344.98},
                  ...
              ]
        None: Returns None if the file cannot be found.
    """
    
    base_path=f"{data_save_base}/data/{data_name}/prices_{hori}"
    # 1. Construct search pattern: matches "META_1d_*.csv"
    if freq == 'day':
        search_pattern = os.path.join(base_path, f"{ticker_name}_1d_*.csv")
        
    # 2. Search for files
    files = glob.glob(search_pattern)
    
    if not files:
        print('search pattern')
        print(search_pattern)
        print(f"❌ No daily data file found for {ticker_name}.")
        return None
    
    # If multiple files are found, default to the first one (usually there should be only one)
    target_file = files[0]
    
    try:
        # 3. Read CSV
        # skiprows=3: Skip the first 3 header rows
        # header=None: Do not use any row from the file as column names
        # usecols=[0, 1, 4]: 
        #   Index 0 -> Date
        #   Index 1 -> Close (Based on structure: Date, Close, High, Low, Open)
        #   Index 4 -> Open
        df = pd.read_csv(target_file, skiprows=3, header=None, usecols=[0, 1, 4])
        
        # 4. Rename columns
        df.columns = ["date", "close", "open"]
        
        # 5. Data Cleaning
        # Ensure date is in string format (YYYY-MM-DD); remove .astype(str) if datetime objects are preferred
        # Ensure close and open are numeric (float)
        df["date"] = df["date"].astype(str)
        df["close"] = pd.to_numeric(df["close"], errors='coerce')
        df["open"] = pd.to_numeric(df["open"], errors='coerce')
        
        # Drop rows with null values (just in case)
        df.dropna(inplace=True)
        
        # 6. Convert to List[Dict]
        # orient='records' generates format: [{'col1': val1, 'col2': val2}, ...]
        # result_list = df.to_dict(orient='records')
        
        # print(f"✅ Successfully loaded {ticker_name}: {len(result_list)} records")
        # return result_list
        
        return df

    except Exception as e:
        print(f"❌ Failed to read {ticker_name}: {e}")
        return None
    



def get_time_series_living(ticker_name , freq ='day', data_save_base = None ):
    """
    Reads the daily CSV file for a specified ticker and returns a list of dictionaries sorted by time.
    
    Args:
        ticker_name (str): The stock ticker symbol, e.g., "META", "AAPL".
        freq (str): Data frequency, defaults to 'day'.
        base_path (str): The directory path where CSV files are stored.

    Returns:
        list: A list containing dictionaries, for example:
              [
                  {'date': '2024-01-02', 'close': 346.29, 'open': 342.30},
                  {'date': '2024-01-03', 'close': 344.47, 'open': 344.98},
                  ...
              ]
        None: Returns None if the file cannot be found.
    """
    
    base_path=f"{data_save_base}/data/stock_outdate/prices"
    # 1. Construct search pattern: matches "META_1d_*.csv"
    if freq == 'day':
        search_pattern = os.path.join(base_path, f"{ticker_name}_1d_*.csv")
        
    # 2. Search for files
    files = glob.glob(search_pattern)
    
    if not files:
        print('search pattern')
        print(search_pattern)
        print(f"❌ No daily data file found for {ticker_name}.")
        return None
    target_file = files[0]
    
    try:

        df = pd.read_csv(target_file, skiprows=3, header=None, usecols=[0, 1, 4])
        
        # 4. Rename columns
        df.columns = ["date", "close", "open"]
        
       
        df["date"] = df["date"].astype(str)
        df["close"] = pd.to_numeric(df["close"], errors='coerce')
        df["open"] = pd.to_numeric(df["open"], errors='coerce')
        
        # Drop rows with null values (just in case)
        df.dropna(inplace=True)
        

        return df

    except Exception as e:
        print(f"❌ Failed to read {ticker_name}: {e}")
        return None