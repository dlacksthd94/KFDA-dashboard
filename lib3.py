# -*- coding: utf-8
import csv, sys, time, datetime, codecs, unicodecsv
import numpy as np
import networkx as nx
from collections import defaultdict as dd
from collections import Counter
from bs4 import BeautifulSoup as soup
from multiprocessing import Pool, cpu_count as cpus
from importlib import reload
from random import sample

# from zipfile import ZipFile
# from io import TextIOWrapper
# import pandas as pd
# from quantecon.util.timing import loop_timer as lt, tic, tac, toc


def now():
    return datetime.datetime.now()


csv.field_size_limit(sys.maxsize)

# def proc_line_csv(args):
#   i, r = args
#   if i%100000==0: print(i, r)
#   return list(csv.reader(r))

# def proc_line_tsv(args):
#   i, r = args
#   if i%1000000==0: print(i, r)
#   return list(csv.reader(r, delimiter='\t'))

# def read_csv_zip(zname, fname, processes=1):
#   print('Reading', zname, fname)
#   output = []
#   with ZipFile(zname, 'r') as z:
#     with z.open(fname, 'r') as f:
#       with Pool(processes=40) as p:
#         ls = TextIOWrapper(f).readlines()
#         print('\t done reading file...')
#         output = list(p.map(proc_line_csv, enumerate(ls)))
#   return output

# def read_tsv_zip(zname, fname, processes=1):
#   print('Reading', zname, fname)
#   output = []
#   with ZipFile(zname, 'r') as z:
#     with z.open(fname, 'r') as f:
#       with Pool(processes=40) as p:
#         ls = TextIOWrapper(f).readlines()
#         print('\t done reading file...')
#         output = list(p.map(proc_line_tsv, enumerate(ls)))
#   return output


def aread_csv(fname):
    print("Reading", fname)
    return list(csv.reader(open(fname, "r", encoding="ISO-8859-1")))


def awrite_csv(fname, data):
    print("Writing", fname)
    output = csv.writer(open(fname, "w", encoding="ISO-8859-1"))
    output.writerows(data)


def read_csv(fname):
    print("Reading", fname)
    return list(csv.reader(open(fname, "r")))


def write_csv(fname, data):
    print("Writing", fname)
    output = csv.writer(open(fname, "w"))
    output.writerows(data)


def read_tsv(fname):
    print("Reading", fname)
    return list(csv.reader(open(fname, "r"), delimiter="\t"))


def write_tsv(fname, data):
    print("Writing", fname)
    output = csv.writer(open(fname, "w"), delimiter="\t")
    output.writerows(data)


def uread_csv(fname):
    print("Reading", fname)
    return list(unicodecsv.reader(open(fname, "rb")))


def uwrite_csv(fname, data):
    print("Writing", fname)
    output = unicodecsv.writer(open(fname, "wb"))
    output.writerows(data)


def usread_csv(fname):
    print("Reading (utf-8-sig)", fname)
    with open(fname, "r", encoding="utf-8-sig") as f:
        return list(csv.reader(f))


def uswrite_csv(fname, data):
    print("Writing (utf-8-sig)", fname)
    with open(fname, "w", encoding="utf-8-sig") as f:
        output = csv.writer(f)
        output.writerows(data)


# def write_dta(fname, data, header=True):
#  print('Writing (stata dta)', fname)
#  if header: pd.DataFrame(data[1:], columns=data[0]).to_stata(fname)
#  else: pd.DataFrame(data).to_stata(fname)


def d2l(dicobj, sortby=1, reverse=True):
    return sorted(dicobj.items(), key=lambda r: r[sortby], reverse=reverse)


def flatten(l):
    return [item for sublist in l for item in sublist]


def _v4p(v):
    if isinstance(v, list):
        return "<L(%d)>" % len(v)
    elif isinstance(v, dict):
        return "<D(%d)>" % len(v)
    elif isinstance(v, tuple):
        return "<T(%d)>" % len(v)
    else:
        return str(v).encode("utf-8").decode("utf-8")


def p(l, nrow=20):
    nrow = int(nrow / 2)
    if nrow == 0 or nrow * 2 > len(l):
        rgs = [range(len(l))]
    else:
        rgs = [range(nrow), range(len(l) - nrow, len(l))]
    for k, rg in enumerate(rgs):
        for i in rg:
            print("\t".join(["[%d]" % i] + [_v4p(v) for v in l[i]]))
        if len(rgs) == 2 and k == 0:
            print("\t".join("..." for v in range(len(l[i]) + 1)))


