# KOSMOS CYCLE PHYSICS & ECONOMICS

## 1. Economics: Paying for the Brain (GCA)
*   **Mechanism**: Google Cloud Billing Account.
*   **SKU**: Gemini Code Assist Enterprise.
*   **Cost**: ~$19/user/mo + Cloud Run Compute ($0.0000240/vCPU-sec).
*   **Optimization**: "UphillSnowball" consolidates users. One "Mega-User" (the Service Account) runs the fleet.

## 2. GCA Memory: The Acceleration Vector
*   **Without GCA**: Monkey tries random code -> Judge Rejects -> Retry. (Cycle Time: 5m).
*   **With GCA Memory**: Monkey queries Memory ("Don't use AWS") -> Writes GCloud code -> Judge Accepts.
*   **Impact**: **Reduces Cycle Waste by 40-60%**. Cycles converge faster because they don't repeat known mistakes.

## 3. Browser Drag: The Speed Limit
The type of "Eye" determines the cycle speed:
1.  **Curldata (No Browser)**: Speed: **100ms**. (API Calls). Use for Financial Data.
2.  **Jetski (Headless/Playwright)**: Speed: **5-10s**. (DOM Parsing). Use for Research.
3.  **Bennett (Headful/Visual)**: Speed: **30-60s**. (Rendering/Screenshots). Use for "Trend Shopping".
    *   *Trade-off*: Visual proof ("I saw the price") costs time.

## 4. The "Whiteboard" Concept (Iteration 0)
*   **Concept**: The Whiteboard is the **Task Graph**.
*   **Impact on Cycle**:
    *   *Without Whiteboard*: Monkey guesses step-by-step. (Wanders).
    *   *With Whiteboard*: Monkey pre-computes the path ("Search -> Click -> Buy").
    *   **Result**: "Iteration 0" takes 5s, but saves 10 futile iterations. It is the **Anchor**.

## 5. The Claude Leak Terminals
*   **Do we have them?**: We have the **Logic**, not the UI.
*   **Implementation**: `kosmos_prompts.py` contains the "Hidden Chain of Thought" (`<antthinking>`) and "Terminal Simulation" (`<tool_code>`).
*   **Effect**: The Kosmos Monkey *simulates* a terminal interaction in its mind before executing it on Cloud Run.
