# Logistics Operations KPI Analysis
# This script loads "angard_parcel_operations.csv" and prints key KPIs pre- vs post- intervention.
import pandas as pd
from datetime import datetime

df = pd.read_csv("angard_parcel_operations.csv", parse_dates=["scan_time","delivery_time"])

layout_change_date = pd.Timestamp("2025-05-15")
pre = df[df["scan_time"] < layout_change_date]
post = df[df["scan_time"] >= layout_change_date]

def kpis(sub):
    total = len(sub)
    on_time = (sub["delivery_status"] == "Delivered On-Time").sum()
    missort = sub["missort_flag"].sum()
    avg_proc = sub["process_seconds"].mean()
    return {
        "parcels": total,
        "on_time_rate": round(on_time/total*100, 2) if total else 0,
        "missort_rate": round(missort/total*100, 2) if total else 0,
        "avg_process_seconds": round(avg_proc, 2) if total else 0,
    }

print("=== OVERALL KPIs ===")
print(kpis(df))
print("\n=== PRE-INTERVENTION (before 2025-05-15) ===")
print(kpis(pre))
print("\n=== POST-INTERVENTION (on/after 2025-05-15) ===")
print(kpis(post))

# Shift-level performance
shift_kpis = df.groupby("shift").apply(kpis).apply(pd.Series)
print("\n=== KPIs by Shift (Overall) ===")
print(shift_kpis)

# Center-level mis-sort breakdown
missort_by_center = df.groupby("center")["missort_flag"].mean().mul(100).round(2).sort_values()
print("\n=== Missort Rate by Center (%) ===")
print(missort_by_center)

# New vs experienced clerks during training window
training_mask = (df["scan_time"].dt.date >= pd.to_datetime("2025-04-15").date()) & (df["scan_time"].dt.date <= pd.to_datetime("2025-05-14").date())
training_df = df[training_mask]
if len(training_df):
    new = training_df[training_df["is_new_clerk"]==1]
    exp = training_df[training_df["is_new_clerk"]==0]
    print("\n=== Training Window Comparison (2025-04-15 to 2025-05-14) ===")
    print("New Clerks Avg Process Seconds:", round(new["process_seconds"].mean(),2))
    print("Experienced Clerks Avg Process Seconds:", round(exp["process_seconds"].mean(),2))
