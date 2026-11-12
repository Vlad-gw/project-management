#!/usr/bin/env python3
"""Фаза 5: RCPSP, 12 правил приоритета и 600 случайных расписаний.
Установка: pip install numpy. Запуск: python phase5_scheduler.py
Каждая работа неделима; FS-связи, возобновляемые ресурсы по дням, календарь Пн–Пт.
Это учебный сценарий, а не утверждённый штат или гарантия оптимума.
"""
from pathlib import Path
from collections import defaultdict
import csv,json,datetime as dt
import numpy as np

HERE=Path(__file__).resolve().parent
SEED=20261112
RULES=['SLK','FREE','LST','LFT','LSTLFT','GRPW','LPT','MIS','GRD','GRWC','GCRWC','ROT']
def load(name):
    with (HERE/name).open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f,delimiter=';'))
def save(name,head,rows):
    with (HERE/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter=';');w.writerow(head);w.writerows(rows)

cfg=json.loads((HERE/'resources.json').read_text(encoding='utf-8'))
CAP=cfg['capacity'];START=dt.date.fromisoformat(cfg['model_start'])
data=load('project_wbs.csv')
B={x['ID']:{'name':x['Работа'],'stage':x['Этап'],
    'd':int(x['Продолжительность, раб.дн.']),
    'pred':x['Предшественники'].split(',') if x['Предшественники'] else [],
    'r':{k:int(x[k+', чел.']) for k in CAP}} for x in data}
assert len(B)==22 and len(B)==len(data)
succ={k:[] for k in B}
for k,v in B.items():
    assert v['d']>0 and all(v['r'][j]<=CAP[j] for j in CAP)
    for p in v['pred']:
        assert p in B
        succ[p].append(k)
topo=[];left=set(B)
while left:
    eligible=sorted(k for k in left if all(p in topo for p in B[k]['pred']))
    if not eligible:raise ValueError('Cycle in dependencies')
    topo.extend(eligible);left.difference_update(eligible)
ES={};EF={}
for k in topo:
    ES[k]=max((EF[p] for p in B[k]['pred']),default=0);EF[k]=ES[k]+B[k]['d']
CP=max(EF.values());LS={};LF={}
for k in reversed(topo):
    LF[k]=min((LS[p] for p in succ[k]),default=CP);LS[k]=LF[k]-B[k]['d']
slack={k:LS[k]-ES[k] for k in B}
free={k:min((ES[p] for p in succ[k]),default=CP)-EF[k] for k in B}

def priority(k,rule):
    d=B[k]['d'];r=B[k]['r'];load=sum(r.values())
    direct_d=sum(B[p]['d'] for p in succ[k])
    direct_r=sum(sum(B[p]['r'].values()) for p in succ[k])
    return {'SLK':slack[k],'FREE':free[k],'LST':LS[k],'LFT':LF[k],
      'LSTLFT':LS[k]+LF[k],'GRPW':-(d+direct_d),'LPT':-d,
      'MIS':-len(succ[k]),'GRD':-d*load,'GRWC':-load,
      'GCRWC':-(load+direct_r),
      'ROT':-sum(r[typ]/CAP[typ] for typ in CAP)/d}[rule]

def schedule(rule=None,seed=None):
    rng=np.random.default_rng(seed) if seed is not None else None
    pending=set(B);s={};used=defaultdict(lambda:defaultdict(int))
    while pending:
        eligible=[k for k in pending if all(p in s for p in B[k]['pred'])]
        if not eligible:raise ValueError('No ready job')
        k=str(rng.choice(sorted(eligible))) if rng is not None else min(eligible,key=lambda i:(priority(i,rule),i))
        t=max((s[p][1] for p in B[k]['pred']),default=0)
        while not all(used[day][typ]+v<=CAP[typ] for day in range(t,t+B[k]['d']) for typ,v in B[k]['r'].items() if v):
            t+=1
            if t>2000:raise RuntimeError('Scheduling horizon exceeded')
        for day in range(t,t+B[k]['d']):
            for typ,v in B[k]['r'].items():used[day][typ]+=v
        s[k]=(t,t+B[k]['d']);pending.remove(k)
    return s,max(x[1] for x in s.values())

def verify(s):
    assert len(s)==len(B)
    for k,v in B.items():
        a,b=s[k]
        assert b-a==v['d']
        assert all(s[p][1]<=a for p in v['pred'])
    for day in range(max(x[1] for x in s.values())):
        for typ,limit in CAP.items():
            assert sum(v['r'][typ] for k,v in B.items() if s[k][0]<=day<s[k][1])<=limit
    return True

def date(index):
    return (START+dt.timedelta(days=(index//5)*7+index%5)).isoformat()

def main():
    candidates=[];best=None
    for rule in RULES:
        s,t=schedule(rule);verify(s);candidates.append((rule,t,'Систематическая'))
        if best is None or (t,rule)<(best[1],best[0]):best=(rule,t,s)
    for i in range(600):
        s,t=schedule(seed=SEED+i);verify(s)
        candidates.append((f'RANDOM_{i+1:03d}',t,'Случайная'))
        if t<best[1]:best=(f'RANDOM_{i+1:03d}',t,s)
    method,days,best_plan=best
    save('heuristic_comparison.csv',['Метод','Длительность, раб.дн.','Длительность, недели','Тип'],
        [(name,d,round(d/5,2),kind) for name,d,kind in candidates])
    rows=[]
    for k in topo:
        v=B[k];a,b=best_plan[k];rr=v['r']
        rows.append((k,v['name'],v['stage'],v['d'],','.join(v['pred']),rr['BAQA'],rr['BE'],rr['FE'],
                     a,b,date(a),date(b-1),v['d']*sum(rr.values())*8,
                     ES[k],EF[k],LS[k],LF[k],slack[k]))
    save('best_schedule.csv',['ID','Работа','Этап','Длит. раб.дн.','Предшественники','BAQA','BE','FE',
        'Начало, день 0','Конец исключ., день','Начало дата','Окончание дата',
        'Трудоёмкость, чел.-ч','ES','EF','LS','LF','Общий резерв'],rows)
    stages=[]
    for stage in dict.fromkeys(v['stage'] for v in B.values()):
        ids=[k for k,v in B.items() if v['stage']==stage]
        a=min(best_plan[k][0] for k in ids);b=max(best_plan[k][1] for k in ids)
        stages.append((stage,len(ids),date(a),date(b-1),a,b))
    save('stage_milestones.csv',['Этап','Число работ','Старт','Окончание','Старт, день','Конец, день'],stages)
    labor=sum(v['d']*sum(v['r'].values())*8 for v in B.values())
    result={'mode':'Сценарный календарно-ресурсный план, не факт реализации',
        'wbs_tasks':len(B),'capacities':CAP,'systematic_heuristics':12,'random_heuristics':600,
        'random_seed_start':SEED,'chosen_heuristic':method,'best_duration_workdays':days,
        'best_duration_workweeks':round(days/5,2),'earliest_start':date(0),'last_finish':date(days-1),
        'cpm_lower_bound_workdays':CP,'labor_hours':labor,'phase3_integral_hours':2983,
        'comparison_to_phase3_percent':round((labor/2983-1)*100,2),
        'validations':{'all_activities_scheduled':True,'precedence':True,'capacity':verify(best_plan),
                       'calendar':'Mon-Fri, 8h/day, public holidays excluded'},
        'heuristic_ranked':sorted([{'method':name,'workdays':d} for name,d,kind in candidates if kind=='Систематическая'],key=lambda x:x['workdays'])}
    (HERE/'schedule_results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
