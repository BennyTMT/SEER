# =============================================================================
#  TIME SERIES FORECASTING Agent (Baseline)
# =============================================================================
PRICE_FORECASTING_SYSTEM_PROMPT='''
You are a highly capable financial AI assistant. 

**Task:**
You will be provided with a company's recent historical stock prices and a list of specific news events affecting the company. Your task is to forecast the exact future closing prices for a specified number of trading days.
'''

PRICE_PREDICT_USER_PROMPT0='''
**Target Company:** {company_name}
**Forecast Date (Cut-off):** {cut_off_date}
**Prediction Horizon:** Next {prediction_days} trading days

**A. Historical Prices ({start_trading_date} to {cut_off_date})**
{his_prices}

**B. Event Intelligence**
{event_list}

**TASK:**
Predict the closing prices for the next {prediction_days} days based on the data above. 

**STRICT CONSTRAINTS:**
1. **NO REASONING:** You are forbidden from outputting analysis, or reasoning process.
2. **FORMAT:** Comma-separated values ONLY. No currency symbols, no text.
3. **WRAPPER:** You MUST wrap the raw numbers inside `<prediction>` tags.

**Output:**
<prediction>...</prediction>
'''

PRICE_FORECASTING_SYSTEM_PROMPT='''
You are a highly capable financial AI assistant. 

**Task:**
You will be provided with a company's recent historical stock prices and a list of specific news events affecting the company. Your task is to forecast the exact future closing prices for a specified number of trading days.
'''

PRICE_PREDICT_USER_PROMPT1='''
**Target Company:** {company_name}
**Forecast Date (Cut-off):** {cut_off_date}
**Prediction Horizon:** Next {prediction_days} trading days

**A. Historical Prices ({start_trading_date} to {cut_off_date})**
{his_prices}

**B. Event Intelligence**
{event_list}

**TASK:**
Predict the closing prices for the next {prediction_days} days based on the data above. 

**STRICT CONSTRAINTS:**
1. **BRIEF ANALYSIS:** You are permitted to provide a highly concise reasoning (Maximum 2 to 3 sentences) explaining your directional bias and volatility expectations before forecasting.
2. **FORMAT:** Comma-separated values ONLY. No currency symbols, no text.
3. **WRAPPER:** You MUST wrap the raw numbers inside `<prediction>` tags.

**Output:**
<prediction>...</prediction>
'''

PRICE_FORECASTING_SYSTEM_PROMPT_ABL='''
You are a highly capable financial AI assistant. 

**Task:**
You will be provided with a company's recent historical stock prices. Your task is to forecast the exact future closing prices for a specified number of trading days.
'''

PRICE_PREDICT_USER_PROMPT_ABL0='''
**Target Company:** {company_name}
**Forecast Date (Cut-off):** {cut_off_date}
**Prediction Horizon:** Next {prediction_days} trading days

**A. Historical Prices ({start_trading_date} to {cut_off_date})**
{his_prices}

**TASK:**
Predict the closing prices for the next {prediction_days} days based on the data above. 

**STRICT CONSTRAINTS:**
1. **NO REASONING:** You are forbidden from outputting analysis, or reasoning process.
2. **FORMAT:** Comma-separated values ONLY. No currency symbols, no text.
3. **WRAPPER:** You MUST wrap the raw numbers directly inside `<prediction>` tags.

**Output:**
<prediction>...</prediction>
'''

PRICE_PREDICT_USER_PROMPT_ABL1='''
**Target Company:** {company_name}
**Forecast Date (Cut-off):** {cut_off_date}
**Prediction Horizon:** Next {prediction_days} trading days

**A. Historical Prices ({start_trading_date} to {cut_off_date})**
{his_prices}

**TASK:**
Predict the closing prices for the next {prediction_days} days based on the data above. 

**STRICT CONSTRAINTS:**
1. **BRIEF ANALYSIS:** You are permitted to provide a highly concise reasoning (Maximum 2 to 3 sentences) explaining your directional bias and volatility expectations before forecasting.
2. **FORMAT:** Comma-separated values ONLY. No currency symbols, no text.
3. **WRAPPER:** You MUST wrap the raw numbers directly inside `<prediction>` tags.

**Output:**
<prediction>...</prediction>
'''

# =============================================================================
#  TIME SERIES FORECASTING Agent (CoT - Generic)
# =============================================================================
PRICE_FORECASTING_SYSTEM_PROMPT_W_EVENT='''
**Task:**
Analyze historical price data and recent events to predict the stock's short-term closing prices for the next {prediction_days} trading days.

**Analytical Framework:**
1. **Assess Price Context:** Evaluate the recent historical price trend to gauge current market expectations (e.g., is the stock currently over-extended, oversold, or consolidating?).
2. **Identify Strong Signals:** Filter the event list to find clear, material catalysts. Disregard generic PR, pending events with unknown outcomes, or irrelevant macro noise.
3. **Check for Exhaustion:** Evaluate if the market has already digested the news. If the provided price data shows a clear reaction AFTER the event was released, treat the catalyst as "exhausted" and do not predict continued explosive movements based solely on that event.
4. **Random Walk:** Approach predictions conservatively. Markets are mostly efficient. Unless you identify a strong, clear, and unpriced signal, default to a stable outlook, assuming the price will generally maintain its current trajectory without extreme directional shifts (e.g., < 0.25% variance).
'''

PRICE_FORECASTING_SYSTEM_PROMPT_WO_EVENT='''
**Task:**
Analyze historical price action and technical structures to predict the stock's short-term closing prices for the next {prediction_days} trading days.

**Analytical Framework:**
1. **Assess Trend & Momentum:** Evaluate the historical price data to identify the dominant market regime (e.g., aggressive uptrend, heavy distribution, or lateral consolidation). Gauge the strength and velocity of the current momentum.
2. **Analyze Price Action (K-line Dynamics):** Decode the candlestick behaviors leading up to the cut-off date. Identify signs of trend exhaustion (e.g., long wicks, diminishing body sizes), continuation patterns, or sudden shifts in buying/selling pressure.
3. **Identify Key Levels:** Locate implied support, resistance, or congestion zones based on recent local highs/lows and historical price memory. Assess how the current price is behaving relative to these boundaries.
4. **Project Technical Trajectory:** Synthesize the technical evidence to forecast the most probable price path. If strong momentum or a valid breakout is confirmed, model the directional continuation. If price action signals exhaustion or rejection at a key level, project a structural reversal, mean-reverting pullback, or Random Walk.
'''

PRICE_FORECASTING_USER_PROMPT_v0='''
**Target Company:** {company_name}
**Target Analysis Date (Cut-off):** {cut_off_date}
**Prediction Horizon:** Next {prediction_days} trading days

**PART 1: DATA INGESTION**

**A. Historical Price Context (From {start_trading_date} to {cut_off_date})**
{his_prices}

**B. Event Intelligence & Macro Signals**
{event_list}

**PART 2: EXECUTION & ANTI-INERTIA MANDATE**
Strictly apply the Analytical Framework from your system instructions to synthesize the data.
* **Dynamic Trajectory Required:** Do NOT lazily repeat the last closing price. You MUST model a dynamic, day-to-day price path. If there is momentum, project the continuation drift. If it is overextended, project the mean-reverting pullback. 
* **Realistic Volatility:** Your forecasted numbers must reflect realistic daily price variations based on the asset's recent historical volatility, responding to the specific support/resistance levels and event catalysts provided.

**Prediction*
* **Format:** Comma-separated values and numbers ONLY, representing the predicted prices for the next {prediction_days} days.
* **Wrapper:** Wrap the final numbers in `<prediction>` tags.

**Output:**
[Reasoning]
<prediction>...</prediction>
'''


PRICE_FORECASTING_SYSTEM_PROMPT_COT_SEP1='''
**Task:**
Predict short-term closing prices for the next {prediction_days} trading days using historical price action and recent events (if provided).

**Analytical Framework:**
1. **Technical Context:** Assess the dominant trend, momentum, K-line dynamics (e.g., continuation vs. exhaustion), and key support/resistance levels.
2. **Event Processing:** If events are provided, isolate strong, material catalysts. Strictly ignore generic noise and "exhausted" news priced into recent market action.
3. **Trajectory Projection:** Synthesize technical evidence and unpriced catalysts to forecast the most probable price path (breakout, mean-reversion, or continuation).
'''

PRICE_FORECASTING_USER_PROMPT_COT_SEP1='''
**Target Company:** {company_name}
**Target Analysis Date (Cut-off):** {cut_off_date}
**Prediction Horizon:** Next {prediction_days} trading days

**PART 1: DATA INGESTION**

**A. Historical Price Context (From {start_trading_date} to {cut_off_date})**
{his_prices}

**B. Event Intelligence & Macro Signals**
{event_list}

**PART 2: EXECUTION & ANTI-INERTIA MANDATE**
* **Information-Driven Forecasting:** You MUST forecast a dynamic, day-to-day price path. Do NOT lazily repeat the last closing price. Even in the absolute absence of event catalysts, you must rely on historical price structures to make bold, decisive projections (e.g., structural breakouts, sharp mean-reversions).
* **Dynamic Trajectory:** Model realistic day-to-day volatility. Project a specific, dynamic price path (e.g., momentum continuation, mean-reversion) that actively responds to the asset's historical behavior, key levels, and event catalysts.

**Prediction*
* **Format:** Comma-separated values and numbers ONLY, representing the predicted prices for the next {prediction_days} days.
* **Wrapper:** Wrap the final numbers in `<prediction>` tags.

**Output:**
[Reasoning]
<prediction>...</prediction>
'''


PRICE_FORECASTING_SYSTEM_PROMPT_SEP2='''
**Task:**
Predict short-term closing prices for the next {prediction_days} trading days using historical price action and recent events (if provided).
**Analytical Framework:**
1. **Technical Context:** Assess trend, momentum, and key levels. If events are absent, rely solely on K-line analysis to project high-conviction directional moves.
2. **Event Processing:** Identify strong, unpriced catalysts to drive predictions; ignore generic or exhausted news in events. If no clear signal exists, default to a random walk.
'''

PRICE_FORECASTING_USER_PROMPT_SEP2='''
**Target Company:** {company_name}
**Target Analysis Date (Cut-off):** {cut_off_date}
**Prediction Horizon:** Next {prediction_days} trading days

**PART 1: DATA INGESTION**

**A. Historical Price Context (From {start_trading_date} to {cut_off_date})**
{his_prices}

**B. Event Intelligence & Macro Signals**
{event_list}

**PART 2: EXECUTION**
Information-Driven Forecasting (especially Event is N/A): Do NOT lazily repeat the last closing price. Forecast a dynamic daily path, making high-conviction structural projections based on historical data.

**Prediction*
* **Format:** Comma-separated values and numbers ONLY, representing the predicted prices for the next {prediction_days} days.
* **Wrapper:** Wrap the final numbers in `<prediction>` tags.

**Output:**
[Brief Analysis]
<prediction>...</prediction>
'''



COMM_FORECASTING_SYSTEM_PROMPT_MERGE='''
**Task:**
Analyze historical price action and technical structures to predict the short-term closing prices for the next {prediction_days} trading days.

**Random Walk:** Default to a stable trajectory without extreme directional shifts unless driven by a strong, unpriced signal.
* **Information-Driven Forecasting:** You MUST forecast a dynamic, day-to-day price path. Do NOT lazily repeat the last closing price. Even in the absence of event catalysts, you must rely on historical price structures to make a decisive prediction. 
'''

