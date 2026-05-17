### **SEER: Self-Evolving Event Retrieval Agent and Environment for Forecasting**
SEER is a closed-loop, self-improving pipeline designed for quantitative market price forecasting. It continuously refines both its local data sourcing (Environment) and its signal filtering (Retrieval) based on historical prediction outcomes as reward.



**1. Environment Construction (Online Retrieval)**

* An external, web-connected retrieval system continuously searches the internet for raw market events to populate a **Local Event Pool** (the Environment).
* This process is actively optimized by the **[MISSING]** module, which instructs the web searcher to hunt for previously uncaptured, sector-level predictive signals, ensuring blind spots are filled.



**2. Local Event Retrieval (Signal Filtering)**

* The SEER Agent uses the domain-specific **[MEMORY]** module to evaluate the local Event Pool.
* It filters out market noise and already-digested information, strictly selecting unpriced, high-impact events to serve as the "conditions" for the forecast.



**3. LLM Forecasting**
* The LLM generates a predictive forecast for the market target based on historical price trends and the highly curated events provided by the Local Retrieval step.


**4. Self-Evolution (Reflection & Feedback)**
* Once the ground-truth label is available, the agent compares its prediction to reality and undergoes a reflection process to evolve its knowledge bases:
* **Optimize [MEMORY] (Improves Retrieval):** The agent extracts success patterns from correct predictions or analyzes the root causes of failures. It learns exactly how sector events impact prices and updates the memory to better identify unpriced signals in future local retrievals.
* **Update [MISSING] (Improves Environment):** The agent identifies valuable information that would have helped the prediction but was absent from the Event Pool. It logs these gaps to upgrade the Environment's future web searches.


**5. Knowledge Condensation**
* To prevent bloat and maintain high information density, both the `[MEMORY]` and `[MISSING]` modules undergo periodic condensation. The system prunes trivial noise, merges redundant concepts, and compresses the text into concise, sector-wide rules.
