from recommendation.mongo_loader import load_data_from_mongodb
from recommendation.mcdm import calculate_mcdm_for_application


# Load data from MongoDB
data = load_data_from_mongodb()

polymers_df = data["polymers"]
properties_df = data["properties"]
applications_df = data["applications"]


# Test A001
result = calculate_mcdm_for_application(
    properties_df,
    applications_df,
    "A001"
)


print("\nMongoDB + MCDM Test")
print("=" * 40)

print("Result Keys:", list(result.keys()))

print("Eligible Materials:", len(result["eligible_ids"]))
print("Rejected Materials:", len(result["rejected"]))

print("\nEligible Polymer IDs:")
for polymer_id in result["eligible_ids"]:
    print(polymer_id)

print("\nRankings:")

for item in result["results"]:
    print(
        item["rank"],
        item["polymer_id"],
        "->",
        round(item["mcdm_score"], 4)
    )