import pandas as pd
import os

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

print("\n================ FILE CHECK ================\n")
files = [f for f in os.listdir() if f.endswith(".csv")]
for f in files:
    print(f)

print("\n================ DATASET OVERVIEW ================\n")
for f in files:
    try:
        df = pd.read_csv(f, nrows=5, low_memory=False)
        print("\nFILE:", f)
        print("Columns:", df.columns.tolist())
        print("Sample Shape:", df.shape)
    except Exception as e:
        print("Error reading", f, ":", e)

print("\n================ IMPORTANT TABLE COLUMNS ================\n")

important_files = [
    "mstr_vw_fact_weekly_retail_scan_data.csv",
    "mstr_vw_fact_weekly_store_sku_volume.csv",
    "mstr_vw_ris_brand_all.csv",
    "mstr_vw_store.csv",
    "mstr_vw_dim_date.csv"
]

for f in important_files:
    print("\n\n-----", f, "-----")
    df = pd.read_csv(f, nrows=5, low_memory=False)
    print(df.columns.tolist())
    print(df.head())

print("\n================ BRAND CHECK ================\n")

brand = pd.read_csv("mstr_vw_ris_brand_all.csv", low_memory=False)

print("\nSearching for Montego and LD:")
for word in ["Montego", "LD"]:
    mask = brand.astype(str).apply(lambda col: col.str.contains(word, case=False, na=False)).any(axis=1)
    print(word, "found rows:", mask.sum())
    if mask.sum() > 0:
        print(brand.loc[mask].head(20))

print("\nFirst 50 brand_title values:")
print(brand[["client_brand_oid", "brand_title"]].head(50))

print("\n================ STATE CHECK ================\n")

store = pd.read_csv("mstr_vw_store.csv", low_memory=False)
print("States available:")
print(store["store_state"].dropna().unique())

print("\nNC store count:", (store["store_state"] == "NC").sum())
print("OH store count:", (store["store_state"] == "OH").sum())

print("\n================ VOLUME TABLE BRAND IDS ================\n")

volume = pd.read_csv("mstr_vw_fact_weekly_store_sku_volume.csv", low_memory=False)

print("Volume columns:")
print(volume.columns.tolist())

print("\nUnique brands in volume table:", volume["client_brand_oid"].nunique())
print("\nTop brand IDs by row count:")
print(volume["client_brand_oid"].value_counts().head(20))

active_brand_ids = volume["client_brand_oid"].drop_duplicates()

active_brands = brand[brand["client_brand_oid"].isin(active_brand_ids)]

print("\nActive brand names in volume data:")
print(active_brands[["client_brand_oid", "brand_title"]].sort_values("brand_title").head(100))

print("\n================ PRICE TABLE CHECK ================\n")

price = pd.read_csv("mstr_vw_fact_weekly_retail_scan_data.csv", low_memory=False)

print("Price table columns:")
print(price.columns.tolist())

print("\nPrice sample:")
print(price.head())

print("\n================ POSSIBLE JOIN KEYS ================\n")

print("Common columns between volume and price:")
print(set(volume.columns).intersection(set(price.columns)))

print("\nCommon columns between volume and brand:")
print(set(volume.columns).intersection(set(brand.columns)))

print("\nCommon columns between volume and store:")
print(set(volume.columns).intersection(set(store.columns)))

print("\n================ SAMPLE FINAL DATASET ================\n")

final_df = volume.merge(
    brand[["client_brand_oid", "brand_title"]],
    on="client_brand_oid",
    how="left"
)

store_cols = ["retail_number", "store_state", "store_name"]
store_cols = [c for c in store_cols if c in store.columns]

final_df = final_df.merge(
    store[store_cols],
    on="retail_number",
    how="left"
)

print("Final joined sample shape:", final_df.shape)
print(final_df.head(20))

print("\nRows by state:")
print(final_df["store_state"].value_counts().head(20))

print("\nRows by brand:")
print(final_df["brand_title"].value_counts().head(20))

print("\n================ ONE BRAND + ONE STATE SAMPLE ================\n")

sample_brand = final_df["brand_title"].dropna().value_counts().index[0]
sample_state = "NC" if "NC" in final_df["store_state"].dropna().unique() else final_df["store_state"].dropna().iloc[0]

filtered = final_df[
    (final_df["brand_title"] == sample_brand) &
    (final_df["store_state"] == sample_state)
]

print("Selected Brand:", sample_brand)
print("Selected State:", sample_state)
print("Filtered shape:", filtered.shape)
print(filtered.head(20))

print("\nWeekly volume summary:")

weekly = filtered.groupby("end_week", as_index=False).agg(
    total_volume=("volume", "sum"),
    total_consumer_unit_volume=("consumer_unit_volume", "sum"),
    records=("volume", "count")
)

print(weekly.head(30))

weekly.to_csv("weekly_volume_summary.csv", index=False)
final_df.head(5000).to_csv("joined_sample_output.csv", index=False)

print("\nDONE.")
print("Created files:")
print("1. weekly_volume_summary.csv")
print("2. joined_sample_output.csv")
