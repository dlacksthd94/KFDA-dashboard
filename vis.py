import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from miami import MiamiPlot
import statsmodels.api as sm
import statsmodels.formula.api as smf

plt.rc("font", family="Malgun Gothic")

# BASE_PATH = "/media/leelabsg-storage0/UKBB_WORK/KFDA_GUEST1"
BASE_PATH = "../.."
DRUG_DATA_PATH = os.path.join(BASE_PATH, "drug_data")
META_DATA_PATH = os.path.join(BASE_PATH, "metabolomics_data")

st.set_page_config(
    page_title="Ex-stream-ly Cool App",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://www.extremelycoolapp.com/help",
        "Report a bug": "https://www.extremelycoolapp.com/bug",
        "About": "made by Lim",
    },
)

sidebar = st.sidebar
sidebar.title(":book: KFDA Dashboard")

menu = sidebar.selectbox(
    "MENU",
    (
        "Chart",
        "Experiment",
    ),
)

sidebar.markdown("---")

# sidebar.markdown(
#     """
#         <style>
#             [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
#                 width: 500px;
#             }
#             [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
#                 width: 500px;
#                 margin-left: -500px;
#             }
#         </style>
#     """,
#     unsafe_allow_html=True,
# )

sidebar.header("filter options")

if menu == 'Chart':
    
    # package = sidebar.radio("vis package", ["streamlit", "matplotlib", "plotly"])

    miami = MiamiPlot()
    col1, col2, col3 = sidebar.columns(3)
    drug = col1.selectbox("drug", miami.list_drug)
    model = col2.selectbox("model", [1, 2, 3])
    p_value = col3.selectbox("p value", ['original', 'FDR'])
    # list_bio_marker = sidebar.multiselect(
    #     "biomarkers", miami.list_bio_marker, miami.list_bio_marker
    # )
    is_all_selected = sidebar.checkbox('select all', value=True)
    is_checked = True if is_all_selected else False
    container = sidebar.container()
    with container:
        col1, col2 = st.columns([0.05, 1])
        list_bio_marker = []
        for bio_marker in miami.list_bio_marker:
            is_bio_marker_checked = col2.checkbox(bio_marker, value=is_checked)
            if is_bio_marker_checked:
                list_bio_marker.append(bio_marker)
        miami.filter(drug, model, p_value, list_bio_marker)
    
    submit = sidebar.button("Submit")

    # if submit:
    with st.spinner("Wait for it..."):
        fig = miami.render()
        st.plotly_chart(fig, use_container_width=True, width=50)

elif menu == 'Experiment':
    st.markdown('_TO BE UPDATED_')
    st.markdown('')
    st.markdown('')
    st.markdown('')
    
    list_file_meta = ['covariates_with_drugs.csv', 'covariates_without_drugs.csv']
    file_name = st.sidebar.selectbox("data", list_file_meta)
    
    @st.cache
    def load_data(file_name):
        df = pd.read_csv(os.path.join(META_DATA_PATH, file_name))
        # df.style # later...
        return df

    df = load_data(file_name)
    x = sidebar.multiselect("x", df.columns.tolist(), default=df.columns.tolist()[2:7])
    # y = sidebar.selectbox("y", list(filter(lambda x: x.endswith('_af') or x.endswith('_bf'), df.columns.tolist())))
    y = sidebar.selectbox("y", df.columns.tolist())

    df = df[[*x, y]].dropna()
    x_value = df[x]#.values.reshape(-1, 1)
    y_value = df[y]

    # x_value = df.iloc[:, 2:7]
    # y_value = df.iloc[:, -8]
    # is_na = x_value.isna().any()
    # x_value = x_value[~is_na]
    # y_value = y_value[~is_na]
    # model = LinearRegression()
    # model.fit(x_value, y_value)

    est = sm.OLS(y_value, x_value)
    est2 = est.fit()
    result = est2.summary()
    st.write(result)