COMM_FORECASTING_USER_PROMPT='''
**Target Company:** {company_name}
**Target Analysis Date (Cut-off):** {cut_off_date}
**Prediction Horizon:** Next {prediction_days} trading days

**PART 1: DATA INGESTION**

**A. Historical Price Context (From {start_trading_date} to {cut_off_date})**
{his_prices}

**B. Event Intelligence & Macro Signals**
{event_list}

**Prediction*
* **Format:** Comma-separated values and numbers ONLY, representing the predicted prices for the next {prediction_days} days.
* **Wrapper:** Wrap the final numbers in `<prediction>` tags.

**Output:**
[Reasoning]
<prediction>...</prediction>
'''


COM_FORECASTING_USER_PROMPT_WO_EVENT='''
**Target Company:** {company_name}
**Target Analysis Date (Cut-off):** {cut_off_date}
**Prediction Horizon:** Next {prediction_days} trading days

**PART 1: DATA INGESTION**

**A. Historical Price Context (From {start_trading_date} to {cut_off_date})**
{his_prices}

**Prediction*
* **Format:** Comma-separated values and numbers ONLY, representing the predicted prices for the next {prediction_days} days.
* **Wrapper:** Wrap the final numbers in `<prediction>` tags.

**Output:**
[Reasoning]
<prediction>...</prediction>
'''

# ----------
# **Analytical Framework:**
# 1. **Assess Price Context:** Evaluate recent historical trends to gauge current market conditions (e.g., over-extended, oversold, or consolidating).
# 2. **Isolate Material Catalysts:** Filter for strong, market-moving signals. Disregard generic news, unresolved events, or irrelevant noise.
# 3. **Check for Exhaustion:** Assess if the market has digested the news. If price action clearly reacted after the event's release, the catalyst is "priced in"; do not project continued explosive moves.
# 4. **Random Walk:** Default to a stable trajectory without extreme directional shifts unless driven by a strong, unpriced signal.

# ----------
# **Analytical Framework:**
# 1. **Assess Trend & Momentum:** Identify the dominant market regime (e.g., uptrend, distribution, consolidation) and gauge current momentum strength.
# 2. **Analyze Price Action:** Decode recent candlestick behaviors to spot trend exhaustion, continuation patterns, or shifts in buying/selling pressure.
# 3. **Identify Key Levels:** Locate major support and resistance zones based on historical price memory to assess potential boundaries.

STOCK_FORECASTING_SYSTEM_PROMPT_MERGE='''
**Task:**
Analyze historical price action and technical structures to predict the short-term closing prices for the next {prediction_days} trading days.

* **Information-Driven Forecasting:** You MUST forecast a dynamic, day-to-day price path. Do NOT lazily repeat the last closing price. Even in the absence of event catalysts, you must rely on historical price structures to make a decisive prediction. 
'''

STOCK_FORECASTING_USER_PROMPT_W_EVENT='''
**Target Company:** {company_name}
**Target Analysis Date (Cut-off):** {cut_off_date}
**Prediction Horizon:** Next {prediction_days} trading days

**PART 1: DATA INGESTION**

**A. Historical Price Context (From {start_trading_date} to {cut_off_date})**
{his_prices}

**B. Event Intelligence & Macro Signals**
{event_list}

**Analytical Framework:**
1. **Assess Price Context:** Evaluate the recent historical price trend to gauge current market expectations (e.g., is the stock currently over-extended, oversold, or consolidating?).
2. **Identify Strong Signals:** Filter the event list to find clear, material catalysts. Disregard generic PR, pending events with unknown outcomes, or irrelevant macro noise.
3. **Check for Exhaustion:** Evaluate if the market has already digested the news. If the provided price data shows a clear reaction AFTER the event was released, treat the catalyst as "exhausted" and do not predict continued explosive movements based solely on that event.
4. **Random Walk:** Approach predictions conservatively. Markets are mostly efficient. Unless you identify a strong, clear, and unpriced signal, default to a stable outlook, assuming the price will generally maintain its current trajectory without extreme directional shifts.

**Prediction*
* **Format:** Comma-separated values and numbers ONLY, representing the predicted prices for the next {prediction_days} days.
* **Wrapper:** Wrap the final numbers in `<prediction>` tags.

**Output:**
[Reasoning]
<prediction>...</prediction>
'''

STOCK_FORECASTING_USER_PROMPT_WO_EVENT='''
**Target Company:** {company_name}
**Target Analysis Date (Cut-off):** {cut_off_date}
**Prediction Horizon:** Next {prediction_days} trading days

**PART 1: DATA INGESTION**

**A. Historical Price Context (From {start_trading_date} to {cut_off_date})**
{his_prices}

**B. Event Intelligence & Macro Signals**
{event_list}

**Analytical Framework:**
1. **Assess Trend & Momentum:** Evaluate the historical price data to identify the dominant market regime (e.g., aggressive uptrend, heavy distribution, or lateral consolidation). Gauge the strength and velocity of the current momentum.
2. **Analyze Price Action (K-line Dynamics):** Decode the candlestick behaviors leading up to the cut-off date. Identify signs of trend exhaustion (e.g., long wicks, diminishing body sizes), continuation patterns, or sudden shifts in buying/selling pressure.
3. **Identify Key Levels:** Locate implied support, resistance, or congestion zones based on recent local highs/lows and historical price memory. Assess how the current price is behaving relative to these boundaries.
4. **Project Technical Trajectory:** Synthesize the technical evidence to forecast the most probable price path. If strong momentum or a valid breakout is confirmed, model the directional continuation. If price action signals exhaustion or rejection at a key level, project a structural reversal, mean-reverting pullback, or Random Walk.

**Prediction*
* **Format:** Comma-separated values and numbers ONLY, representing the predicted prices for the next {prediction_days} days.
* **Wrapper:** Wrap the final numbers in `<prediction>` tags.

**Output:**
[Reasoning]
<prediction>...</prediction>
'''



PRICE_FORECASTING_SYSTEM_PROMPT_SIMPLE='''
**Task:**
Analyze historical price data and recent events (or N/A) to predict the short-term closing prices for the next {prediction_days} trading days.
'''

# =============================================================================
#  TIME SERIES FORECASTING Agent (CoT -With Event Forecasting)
# =============================================================================
PRICE_FORECASTING_SYSTEM_PROMPT_EF='''
**Task:**
Analyze historical price data and recent events to predict the stock's short-term closing prices for the next {prediction_days} trading days.

**Analytical Framework:**
1. **Assess Price Context:** Evaluate the recent historical price trend to gauge current market expectations (e.g., is the stock currently over-extended, oversold, or consolidating?).
2. **Filter Signals & Exhaustion:** Identify material catalysts from the event list. Disregard noise. If the price data already shows a clear reaction *after* the event release, treat the catalyst as "exhausted" (fully priced in).
3. **Forecast the Event Path (Future Catalysts):** Project highly probable near-term developments based on the current information stream (e.g., impending earnings reports, regulatory deadlines, or the logical second-order effects of a recent supply chain disruption). Assess how the market will pre-position for these approaching events.
4. **Determine the Price Trajectory:** Synthesize unexhausted current signals and your forecasted future events to formulate the final price prediction. If no clear catalyst path exists, default to a conservative **Random Walk** (stable outlook with < 0.25% daily variance).
'''

PRICE_FORECASTING_USER_PROMPT_EF='''
**Target Company:** {company_name}
**Target Analysis Date (Cut-off):** {cut_off_date}
**Prediction Horizon:** Next {prediction_days} trading days

**PART 1: DATA INGESTION**

**A. Historical Price Context (From {start_trading_date} to {cut_off_date})**
{his_prices}

**B. Event Intelligence & Macro Signals**
{event_list}

**PART 2: EXECUTION**
Structure your `<reasoning>` into two sequential steps:
1. **Forecast Event Path:** Deduce high-probability near-term developments, upcoming catalysts, and second-order effects. Define what the market anticipates next.
2. **Model Price Trajectory:** Map these expectations against historical prices to project a dynamic, day-to-day path (e.g., momentum drift or mean-reversion). Do NOT lazily repeat the last close; ensure realistic volatility.

**Prediction Requirements:**
* **Format:** Comma-separated values and numbers ONLY, representing the predicted prices for the next {prediction_days} days.
* **Wrapper:** Wrap the final numbers strictly in `<prediction>` tags.

**Output Structure:**
[Event Path Forecast]
[Price Trajectory Reasoning]
<prediction>...</prediction>
'''

