import pandas as pd

df = pd.read_csv(
    "mstr_vw_fact_weekly_store_sku_volume.csv",
    nrows=10000,
    low_memory=False
)

print("Unique Brands:", df['client_brand_oid'].nunique())
print("\nSample Brand IDs:")
print(df['client_brand_oid'].drop_duplicates().head(20))
