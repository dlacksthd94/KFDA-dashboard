import dash_bio as db
from matplotlib.pyplot import plot
import pandas as pd
import os
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly


class MiamiPlot:
    def __init__(self) -> None:
        self.df_metabolite = self.load_data()
        self.list_drug = (
            self.df_metabolite["drug_exposure"].str.replace("_bf", "").unique().tolist()
        )
        self.list_bio_marker = self.df_metabolite["Order"].unique().tolist()
        self.df_select = None

    def load_data(self):
        # load file
        df = pd.read_csv("../../outcome/KFDA_vis_data.csv")
        # df = pd.read_csv('outcome/KFDA_vis_data.csv')
        df["Suborder"] = df["Suborder"].fillna(' ').astype(str).str.strip('.0')
        df["title"] = df["title"].str[:30]
        return df

    def filter(self, drug, list_bio_marker):
        # filtering
        DRUG = drug
        # DRUG = "statin"

        df_select = self.df_metabolite[
            self.df_metabolite["drug_exposure"] == f"{DRUG}_bf"
        ]  # select drug
        df_select = df_select[df_select["Order"].isin(list_bio_marker)]

        self.df_select = df_select

    def render(self):
        # select model
        MODEL_NUM = 1
        CI_LEVEL = 1.96

        df_model = self.df_select[
            ["drug_exposure", "Order", "Suborder", "title"]
            + list(
                filter(lambda val: val.endswith(str(MODEL_NUM)), self.df_select.columns)
            )
        ]

        # calculate CI
        df_model[f"CI{MODEL_NUM}"] = (
            CI_LEVEL
            * df_model[f"se{MODEL_NUM}"]  # / np.sqrt(df_model[f'n{MODEL_NUM}'])
        )

        # make multi-level index
        df_model = df_model.set_index(["Order", "Suborder", "title"])

        # set color
        def set_color(row):
            beta = row[f"beta{MODEL_NUM}"]
            if beta >= 0:
                row["color"] = plotly.colors.qualitative.Pastel1[0]  # pastel red
            else:
                row["color"] = plotly.colors.qualitative.Pastel1[1]  # pastel blue
            return row

        df_model = df_model.apply(set_color, axis="columns")

        # make vis
        # fig = go.Figure()
        set_bio_marker = set(df_model.index.get_level_values(0))
        fig = make_subplots(
            rows=1,
            cols=len(set_bio_marker),
            shared_yaxes=True,
            horizontal_spacing=0,
            column_widths=df_model.groupby("Order").apply(lambda df: len(df.index)).to_list(),
        )
        range_max = (
            df_model[f"beta{MODEL_NUM}"].max() + df_model[f"CI{MODEL_NUM}"].max()
        )
        range_min = (
            df_model[f"beta{MODEL_NUM}"].min() - df_model[f"CI{MODEL_NUM}"].max()
        )
        
        for i, (bio_marker, df_group) in enumerate(df_model.groupby("Order")):
            xlabels = [
                df_group.index.get_level_values(1),
                df_group.index.get_level_values(2),
                df_group.index,
            ]

            _ = fig.add_trace(
                go.Bar(
                    y=df_group[f"beta{MODEL_NUM}"],
                    x=xlabels,
                    showlegend=False,
                    error_y=dict(
                        type="data",
                        symmetric=True,
                        array=df_group[f"CI{MODEL_NUM}"],
                        thickness=0.7,
                    ),
                    marker=dict(color=df_group["color"])
                    # width=0.5,
                ),
                row=1,
                col=i + 1,
            )

        vrect_offset = -0.5
        vrect_width = 0
        num_lipo = 0
        num_vrect = 0

        for i, (bio_marker, df_group) in enumerate(df_model.groupby("Order")):
            list_lipo = df_group.groupby("Suborder").count()["color"].to_list()
            for lipo in list_lipo:
                vrect_width = lipo
                if num_lipo % 2 == 1:
                    _ = fig.add_vrect(
                        x0=vrect_offset,
                        x1=vrect_offset + vrect_width,
                        fillcolor="grey",
                        opacity=0.1,
                        layer="below",
                        line_width=0,
                        row=1,
                        col=i + 1,
                    )
                    num_vrect += 1
                num_lipo += 1
                vrect_offset += lipo
            vrect_offset = -0.5

        for i, (bio_marker, df_group) in enumerate(df_model.groupby("Order")):
            _ = fig.update_xaxes(
                title_text=bio_marker,
                side="top",
                titlefont_size=12,
                tickfont_size=10,
                tickmode="linear",
                row=1,
                col=i + 1,
            )

        _ = fig.update_layout(
            autosize=True,
            yaxis=dict(
                titlefont_size=16,
                tickfont_size=12,
                title="coefficient",
                showspikes=True,
            ),
            template="plotly_white",
        )

        return fig


self = MiamiPlot()