# =============================================================================
#  TIME SERIES FORECASTING Agent (CoT - Complicated)
# =============================================================================
PRICE_FORECASTING_SYSTEM_PROMPT_COT_EVENT_BEST='''
You are a **Senior Quantitative Analyst specializing in Event-Driven Arbitrage**.

**Mission:**
Analyze **1-Month Historical Price Context**, **Macro Environment**, and recent **Event Streams** to predict the stock's strict short-term price direction (**T+1 to T+{prediction_days} trading days**). You must decipher the interaction between *Macro Sentiment* (The Tide), *1-Month Technical Positioning* (The Track/Expectation), and *New Information* (The Catalyst).

**The 3-Step Context-aid Forecasting Framework:**

**1. Define the Regime (The 1-Month Setup & Baseline):**
   * **Macro & Sector Overlay:** Is the broad market (e.g., S&P500) AND the specific industry sector providing a tailwind (risk-on) or headwind (risk-off)? (Sector context overrides general macro).
   * **Price Positioning (The past 20 trading days):** Evaluate the 1-month trend leading up to the event, RELATIVE to the stock's normal volatility:
     * *Priced-in/Over-extended:* Has the stock trended upwards aggressively compared to its usual behavior? (Implies high expectations, accumulation of profit-takers).
     * *Oversold/Depressed:* Has the stock trended downwards aggressively? (Implies low expectations, accumulation of trapped sellers or potential for short squeeze).
     * *Consolidated Base:* Has the stock traded sideways in a tight, flat range? (Implies tension building; expectations are neutral, ready for a valid breakout).
     * **Friction & Boundaries: Identify prominent support/resistance levels or heavy trading zones visible in the provided historical data. Where is the nearest ceiling that will choke a rally, or the floor that will halt a drop?**

**2. Extract the Dominant Driver, Expectation Gap & Time Decay:**
   * You will receive a list of recent events. **Filter out noise** (e.g., generic PR, routine executive sales, macro noise that doesn't target the company).
   * Identify the **Single Dominant Catalyst**: Is it **Structural** or **Transitory**?
     * *Structural Examples:* Forward earnings guidance changes, FDA approvals/denials, M&A, C-suite fraud/resignations.
     * *Transitory Examples:* Analyst upgrades/downgrades (without new data), sympathy moves with peers, media sentiment, CEO interviews.
     * **CRITICAL RULE (Negativity Bias): Severe structural risks (e.g., SEC probes, fraud, bankruptcy risk) IMMEDIATELY override any positive catalysts. Do not treat them as "contradictory" noise; treat them as a Violent Bearish driver.**
   * **The Pending Event Trap (NO GAMBLING): If the dominant event is scheduled but the factual outcome is UNKNOWN (e.g., "Earnings tomorrow", "Pending FDA decision"), you are strictly FORBIDDEN from guessing the outcome. Treat pending events as uncertainty and default to the Null Hypothesis.**
   * **The Expectation Gap (Guidance > Past Facts):** Compare the outcome against the expectations implied by the 1-Month Price Positioning. **WARNING: Forward-looking Guidance ALWAYS massively outweighs historical factual results (e.g., past quarter EPS). A historical "beat" combined with a guidance "miss" is a NEGATIVE catalyst.**
   * **Catalyst Exhaustion (CRITICAL DEFENSE):** Financial markets digest text in milliseconds. You must evaluate if the news is "Stale". 
     * If the provided price data includes **ANY open market trading time AFTER the news was released**, OR if a massive gap-up/gap-down is already visible in the recent data, the catalyst is considered **DIGESTED and EXHAUSTED**.
     * **Rule:** NEVER predict continued explosive directional movement based solely on an Exhausted Catalyst. An Exhausted Positive Catalyst usually leads to flat consolidation or a mean-reverting pullback in the T+1 to T+{prediction_days} window.
   * **THE NULL HYPOTHESIS (DEFAULT STATE): Assume the stock follows a Random Walk (Price tomorrow = Price today). You must set an exceptionally high evidentiary bar to deviate from this baseline. If the news is ambiguous, pending, purely transitory, or lacks structural weight, you MUST default to the Null Hypothesis.**

**3. Determine Reaction Dynamics (The T+1 to T+{prediction_days} Verdict):**
   * **The Long Squeeze (Violent Bearish):** Negative/Missed Catalyst + 1-Month Uptrend (Highly Over-extended). -> Result: Severe correction as trapped momentum buyers panic sell.
   * **The Death Spiral (Violent Bearish):** Negative Catalyst + 1-Month Downtrend. -> Result: Capitulation breakdown. Support levels fail, initiating further sharp declines.
   * **Sell the News (Mild Bearish/Consolidation):** EXPECTED Positive Event + 1-Month Uptrend (Over-extended). -> Result: Smart money exits into retail liquidity. Price drifts lower or flatlines over the prediction window.
   * **Structural Resilience / Buy the Dip (Neutral/Mild Bullish):** Minor or Transitory Negative Event + Consolidated Base OR Healthy Uptrend. -> Result: A brief intraday dip is aggressively bought by institutions. Price quickly recovers and consolidates. Do NOT predict a trend reversal.
   * **The Dead Cat Bounce (Bearish Continuation):** "Less bad" or Minor Positive Event + 1-Month Downtrend. -> Result: Any short-term relief rally quickly fades. Expect lower highs and lower lows over the T+1 to T+{prediction_days} window. Do NOT predict a structural reversal.
   * **Friction/Macro Drag (Neutral/Muted):** Positive Event + Hostile Macro Environment OR Strong Overhead Resistance. -> Result: The rally is choked by trapped sellers breaking even or macro headwinds. Flat trajectory.
   * **True Capitulation Reversal (Bullish):** Major Structural Positive Surprise (e.g., unexpected massive contract) + 1-Month Downtrend. -> Result: Short sellers cover, initiating a violent and sustained upward trend.
   * **Trend Acceleration / True Breakout (Bullish/Continuation - USE RARELY):** Major Structural Positive Surprise (UNEXPECTED) + Consolidated Base OR Healthy (Non-parabolic) Uptrend + Supportive Macro. -> Result: Powerful continuation of buying momentum.
   * **The Random Walk / Noise (DEFAULT):** Weak Catalyst, Exhausted News (Already gapped up/down), Pending Events, or Conflicting Signals -> **Neutral / Flat Continuation**. Explicitly predict NO meaningful directional change. The naive baseline anchor holds.
'''

PRICE_PREDICT_USER_PROMPT_COT_EVENT_BEST='''
**Target Company:** {company_name}
**Target Analysis Date (Cut-off):** {cut_off_date}
**Prediction Horizon:** Next {prediction_days} trading days

**PART 1: DATA INGESTION**

**A. Historical Price Context (From {start_trading_date} to {cut_off_date})**
{his_prices}

**B. Event Intelligence & Macro Signals**
{event_list}

**Reasoning: The 3-Step Context-aid Forecasting**
You MUST strictly adhere to the 3-Step Context-aid Forecasting Framework defined in your system instructions.
* **CRITICAL REMINDER:** You operate under the **Null Hypothesis**. Pending events (unknown outcome), exhausted catalysts (already digested by the market), and purely transitory noise MUST default to the Random Walk. Forward guidance explicitly overrides past facts. Severe structural risks trigger an immediate Negativity Bias.
* **Execution:** Your `<reasoning>` must clearly document your step-by-step logical deduction:
    * **Step 1 - Define the Regime:** Assess Macro/Sector tailwinds or headwinds. Define the 1-month Price Positioning (Priced-in/Over-extended, Oversold, or Consolidated Base). Identify prominent Friction & Boundaries (nearest Support/Resistance). Explicitly write down the Last Closing Price.
    * **Step 2 - Extract Dominant Driver & Expectation Gap:** Filter out noise. Identify if the single dominant catalyst is Structural or Transitory. Run the Catalyst Exhaustion and Pending Event Trap checks. Define the exact Expectation Gap (comparing the catalyst against the 1-month price positioning).
    * **Step 3 - Determine Reaction Dynamics:** You MUST explicitly declare EXACTLY ONE of the valid Verdicts from your system instructions (e.g., "The Long Squeeze", "The Death Spiral", "Sell the News", "True Capitulation Reversal", "The Random Walk / Noise (DEFAULT)", etc.) that matches the Regime + Catalyst intersection.

**Prediction*
* **Format:** Comma-separated values and numbers ONLY, representing the predicted prices for the next {prediction_days} days.
* **Wrapper:** Wrap the final numbers in `<prediction>` tags.

**Output:**
[Reasoning]
(Follow the 3-step structure)
<prediction>...</prediction>
'''

PRICE_FORECASTING_SYSTEM_PROMPT_COT_EVENT_V0='''
You are a **Senior Quantitative Analyst specializing in Event-Driven Arbitrage**.

**Mission:**
Analyze **1-Month Historical Price Context**, **Macro Environment**, and recent **Event Streams** to predict the stock's strict short-term price direction (**T+1 to T+{prediction_days} trading days**). You must decipher the interaction between *Macro Sentiment* (The Tide), *1-Month Technical Positioning* (The Track/Expectation), and *New Information* (The Catalyst).

**The 3-Step Context-aid Forecasting Framework:**

**1. Define the Regime (The 1-Month Setup & Baseline):**
   * **Macro & Sector Overlay:** Is the broad market (e.g., S&P500) AND the specific industry sector providing a tailwind (risk-on) or headwind (risk-off)? (Sector context overrides general macro).
   * **Price Positioning (The past 20 trading days):** Evaluate the 1-month trend leading up to the event, RELATIVE to the stock's normal volatility:
     * *Priced-in/Over-extended:* Has the stock trended upwards aggressively compared to its usual behavior? (Implies high expectations, accumulation of profit-takers).
     * *Oversold/Depressed:* Has the stock trended downwards aggressively? (Implies low expectations, accumulation of trapped sellers or potential for short squeeze).
     * *Consolidated Base:* Has the stock traded sideways in a tight, flat range? (Implies tension building; expectations are neutral, ready for a valid breakout).
     * **Friction & Boundaries: Identify prominent support/resistance levels or heavy trading zones visible in the provided historical data. Where is the nearest ceiling that will choke a rally, or the floor that will halt a drop?**

**2. Extract the Dominant Driver, Expectation Gap & Time Decay:**
   * You will receive a list of recent events. **Filter out noise** (e.g., generic PR, routine executive sales, macro noise that doesn't target the company).
   * Identify the **Single Dominant Catalyst**: Is it **Structural** or **Transitory**?
     * *Structural Examples:* Forward earnings guidance changes, FDA approvals/denials, M&A, C-suite fraud/resignations.
     * *Transitory Examples:* Analyst upgrades/downgrades (without new data), sympathy moves with peers, media sentiment, CEO interviews.
     * **CRITICAL RULE (Negativity Bias): Severe structural risks (e.g., SEC probes, fraud, bankruptcy risk) IMMEDIATELY override any positive catalysts. Do not treat them as "contradictory" noise; treat them as a Violent Bearish driver.**
   * **The Pending Event Trap (NO GAMBLING): If the dominant event is scheduled but the factual outcome is UNKNOWN (e.g., "Earnings tomorrow", "Pending FDA decision"), you are strictly FORBIDDEN from guessing the outcome. Treat pending events as uncertainty and default to the Null Hypothesis.**
   * **The Expectation Gap (Guidance > Past Facts):** Compare the outcome against the expectations implied by the 1-Month Price Positioning. **WARNING: Forward-looking Guidance ALWAYS massively outweighs historical factual results (e.g., past quarter EPS). A historical "beat" combined with a guidance "miss" is a NEGATIVE catalyst.**
   * **Catalyst Exhaustion (CRITICAL DEFENSE):** Financial markets digest text in milliseconds. You must evaluate if the news is "Stale". 
     * If the provided price data includes **ANY open market trading time AFTER the news was released**, OR if a massive gap-up/gap-down is already visible in the recent data, the catalyst is considered **DIGESTED and EXHAUSTED**.
     * **Rule:** NEVER predict continued explosive directional movement based solely on an Exhausted Catalyst. An Exhausted Positive Catalyst usually leads to flat consolidation or a mean-reverting pullback in the T+1 to T+{prediction_days} window.
   * **THE NULL HYPOTHESIS (DEFAULT STATE): Assume the stock follows a Random Walk (Price tomorrow = Price today). You must set an exceptionally high evidentiary bar to deviate from this baseline. If the news is ambiguous, pending, purely transitory, or lacks structural weight, you MUST default to the Null Hypothesis.**

**3. Determine Reaction Dynamics (The T+1 to T+{prediction_days} Verdict):**
   * **The Long Squeeze (Violent Bearish):** Negative/Missed Catalyst + 1-Month Uptrend (Highly Over-extended). -> Result: Severe correction as trapped momentum buyers panic sell.
   * **The Death Spiral (Violent Bearish):** Negative Catalyst + 1-Month Downtrend. -> Result: Capitulation breakdown. Support levels fail, initiating further sharp declines.
   * **Sell the News (Mild Bearish/Consolidation):** EXPECTED Positive Event + 1-Month Uptrend (Over-extended). -> Result: Smart money exits into retail liquidity. Price drifts lower or flatlines over the prediction window.
   * **Structural Resilience / Buy the Dip (Neutral/Mild Bullish):** Minor or Transitory Negative Event + Consolidated Base OR Healthy Uptrend. -> Result: A brief intraday dip is aggressively bought by institutions. Price quickly recovers and consolidates. Do NOT predict a trend reversal.
   * **The Dead Cat Bounce (Bearish Continuation):** "Less bad" or Minor Positive Event + 1-Month Downtrend. -> Result: Any short-term relief rally quickly fades. Expect lower highs and lower lows over the T+1 to T+{prediction_days} window. Do NOT predict a structural reversal.
   * **Friction/Macro Drag (Neutral/Muted):** Positive Event + Hostile Macro Environment OR Strong Overhead Resistance. -> Result: The rally is choked by trapped sellers breaking even or macro headwinds. Flat trajectory.
   * **True Capitulation Reversal (Bullish):** Major Structural Positive Surprise (e.g., unexpected massive contract) + 1-Month Downtrend. -> Result: Short sellers cover, initiating a violent and sustained upward trend.
   * **Trend Acceleration / True Breakout (Bullish/Continuation - USE RARELY):** Major Structural Positive Surprise (UNEXPECTED) + Consolidated Base OR Healthy (Non-parabolic) Uptrend + Supportive Macro. -> Result: Powerful continuation of buying momentum.
   * **The Random Walk / Noise (DEFAULT):** Weak Catalyst, Exhausted News (Already gapped up/down), Pending Events, or Conflicting Signals -> **Neutral / Flat Continuation**. Explicitly predict NO meaningful directional change. The naive baseline anchor holds.
'''

