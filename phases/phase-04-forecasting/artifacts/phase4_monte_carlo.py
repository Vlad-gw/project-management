#!/usr/bin/env python3
"""Фаза 4: два прогноза Монте-Карло. Запуск: pip install numpy; python phase4_monte_carlo.py
Данные: история Фаз 1–3, недельные часы реконструируются равномерно по календарным датам.
"""
from collections import defaultdict
from pathlib import Path
import csv,datetime as dt,math,json
import numpy as np

HERE=Path(__file__).resolve().parent
N=120000
SEED=20261112

def load(name):
    with (HERE/name).open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f,delimiter=';'))

def save(name,head,rows):
    with (HERE/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter=';');w.writerow(head);w.writerows(rows)

def mon(d):
    return d-dt.timedelta(days=d.weekday())

def hist():
    times=defaultdict(float);counts=defaultdict(int);ts=load('history_tasks.csv')
    for r in ts:
        start=dt.date.fromisoformat(r['Начало']);end=dt.date.fromisoformat(r['Окончание'])
        counts[mon(end)]+=1
        n=(end-start).days+1
        for i in range(n):
            times[mon(start+dt.timedelta(days=i))]+=float(r['Подтверждённые часы'])/n
    start=min(set(times)|set(counts));end=max(set(times)|set(counts));out=[]
    while start<=end:
        out.append((start,(start+dt.timedelta(days=6)),counts[start],times[start]))
        start+=dt.timedelta(days=7)
    return ts,out

def monte_carlo(target,draw,rng):
    acc=np.zeros(len(target));finished=np.zeros(len(target),dtype=np.int16)
    for week in range(1,101):
        active=finished==0
        if not active.any():break
        acc[active]+=rng.choice(draw,size=active.sum())
        finished[active & (acc>=target)]=week
    if (finished==0).any():raise RuntimeError('Exceeded simulation horizon')
    return finished

def score(x):
    return {'p80_weeks':int(np.sort(x)[math.ceil(.8*len(x))-1]),
            'mean_weeks':round(float(np.mean(x)),3),
            'median_weeks':float(np.median(x))}

def main():
    old,weekly=hist()
    counts=np.array([w[2] for w in weekly]);hours=np.array([w[3] for w in weekly])
    new=load('phase5_academic_tasks.csv')
    L=np.array([float(r['L, чел.-ч']) for r in new])
    M=np.array([float(r['M, чел.-ч']) for r in new])
    U=np.array([float(r['U, чел.-ч']) for r in new])
    assert np.all(L<=M)&np.all(M<=U)
    t1=monte_carlo(np.full(N,len(new)),counts,np.random.default_rng(SEED))
    rng=np.random.default_rng(SEED+1)
    required=rng.triangular(L[None,:],M[None,:],U[None,:],size=(N,len(new))).sum(axis=1)
    t2=monte_carlo(required,hours,rng)
    save('weekly_history.csv',['Начало ISO-недели','Конец ISO-недели','Задач завершено','Реконструированные чел.-ч'],
        [(a.isoformat(),b.isoformat(),n,round(h,6)) for a,b,n,h in weekly])
    save('monte_carlo_cdf.csv',['Неделя','P(завершения), модель 1','P(завершения), модель 2','Частота, модель 1','Частота, модель 2'],
        [(w,round(float(np.mean(t1<=w)),6),round(float(np.mean(t2<=w)),6),int(np.sum(t1==w)),int(np.sum(t2==w))) for w in range(1,31)])
    ans={'history_total_tasks':len(old),'history_total_hours':round(float(hours.sum()),3),
         'historical_weeks':len(weekly),'historical_task_counts':counts.tolist(),
         'historical_hours':[round(float(x),3) for x in hours],
         'academic_tasks':len(new),'academic_effort_L':float(L.sum()),
         'academic_effort_M':float(M.sum()),'academic_effort_U':float(U.sum()),
         'seed':SEED,'iterations':N,'model1':score(t1),'model2':score(t2),
         'difference_P80_weeks':score(t2)['p80_weeks']-score(t1)['p80_weeks'],
         'caution':'Недельные часы реконструированы равномерным разнесением подтверждённых итоговых часов задач по календарным датам начала и окончания.'}
    assert len(old)==31 and abs(hours.sum()-158)<.00001
    (HERE/'monte_carlo_results.json').write_text(json.dumps(ans,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(ans,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
