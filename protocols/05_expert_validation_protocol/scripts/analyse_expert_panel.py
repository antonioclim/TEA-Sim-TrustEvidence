#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, statistics
from collections import defaultdict
from pathlib import Path

def quartiles(xs):
    if len(xs) < 2: return ('','','')
    q=statistics.quantiles(xs, n=4, method='inclusive')
    return q[0], q[1], q[2]

def load(path):
    rows=[]
    with open(path, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if not r.get('item_id') or not r.get('rating'): continue
            r=dict(r); r['rating']=float(r['rating']); rows.append(r)
    return rows

def summarise(rows):
    vals=defaultdict(list)
    for r in rows: vals[r['item_id']].append(float(r['rating']))
    out={}
    for item,xs in sorted(vals.items()):
        xs=sorted(xs); n=len(xs); q1,_,q3=quartiles(xs); med=statistics.median(xs)
        iqr=(q3-q1) if q1!='' else ''
        p13=round(sum(1 for x in xs if 1<=x<=3)/n*100,1)
        p46=round(sum(1 for x in xs if 4<=x<=6)/n*100,1)
        p79=round(sum(1 for x in xs if 7<=x<=9)/n*100,1)
        if iqr!='' and med>=7 and iqr<=2 and p79>=70: dec='endorsement_consensus'
        elif iqr!='' and med<=3 and iqr<=2 and p13>=70: dec='rejection_consensus'
        else: dec='no_consensus'
        out[item]={'item_id':item,'n':n,'median':med,'q1':q1,'q3':q3,'iqr':iqr,'agreement_1_3_percent':p13,'agreement_4_6_percent':p46,'agreement_7_9_percent':p79,'decision':dec}
    return out

def main():
    ap=argparse.ArgumentParser(description='Summarise two-round expert panel ratings. Use only with ethics-cleared anonymised data.')
    ap.add_argument('--round1', required=True); ap.add_argument('--round2', required=True); ap.add_argument('--out', required=True)
    args=ap.parse_args()
    r1=summarise(load(args.round1)); r2=summarise(load(args.round2))
    keys=sorted(set(r1)|{k.replace('R2_','R1_') for k in r2})
    rows=[]
    for k in keys:
        k2=k.replace('R1_','R2_')
        a=r1.get(k,{}); b=r2.get(k2,{}) or r2.get(k,{})
        med1=a.get('median',''); med2=b.get('median','')
        shift=''; stable=''
        if med1!='' and med2!='':
            shift=med2-med1; stable=abs(shift)<=1
        rows.append({'item_id_round1':a.get('item_id',k),'item_id_round2':b.get('item_id',k2),'round1_n':a.get('n',''),'round1_median':med1,'round1_iqr':a.get('iqr',''),'round1_agreement_7_9_percent':a.get('agreement_7_9_percent',''),'round1_decision':a.get('decision',''),'round2_n':b.get('n',''),'round2_median':med2,'round2_iqr':b.get('iqr',''),'round2_agreement_7_9_percent':b.get('agreement_7_9_percent',''),'round2_decision':b.get('decision',''),'median_shift_round2_minus_round1':shift,'stable_shift_abs_le_1':stable,'interpretation_boundary':'Only real ethics-cleared data with >=12 two-round completers may support preliminary expert-panel wording.'})
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else []); w.writeheader(); w.writerows(rows)
    print(f'wrote {args.out}; rows={len(rows)}')
if __name__=='__main__': main()