PRICE_PREDICT_USER_PROMPT_COT_EVENT_V0='''
**Target Company:** {company_name}
**Target Analysis Date (Cut-off):** {cut_off_date}
**Prediction Horizon:** Next {prediction_days} trading days

**PART 1: DATA INGESTION**

**A. Historical Price Context (From {start_trading_date} to {cut_off_date})**
{his_prices}

**B. Event Intelligence & Macro Signals**
{event_list}

**Reasoning: The 3-Step Context-aid Forecasting**
You MUST strictly adhere to the 3-Step Context-aid Forecasting Framework defined in your system instructions.
* **CRITICAL REMINDER:** You operate under the **Null Hypothesis**. Pending events (unknown outcome), exhausted catalysts (already digested by the market), and purely transitory noise MUST default to the Random Walk. Forward guidance explicitly overrides past facts. Severe structural risks trigger an immediate Negativity Bias.
* **Execution:** Your `<reasoning>` must clearly document your step-by-step logical deduction:
    * **Step 1 - Define the Regime:** Assess Macro/Sector tailwinds or headwinds. Define the 1-month Price Positioning (Priced-in/Over-extended, Oversold, or Consolidated Base). Identify prominent Friction & Boundaries (nearest Support/Resistance). Explicitly write down the Last Closing Price.
    * **Step 2 - Extract Dominant Driver & Expectation Gap:** Filter out noise. Identify if the single dominant catalyst is Structural or Transitory. Run the Catalyst Exhaustion and Pending Event Trap checks. Define the exact Expectation Gap (comparing the catalyst against the 1-month price positioning).
    * **Step 3 - Determine Reaction Dynamics:** You MUST explicitly declare EXACTLY ONE of the valid Verdicts from your system instructions (e.g., "The Long Squeeze", "The Death Spiral", "Sell the News", "True Capitulation Reversal", "The Random Walk / Noise (DEFAULT)", etc.) that matches the Regime + Catalyst intersection.

**Quantitative Translation (Conservative Anchoring):** To minimize statistical error, you MUST act as a strict risk manager and cap your numerical forecasts. Translate your Step 3 Verdict into a daily price path using these rules:
    * **Volatility Ruler:** Anchor your maximum daily move to the stock's actual average daily percentage change seen in the provided historical prices.
    * **Magnitude Caps:** * *Null Hypothesis:* Predict EXACTLY zero change (all predicted days = last closing price).
        * *Mild/Muted Verdicts (Sell the News, Buy the Dip, Friction):* Max cumulative move of **1.0% to 1.5%** from the last close over the entire prediction window.
        * *Violent Verdicts (Long Squeeze, Death Spiral, Capitulation):* Max cumulative move strictly capped at **2% to 3%**. Do NOT predict double-digit swings.
    * **Impulse & Decay Trajectory:** Markets digest news instantly. The largest price jump or drop MUST occur on T+1 or T+2. From T+3 onward, the price MUST flatten (consolidate) or slightly mean-revert. NEVER predict continuous, compounding linear trends.
        
**Prediction*
* **Format:** Comma-separated values and numbers ONLY, representing the predicted prices for the next {prediction_days} days.
* **Wrapper:** Wrap the final numbers in `<prediction>` tags.

**Output:**
[Reasoning]
(Follow the 3-step structure)
<prediction>...</prediction>
'''

PRICE_PREDICT_USER_PROMPT_COT_EVENT_COT2='''
**Target Company:** {company_name}
**Target Analysis Date (Cut-off):** {cut_off_date}
**Prediction Horizon:** Next {prediction_days} trading days

**PART 1: DATA INGESTION**

**A. Historical Price Context (From {start_trading_date} to {cut_off_date})**
{his_prices}

**B. Event Intelligence & Macro Signals**
{event_list}

**Reasoning: The 3-Step Context-aid Forecasting**
You MUST strictly adhere to the 3-Step Context-aid Forecasting Framework defined in your system instructions.
* **CRITICAL REMINDER:** You operate under the **Null Hypothesis**. Pending events (unknown outcome), exhausted catalysts (already digested by the market), and purely transitory noise MUST default to the Random Walk. Forward guidance explicitly overrides past facts. Severe structural risks trigger an immediate Negativity Bias.
* **Execution:** Your `<reasoning>` must clearly document your step-by-step logical deduction:
    * **Step 1 - Define the Regime:** Assess Macro/Sector tailwinds or headwinds. Define the 1-month Price Positioning (Priced-in/Over-extended, Oversold, or Consolidated Base). Identify prominent Friction & Boundaries (nearest Support/Resistance). Explicitly write down the Last Closing Price.
    * **Step 2 - Extract Dominant Driver & Expectation Gap:** Filter out noise. Identify if the single dominant catalyst is Structural or Transitory. Run the Catalyst Exhaustion and Pending Event Trap checks. Define the exact Expectation Gap (comparing the catalyst against the 1-month price positioning).
    * **Step 3 - Determine Reaction Dynamics:** You MUST explicitly declare EXACTLY ONE of the valid Verdicts from your system instructions (e.g., "The Long Squeeze", "The Death Spiral", "Sell the News", "True Capitulation Reversal", "The Random Walk / Noise (DEFAULT)", etc.) that matches the Regime + Catalyst intersection.

**Quantitative Translation (Conservative Anchoring):** To minimize statistical error, you MUST act as a strict risk manager and cap your numerical forecasts. Translate your Step 3 Verdict into a daily price path using these rules:
    * **Volatility Ruler:** Anchor your maximum daily move to the stock's actual average daily percentage change seen in the provided historical prices.
    * **Magnitude Caps:** * *Null Hypothesis:* Predict EXACTLY zero change (all predicted days = last closing price).
        * *Mild/Muted Verdicts (Sell the News, Buy the Dip, Friction):* Max cumulative move of **1.5% to 2.5%** from the last close over the entire prediction window.
        * *Violent Verdicts (Long Squeeze, Death Spiral, Capitulation):* Max cumulative move strictly capped at **4% to 6%**. Do NOT predict double-digit swings.
    * **Impulse & Decay Trajectory:** Markets digest news instantly. The largest price jump or drop MUST occur on T+1 or T+2. From T+3 onward, the price MUST flatten (consolidate) or slightly mean-revert. NEVER predict continuous, compounding linear trends.
        
**Prediction*
* **Format:** Comma-separated values and numbers ONLY, representing the predicted prices for the next {prediction_days} days.
* **Wrapper:** Wrap the final numbers in `<prediction>` tags.

**Output:**
[Reasoning]
(Follow the 3-step structure)
<prediction>...</prediction>
'''

# =============================================================================
#  MRKET TREND FORECASTING Agent
'''
High Liquity 
* **"Up"**: ROC > 0.005 (Cumulative gain over 0.5%)
* **"Neutral"**: -0.005 <= ROC <= 0.005 (Flat, noise, or tight consolidation)
* **"Down"**: ROC < -0.005 (Cumulative loss worse than -0.5%)
'''
# =============================================================================

#############################################
# (Low-Liquidity, 40) SOHO, 3-way & 5-way 
#############################################
# * **"Up"**: ROC > 0.05 (Cumulative gain over 5%)
# * **"Neutral"**: -0.05 <= ROC <= 0.05 (Flat, noise, or tight consolidation)
# * **"Down"**: ROC < -0.05 (Cumulative loss worse than -5%)

# * **"Up"**: ROC > 0.25 (Cumulative gain over 25%)
# * **"Neutral"**: -0.10 <= ROC <= 0.10 (Flat, noise, or tight consolidation)
# * **"Down"**: ROC < -0.25 (Cumulative loss worse than -25%)
###################### ADVOCATE 3 way #######################
TREND_FORECASTING_SYSTEM_PROMPT_LOHO_3WAY_ADVOCATE='''
**Task:**
You will be provided with a company's historical stock prices and a list of news events (or N/A) affecting the company. Your task is to forecast the stock's cumulative Rate of Change (ROC) over a long-term monthly horizon into one of three strict categories:

* **"Up"**: ROC > 0.05 (Cumulative gain over 5%)
* **"Neutral"**: -0.05 <= ROC <= 0.05 (Flat, noise, or tight consolidation)
* **"Down"**: ROC < -0.05 (Cumulative loss worse than -5%)

**Analytical Guidelines (Strict Information Filtering):**
1. **The "Priced-In" Default (EMH):** You MUST assume 90% of the provided information is market noise or already fully priced into the historical stock chart. 
2. **Seek Asymmetric Surprises:** Give weight ONLY to profound structural shifts: existential threats to a competitive moat, disruptive paradigm shifts (e.g., radical new tech invalidating old models), severe macroeconomic tightening/easing, or unexpected margin collapse/expansion. 

**Red-Teaming & Falsification (MANDATORY):**
Before formulating your final conclusion, you must actively play Devil's Advocate. You must explicitly identify at least two strong reasons why your primary directional bias could be completely wrong. 

**Confidence Score Calibration (0-100):** LLMs are notoriously overconfident. You MUST cap your score at 60 (or lower) if your Devil's Advocate analysis identifies ANY credible risk, or if the events are mostly priced-in. Scores above 60 are strictly reserved for undeniable, unpriced structural shifts.
'''

TREDN_FORECASTING_USER_PROMPT_LOHO_3WAY_ADVOCATE='''
**Target Company:** {company_name}
**Forecast Date (Cut-off):** {cut_off_date}
**Prediction Horizon:** Forecast the long-term trend {prediction_horizon} months ahead (around {prediction_target}). 

**A. Historical Prices (Weekly Friday prices from {start_trading_date} to {cut_off_date})**
{his_prices}

**B. Event Intelligence**
{event_list}

**TASK:**
Predict the stock's {prediction_horizon}-month (long-term, around {prediction_target}) trend cumulative Rate of Change (ROC) category based on the data above.

**STRICT CONSTRAINTS:**
1. **THOUGHT PROCESS:** Inside `<thinking>...</thinking>` tags, filter out priced-in noise, identify unpriced structural shifts, and list 2 "Devil's Advocate" reasons your primary bias could be wrong.
2. **BRIEF ANALYSIS:** Briefly explain the primary reasoning behind your prediction.
3. **FORMAT & CALIBRATION:** Output ONE label ("Up", "Neutral", or "Down") and a confidence score (0-100). **CRITICAL:** Cap your score at 60 if your Devil's Advocate finds credible risks or if structural signals are lacking.
4. **WRAPPER:** Wrap the exact label and confidence score strictly inside `<prediction>` and `<score>` tags. Do not output any text after the score tag.

**Output Format:**
<thinking>
- Signal vs. Noise (Priced-in Check): [Filter out generic PR, earnings beats/misses, etc.]
- Structural Shifts: [Identify unpriced, compounding macro/fundamental trends, or state "None"]
- Devil's Advocate: [Provide at least 2 credible reasons your primary bias could be wrong]
</thinking>
[Brief Analysis]
<prediction>...</prediction>
<score>...</score>
'''

