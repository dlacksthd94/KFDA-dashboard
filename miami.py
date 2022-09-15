# import dash_bio as db
from matplotlib.pyplot import plot
import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly


class MiamiPlot:
    def __init__(self) -> None:
        self.df_metabolite = self.load_data()
        self.list_drug = (
            self.df_metabolite["drug_exposure"].str.replace("_bf", "").unique().tolist()
        )
        self.drug = None
        self.model = None
        self.p_value = None
        self.list_bio_marker = self.df_metabolite["Group"].unique().tolist()
        self.df_select = None

    def load_data(self):
        ### load file
        df = pd.read_csv("../../outcome/metab_example.csv", index_col=0)
        df = df.replace(['Branched-chain amino acids', 'Aromatic amino acids'], 'Amino acids')
        return df

    def filter(self, drug, model, p_value, list_bio_marker):
        ### filtering
        self.drug = drug

        df_select = self.df_metabolite[
            self.df_metabolite["drug_exposure"] == f"{self.drug}_bf"
        ]  # select drug
        df_select = df_select[df_select["Group"].isin(list_bio_marker)]

        ### select model
        self.model = model
        CI_LEVEL = 1.96

        df_select = df_select[
            ["drug_exposure", "Order", "Suborder", "title", "name", "Group", "Subgroup"]
            + list(
                filter(
                    lambda val: val.endswith(str(self.model))
                    or val.endswith(str(self.model) + "_FDR"),
                    df_select.columns,
                )
            )
        ]

        ### calculate CI
        df_select[f"CI{self.model}"] = (
            CI_LEVEL
            * df_select[
                f"se{self.model}"
            ]  # / np.sqrt(self.df_select[f'n{self.model}'])
        )

        ### p-value
        self.p_value = "" if p_value == "original" else "_" + p_value
        
        df_select["title"] = df_select["title"] + '  ' + (
            df_select[f"p{self.model}{self.p_value}"] <= 5e-2
        ).apply(lambda x: "*" if x else " ")
        
        df_select["title"] = df_select["title"] + (
            df_select[f"p{self.model}{self.p_value}"] <= 1e-2
        ).apply(lambda x: "*" if x else " ")
        
        df_select["title"] = df_select["title"] + (
            df_select[f"p{self.model}{self.p_value}"] <= 1e-3
        ).apply(lambda x: "*" if x else " ")
        
        ### labels
        df_select['Group'] = df_select['Group'].str.split(' ').str.join('\n')

        ### reverse order
        df_select = df_select.reindex(index=df_select.index[::-1])
        
        self.df_select = df_select

    def render(self):
        ### make multi-level index
        self.df_select = self.df_select.set_index(["Order", "Suborder", "title"])

        ### set color
        def set_color(row):
            beta = row[f"beta{self.model}"]
            if beta >= 0:
                row["color"] = plotly.colors.qualitative.Pastel1[0]  # pastel red
            else:
                row["color"] = plotly.colors.qualitative.Pastel1[1]  # pastel blue
            return row

        self.df_select = self.df_select.apply(set_color, axis="columns")

        fig = go.Figure()
        
        labels = [
            self.df_select["Group"].values,
            self.df_select.index.get_level_values(2),
            self.df_select.index,
        ]

        bar_chart = go.Bar(
            x=self.df_select[f"beta{self.model}"],
            y=labels,
            showlegend=False,
            error_x=dict(
                type="data",
                symmetric=True,
                array=self.df_select[f"CI{self.model}"],
                thickness=0.7,
            ),
            marker=dict(color=self.df_select["color"]),
            orientation="h",
            hoverinfo='text',
            hovertext=[
                f"Group: {row['Group']} \
                <br>Title: {i[2][:-4]} \
                <br>Full name: {row['name']} \
                <br>Covariates: {row[f'cov{self.model}']} \
                <br>N: {row[f'n{self.model}']} \
                <br>Beta & CI: {round(row[f'beta{self.model}'], 5)} ± {round(row[f'CI{self.model}'], 5)} \
                <br>Standard Error: {round(row[f'se{self.model}'], 5)} \
                <br>P-value: {row[f'p{self.model}{self.p_value}']}"
                for i, row in self.df_select.iterrows()
            ],
        )

        _ = fig.add_trace(
            bar_chart
        )

        _ = fig.update_xaxes(
            title_text="coefficient",
            side="bottom",
            titlefont_size=12,
            tickfont_size=10,
            mirror='ticks',
        )

        _ = fig.update_yaxes(
            side="top",
            tickfont_size=10,
            tickfont={"family": "Courier New"},
            tickmode="linear",
        )

        _ = fig.update_layout(
            # autosize=True,
            template="plotly_white",
            height=int(self.df_select.shape[0]) * 20 + 180,
            title={
                'text': 'Statin',
                'x': 0.5,
                'font': {
                    'size': 20,
                }
            },
            hovermode='y',
        )

        return fig