"""Run full model across seeds without rendering. Prints scientific QA metrics.

Usage: PYTHONPATH=. python scripts/seed_sensitivity.py 7 11 21
"""
import sys, json, time
from physarum_india import (build_geometry, Slime, analyse, choose_block,
                            BLOCK_R, T_GROW, T_REPAIR, unproj)


def run(seed, geo):
    sl = Slime(geo,seed)
    for _ in range(T_GROW): sl.step()
    before=analyse(geo,sl.D,sl.alive)
    center=choose_block(sl, geo['city_xy'], BLOCK_R)
    sl.block(center,BLOCK_R)
    immed=analyse(geo,sl.D,sl.alive)
    for _ in range(T_REPAIR): sl.step()
    after=analyse(geo,sl.D,sl.alive)
    out={'seed':seed,'block_center_lon_lat':[float(a) for a in unproj(*center)]}
    for label, m in [('before',before),('immediate',immed),('after',after)]:
        out[label]={k:float(v) if k in ('detour','total_km') else int(v) for k,v in m.items() if k!='mask'}
    return out


if __name__=='__main__':
    seeds=[int(x) for x in sys.argv[1:]] or [7,11,21]
    g=build_geometry(); results=[]; t=time.time()
    for seed in seeds:
        q=run(seed,g); results.append(q)
        print('seed',seed,'before',q['before'],'immediate',q['immediate'],'after',q['after'],'elapsed',round(time.time()-t,1),'s',flush=True)
    with open('out/sensitivity.json','w') as f:json.dump(results,f,indent=2)