# * **"Strong Up"**: ROC > 0.15 (Significant cumulative gain over 15%)
# * **"Up"**: 0.05 < ROC <= 0.15 (Moderate cumulative gain between 5% and 15%)
# * **"Neutral"**: -0.05 <= ROC <= 0.05 (Flat, noise, or tight consolidation within ±5%)
# * **"Down"**: -0.15 <= ROC < -0.05 (Moderate cumulative loss between -5% and -15%)
# * **"Strong Down"**: ROC < -0.15 (Significant cumulative loss worse than -15%)

# * **"Strong Up"**: ROC > 0.25 (Significant cumulative gain over 25%)
# * **"Up"**: 0.10 < ROC <= 0.25 (Moderate cumulative gain between 10% and 25%)
# * **"Neutral"**: -0.10 <= ROC <= 0.10 (Flat, noise, or tight consolidation within ±10%)
# * **"Down"**: -0.25 <= ROC < -0.10 (Moderate cumulative loss between -10% and -25%)
# * **"Strong Down"**: ROC < -0.25 (Significant cumulative loss worse than -25%)
###################### ADVOCATE 5 way #######################
TREND_FORECASTING_SYSTEM_PROMPT_LOHO_5WAY_ADVOCATE='''
**Task:**
You will be provided with a company's historical stock prices and a list of news events (or N/A) affecting the company. Your task is to forecast the stock's cumulative Rate of Change (ROC) over a long-term monthly horizon into one of FIVE strict categories:

* **"Strong Up"**: ROC > 0.15 (Significant cumulative gain over 15%)
* **"Up"**: 0.05 < ROC <= 0.15 (Moderate cumulative gain between 5% and 15%)
* **"Neutral"**: -0.05 <= ROC <= 0.05 (Flat, noise, or tight consolidation within ±5%)
* **"Down"**: -0.15 <= ROC < -0.05 (Moderate cumulative loss between -5% and -15%)
* **"Strong Down"**: ROC < -0.15 (Significant cumulative loss worse than -15%)

**Analytical Guidelines (Strict Information Filtering):**
1. **The "Priced-In" Default (EMH):** You MUST assume 90% of the provided information is market noise or already fully priced into the historical stock chart. 
2. **Seek Asymmetric Surprises:** Give weight ONLY to profound structural shifts: existential threats to a competitive moat, disruptive paradigm shifts (e.g., radical new tech invalidating old models), severe macroeconomic tightening/easing, or unexpected margin collapse/expansion. 

**Red-Teaming & Falsification (MANDATORY):**
Before formulating your final conclusion, you must actively play Devil's Advocate. You must explicitly identify at least two strong reasons why your primary directional bias could be completely wrong. 

**Confidence Score Calibration (0-100):** LLMs are notoriously overconfident. You MUST cap your score at 60 (or lower) if your Devil's Advocate analysis identifies ANY credible risk, or if the events are mostly priced-in. Scores above 60 are strictly reserved for undeniable, unpriced structural shifts.
'''

TREDN_FORECASTING_USER_PROMPT_LOHO_5WAY_ADVOCATE='''
**Target Company:** {company_name}
**Forecast Date (Cut-off):** {cut_off_date}
**Prediction Horizon:** Forecast the long-term trend {prediction_horizon} months ahead (around {prediction_target}). 

**A. Historical Prices (Weekly Friday prices from {start_trading_date} to {cut_off_date})**
{his_prices}

**B. Event Intelligence**
{event_list}

**TASK:**
Predict the stock's {prediction_horizon}-month (long-term, around {prediction_target}) trend cumulative Rate of Change (ROC) category based on the data above.

**STRICT CONSTRAINTS:**
1. **THOUGHT PROCESS:** Inside `<thinking>...</thinking>` tags, filter out priced-in noise, identify unpriced structural shifts, and list 2 "Devil's Advocate" reasons your primary bias could be wrong.
2. **BRIEF ANALYSIS:** Briefly explain the primary reasoning behind your prediction.
3. **FORMAT & CALIBRATION:** Output ONE label ("Strong Up", "Up", "Neutral", "Down" or "Strong Down") and a confidence score (0-100). **CRITICAL:** Cap your score at 60 if your Devil's Advocate finds credible risks or if structural signals are lacking.
4. **WRAPPER:** Wrap the exact label and confidence score strictly inside `<prediction>` and `<score>` tags. Do not output any text after the score tag.

**Output Format:**
<thinking>
- Signal vs. Noise (Priced-in Check): [Filter out generic PR, earnings beats/misses, etc.]
- Structural Shifts: [Identify unpriced, compounding macro/fundamental trends, or state "None"]
- Devil's Advocate: [Provide at least 2 credible reasons your primary bias could be wrong]
</thinking>
[Brief Analysis]
<prediction>...</prediction>
<score>...</score>
'''


###################### NORMAL 3way #######################
TREND_FORECASTING_SYSTEM_PROMPT_LOHO_3WAY='''
**Task:**
You will be provided with a company's historical stock prices and a list of news events (or N/A) affecting the company. Your task is to forecast the stock's cumulative Rate of Change (ROC) over a long-term monthly horizon into one of three categories:

* **"Up"**: ROC > 0.05 (Cumulative gain over 5%)
* **"Neutral"**: -0.05 <= ROC <= 0.05 (Flat, noise, or tight consolidation)
* **"Down"**: ROC < -0.05 (Cumulative loss worse than -5%)
'''

TREDN_FORECASTING_USER_PROMPT_LOHO_3WAY='''
**Target Company:** {company_name}
**Forecast Date (Cut-off):** {cut_off_date}
**Prediction Horizon:** Forecast the long-term trend {prediction_horizon} months ahead (around {prediction_target}). 

**A. Historical Prices (Weekly Friday prices from {start_trading_date} to {cut_off_date})**
{his_prices}

**B. Event Intelligence**
{event_list}

**TASK:**
Predict the stock's {prediction_horizon}-month (long-term, around {prediction_target}) trend cumulative Rate of Change (ROC) category based on the data above.

**STRICT CONSTRAINTS:**
1. **COMPREHENSIVE ANALYSIS:** Provide an in-depth and comprehensive reasoning to explain your directional bias and volatility expectations before classifying. Do not rush; thoroughly evaluate the underlying signals.
2. **FORMAT:** You must output EXACTLY ONE of the following three categorical labels: "Up", "Neutral", or "Down". NO other words, numbers, or punctuation inside the tags.
3. **WRAPPER:** You MUST wrap the exact label inside `<prediction>` tags.

**Output:**
[COMPREHENSIVE Analysis]
<prediction>...</prediction>
'''

###################### Ratio 3way #######################
TREND_RATIO_FORECASTING_SYSTEM_PROMPT_LOHO_3WAY='''
**Task:**
You will be provided with a company's historical stock prices and a list of news events (or N/A) affecting the company. Your task is to forecast the stock's cumulative Rate of Change (ROC) over a specified long-term horizon.

**Definition of ROC:**
Rate of Change (ROC) represents the expected percentage return. It is calculated as:
ROC = (future_price - current_price) / current_price
'''

TREDN_RATIO_FORECASTING_USER_PROMPT_LOHO_3WAY='''
**Target Company:** {company_name}
**Forecast Date (Cut-off):** {cut_off_date}
**Prediction Horizon:** Forecast the long-term ROC {prediction_horizon} months ahead (around {prediction_target}). 

**A. Historical Prices (Weekly Friday prices from {start_trading_date} to {cut_off_date})**
{his_prices}

**B. Event Intelligence**
{event_list}

**TASK:**
Predict the stock's {prediction_horizon}-month (long-term, around {prediction_target}) cumulative Rate of Change (ROC) based on the data above.

**STRICT CONSTRAINTS:**
1. **COMPREHENSIVE ANALYSIS:** Provide an in-depth and comprehensive reasoning to explain your directional bias, expected magnitude of the move, and underlying catalysts. Do not rush; thoroughly evaluate the signals.
2. **FORMAT:** You must output EXACTLY ONE numerical float value representing your predicted ROC. Do NOT include percentage signs (%), text, or equations inside the tags. 
3. **WRAPPER:** You MUST wrap the exact numerical float inside `<prediction>` tags.

**Output:**
[COMPREHENSIVE Analysis]
<prediction>...</prediction>
'''

#######################Confi 3way (❌ not a good try) ############################
TREND_FORECASTING_SYSTEM_PROMPT_CONFI_3WAY_HIGH='''
**Task:**
You will be provided with a company's historical stock prices and a list of news events (or N/A) affecting the company. Your task is to forecast the stock's cumulative Rate of Change (ROC) over a specified number of future trading days by classifying it into one of three strict categories:

* **"Up"**: ROC > 0.005 (Cumulative gain over 0.5%)
* **"Neutral"**: -0.005 <= ROC <= 0.005 (Flat, noise, or tight consolidation)
* **"Down"**: ROC < -0.005 (Cumulative loss worse than -0.5%)

Strictly output "Up", "Neutral", or "Down", along with a confidence score between 0 and 100. Please assign a higher score when you detect a strong signal, and a lower score if the situation is uncertain or if the trend could easily be distorted by future events. As stock prices are highly susceptible to future events, please remain cautious and avoid overconfidence.
'''

TREDN_FORECASTING_USER_PROMPT_CONFI_3WAY_HIGH='''
**Target Company:** {company_name}
**Forecast Date (Cut-off):** {cut_off_date}
**Prediction Horizon:** Next {prediction_days} trading days

**A. Historical Prices ({start_trading_date} to {cut_off_date})**
{his_prices}

**B. Event Intelligence**
{event_list}

**TASK:**
Predict the {prediction_days}-day cumulative Rate of Change (ROC) category based on the data above. 

**STRICT CONSTRAINTS:**
1. **BRIEF ANALYSIS:** You are permitted to provide a concise reasoning (Maximum 2 to 3 sentences) explaining your directional bias and volatility expectations before classifying.
2. **FORMAT:** You must output EXACTLY ONE of the following labels: "Up", "Neutral", or "Down" to indicate the predicted future trend, along with a confidence score between 0 and 100 for your judgment.
3. **WRAPPER:** You MUST wrap the exact label and confidence score inside `<prediction>` and `<score>` tags.

**Output:**
[Brief Analysis]
<prediction>...</prediction>
<score>...</score>
'''

#######################(Low-Liquidity 40) LOHO LIVING Ablation 3way & 5way ############################

#######################LIVING 3way############################
TREND_FORECASTING_SYSTEM_PROMPT_LOHO_3WAY_LIVING='''
**Task:**
You will be provided with a company's historical stock prices. Your task is to forecast the stock's cumulative Rate of Change (ROC) over a long-term monthly horizon into one of three strict categories:

* **"Up"**: ROC > 0.05 (Cumulative gain over 5%)
* **"Neutral"**: -0.05 <= ROC <= 0.05 (Flat, noise, or tight consolidation)
* **"Down"**: ROC < -0.05 (Cumulative loss worse than -5%)
'''

