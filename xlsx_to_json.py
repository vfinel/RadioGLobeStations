import pandas as pd
import json
import os


# Read the CSV file
df = pd.read_excel("./RadioGarden_Complete_Data.xlsx")


# Group by 'Name' and aggregate into the desired JSON structure
grouped = (
    df.groupby("Name")
    .apply(
        lambda x: {
            "coords": {
                "n": x["Value.coords.n"].iloc[0],
                "e": x["Value.coords.e"].iloc[0],
            },
            "urls": [
                {"name": row["Value.urls.name"], "url": row["Value.urls.url"]}
                for _, row in x.iterrows()
            ],
        }
    )
    .to_dict()
)

# Convert the dictionary to JSON
json_data = {k: v for k, v in grouped.items()}

# Write the JSON data to a file on the desktop
output_file_path = "stations.json"
with open(output_file_path, "w") as f:
    json.dump(json_data, f, indent=2)

print(f"The following JSON file has been created successfully: {output_file_path}")