def repd(lol, reprule):
    # if a key in reprule is a string, the first row is assumed to be header. if a key is int, direct index.
    # repd = replace with dict; with lambda, there could be repf = replace with function
    thisrule = {}
    for k in reprule:
        if not isinstance(k, int):
            thisrule[lol[0].index(k)] = reprule[k]
        else:
            thisrule[k] = reprule[k]
    if sorted(thisrule.keys()) != sorted(reprule.keys()):
        lol = lol[1:]
    for r in lol:
        for k in thisrule:
            r[k] = thisrule[k][r[k]]


def col(lol, c):
    return [r[c] for r in lol]


def cols(lol, cs):
    out = []
    for r in lol:
        newr = []
        for c in cs:
            newr.append(r[c])
        out.append(newr)
    return out


def count(l, sorted=False):
    cnt = dd(int)
    for v in l:
        cnt[v] += 1
    if not sorted:
        return cnt
    else:
        return d2l(cnt)


def unique(l):
    return sorted(list(set(l)))


def lrange(*args):
    return list(range(*args))


def lmap(f, l):
    return list(map(f, l))


def enum(l):
    for i, v in enumerate(l):
        print("# [%d]" % i, v)


def check_rect(lol):
    for i, r in enumerate(lol):
        assert len(r) == len(lol[0]), [i, r]
    # print('All rows have the same length of %d.'%len(r))


def transpose(lol):
    return list(map(list, zip(*lol)))


def shape(l):
    return len(l), len(l[0])


def t(l):
    return list(zip(*l))


def summary(l):
    l = [float(v) for v in l if v != ""]
    print(
        "N\t%d\nmean\t%f\nstd\t%f\nmin\t%f\nmax\t%f"
        % (len(l), np.mean(l), np.std(l), np.min(l), np.max(l))
    )


def to_int(l, cs):
    for r in l:
        if isinstance(cs, list):
            for c in cs:
                r[c] = int(r[c])
        else:
            c = cs
            r[c] = int(r[c])


def to_int64(l, cs):
    for r in l:
        if isinstance(cs, list):
            for c in cs:
                r[c] = np.int64(r[c])
        else:
            c = cs
            r[c] = np.int64(r[c])


def to_float(l, cs):
    for r in l:
        if isinstance(cs, list):
            for c in cs:
                r[c] = float(r[c])
        else:
            c = cs
            r[c] = float(r[c])


def to_float64(l, cs):
    for r in l:
        if isinstance(cs, list):
            for c in cs:
                r[c] = np.float64(r[c])
        else:
            c = cs
            r[c] = np.float64(r[c])


def hhi(l):
    l = np.array(l)
    return sum((l / float(sum(l))) ** 2)


def shannon(l):
    l = np.array(l) / float(sum(l))
    return -sum(l * np.log2(l))


def xcol(index):
    s = 0
    pow = 1
    for letter in index[::-1]:
        d = int(letter, 36) - 9
        s += pow * d
        pow *= 26
    # excel starts column numeration from 1
    return s - 1


def simp(g):
    """nx.MultiGraph() => nx.Graph()"""
    newg = nx.Graph()
    for u, v, data in g.edges_iter(data=True):
        w = data["weight"]
        if newg.has_edge(u, v):
            newg[u][v]["weight"] += w
        else:
            newg.add_edge(u, v, weight=w)
    return newg


def hex_to_rgb(value):
    value = value.lstrip("#")
    lv = len(value)
    return tuple(int(value[i : i + int(lv / 3)], 16) for i in range(0, lv, int(lv / 3)))


def hex_to_rgb1(value):
    value = value.lstrip("#")
    lv = len(value)
    return tuple(
        int(value[i : i + int(lv / 3)], 16) / 256.0 for i in range(0, lv, int(lv / 3))
    )


def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb


gdefhex = "#3366CC #DC3912 #FF9900 #109618 #990099 #0099C6 #DD4477 #66A900 #B52D2D #2F5F8F #994499 #21A797 #AAAA11 #6633CC #E67300 #8B0707 #651067 #329262 #5574A6 #3B3EAC #B77322 #16D620 #B91383 #F4359E #9C5935 #A9C413 #2A778D #668D1C #BEA413 #0C5922 #743411 #000000".split()
gdef = [hex_to_rgb(h) for h in gdefhex]

d3colhex = "#1f77b4 #ff7f0e #2ca02c #d62728 #9467bd #8c564b #e377c2 #7f7f7f #bcbd22 #17becf".split()
d3def = [hex_to_rgb(h) for h in d3colhex]


def strip_non_ascii(t):
    return "".join([i if ord(i) < 128 else " " for i in t])