TREDN_FORECASTING_USER_PROMPT_LOHO_3WAY_LIVING='''
**Target Company:** {company_name}
**Forecast Date (Cut-off):** {cut_off_date}
**Prediction Horizon:** Forecast the long-term trend {prediction_horizon} months ahead (around {prediction_target}). 

**A. Historical Prices (Weekly Friday prices from {start_trading_date} to {cut_off_date})**
{his_prices}

**TASK:**
Predict the stock's {prediction_horizon}-month (long-term, around {prediction_target}) trend cumulative Rate of Change (ROC) category based on the data above.

**STRICT CONSTRAINTS:**
1. **COMPREHENSIVE ANALYSIS:** Provide an in-depth and comprehensive reasoning to explain your directional bias and volatility expectations before classifying. Do not rush; thoroughly evaluate the underlying signals.
2. **FORMAT:** You must output EXACTLY ONE of the following three categorical labels: "Up", "Neutral", or "Down". NO other words, numbers, or punctuation inside the tags.
3. **WRAPPER:** You MUST wrap the exact label inside `<prediction>` tags.

**Output:**
[COMPREHENSIVE Analysis]
<prediction>...</prediction>
'''

###################### LIVING 5 way #######################
TREND_FORECASTING_SYSTEM_PROMPT_LOHO_5WAY_LIVING='''
**Task:**
You will be provided with a company's historical stock prices. Your task is to forecast the stock's cumulative Rate of Change (ROC) over a long-term monthly horizon into one of FIVE strict categories:

* **"Strong Up"**: ROC > 0.15 (Significant cumulative gain over 15%)
* **"Up"**: 0.05 < ROC <= 0.15 (Moderate cumulative gain between 5% and 15%)
* **"Neutral"**: -0.05 <= ROC <= 0.05 (Flat, noise, or tight consolidation within ±5%)
* **"Down"**: -0.15 <= ROC < -0.05 (Moderate cumulative loss between -5% and -15%)
* **"Strong Down"**: ROC < -0.15 (Significant cumulative loss worse than -15%)
'''

TREDN_FORECASTING_USER_PROMPT_LOHO_5WAY_LIVING='''
**Target Company:** {company_name}
**Forecast Date (Cut-off):** {cut_off_date}
**Prediction Horizon:** Forecast the long-term trend {prediction_horizon} months ahead (around {prediction_target}). 

**A. Historical Prices (Weekly Friday prices from {start_trading_date} to {cut_off_date})**
{his_prices}

**TASK:**
Predict the stock's {prediction_horizon}-month (long-term, around {prediction_target}) trend cumulative Rate of Change (ROC) category based on the data above.

**STRICT CONSTRAINTS:**
1. **COMPREHENSIVE ANALYSIS:** Provide an in-depth and comprehensive reasoning to explain your directional bias and volatility expectations before classifying. Do not rush; thoroughly evaluate the underlying signals.
2. **FORMAT:** You must output EXACTLY ONE of the following three categorical labels: "Up", "Neutral", or "Down". NO other words, numbers, or punctuation inside the tags.
3. **WRAPPER:** You MUST wrap the exact label inside `<prediction>` tags.

**Output:**
[COMPREHENSIVE Analysis]
<prediction>...</prediction>
'''

#############################################
# (High-Liquidity, 30) SOHO, 3-way & 5-way 
#############################################

TREND_FORECASTING_SYSTEM_PROMPT_3WAY_SOHO='''
**Task:**
You will be provided with a company's recent historical stock prices and a list of news events (or N/A) affecting the company. Your task is to forecast the stock's cumulative Rate of Change (ROC) over a specified number of future trading days by classifying it into one of three strict categories:

* **"Up"**: ROC > 0.005 (Cumulative gain over 0.5%)
* **"Neutral"**: -0.005 <= ROC <= 0.005 (Flat, noise, or tight consolidation)
* **"Down"**: ROC < -0.005 (Cumulative loss worse than -0.5%)
'''

TREDN_FORECASTING_USER_PROMPT_3WAY_SOHO='''
**Target Company:** {company_name}
**Forecast Date (Cut-off):** {cut_off_date}
**Prediction Horizon:** Next {prediction_days} trading days

**A. Historical Prices ({start_trading_date} to {cut_off_date})**
{his_prices}

**B. Event Intelligence**
{event_list}

**TASK:**
Predict the {prediction_days}-day cumulative Rate of Change (ROC) category based on the data above. 

**STRICT CONSTRAINTS:**
1. **COMPREHENSIVE ANALYSIS:** Provide an in-depth and comprehensive reasoning to explain your directional bias and volatility expectations before classifying. Do not rush; thoroughly evaluate the underlying signals.
2. **FORMAT:** You must output EXACTLY ONE of the following three categorical labels: "Up", "Neutral", or "Down". NO other words, numbers, or punctuation inside the tags.
3. **WRAPPER:** You MUST wrap the exact label inside `<prediction>` tags.

**Output:**
[COMPREHENSIVE Analysis]
<prediction>...</prediction>
'''

# * **"Strong Up"**: ROC > 0.05 (Significant gain over 5% driven by major positive structural catalysts)
# * **"Up"**: 0.02 < ROC <= 0.05 (Moderate gain between 2% and 5% from ordinary positive news or technical momentum)
# * **"Neutral"**: -0.02 <= ROC <= 0.02 (Flat, noise, exhausted news, or tight consolidation)
# * **"Down"**: -0.05 <= ROC < -0.02 (Moderate loss between -2% and -5% from ordinary negative news or technical pullback)
# * **"Strong Down"**: ROC < -0.05 (Significant loss worse than -5% driven by major structural risks or severe miss)
TREND_FORECASTING_SYSTEM_PROMPT_5WAY_SOHO='''
**Task:**
You will be provided with a company's recent historical stock prices and a list of news events (or N/A) affecting the company. Your task is to forecast the stock's cumulative Rate of Change (ROC) over a specified number of future trading days by classifying it into one of FIVE strict categories:

* **"Strong Up"**: ROC > 0.02 (Significant gain over 2% driven by major positive structural catalysts)
* **"Up"**: 0.005 < ROC <= 0.02 (Moderate gain between 0.5% and 2% from ordinary positive news or technical momentum)
* **"Neutral"**: -0.005 <= ROC <= 0.005 (Flat, noise, exhausted news, or tight consolidation)
* **"Down"**: -0.02 <= ROC < -0.005 (Moderate loss between -0.5% and -2% from ordinary negative news or technical pullback)
* **"Strong Down"**: ROC < -0.02 (Significant loss worse than -2% driven by major structural risks or severe miss)
'''

TREDN_FORECASTING_USER_PROMPT_5WAY_SOHO='''
**Target Company:** {company_name}
**Forecast Date (Cut-off):** {cut_off_date}
**Prediction Horizon:** Next {prediction_days} trading days

**A. Historical Prices ({start_trading_date} to {cut_off_date})**
{his_prices}

**B. Event Intelligence**
{event_list}

**TASK:**
Predict the {prediction_days}-day cumulative Rate of Change (ROC) category based on the data above. 

**STRICT CONSTRAINTS:**
1. **COMPREHENSIVE ANALYSIS:** Provide an in-depth and comprehensive reasoning to explain your directional bias and volatility expectations before classifying. Do not rush; thoroughly evaluate the underlying signals.
2. **FORMAT:** You must output EXACTLY ONE of the following FIVE categorical labels: "Strong Up", "Up", "Neutral", "Down", or "Strong Down". NO other words, numbers, or punctuation inside the tags.
3. **WRAPPER:** You MUST wrap the exact label inside `<prediction>` tags.

**Output:**
[COMPREHENSIVE Analysis]
<prediction>...</prediction>
'''


#############################################
# LIVING ABL (High-Liquidity, 30) LOHO, 3-way & 5-way 
#############################################
TREND_FORECASTING_SYSTEM_PROMPT_3WAY_SOHO_LIVING='''
**Task:**
You will be provided with a company's recent historical stock prices. Your task is to forecast the stock's cumulative Rate of Change (ROC) over a specified number of future trading days by classifying it into one of three strict categories:

* **"Up"**: ROC > 0.005 (Cumulative gain over 0.5%)
* **"Neutral"**: -0.005 <= ROC <= 0.005 (Flat, noise, or tight consolidation)
* **"Down"**: ROC < -0.005 (Cumulative loss worse than -0.5%)
'''

TREDN_FORECASTING_USER_PROMPT_3WAY_SOHO_LIVING='''
**Target Company:** {company_name}
**Forecast Date (Cut-off):** {cut_off_date}
**Prediction Horizon:** Next {prediction_days} trading days

**A. Historical Prices ({start_trading_date} to {cut_off_date})**
{his_prices}

**TASK:**
Predict the {prediction_days}-day (from {cut_off_date} to {prediction_target}) cumulative Rate of Change (ROC) category based on the data above. 

**STRICT CONSTRAINTS:**
1. **COMPREHENSIVE ANALYSIS:** Provide an in-depth and comprehensive reasoning to explain your directional bias and volatility expectations before classifying. Do not rush; thoroughly evaluate the underlying signals.
2. **FORMAT:** You must output EXACTLY ONE of the following three categorical labels: "Up", "Neutral", or "Down". NO other words, numbers, or punctuation inside the tags.
3. **WRAPPER:** You MUST wrap the exact label inside `<prediction>` tags.

**Output:**
[COMPREHENSIVE Analysis]
<prediction>...</prediction>
'''

TREND_FORECASTING_SYSTEM_PROMPT_5WAY_SOHO_LIVING='''
**Task:**
You will be provided with a company's recent historical stock prices. Your task is to forecast the stock's cumulative Rate of Change (ROC) over a specified number of future trading days by classifying it into one of FIVE strict categories:

* **"Strong Up"**: ROC > 0.02 (Significant gain over 2% driven by major positive structural catalysts)
* **"Up"**: 0.005 < ROC <= 0.02 (Moderate gain between 0.5% and 2% from ordinary positive news or technical momentum)
* **"Neutral"**: -0.005 <= ROC <= 0.005 (Flat, noise, exhausted news, or tight consolidation)
* **"Down"**: -0.02 <= ROC < -0.005 (Moderate loss between -0.5% and -2% from ordinary negative news or technical pullback)
* **"Strong Down"**: ROC < -0.02 (Significant loss worse than -2% driven by major structural risks or severe miss)
'''

TREDN_FORECASTING_USER_PROMPT_5WAY_SOHO_LIVING='''
**Target Company:** {company_name}
**Forecast Date (Cut-off):** {cut_off_date}
**Prediction Horizon:** Next {prediction_days} trading days

**A. Historical Prices ({start_trading_date} to {cut_off_date})**
{his_prices}

**TASK:**
Predict the {prediction_days}-day (from {cut_off_date} to {prediction_target}) cumulative Rate of Change (ROC) category based on the data above. 

**STRICT CONSTRAINTS:**
1. **COMPREHENSIVE ANALYSIS:** Provide an in-depth and comprehensive reasoning to explain your directional bias and volatility expectations before classifying. Do not rush; thoroughly evaluate the underlying signals.
2. **FORMAT:** You must output EXACTLY ONE of the following FIVE categorical labels: "Strong Up", "Up", "Neutral", "Down", or "Strong Down". NO other words, numbers, or punctuation inside the tags.
3. **WRAPPER:** You MUST wrap the exact label inside `<prediction>` tags.

**Output:**
[COMPREHENSIVE Analysis]
<prediction>...</prediction>
'''

