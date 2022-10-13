import csv, sys
from collections import defaultdict as dd
from flask import Flask
from flask import render_template
from flask import request

csv.field_size_limit(sys.maxsize)


def read_csv(fname):
    return list(csv.reader(open(fname, "r")))


def unique(l):
    return sorted(list(set(l)))


def unique2(l):
    return list(dict.fromkeys(l))


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api")
def api():
    df = read_csv("../../outcome/metab_example.csv")
    for r in df:
        if r[7] in "Branched-chain amino acids|Aromatic amino acids".split("|"):
            r[7] = "Amino acids"
    a = request.args
    m = a.get("m")  # mode
    if m == "list":
        q = a.get("q")  # query
        if q == "drug":
            return dict(
                status=0, response=unique2(r[9].replace("_bf", "") for r in df[1:])
            )
        elif q == "biom":
            return dict(status=0, response=unique2(r[7] for r in df[1:]))
    elif m == "drug_chart":
        drug, model, pvalue, bioms = [
            a.get(v) for v in "drug model pvalue bioms".split()
        ]
        if model == "1":
            cols = list(range(10, 15))
        elif model == "2":
            cols = list(range(15, 20))
        elif model == "3":
            cols = list(range(20, 25))
        else:
            return dict(status=2)
        if pvalue == "O":
            pass
        elif pvalue == "F":
            cols[4] = 24 + int(model)
        else:
            return dict(status=3)
        out, biomcnt, highs, lows = [], dd(int), [0], [0]
        for r in df[1:]:
            if r[9] == "%s_bf" % drug and r[7] in bioms.split("|"):
                out.append(
                    r[:10]
                    + [r[cols[0]], int(r[cols[1]])]
                    + [float(r[c]) for c in cols[2:]]
                )
                biomcnt[r[7]] += 1
                beta, se = float(r[cols[2]]), float(r[cols[3]])
                highs.append(beta + 1.96 * se)
                lows.append(beta - 1.96 * se)
        # out = [r[:10]+[r[c] for c in cols] for r in df[1:] if r[9]=='%s_bf'%drug and r[7] in bioms.split('|')]
        return dict(
            status=0,
            query=dict(drug=drug, model=model, pvalue=pvalue, bioms=bioms),
            response=dict(
                meta=dict(
                    count=len(out),
                    group_count=biomcnt,
                    minval=min(lows),
                    maxval=max(highs),
                ),
                header=df[0][:10] + "cov n beta se p".split(),
                content=out,
            ),
        )
    return dict(status=1)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
