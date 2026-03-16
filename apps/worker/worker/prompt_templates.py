def build_geo_intent_prompt(brand_name: str, industry: str, intent: str) -> str:
    return (
        "You are evaluating AI search visibility for a brand. "
        "Given the user intent, decide if the brand should be mentioned and provide sentiment.\n"
        f"Brand: {brand_name}\n"
        f"Industry: {industry}\n"
        f"Intent: {intent}\n"
        "Return structured analysis for mention and sentiment."
    )