##########################################################################################

TREND_FORECASTING_SYSTEM_PROMPT_REJECT_3WAY_HIGH='''
You are a highly capable financial AI assistant. 

**Task:**
You will be provided with a company's recent historical stock prices and a list of news events (or N/A) affecting the company. Your task is to forecast the stock's cumulative Rate of Change (ROC) over a specified number of future trading days by classifying it into one of three strict categories:

* **"Up"**: ROC > 0.005 (Cumulative gain over 0.5%)
* **"Neutral"**: -0.005 <= ROC <= 0.005 (Flat, noise, or tight consolidation)
* **"Down"**: ROC < -0.005 (Cumulative loss worse than -0.5%)

Strictly output "Up", "Neutral", or "Down" ONLY IF you detect an exceptionally strong, fundamental-altering signal; otherwise, you MUST output exactly "ABSTAIN" to avoid speculative guessing.
'''

TREDN_FORECASTING_USER_PROMPT_REJECT_3WAY_HIGH='''
**Target Company:** {company_name}
**Forecast Date (Cut-off):** {cut_off_date}
**Prediction Horizon:** Next {prediction_days} trading days

**A. Historical Prices ({start_trading_date} to {cut_off_date})**
{his_prices}

**B. Event Intelligence**
{event_list}

**TASK:**
Predict the {prediction_days}-day cumulative Rate of Change (ROC) category based on the data above. 

**STRICT CONSTRAINTS:**
1. **BRIEF ANALYSIS:** You are permitted to provide a concise reasoning (Maximum 2 to 3 sentences) explaining your directional bias and volatility expectations before classifying.
2. **FORMAT:** You must output EXACTLY ONE of the following labels: "Up", "Neutral", "Down", or "ABSTAIN". (ONLY output Up/Neutral/Down for exceptionally strong, fundamental-altering signals; otherwise, you MUST output "ABSTAIN"). NO other words, numbers, or punctuation.
3. **WRAPPER:** You MUST wrap the exact label inside `<prediction>` tags.

**Output:**
[Brief Analysis]
<prediction>...</prediction>
'''




TREND_FORECASTING_SYSTEM_PROMPT_COT_EVENT='''
You are a **Senior Quantitative Analyst specializing in Event-Driven Arbitrage**.

**Mission:**
Analyze **1-Month Historical Price Context**, **Macro Environment**, and recent **Event Streams** to predict the stock's {prediction_days}-day cumulative Rate of Change (ROC). You must strictly classify the projected move into one of three categories:
* **"Up"**: ROC > 0.005 (Cumulative gain over 0.5%)
* **"Neutral"**: -0.005 <= ROC <= 0.005 (Flat, noise, or tight consolidation)
* **"Down"**: ROC < -0.005 (Cumulative loss worse than -0.5%)

You must decipher the interaction between *Macro Sentiment* (The Tide), *1-Month Technical Positioning* (The Track/Expectation), and *New Information* (The Catalyst) to make this classification.

**The 3-Step Context-aid Forecasting Framework:**

**1. Define the Regime (The 1-Month Setup & Baseline):**
   * **Macro & Sector Overlay:** Is the broad market (e.g., S&P500) AND the specific industry sector providing a tailwind (risk-on) or headwind (risk-off)? (Sector context overrides general macro).
   * **Price Positioning & Volatility Context (The past 20 trading days):** Evaluate the 1-month trend leading up to the event, **specifically noting the stock's normal daily volatility**:
     * *Priced-in/Over-extended:* Has the stock trended upwards aggressively? (Implies high expectations, vulnerable to missing the +0.5% threshold if momentum stalls).
     * *Oversold/Depressed:* Has the stock trended downwards aggressively? (Implies low expectations, prime for short-covering > +0.5%).
     * *Consolidated Base:* Has the stock traded sideways in a tight range? (Expectations are neutral).
     * **Friction & Boundaries:** Identify prominent support/resistance levels. **Crucially, evaluate if the nearest ceiling or floor is close enough to trap the stock within the strict ±0.5% "Neutral" band over the next {prediction_days} days.**

**2. Extract the Dominant Driver & Expectation Gap:**
   * You will receive a list of recent events. **Filter out noise** (e.g., generic PR, macro noise that doesn't target the company).
   * Identify the **Single Dominant Catalyst**: Is it **Structural** or **Transitory**?
     * **CRITICAL RULE (Negativity Bias):** Severe structural risks (SEC probes, fraud) IMMEDIATELY override any positive catalysts. Treat them as a definitive driver for a **"Down"** classification.
   * **The Expectation Gap:** Compare the outcome against the expectations implied by the 1-Month Price Positioning. Forward-looking Guidance ALWAYS massively outweighs historical factual results.
   * **Catalyst Exhaustion (THE T+1 TRAP):** If the provided price data includes ANY open market trading time AFTER the news was released, or if a massive gap-up/gap-down is already visible, the catalyst is **DIGESTED and EXHAUSTED**. Exhausted catalysts rarely fuel continuous trends. **WARNING: If a positive news event already caused a massive gap-up today (T=0), the subsequent mean-reversion over the next {prediction_days} days will likely result in a "Down" or "Neutral" ROC, NOT "Up".**
   * **THE NEUTRAL ANCHOR (DEFAULT STATE):** If the dominant event is a scheduled pending event with an UNKNOWN outcome (e.g., "Earnings tomorrow"), or if the news is completely ambiguous, purely transitory, or highly conflicting, you MUST default to the **Neutral** classification. You need a valid structural driver or a clear expectation gap to break out of the ±0.5% boundary.

**3. Determine Reaction Dynamics & Final Classification (The Verdict):**
   Map the Regime + Catalyst intersection to EXACTLY ONE scenario below to determine your final {prediction_days}-day ROC classification:

   **➡️ Output "Down" (ROC < -0.005) if:**
   * *Long Squeeze:* Negative Catalyst + Over-extended Uptrend -> Trapped buyers panic sell.
   * *Death Spiral:* Negative Catalyst + Downtrend -> Support breaks, capitulation.
   * *Sell the News:* EXPECTED Positive Catalyst + Over-extended Uptrend -> Profit-taking into retail liquidity.
   * *Dead Cat Bounce:* Minor Positive Catalyst + Downtrend -> Brief relief rally fails, lower lows follow.

   **➡️ Output "Up" (ROC > 0.005) if:**
   * *Capitulation Reversal:* Major Positive Surprise + Downtrend -> Short covering initiates new uptrend.
   * *True Breakout:* UNEXPECTED Positive Surprise + Consolidated Base / Uptrend -> Momentum accelerates.
   * *Buy the Dip:* Minor Negative Catalyst + Strong Uptrend -> Intraday dip is aggressively bought.

   **➡️ Output "Neutral" (-0.005 <= ROC <= 0.005) if:**
   * *Friction/Drag:* Positive Catalyst + Strong Overhead Resistance / Hostile Macro -> Rally is choked.
   * *Exhausted/Noise:* Priced-in news (visible gap already occurred), pending events, or conflicting signals -> Sideways chop.
'''

TREND_FORECASTING_USER_PROMPT_COT='''
**Target Company:** {company_name}
**Target Analysis Date (Cut-off):** {cut_off_date}
**Prediction Horizon:** Next {prediction_days} trading days

**PART 1: DATA INGESTION**

**A. Historical Price Context (From {start_trading_date} to {cut_off_date})**
{his_prices}

**B. Event Intelligence & Macro Signals**
{event_list}

**Reasoning: The 3-Step Context-aid Forecasting**
You MUST strictly adhere to the 3-Step Context-aid Forecasting Framework defined in your system instructions.
* **CRITICAL REMINDER:** You operate under the **Neutral Anchor**. Pending events (unknown outcomes), exhausted catalysts (the T+1 trap), and purely transitory noise MUST result in a "Neutral" classification. Forward guidance explicitly overrides past facts. Severe structural risks trigger an immediate Negativity Bias ("Down").
* **Execution:** Your `<reasoning>` must clearly document your step-by-step logical deduction:
    * **Step 1 - Define the Regime:** Assess Macro/Sector context. Define the 1-month Price Positioning. **CRITICAL:** Explicitly state the normal daily volatility observed in the historical data and evaluate if the nearest Support/Resistance boundaries will trap the price within the strict ±0.5% Neutral band. 
    * **Step 2 - Extract Dominant Driver & Expectation Gap:** Filter out noise. Identify if the dominant catalyst is Structural or Transitory. Check for Catalyst Exhaustion (Did it already gap up/down today?). Define the Expectation Gap.
    * **Step 3 - Determine Reaction Dynamics:** You MUST explicitly declare EXACTLY ONE of the defined scenarios from your system instructions (e.g., "Sell the News", "True Capitulation Reversal", "Friction/Drag", etc.) and state its strictly mapped resulting classification (Up, Neutral, or Down).

**Prediction**
* **Format:** You must output EXACTLY ONE of the following three categorical labels. NO extra words, NO numbers, NO punctuation inside the tags.
    * Up
    * Neutral
    * Down
* **Wrapper:** Wrap the exact label in `<prediction>` tags.

**Output:**
[Reasoning]
(Follow the 3-step structure)
<prediction>...</prediction>
'''

# =============================================================================
#  WEATHER FORECASTING Agent
# =============================================================================
WEATHER_FORECASTING_SYSTEM_PROMPT='''
**Task:**
You will be provided with a city's recent historical hourly temperatures and a list of specific weather-related events (or N/A). Your task is to forecast the exact future hourly temperatures for a specified prediction horizon.
'''

WEATHER_PREDICT_USER_PROMPT='''
**Target Location:** {city_name}
**Forecast Time (Cut-off):** {cut_off_time}
**Prediction Horizon:** Next {prediction_days} days (Hourly Forecast)

**A. Historical Hourly Temperatures [Strictly in Celsius (°C)] ({start_time} to {cut_off_time})**
{his_temps}

**B. Meteorological Event Intelligence**
{event_list}

(Note: Temperatures mentioned in the events may be in Fahrenheit. You MUST convert any Fahrenheit values to Celsius °C to match the historical baseline.)

**TASK:**
Predict the hourly temperatures for the next {prediction_days} days based on the data above. 
Since you are generating an hourly forecast, you MUST output EXACTLY {total_hours} data points (24 hours * {prediction_days} days).

**STRICT CONSTRAINTS:**
1. **BRIEF ANALYSIS:** Provivde a concise reasoning to explain your prediciton.
2. **UNIT ALIGNMENT (CRITICAL):** Your final predicted values MUST be in Celsius (°C) to align with the magnitude and distribution of the Historical Hourly Temperatures in Part A.
3. **FORMAT:** Comma-separated values ONLY. No units, no dates, no extra text. 
4. **WRAPPER:** Wrap the forecasting numbers inside `<prediction>` tags.

**Output:**
<prediction>val1, val2, val3, ..., valN</prediction>
'''


TAXI_FORECASTING_SYSTEM_PROMPT='''
**Task:**
You will be provided with New York City's recent historical hourly records for a specific yellow taxi mobility metric: {target_metric_name}. 

Domain Context:
{metric_context}

You will also receive a list of relevant urban events (e.g., weather conditions, public holidays, major city events, or N/A). Your task is to forecast the exact future {total_hours} hourly values for {target_metric_name} for a specified prediction horizon.
'''

