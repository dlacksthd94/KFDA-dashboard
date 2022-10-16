import csv, sys
from collections import defaultdict as dd
from flask import Flask
from flask import render_template
from flask import request

csv.field_size_limit(sys.maxsize)
app = Flask(__name__)


def read_csv(fname):
    return list(csv.reader(open(fname, "r")))


def list2set(l):
    return list(dict.fromkeys(l))


def meta2dict(df):
    dict_meta = {}
    for row in df:
        group = row[7]
        name = row[3]
        if group not in dict_meta:
            dict_meta[group] = []
        if name not in dict_meta[group]:
            dict_meta[group].append(name)
    return dict_meta


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api")
def api():
    df = read_csv("../../outcome/metab_all.csv")
    for row in df:
        if row[7] in ["Branched-chain amino acids", "Aromatic amino acids"]:
            row[7] = "Amino acids"
    args = request.args  # flask gets request. (e.g. "/api?mode=list&query=drug")
    mode = args.get("mode")  # mode
    if mode == "sidebar":
        query = args.get("query")  # query
        if query == "drug":
            return dict(
                status=0,
                response=list2set(
                    row[9].replace("_bf", "") for row in df[1:]
                ),  # 9 is the col idx of col 'drug_exposure'
            )
        elif query == "meta_group":
            return dict(
                status=0, response=list2set(row[7] for row in df[1:])
            )  # 7 is the col idx of col 'Group'
        elif query == "meta_name":
            return dict(
                status=0, response=list2set(row[3] for row in df[1:])
            )  # 3 is the col idx of col 'title'
        elif query == "meta":
            return dict(
                status=0, response=meta2dict(df[1:])
            )  # 3 is the col idx of col 'title'

    elif mode == "drug_chart":
        drug, model, pvalue, meta = [
            args.get(val) for val in ["drug", "model", "pvalue", "meta"]
        ]

        # filtering option: model
        if model == "1":
            cols = list(range(10, 15))
        elif model == "2":
            cols = list(range(15, 20))
        elif model == "3":
            cols = list(range(20, 25))
        else:
            return dict(status=2)

        # filtering option: p-value
        if pvalue == "original":
            pass
        elif pvalue == "FDR":
            cols[4] = 24 + int(model)
        else:
            return dict(status=3)

        # get chart info from df
        out, group_cnt, highs, lows = [], dd(int), [0], [0]
        for row in df[1:]:
            if row[9] == f"{drug}_bf" and row[7] in meta.split("|"):
                cov, n, (beta, se, p) = (
                    row[cols[0]],
                    int(row[cols[1]]),
                    (float(row[c]) for c in cols[2:]),
                )
                out.append(row[:10] + [cov, n, beta, se, p])  # each data
                group_cnt[row[7]] += 1  # num of each 'Groups'
                highs.append(beta + 1.96 * se)  # CI
                lows.append(beta - 1.96 * se)

        return dict(
            status=0,
            query=dict(drug=drug, model=model, pvalue=pvalue, meta=meta),
            response=dict(
                meta=dict(
                    count=len(out),
                    group_cnt=group_cnt,
                    minval=min(lows),
                    maxval=max(highs),
                ),
                header=df[0][:10] + ["cov", "n", "beta", "se", "p"],
                content=out,
            ),
        )

    elif mode == "meta_chart":
        meta, model, pvalue, drug = [
            args.get(val) for val in ["meta", "model", "pvalue", "drug"]
        ]

        # filtering option: model
        if model == "1":
            cols = list(range(10, 15))
        elif model == "2":
            cols = list(range(15, 20))
        elif model == "3":
            cols = list(range(20, 25))
        else:
            return dict(status=2)

        # filtering option: p-value
        if pvalue == "original":
            pass
        elif pvalue == "FDR":
            cols[4] = 24 + int(model)
        else:
            return dict(status=3)

        # get chart info from df
        out, drug_cnt, highs, lows = [], dd(int), [0], [0]
        for row in df[1:]:
            if row[3] == meta and row[9][:-3] in drug.split("|"):
                cov, n, (beta, se, p) = (
                    row[cols[0]],
                    int(row[cols[1]]),
                    (float(row[c]) for c in cols[2:]),
                )
                out.append(row[:10] + [cov, n, beta, se, p])  # each data
                # drug_cnt[row[7]] += 1  # num of each 'Groups'
                highs.append(beta + 1.96 * se)  # CI
                lows.append(beta - 1.96 * se)

        return dict(
            status=0,
            query=dict(meta=meta, model=model, pvalue=pvalue, drug=drug),
            response=dict(
                drug=dict(
                    count=len(out),
                    # group_cnt=drug_cnt,
                    minval=min(lows),
                    maxval=max(highs),
                ),
                header=df[0][:10] + ["cov", "n", "beta", "se", "p"],
                content=out,
            ),
        )
        
    return dict(status=1)


if __name__ == "__main__":
    app.run(debug=True)
