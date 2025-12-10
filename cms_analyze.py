import os 
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="DRG Explorer")

st.title("🏥 DRG Explorer Dashboard")

uploaded_file = st.sidebar.file_uploader("Upload MIH-by Provider & Service CSV", type="csv")

if not uploaded_file:
    st.info("Upload a CSV to continue.")
    st.stop()
df = pd.read_csv(uploaded_file, encoding='latin1')
# DEFAULT_FILE = "MUP_INP_RY25_P03_V10_DY23_PrvSvc.CSV"


# uploaded_file = st.sidebar.file_uploader("Upload MIH-by Provider and Service CSV", type="csv")

# if uploaded_file is not None:
#     data_source = uploaded_file
# else:
#     if os.path.exists(DEFAULT_FILE):
#         data_source = DEFAULT_FILE
#         st.sidebar.info("Using default CSV file (MIH-by Provider and Service 2023).")
#     else:
#         st.error("File not found. Please upload a CSV file.")
#         st.stop()

# @st.cache_data
# def load_data(source):
#     return pd.read_csv(source, encoding='latin1')

# df = load_data(data_source)

# Derived columns
df["payment_yield"] = df["Avg_Tot_Pymt_Amt"] / df["Avg_Submtd_Cvrd_Chrg"]
df["RUCA_Category"] = df["Rndrng_Prvdr_RUCA_Desc"].fillna("Unknown")

# Rural/Urban 2 cats
urban_keywords = [
    "Metropolitan area core",
    "Metropolitan area high commuting",
    "Metropolitan area low commuting"
]
df["RUCA_Group"] = df["Rndrng_Prvdr_RUCA_Desc"].apply(
    lambda x: "Urban" if any(k in str(x) for k in urban_keywords)
    else ("Unknown" if "Unknown" in str(x) else "Rural")
)

mode = st.sidebar.radio("Choose View:", ["By DRG", "By State", "By RUCA"])

