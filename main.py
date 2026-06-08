import pandas as pd

brand = pd.read_csv(
    "mstr_vw_ris_brand_all.csv",
    low_memory=False
)

volume = pd.read_csv(
    "mstr_vw_fact_weekly_store_sku_volume.csv",
    nrows=10000,
    low_memory=False
)

brand_ids = volume['client_brand_oid'].drop_duplicates()

result = brand[
    brand['client_brand_oid'].isin(brand_ids)
]

print(result[['client_brand_oid','brand_title']].sort_values('brand_title'))
