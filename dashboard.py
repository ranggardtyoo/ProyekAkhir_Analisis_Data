import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_sum_season_x_df(df):
    sum_season_x_df = all_df.groupby("season_x").cnt_y.sum().sort_values(ascending=False).reset_index()
    return sum_season_x_df

def create_bycasual_df(df):
    bycasual_df = all_df.groupby(by="mnth_x").casual_y.nunique().reset_index()
    bycasual_df.rename(columns={
    "casual_y": "pengguna_casual"
    }, inplace=True)
    
    return bycasual_df

def create_byregistered_df(df):
    byregistered_df = all_df.groupby(by="mnth_x").registered_y.nunique().reset_index()
    byregistered_df.rename(columns={
    "registered_y": "pengguna_registered"
    }, inplace=True)
    
    return byregistered_df

def create_rfm_df(df):
    rfm_df = all_df.groupby(by="instant", as_index=False).agg({
    "dteday_x": "max", #mengambil tanggal order terakhir
    "casual_y": "nunique",
    "registered_y": "nunique",
    "cnt_y": "sum"
})
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency_casual", "frequency_registered", "monetary"]
    
    rfm_df["max_order_timestamp"] = pd.to_datetime(rfm_df["max_order_timestamp"]).dt.date 
    recent_date = pd.to_datetime(all_df["dteday_x"]).dt.date.max() 
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

all_df = pd.read_csv("all_data.csv")

datetime_columns = ["dteday_x"]
all_df.sort_values(by="dteday_x", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["dteday_x"].min()
max_date = all_df["dteday_x"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["dteday_x"] >= str(start_date)) & 
                (all_df["dteday_x"] <= str(end_date))]

sum_season_x_df = create_sum_season_x_df(main_df)
bycasual_df = create_bycasual_df(main_df)
byregistered_df = create_byregistered_df(main_df)
rfm_df = create_rfm_df(main_df)

st.header('Dicoding Collection Dashboard :sparkles:')

#pertanyaan 1
st.subheader("Perbandingan Jumlah Pemakaian Berdasarkan Musim")

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(24, 6))

colors = ["#D3D3D3", "#72BCD4","#D3D3D3", "#D3D3D3"]

sns.barplot(x="season_x", y="cnt_y", data=sum_season_x_df.head(5), palette=colors, ax=ax)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis ='y', labelsize=12)

plt.suptitle("Jumlah Pengguna Terbanyak Berdasarkan Musim ", fontsize=20)
plt.show()

st.pyplot(fig)

#pertanyaan 2
st.subheader("Perbandingan Jumlah Pengguna Setiap Bulan Berdasarkan Status Pengguna")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(20, 10))

    colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    sns.barplot(
        y="pengguna_casual",
    x="mnth_x",
    data=bycasual_df.sort_values(by="pengguna_casual", ascending=False),
    palette=colors
    )
    plt.title("Jumlah Penguna Casual Setiap Bulan Dalam Setahun", loc="center", fontsize=15)
    plt.ylabel(None)
    plt.xlabel(None)
    plt.tick_params(axis='x', labelsize=12)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(20, 10))
    
    colors = ["#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    sns.barplot(
    y="pengguna_registered",
    x="mnth_x",
    data=byregistered_df.sort_values(by="pengguna_registered", ascending=False),
    palette=colors
)
    plt.title("Jumlah Penguna Registered Setaip Bulan Dalam Setahun", loc="center", fontsize=15)
    plt.ylabel(None)
    plt.xlabel(None)
    plt.tick_params(axis='x', labelsize=12)
    st.pyplot(fig)

# Best Customer Based on RFM Parameters
st.subheader("Pengguna Casual dan Registered Berdasarkan RFM Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

rfm_df["frequency"] = rfm_df["frequency_casual"] + rfm_df["frequency_registered"]
with col2:
    avg_frequency = round(rfm_df["frequency"].mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)

sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)

sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)

st.pyplot(fig)