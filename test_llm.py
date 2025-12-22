from core.llm_client import LLMClient

llm = LLMClient()

print("\n=== LLM TEST OUTPUT ===\n")
print(llm.generate_insights(
    context="Sales data for an e-commerce company",
    data_summary="Average sales: 12000, Highest month: March"
))
