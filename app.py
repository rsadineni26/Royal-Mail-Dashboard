import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Logistics Ops Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("angard_parcel_operations.csv", parse_dates=["scan_time","delivery_time"])
    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data()
st.title("📦 Logistics Operations Data Optimization ")

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    centers = st.multiselect("Center", sorted(df["center"].unique().tolist()), default=sorted(df["center"].unique().tolist()))
    shifts = st.multiselect("Shift", sorted(df["shift"].unique().tolist()), default=sorted(df["shift"].unique().tolist()))
    date_range = st.date_input("Date range", [df["date"].min().date(), df["date"].max().date()])

mask = (
    df["center"].isin(centers) &
    df["shift"].isin(shifts) &
    (df["date"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
)
data = df[mask]

layout_change_date = pd.Timestamp("2025-05-15")

# KPIs
total = len(data)
on_time = (data["delivery_status"] == "Delivered On-Time").sum()
missort = data["missort_flag"].sum()
avg_proc = data["process_seconds"].mean()

kpi_cols = st.columns(4)
kpi_cols[0].metric("Parcels", f"{total:,}")
kpi_cols[1].metric("On-Time Rate", f"{(on_time/total*100 if total else 0):.1f}%")
kpi_cols[2].metric("Missort Rate", f"{(missort/total*100 if total else 0):.2f}%")
kpi_cols[3].metric("Avg Process (s)", f"{(avg_proc if not np.isnan(avg_proc) else 0):.1f}")

# Trend: On-time rate over time
daily = data.groupby("date").agg(
    parcels=("parcel_id","count"),
    on_time=("delivery_status", lambda s: (s=="Delivered On-Time").mean()*100),
    missort_rate=("missort_flag", "mean")
).reset_index()
daily["missort_rate"] = daily["missort_rate"]*100

st.subheader("On-time Rate Over Time")
fig1 = plt.figure()
plt.plot(daily["date"], daily["on_time"])
plt.axvline(layout_change_date, linestyle="--")
plt.title("On-time Rate (%) by Day")
plt.xlabel("Date")
plt.ylabel("On-time Rate (%)")
st.pyplot(fig1)

st.subheader("Missort Rate Over Time")
fig2 = plt.figure()
plt.plot(daily["date"], daily["missort_rate"])
plt.axvline(layout_change_date, linestyle="--")
plt.title("Missort Rate (%) by Day")
plt.xlabel("Date")
plt.ylabel("Missort Rate (%)")
st.pyplot(fig2)

st.subheader("Process Seconds by Shift")
by_shift = data.groupby("shift")["process_seconds"].mean().reindex(["Morning","Afternoon","Night"])
fig3 = plt.figure()
plt.bar(by_shift.index, by_shift.values)
plt.title("Average Process Seconds by Shift")
plt.xlabel("Shift")
plt.ylabel("Avg Process Seconds")
st.pyplot(fig3)

st.subheader("Missorts by Error Type")
error_counts = data[data["missort_flag"]==1]["error_type"].value_counts().reset_index()
error_counts.columns = ["error_type","count"]
fig4 = plt.figure()
plt.bar(error_counts["error_type"], error_counts["count"])
plt.title("Missorts by Error Type")
plt.xlabel("Error Type")
plt.ylabel("Count")
st.pyplot(fig4)

st.caption("Dashed line shows the layout optimization go-live: 2025-05-15.")
