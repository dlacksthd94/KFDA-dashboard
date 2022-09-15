# import dash_bio as db
from matplotlib.pyplot import plot
import pandas as pd
import os
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly


class MiamiPlot:
    def __init__(self) -> None:
        self.df_outcome, self.df_meta = self.load_data()
        self.list_drug = (
            self.df_outcome["drug_exposure"].str.replace("_bf", "").unique().tolist()
        )
        self.list_bio_marker = [
            "Triglycerides",
            "Free Cholesterol",
            "Esterified Cholesteryl",
            "Cholesterol",
            "Phospholipids",
            "Total Lipids",
            "Lipoprotein particles",
        ]
        self.df_merge = None

    def load_data(self):
        # load file
        WORKSPACE_DIR_PATH = r"/media/leelabsg-storage0/UKBB_WORK/KFDA_GUEST1/"
        DATA_DIR_PATH = os.path.join(WORKSPACE_DIR_PATH, "outcome")
        USER_DIR_PATH = os.path.join(WORKSPACE_DIR_PATH, "users/vis")

        file = r"UKBB_EUR_multivariate_5drugs_249metabolites_cross_sectional.csv"
        file_path = os.path.join(DATA_DIR_PATH, file)
        df_outcome = pd.read_csv(file_path)

        file = r"Nightingale_biomarker_groups.txt"
        file_path = os.path.join(USER_DIR_PATH, file)
        df_meta = pd.read_csv(file_path, sep="\t")

        df_meta["title"] = df_meta["title"].str.replace(
            "Concentration of", "Lipoprotein particles in"
        )
        df_meta["title"] = df_meta["title"].str.replace(
            "Cholesteryl Esters", "Esterified Cholesteryl"
        )
        df_meta["title"] = df_meta["title"].str.replace(
            "Chylomicrons and Extremely Large", "Extremely Large"
        )
        df_meta["title"] = df_meta["title"].str.replace(" Particles", "")

        return df_outcome, df_meta

    def filter(self, drug, list_bio_marker):
        # filtering
        DRUG = drug
        # DRUG = 'statin'
        LIST_BIO_MARKER = list_bio_marker
        # LIST_BIO_MARKER = ['Esterified Cholesteryl', 'Cholesterol']

        df_drug = self.df_outcome[
            self.df_outcome["drug_exposure"] == f"{DRUG}_bf"
        ]  # select drug
        df_drug = df_drug.reset_index(drop=True)
        df_drug

        list_size = [
            "Extremely Large",
            "Very Large",
            "Large",
            "Medium",
            "Small",
            "Very Small",
        ]
        list_lipo = ["LDL", "VLDL", "HDL"]
        dict_title = {
            f"{bio_marker} in {size} {lipo}": [size, lipo, bio_marker]
            for size in list_size
            for lipo in list_lipo
            for bio_marker in LIST_BIO_MARKER
        }
        df_lipo = self.df_meta[
            self.df_meta["title"].isin(dict_title)
        ]  # select metabolite
        df_lipo = df_lipo.drop(columns=["units", "Group", "Subgroup"])
        df_lipo["title"].unique()

        # preprocess
        dict_size = {
            "Extremely Large": "XXL",
            "Very Large": "XL",
            "Large": "L",
            "Medium": "M",
            "Small": "S",
            "Very Small": "XS",
        }

        def preprocess(row):
            title = row["title"]
            row = row.append(
                pd.Series(
                    dict_title[title], index=["size", "lipoprotein", "bio_marker"]
                )
            )
            row["size"] = dict_size[row["size"]]
            row = row.drop("title")
            return row

        df_lipo = df_lipo.apply(preprocess, axis="columns")
        df_lipo = df_lipo.sort_values(["bio_marker", "lipoprotein"])
        df_lipo.head(50)

        df_drug["metabolite"] = df_drug["metabolite"].str[1:6].astype(int)

        # join tables
        df_merge = pd.merge(
            df_drug, df_lipo, how="inner", left_on="metabolite", right_on="field_id"
        )
        df_merge = df_merge.sort_values(["bio_marker", "lipoprotein"])

        self.df_merge = df_merge

    def render(self):
        # select model
        MODEL_NUM = 1
        CI_LEVEL = 1.96

        df_model = self.df_merge[
            ["bio_marker", "drug_exposure", "size", "lipoprotein"]
            + list(
                filter(lambda val: val.endswith(str(MODEL_NUM)), self.df_merge.columns)
            )
        ]

        # calculate CI
        df_model[f"CI{MODEL_NUM}"] = (
            CI_LEVEL
            * df_model[f"se{MODEL_NUM}"]  # / np.sqrt(df_model[f'n{MODEL_NUM}'])
        )

        # make multi-level index
        df_model = df_model.set_index(["bio_marker", "lipoprotein", "size"])

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
            rows=1, cols=len(set_bio_marker), shared_yaxes=True, horizontal_spacing=0
        )
        range_max = (
            df_model[f"beta{MODEL_NUM}"].max() + df_model[f"CI{MODEL_NUM}"].max()
        )
        range_min = (
            df_model[f"beta{MODEL_NUM}"].min() - df_model[f"CI{MODEL_NUM}"].max()
        )

        for i, (bio_marker, df_group) in enumerate(df_model.groupby("bio_marker")):
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

        for i, (bio_marker, df_group) in enumerate(df_model.groupby("bio_marker")):
            list_lipo = df_group.groupby("lipoprotein").count()["color"].to_list()
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

        for i, (bio_marker, df_group) in enumerate(df_model.groupby("bio_marker")):
            _ = fig.update_xaxes(
                title_text=bio_marker,
                side="top",
                titlefont_size=12,
                tickfont_size=10,
                tickmode="linear",
                row=1,
                col=i + 1,
            )
            _ = fig.update_yaxes(
                showspikes=False,
                showline=False,
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
