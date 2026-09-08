from pathlib import Path

p=Path('home.html')
t=p.read_text(encoding='utf-8')
assert '<title>Fantacalcio Live</title>' in t
assert 'Fantacalcio Live - tool per asta online' in t
old="""      const vals=[num(p?.pfc),num(p?.pma)].filter(v=>v!=null&&v>=0);
      if(idx==null||!vals.length)return;
      const market=vals.reduce((a,b)=>a+b,0)/vals.length;
      const delta=idx-market;"""
new="""      const pma=num(p?.pma),pfc=num(p?.pfc);
      if(idx==null||(pma==null&&pfc==null))return;
      const market=pma!=null&&pfc!=null ? (.75*pma+.25*pfc) : (pma??pfc);
      const delta=idx-market;"""
count=t.count(old)
if count<1:
    raise SystemExit('V33 gradient source not found')
t=t.replace(old,new)
p.write_text(t,encoding='utf-8')
print('updated',count,'V33 gradient source block(s) to PMA-weighted market anchor')
