
##################################
# v0: Forecast with retrieval Agent 
##################################

SYSTEM_FIN_RETRIEVAL_PROMPT='''Your Task is to analyze raw market events, extract high-value signals, and discard irrelevant noise for quantitative stock price/trend forecasting.
# OBJECTIVE
Based on the provided [DOMAIN], [TARGET] introduction and corresponding [MEMORY], evaluate a given list of recent events. Your goal is to select the events that possess predictive power for future price trends, filtering out market noise and information that has been priced in. You must strictly base your event selection on the knowledge provided in [MEMORY]. If [MEMORY] is empty, select all available events.
'''

USER_FIN_RETRIEVAL_PROMPT='''
**Target Company:** {company_name}
**Target Analysis Date (Cut-off):** {fore_cut_off_date}
**Prediction:** Next {prediction_horizon} Trading Day Price Trend

**A. [DOMAIN], [TARGET] and [MEMORY]**
{memory_info}
**B. RAW EVENTS LIST:**
{event_list_str_ids}

Based on the above information, please perform a comprehensive analysis and list the IDs of the useful events from the "RAW EVENTS", separated by commas. You must strictly base your event selection on the knowledge provided in [MEMORY]. If [MEMORY] is empty, select all available events.

Output Format:
[Analysis]
<events> ... </events>
'''

##################################
# 2.1 Add to Memory **TASK:**
##################################
SYSTEM_FIN_IMPROVING_PROMPT='''
**TASK:** Optimize the [MEMORY] module based on the LLM's prediction and the given "conditions" for the [SECTOR].  
([MEMORY] is to help the LLM identify events that are not fully priced in during forecasting.)
* **Reflect:** If the prediction and reasoning are correct, extract the success patterns. If incorrect, analyze the root causes of the failure. Summarize the patterns of how events in this sector impact stock prices and document them within the [MEMORY] module.
* **Context:** "Conditions" are unpriced, high-impact events retrieved from the "Event Pool" based on [MEMORY] (assuming an Efficient Market).
* **Update [MISSING]:** Populate the [MISSING] module by identifying valuable predictive signals in this sector that were absent from the current conditions.
'''

USER_FIN_IMPROVING_PROMPT='''
(1) Current Event Pool:
{event_list_pool}

(2) Prediction Conditions:
**Target Company:** {company_name}
**Target Analysis Date (Cut-off):** {fore_cut_off_date}
**Prediction Horizon:** Next {prediction_horizon} trading days

**A. Historical Prices (From {start_trading_date} to {fore_cut_off_date})**
{his_prices}

**B. Events Selected**
{event_list_selected}

(3) Prediction Process & Label:
{llm_forecasting_resp}

**Ground-Truth Label:** {label}

(4) [SECTOR] Information:
{sector}

(5) Current [MEMORY] Module  [{memory_cap}% — {memory_char}/12,000 chars]:
{memory_info}

(6) Current [MISSING] Module  [{missing_cap}% — {missing_char}/8,000 chars]:
{missing_info}

**INSTRUCTIONS:**
Comprehensively analyze the prediction under the current conditions. 
1. Add any new insights related to event selection inside the `<MEMORY>` tags. 
2. If any existing memory entries are explicitly incorrect and need removal, list their IDs (comma-separated) inside the `<delete>` tags. 
3. Summarize the currently missing predictive event types inside the `<MISSING>` tags.

**OUTPUT FORMAT:**
[Comprehensive Analysis]
<MEMORY> ... </MEMORY>
<delete> ... </delete>
<MISSING> ... </MISSING>
'''

##################################
# 2.2: Condense the memory 
##################################
CONDENSE_MEM_SYSTEM_PROMPT='''Your task is to optimize a "Memory List" containing historical market drivers and predictive factors for the sector:
{sector}
    
Guidelines for condensing the memory:
1. Prune the unimportant: Remove trivial, highly specific, or outdated noise that does not possess strong, recurring predictive power for future price movements.
2. Merge the redundant: Identify overlapping concepts or highly similar factors and synthesize them into a single, comprehensive rule.
3. Compress the size: You must compress the memory to approximately HALF of its original words.

**OUTPUT FORMAT:**
First, provide a comprehensive analysis, then, output the final condensed memory list enclosed within `<CONDENSED_MEMORY> ... </CONDENSED_MEMORY>` tags.

Provide one rule per line inside the `<CONDENSED_MEMORY>` tags.
'''

CONDENSE_MEM_USER_PROMPT='''Here is the current memory list:
{memory_str}
'''

##################################
# 2.3: Condense the Missing 
##################################
CONDENSE_MISS_SYSTEM_PROMPT='''Your task is to optimize a "Missing Signals List" containing suggestions for uncaptured predictive factors and information gaps that could improve future forecasting for the sector:
{sector}
    
Guidelines for condensing the missing signals:
1. Elevate to Sector-Level: Generalize highly specific, single-stock suggestions into broader, sector-wide predictive signals. Remove narrow metrics that lack structural relevance to the overall sector.
2. Merge the redundant: Identify overlapping concepts or highly similar missing factors and synthesize them into a single, comprehensive signal.
3. Compress the size: You must compress the list to approximately HALF of its original words, retaining only the most critical, high-impact missing variables.

**OUTPUT FORMAT:**
First, provide a comprehensive analysis, then, output the final condensed missing list enclosed within `<CONDENSED_MEMORY> ... </CONDENSED_MEMORY>` tags.

Provide one signal per line inside the `<CONDENSED_MEMORY>` tags.
'''

CONDENSE_MISS_USER_PROMPT='''Here is the current list of missing signals:
{memory_str}
'''

