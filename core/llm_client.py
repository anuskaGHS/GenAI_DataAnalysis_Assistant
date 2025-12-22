import requests
import json
import config


class LLMClient:
    """Handles communication with LLM (OpenAI-compatible & Ollama APIs)"""

    def __init__(self):
        """Initialize LLM client with config settings"""
        self.provider = config.LLM_PROVIDER
        self.base_url = config.LLM_BASE_URL
        self.model = config.LLM_MODEL
        self.api_key = config.LLM_API_KEY
        self.available = True

    def _check_availability(self):
        """Check if LLM is available and responding"""
        try:
            response = self._make_request(
                prompt="Hello",
                max_tokens=10,
                temperature=0.7
            )
            return response is not None
        except Exception as e:
            print(f"LLM not available: {e}")
            return False

    def _make_request(self, prompt, max_tokens=1000, temperature=0.7):
        print("LLM CALLED WITH PROMPT:", prompt[:200])

        """Make a request to the LLM API (Ollama or OpenAI-style)"""
        try:
            # -------------------------------
            # OLLAMA (local)
            # -------------------------------
            if self.provider == "ollama":
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }

                response = requests.post(
                    self.base_url,
                    json=payload,
                    timeout=180
                )

                if response.status_code == 200:
                    print("LLM RAW RESPONSE:", response.text[:500])
                    return response.json().get("response", "").strip()
                else:
                    print(f"Ollama error: {response.status_code} - {response.text}")
                    return None

            # -------------------------------
            # OPENAI / COMPATIBLE
            # -------------------------------
            else:
                endpoint = f"{self.base_url}/chat/completions"

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }

                payload = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are a professional data analyst. "
                                "Provide clear, accurate insights based only on the data provided. "
                                "Never hallucinate or make up information."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }

                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=payload,
                    timeout=60
                )

                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content']
                else:
                    print(f"LLM API error: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            print(f"Error making LLM request: {e}")
            return None

    # ===============================
    # HIGH-LEVEL AGENT FUNCTIONS
    # ===============================

    print(">> generate_insights CALLED")

    def generate_insights(self, context, data_summary):
        if not self.available:
            return self._fallback_insights()

        prompt = f"""
STRICT RULES:
- Use only the provided dataset information
- Do not invent numbers or facts
- If information is missing, say "Not enough data"
- Keep responses concise

You are analyzing a dataset. Based on the following information, provide clear insights.

DATASET CONTEXT:
{context}

DATA SUMMARY:
{data_summary}

Please provide:
1. Key observations (3-5 points)
2. Interesting patterns or trends
3. Potential data quality issues
4. Suggestions for further analysis

Keep your response clear, concise, and based ONLY on the provided data.
Do not make assumptions beyond what the data shows.
"""
        response = self._make_request(prompt, max_tokens=800, temperature=0.7)
        return response if response else self._fallback_insights()

    def generate_executive_summary(self, analysis_results):
        if not self.available:
            return self._fallback_summary()

        prompt = f"""
You are creating an executive summary for a data analysis report.

ANALYSIS RESULTS:
{analysis_results}

Write a concise executive summary (3-4 paragraphs) that:
1. Describes what the dataset contains
2. Highlights the most important findings
3. Provides actionable insights

Use clear, professional language. Base everything on the provided data.
"""
        response = self._make_request(prompt, max_tokens=600, temperature=0.7)
        return response if response else self._fallback_summary()

    def generate_recommendations(self, analysis_results):
        if not self.available:
            return self._fallback_recommendations()

        prompt = f"""
Based on the following data analysis, provide 3-5 actionable recommendations.

ANALYSIS RESULTS:
{analysis_results}

Each recommendation should:
- Be specific and actionable
- Be based on the data provided
- Focus on insights or improvements

Format as a numbered list.
"""
        response = self._make_request(prompt, max_tokens=500, temperature=0.7)
        return response if response else self._fallback_recommendations()

    def explain_chart(self, chart_description, data_context):
        if not self.available:
            return f"This chart shows: {chart_description}"

        prompt = f"""
Explain this chart in simple, plain English (2-3 sentences).

CHART DESCRIPTION:
{chart_description}

DATA CONTEXT:
{data_context}

Focus on what the chart reveals about the data.
"""
        response = self._make_request(prompt, max_tokens=200, temperature=0.7)
        return response if response else f"This chart shows: {chart_description}"

    # ===============================
    # FALLBACKS
    # ===============================

    def _fallback_insights(self):
        return """
**Insights (Basic Analysis):**

The LLM service is currently unavailable. Here are basic observations:

1. The dataset has been successfully loaded and cleaned
2. Statistical analysis has been performed on all numeric columns
3. Visualizations have been generated for key variables
4. Please review the charts and statistics for detailed information
"""

    def _fallback_summary(self):
        return """
This report presents an analysis of the uploaded dataset. The data has been processed,
cleaned, and analyzed to extract key statistics and patterns.
"""

    def _fallback_recommendations(self):
        return """
1. Review the statistical summaries for each variable
2. Examine the visualizations to identify patterns
3. Check for any data quality issues
4. Consider domain-specific analysis
5. Use insights to guide decisions
"""