# -------------------------------------------------------------------------
# 1) BY DRG
# -------------------------------------------------------------------------
if mode == "By DRG":
    st.header("🔵 View: By DRG")

    drg_list = st.sidebar.multiselect(
        "Select DRG Description",
        sorted(df["DRG_Desc"].unique()),
        max_selections=1
    )
    if not drg_list:
        st.stop()

    df_sel = df[df["DRG_Desc"].isin(drg_list)]

    st.subheader("Selected DRG Descriptions")
    st.write(df_sel[["DRG_Cd", "DRG_Desc"]].drop_duplicates())
    df_sel = df_sel.dropna(subset=["DRG_Cd", "DRG_Desc"])

    # ---- Total Discharges per State ----
    discharges = (
        df_sel.groupby("Rndrng_Prvdr_State_Abrvtn")["Tot_Dschrgs"]
        .sum()
        .reset_index()
    )
    discharges = discharges.sort_values("Tot_Dschrgs",ascending=False)

    fig1 = px.bar(
        discharges,
        x="Rndrng_Prvdr_State_Abrvtn",
        y="Tot_Dschrgs",
        title="Total Discharges per State"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # ---- Average Payment per State ----
    avg_payment = (
        df_sel.groupby("Rndrng_Prvdr_State_Abrvtn")["Avg_Tot_Pymt_Amt"]
        .mean()
        .reset_index()
    )

    avg_payment = avg_payment.sort_values("Avg_Tot_Pymt_Amt", ascending=False)
    fig2 = px.choropleth(
        avg_payment,
        locations="Rndrng_Prvdr_State_Abrvtn",
        locationmode="USA-states",
        color="Avg_Tot_Pymt_Amt",
        color_continuous_scale="Viridis",
        scope="usa",
        title="Average Total Payment Amount per State"
    )
    fig2.add_scattergeo(
    locations=avg_payment['Rndrng_Prvdr_State_Abrvtn'],
    locationmode='USA-states',
    text=avg_payment['Rndrng_Prvdr_State_Abrvtn'],
    mode='text', 
    showlegend=False  
)
    fig2.update_layout(
        geo=dict(bgcolor='rgba(0,0,0,0)'),
        width=1000,
        height=800
    ) 
    st.plotly_chart(fig2, use_container_width=True)
    # fig2 = px.bar(
    #     avg_payment,
    #     x="Rndrng_Prvdr_State_Abrvtn",
    #     y="Avg_Tot_Pymt_Amt",
    #     title="Average Total Payment Amount per State"
    # )
    # st.plotly_chart(fig2, use_container_width=True)

    # ---- Average Submited Covered Charges per State ----
    # avg_charge = (
    #     df_sel.groupby("Rndrng_Prvdr_State_Abrvtn")["Avg_Submtd_Cvrd_Chrg"]
    #     .mean()
    #     .reset_index()
    # )
    # avg_charge = avg_charge.sort_values("Avg_Submtd_Cvrd_Chrg", ascending=False)
    # fig2b = px.bar(
    #     avg_charge,
    #     x="Rndrng_Prvdr_State_Abrvtn",
    #     y="Avg_Submtd_Cvrd_Chrg",
    #     title="Average Submitted Covered Charges per State"
    # )
    # st.plotly_chart(fig2b, use_container_width=True)

    avg_charge = (
        df_sel.groupby("Rndrng_Prvdr_State_Abrvtn")["Avg_Submtd_Cvrd_Chrg"]
        .mean()
        .reset_index()
    )
    avg_charge = avg_charge.sort_values("Avg_Submtd_Cvrd_Chrg", ascending=False)
    fig2b = px.choropleth(
        avg_charge,
        locations="Rndrng_Prvdr_State_Abrvtn",
        locationmode="USA-states",
        color="Avg_Submtd_Cvrd_Chrg",
        color_continuous_scale="Viridis",
        scope="usa",
        title="Average Submitted Covered Charges per State"
    )
    fig2b.add_scattergeo(
    locations=avg_charge['Rndrng_Prvdr_State_Abrvtn'],
    locationmode='USA-states',
    text=avg_charge['Rndrng_Prvdr_State_Abrvtn'],
    mode='text', 
    showlegend=False  
)
    fig2b.update_layout(
        geo=dict(bgcolor='rgba(0,0,0,0)'),
        width=1000,
        height=800
    ) 
    st.plotly_chart(fig2b, use_container_width=True)

    # City distribution

    city_counts = (
        df_sel.groupby("Rndrng_Prvdr_City")["Tot_Dschrgs"]
        .sum()
        .reset_index()
    )
    city_counts = city_counts.sort_values("Tot_Dschrgs", ascending=False).head(20)
    fig2c = px.bar(
        city_counts,    
        x="Rndrng_Prvdr_City",
        y="Tot_Dschrgs",
        title="City Distribution by Total Discharges"
    )
    st.plotly_chart(fig2c, use_container_width=True)

    # ---- RUCA distribution ----
    ruca_counts = (
        df_sel.groupby("RUCA_Category")["Tot_Dschrgs"]
        .sum()
        .reset_index()
    )

    fig3 = px.bar(
        ruca_counts,
        x="RUCA_Category",
        y="Tot_Dschrgs",
        title="RUCA Distribution (Rural / Urban) by Total Discharges"
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Hospitals distribution
    hospital_counts = (
        df_sel.groupby("Rndrng_Prvdr_Org_Name")["Tot_Dschrgs"]
        .sum()
        .reset_index()
    )
    hospital_counts = hospital_counts.sort_values("Tot_Dschrgs", ascending=False).head(20)

    fig4 = px.bar(
        hospital_counts,
        x="Rndrng_Prvdr_Org_Name",
        y="Tot_Dschrgs",
        title="Providers Distribution by Total Discharges"
    )
    st.plotly_chart(fig4, use_container_width=True)

    fig5= px.scatter(
        df_sel,
        x="Avg_Submtd_Cvrd_Chrg",
        y="Avg_Tot_Pymt_Amt",
        color="Rndrng_Prvdr_Org_Name",
        hover_data=["DRG_Desc"],
        title="Charges vs Payment (DRG-level)"
    )
    st.plotly_chart(fig5, use_container_width=True)

    # ruca_counts2= (
    #     df_sel.groupby("RUCA_Group")["Tot_Dschrgs"]
    #     .sum()
    #     .reset_index()
    # )
    # fig3b = px.bar(
    #     ruca_counts2,
    #     x="RUCA_Group",
    #     y="Tot_Dschrgs",
    #     title="RUCA Distribution (Rural / Urban)"
    # )
    # st.plotly_chart(fig3b, use_container_width=True)


# -------------------------------------------------------------------------
# 2) BY STATE
# -------------------------------------------------------------------------
elif mode == "By State":
    st.header("🟢 View: By State")

    state = st.sidebar.selectbox(
        "Select State",
        sorted(df["Rndrng_Prvdr_State_Abrvtn"].unique())
    )

    df_sel = df[df["Rndrng_Prvdr_State_Abrvtn"] == state]

    st.subheader(f"State: **{state}**")

    # Top DRGs by Discharges
    top_drg = (
        df_sel.groupby(["DRG_Cd", "DRG_Desc"])["Tot_Dschrgs"]
        .sum()
        .nlargest(10)
        .reset_index()
    )
    top_drg = top_drg.sort_values("Tot_Dschrgs", ascending=True)

    fig1 = px.bar(
        top_drg,
        x="Tot_Dschrgs",
        y="DRG_Desc",
        title="Top 10 DRGs by Discharges",
        orientation="h"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Top DRGs by payment
    top_payment = (
        df_sel.groupby(["DRG_Cd", "DRG_Desc"])["Avg_Tot_Pymt_Amt"]
        .mean()
        .nlargest(10)
        .reset_index()
    )

    top_payment = top_payment.sort_values("Avg_Tot_Pymt_Amt", ascending=True)
    fig2 = px.bar(
        top_payment,
        x="Avg_Tot_Pymt_Amt",
        y="DRG_Desc",
        title="Top 10 DRGs by Average Total Payment Amount",
        orientation="h"
    )
    st.plotly_chart(fig2, use_container_width=True)

    top_submitted = (
        df_sel.groupby(["DRG_Cd", "DRG_Desc"])["Avg_Submtd_Cvrd_Chrg"]
        .mean()
        .nlargest(10)
        .reset_index()
    )
    top_submitted = top_submitted.sort_values("Avg_Submtd_Cvrd_Chrg", ascending=True)  
    fig2b = px.bar(
        top_submitted,
        x="Avg_Submtd_Cvrd_Chrg",
        y="DRG_Desc",
        title="Top 10 DRGs by Average Submitted Covered Charges",
        orientation="h"
    )
    st.plotly_chart(fig2b, use_container_width=True)

    # RUCA distribution
    ruca_counts = df_sel["RUCA_Category"].value_counts().reset_index()
    ruca_counts.columns = ["RUCA", "Count"]

    fig3 = px.bar(
        ruca_counts,
        x="RUCA",
        y="Count",
        title="RUCA Distribution"
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Payment vs Charges
    fig4 = px.scatter(
        df_sel,
        x="Avg_Submtd_Cvrd_Chrg",
        y="Avg_Tot_Pymt_Amt",
        color="DRG_Cd",
        hover_data=["DRG_Desc"],
        title="Charges vs Payment (DRG-level)"
    )
    st.plotly_chart(fig4, use_container_width=True)

    # City distribution
    city_counts = (
        df_sel.groupby("Rndrng_Prvdr_City")["Tot_Dschrgs"]
        .sum()
        .reset_index()
    )
    city_counts = city_counts.sort_values("Tot_Dschrgs", ascending=False).head(20)
    fig5 = px.bar(
        city_counts,    
        x="Rndrng_Prvdr_City",
        y="Tot_Dschrgs",
        title="City Distribution by Total Discharges"
    )
    st.plotly_chart(fig5, use_container_width=True)

    # Hospitals distribution
    hospital_counts = (
        df_sel.groupby("Rndrng_Prvdr_Org_Name")["Tot_Dschrgs"]
        .sum()
        .reset_index()
    )
    hospital_counts = hospital_counts.sort_values("Tot_Dschrgs", ascending=False).head(20)

    fig6 = px.bar(
        hospital_counts,
        x="Rndrng_Prvdr_Org_Name",
        y="Tot_Dschrgs",
        title="Provider Distribution by Total Discharges"
    )
    st.plotly_chart(fig6, use_container_width=True)


# -------------------------------------------------------------------------
# 3) BY RUCA
# -------------------------------------------------------------------------
else:
    st.header("🟣 View: By RUCA")

    ruca_selected = st.sidebar.selectbox(
        "Select RUCA Category",
        sorted(df["RUCA_Category"].unique())
    )

    df_sel = df[df["RUCA_Category"] == ruca_selected]

    st.subheader(f"RUCA Category: **{ruca_selected}**")

    # Top DRGs
    top_drg = (
        df_sel.groupby(["DRG_Cd", "DRG_Desc"])["Tot_Dschrgs"]
        .sum()
        .nlargest(10)
        .reset_index()
    )
    top_drg = top_drg.sort_values("Tot_Dschrgs", ascending=True)

    fig1 = px.bar(
        top_drg,
        x="Tot_Dschrgs",
        y="DRG_Desc",
        orientation="h",
        title="Top DRGs in Selected RUCA"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Scatter Payment vs Charge
    fig2 = px.scatter(
        df_sel,
        x="Avg_Submtd_Cvrd_Chrg",
        y="Avg_Tot_Pymt_Amt",
        color="DRG_Cd",
        hover_data=["DRG_Desc"],
        title="Avg Charge vs Avg Payment"
    )
    st.plotly_chart(fig2, use_container_width=True)

    #Hospital distribution
    hospital_counts = (
        df_sel.groupby("Rndrng_Prvdr_Org_Name")["Tot_Dschrgs"]
        .sum()
        .reset_index()
    )
    hospital_counts = hospital_counts.sort_values("Tot_Dschrgs", ascending=False).head(20)
    fig2b = px.bar(
        hospital_counts,
        x="Rndrng_Prvdr_Org_Name",
        y="Tot_Dschrgs",
        title="Provider Distribution by Total Discharges"
    )
    st.plotly_chart(fig2b, use_container_width=True)
    # # State distribution
    # state_counts = (
    #     df_sel.groupby("Rndrng_Prvdr_St")["Tot_Dschrgs"]
    #     .sum()
    #     .reset_index()
    # )

    # fig3 = px.bar(
    #     state_counts,
    #     x="Rndrng_Prvdr_St",
    #     y="Tot_Dschrgs",
    #     title="State Distribution"
    # )
    # st.plotly_chart(fig3, use_container_width=True)
