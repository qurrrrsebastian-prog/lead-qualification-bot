"""Generate dummy leads for qualification bot. Author: Avatar Putra Sigit"""
import random
import pandas as pd
import os

def generate_leads(n: int = 50) -> pd.DataFrame:
    random.seed(42)
    industries = ["Property", "Hotel", "Hospital", "Retail", "Office", "Factory"]
    sources = ["Website", "Google Ads", "Referral", "Instagram", "LinkedIn"]
    data = []
    for i in range(1, n+1):
        days_ago = random.randint(1, 60)
        data.append({
            "id": i,
            "name": f"Lead_{i}",
            "company": f"PT {random.choice(['Mega','Grand','Royal','Elite','Prime'])} {random.choice(industries)}",
            "industry": random.choice(industries),
            "email": f"lead{i}@example.com",
            "phone": f"0812{random.randint(10000000,99999999)}",
            "contract_value_estimate": random.randint(5_000_000, 100_000_000),
            "source": random.choice(sources),
            "days_since_contact": days_ago,
            "engagement_score": random.randint(1, 10)
        })
    df = pd.DataFrame(data)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/leads.csv", index=False)
    print(f"Generated {n} leads")
    return df

if __name__ == "__main__":
    generate_leads()