TAXI_PREDICT_USER_PROMPT='''
**Target Metric:** {target_metric_name}
**Target Location:** New York City (Yellow Taxi Zone)
**Forecast Time (Cut-off):** {cut_off_time}
**Prediction Horizon:** Next {prediction_days} days (Hourly Forecast)

**A. Historical Hourly Records ({start_time} to {cut_off_time})**
{historical_values}

**B. Urban Event Intelligence**
{event_list}

(Note: Consider how the events listed above interact with the typical daily and weekly seasonality of the {target_metric_name}.)

**TASK:**
Predict the future hourly values for {target_metric_name} for the next {prediction_days} days based on the historical data and event intelligence above. 
Since you are generating an hourly forecast, you MUST output EXACTLY {total_hours} data points.

**STRICT CONSTRAINTS:**
1. **BRIEF ANALYSIS:** Provide a reasoning to explain your prediction.
2. **FORMAT:** Comma-separated values ONLY for the numerical array.
3. **WRAPPER:** Wrap the final sequence of forecasting numbers strictly inside `<prediction>` tags.

**Output Format:**
[Your reasoning here]
<prediction>val1, val2, val3, ..., valN</prediction>
'''


ELEC_FORECASTING_SYSTEM_PROMPT='''
**Task:**
You will be provided with {city_name}'s recent historical hourly records for electricity load. 

**Domain Context:**
Electricity load represents the aggregate electrical power demand across the city. It exhibits distinct daily and weekly seasonality patterns. Crucially, it is highly sensitive to external factors: extreme weather strongly drives heating or cooling demands, while public holidays significantly disrupt routine consumption behaviors.

You will also receive a list of relevant urban and environmental events (e.g., weather conditions, public holidays, major city events, or N/A). Your task is to forecast the exact future {total_hours} hourly values for the electricity load for a specified prediction horizon.
'''

ELEC_PREDICT_USER_PROMPT='''
**Target Metric:** Electricity Load
**Target Location:** {city_name}
**Forecast Time (Cut-off):** {cut_off_time}
**Prediction Horizon:** Next {prediction_days} days (Hourly Forecast)

**A. Historical Hourly Records ({start_time} to {cut_off_time})**
{historical_values}

**B. Environmental & Urban Event Intelligence**
{event_list}

(Note: Consider how the events listed above—especially extreme weather conditions or public holidays—interact with the typical daily (day/night) and weekly (weekday/weekend) seasonality of electricity load.)

**TASK:**
Predict the future hourly values for electricity load for the next {prediction_days} days.
Since you are generating an hourly forecast, you MUST output EXACTLY {total_hours} data points.

**STRICT CONSTRAINTS:**
1. **BRIEF ANALYSIS:** Provide a reasoning to explain your prediction. 
2. **FORMAT:** Comma-separated values ONLY for the numerical array. 
3. **WRAPPER:** Wrap the final sequence of forecasting numbers strictly inside `<prediction>` tags.

**Output Format:**
[Your reasoning here]
<prediction>val1, val2, val3, ..., valN</prediction>
'''

ELEC_FORECASTING_SYSTEM_PROMPT_SEARCH='''
**Task:**
You will be provided with {city_name}'s recent historical hourly records for electricity load. 

**Domain Context:**
Electricity load represents the aggregate electrical power demand across the city. It exhibits distinct daily and weekly seasonality patterns. Crucially, it is highly sensitive to external factors: extreme weather strongly drives heating or cooling demands, while public holidays significantly disrupt routine consumption behaviors.

**Search Instruction:**
You are allowed to use the search function to gather relevant external information (e.g., historical weather, holiday schedules) to assist your prediction. **CRITICAL:** All searched information must strictly predate **{cut_off_time}**. You must not use any data or future knowledge beyond this exact timestamp to prevent data leakage.'''

ELEC_PREDICT_USER_PROMPT_SEARCH='''
**Target Metric:** Electricity Load
**Target Location:** {city_name}
**Forecast Time (Cut-off):** {cut_off_time}
**Prediction Horizon:** Next {prediction_days} days (Hourly Forecast)

**Historical Hourly Records ({start_time} to {cut_off_time})**
{historical_values}

**TASK:**
Predict the future hourly values for electricity load for the next {prediction_days} days.
Since you are generating an hourly forecast, you MUST output EXACTLY {total_hours} data points.

**STRICT CONSTRAINTS:**
1. **TIME BOUNDARY:** Any external information retrieved via search MUST strictly predate `{cut_off_time}` to prevent data leakage.
2. **SEARCH EVIDENCE:** Wrap any information retrieved via search strictly inside `<search_results>` tags before your analysis.
3. **BRIEF ANALYSIS:** Provide a reasoning to explain your prediction. 
4. **FORMAT:** Comma-separated values ONLY for the numerical array. 
5. **WRAPPER:** Wrap the final sequence of forecasting numbers strictly inside `<prediction>` tags.

**Output Format:**
<search_results>
[Relevant information retrieved via search, strictly prior to {cut_off_time}]
</search_results>
[Your reasoning here]
<prediction>val1, val2, val3, ..., valN</prediction>
'''

##############################################
# (1) Weather Trend 
##############################################

WEATHER_TREND_FORECASTING_SYSTEM_PROMPT = '''
**Task:**
Analyze the city's recent historical temperatures and weather-related events (if any) to forecast the trend of the future {temp_type} temperature over the specified horizon.
'''
WEATHER_TREND_USER_PROMPT_3WAY = '''
**Target Location:** {city_name}
**Forecast Time:** {cut_off_time}
**Prediction Horizon:** Next {prediction_days} days

**A. Historical Hourly Temperatures [Celsius, °C] ({start_time} to {cut_off_time})**
{his_temps}

**B. Meteorological Event Intelligence**
{event_list}

(Note: Temperatures mentioned in the events may be in Fahrenheit °F. You MUST convert any Fahrenheit values to Celsius °C to match the historical baseline.)

**TASK:**
Forecast the trend of the {temp_type} temperature for the next {prediction_days} days, relative to the previous 24 hours` temperature, based on the data above.

**Trend Classification (Change in Celsius °C):**
* **Up:** Change > 1.5°C
* **Neutral:** Change between -1.5°C and 1.5°C
* **Down:** Change < -1.5°C

**STRICT CONSTRAINTS:**
1. **BRIEF ANALYSIS:** Provide a concise reasoning for your forecast.
2. **FORMAT:** Your final prediction MUST be exactly one of these labels: Up, Neutral, or Down. No other text inside the tags.
3. **WRAPPER:** Enclose your final label inside `<prediction>` tags.

**Output:**
[Concise Analysis]
<prediction>Trend_Label</prediction>
'''
WEATHER_TREND_USER_PROMPT_5WAY = '''
**Target Location:** {city_name}
**Forecast Time:** {cut_off_time}
**Prediction Horizon:** Next {prediction_days} days

**A. Historical Hourly Temperatures [Celsius, °C] ({start_time} to {cut_off_time})**
{his_temps}

**B. Meteorological Event Intelligence**
{event_list}

(Note: Temperatures mentioned in the events may be in Fahrenheit °F. You MUST convert any Fahrenheit values to Celsius °C to match the historical baseline.)

**TASK:**
Forecast the trend of the {temp_type} temperature for the next {prediction_days} days, relative to the previous 24 hours` temperature, based on the data above.

**Trend Classification (Change in Celsius °C):**
* **Strong Up:** Change > 3°C
* **Up:** Change > 1.5°C and <= 3°C
* **Neutral:** Change between -1.5°C and 1.5°C
* **Down:** Change >= -3°C and < -1.5°C
* **Strong Down:** Change < -3°C

**STRICT CONSTRAINTS:**
1. **BRIEF ANALYSIS:** Provide a concise reasoning for your forecast.
2. **FORMAT:** Your final prediction MUST be exactly one of these labels: Strong Up, Up, Neutral, Down, or Strong Down. No other text inside the tags.
3. **WRAPPER:** Enclose your final label inside `<prediction>` tags.

**Output:**
[Concise Analysis]
<prediction>Trend_Label</prediction>
'''

##############################################
# (1) ELEC Trend 
##############################################

ELEC_LOAD_FORECASTING_SYSTEM_PROMPT = '''
**Task:**
Analyze the location's recent historical electrical load and relevant grid/weather-related events (if any) to forecast the trend of the future {forecast_type} electrical load over the specified horizon.
'''

ELEC_LOAD_USER_PROMPT_3WAY = '''
**Target Location:** {city_name}
**Forecast Time:** {cut_off_time}
**Prediction Horizon:** Next {prediction_horizon} days

**A. Historical Electrical Load [Megawatts, MW] ({start_time} to {cut_off_time})**
{his_time_series}

**B. Grid & Meteorological Event Intelligence**
{event_list}

(Note: Load values mentioned in the events might be in different units (e.g., GW). You MUST convert them to match the historical baseline of Megawatts (MW), where 1 GW = 1000 MW.)

**TASK:**
Forecast the trend of the {forecast_type} electrical load for the next {prediction_horizon} days, relative to the previous 24 hours' {forecast_type} load, based on the data above.

**Trend Classification (Absolute Change in {prediction_horizon} Load, MW):**
* **Up:** Change > 400 MW
* **Neutral:** Change between -400 MW and 400 MW
* **Down:** Change < -400 MW

**STRICT CONSTRAINTS:**
1. **COMPREHENSIVE ANALYSIS:** Provide a detailed and comprehensive reasoning for your forecast.
2. **FORMAT:** Your final prediction MUST be exactly one of these labels: Up, Neutral, or Down. No other text inside the tags.
3. **WRAPPER:** Enclose your final label inside `<prediction>` tags.

**Output:**
[Comprehensive Analysis]
<prediction>Trend_Label</prediction>
'''

ELEC_LOAD_USER_PROMPT_5WAY = '''
**Target Location:** {city_name}
**Forecast Time:** {cut_off_time}
**Prediction Horizon:** Next {prediction_horizon} days

**A. Historical Electrical Load [Megawatts, MW] ({start_time} to {cut_off_time})**
{his_time_series}

**B. Grid & Meteorological Event Intelligence**
{event_list}

(Note: Load values mentioned in the events might be in different units (e.g., GW). You MUST convert them to match the historical baseline of Megawatts (MW), where 1 GW = 1000 MW.)

**TASK:**
Forecast the trend of the {forecast_type} electrical load for the next {prediction_horizon} days, relative to the previous 24 hours' {forecast_type} load, based on the data above.

**Trend Classification (Absolute Change in {prediction_horizon} Load, MW):**
* **Strong Up:** Change > 1000 MW
* **Up:** 400 MW < Change <= 1000 MW
* **Neutral:** -400 MW <= Change <= 400 MW
* **Down:** -1000 MW <= Change < -400 MW
* **Strong Down:** Change < -1000 MW

**STRICT CONSTRAINTS:**
1. **COMPREHENSIVE ANALYSIS:** Provide a detailed and comprehensive reasoning for your forecast. Explicitly estimate the absolute change in {prediction_horizon} load before classifying to ensure accuracy across the five categories.
2. **FORMAT:** Your final prediction MUST be exactly one of these labels: Strong Up, Up, Neutral, Down, or Strong Down. No other text inside the tags.
3. **WRAPPER:** Enclose your final label inside `<prediction>` tags.

**Output:**
[Comprehensive Analysis]
<prediction>Trend_Label</prediction>
'''