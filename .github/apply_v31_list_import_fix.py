from pathlib import Path
import re

p=Path('home.html')
s=p.read_text(encoding='utf-8')
assert '<title>Fantacalcio Live</title>' in s

if 'v31-list-import-style' in s and 'function v13RowsFromSheet' in s:
    print('V31 list import fix already applied')
    raise SystemExit(0)

start=s.find('<script id="v13-list-index-import-runtime">')
end=s.find('</script>',start)
if start<0 or end<0:
    raise SystemExit('V13 runtime not found')
block=s[start:end]

# 1) SheetJS: current official full build (includes Apple Numbers support),
#    one shared loader promise, and tolerant normalized header lookup.
load_pick_pat=re.compile(
    r"  function v13LoadXlsx\(\)\{.*?\}\n"
    r"  const v13Pick=.*?;\n",
    re.S,
)
loader_pick=r'''  let v13XlsxPromise=null;
  function v13LoadXlsx(){
    const version=String(window.XLSX?.version||'');
    if(window.XLSX&&/^0\.(2[0-9]|[3-9][0-9])\./.test(version))return Promise.resolve(window.XLSX);
    if(v13XlsxPromise)return v13XlsxPromise;
    v13XlsxPromise=new Promise((resolve,reject)=>{
      const existing=document.querySelector('script[data-fanta-sheetjs]');
      if(existing){
        existing.addEventListener('load',()=>window.XLSX?resolve(window.XLSX):reject(new Error('Parser Excel non disponibile.')),{once:true});
        existing.addEventListener('error',()=>reject(new Error('Impossibile caricare il parser Excel.')),{once:true});
        return;
      }
      const sc=document.createElement('script');
      sc.dataset.fantaSheetjs='1';
      sc.src='https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.full.min.js';
      sc.onload=()=>window.XLSX?resolve(window.XLSX):reject(new Error('Parser Excel non disponibile.'));
      sc.onerror=()=>reject(new Error('Impossibile caricare il parser Excel.'));
      document.head.appendChild(sc);
    }).catch(e=>{v13XlsxPromise=null;throw e});
    return v13XlsxPromise;
  }
  const v13Key=v=>String(v??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]/g,'');
  const v13Pick=(row,names)=>{
    const entries=Object.entries(row||{}),wanted=new Set(names.map(v13Key));
    for(const [k,v] of entries){if(wanted.has(v13Key(k))&&v!==''&&v!==null&&v!==undefined)return v;}
    return null;
  };
'''
if not load_pick_pat.search(block):
    raise SystemExit('V13 XLSX loader/header picker block not found')
block=load_pick_pat.sub(lambda _m: loader_pick,block,count=1)

# 2) Header aliases actually present in the attached Fantaculo workbook.
block=block.replace(
    "expected_fantasy_avg:v13Number(v13Pick(row,['expectedFantamedia','expected_fantasy_avg']))",
    "expected_fantasy_avg:v13Number(v13Pick(row,['expectedFantamedia','xFantamedia','fantamedia','expected_fantasy_avg']))"
)
block=block.replace(
    "free_kick_probability:v13Number(v13Pick(row,['freeKickProbability','free_kick_probability']))",
    "free_kick_probability:v13Number(v13Pick(row,['freeKickProbability','freeKickP','free_kick_probability']))"
)

# 3) Replace import + mount with multi-sheet/header detection and a single stable control.
pat=re.compile(r"  async function v13ImportFile\(file\)\{.*?\n  \}\n  function v13MountImport\(\)\{.*?\n  \}\n\n  if\(typeof loadList==='function'\)\{",re.S)
new=r'''  function v13LooksLikeNumbers(buffer){
    try{
      const u8=new Uint8Array(buffer),from=Math.max(0,u8.length-180000);
      return new TextDecoder('latin1').decode(u8.subarray(from)).includes('Index/Document.iwa');
    }catch{return false}
  }
  function v13HeaderScore(row){
    const keys=(row||[]).map(v13Key),has=(...x)=>x.some(k=>keys.includes(v13Key(k)));
    let score=0;
    if(has('name','nome','player','calciatore'))score+=8;
    if(has('team','squadra'))score+=3;
    if(has('role','classic_role','ruolo','roleMantra','mantra_roles'))score+=3;
    if(has('pfc'))score+=2;if(has('pma'))score+=2;if(has('slot'))score+=1;
    if(has('expectedTitolarita','expectedTitolarity'))score+=1;
    if(has('expectedFantamedia','xFantamedia','fantamedia'))score+=1;
    return score;
  }
  function v13RowsFromSheet(XLSX,ws){
    const matrix=XLSX.utils.sheet_to_json(ws,{header:1,defval:'',raw:false,blankrows:false});
    if(!matrix?.length)return null;
    let headerIndex=-1,best=-1;
    for(let i=0;i<Math.min(20,matrix.length);i++){
      const score=v13HeaderScore(matrix[i]);
      if(score>best){best=score;headerIndex=i;}
    }
    if(headerIndex<0||best<8)return null;
    const headers=matrix[headerIndex].map(v=>String(v??'').trim());
    const rawRows=matrix.slice(headerIndex+1).filter(r=>r.some(v=>String(v??'').trim()!==''))
      .map(r=>Object.fromEntries(headers.map((h,i)=>[h||`col_${i+1}`,r[i]??''])));
    const rows=rawRows.map(v13NormalizeRow).filter(x=>x.normalized.name);
    return {rawRows,rows,headers,headerScore:best,headerIndex};
  }
  async function v13ImportFile(file){
    if(!file)return;
    const XLSX=await v13LoadXlsx(),buffer=await file.arrayBuffer(),isNumbers=v13LooksLikeNumbers(buffer);
    let wb;
    try{wb=XLSX.read(buffer,{type:'array',cellDates:true,dense:true});}
    catch(error){
      if(isNumbers)throw new Error('Il file ha estensione Excel ma contenuto Apple Numbers. Il parser aggiornato non riesce a leggerlo: in Numbers usa File → Esporta in → Excel e riprova.');
      throw error;
    }
    const candidates=[];
    for(const sheetName of wb.SheetNames||[]){
      const parsed=v13RowsFromSheet(XLSX,wb.Sheets[sheetName]);
      if(parsed?.rows?.length)candidates.push({sheetName,...parsed});
    }
    candidates.sort((a,b)=>b.rows.length-a.rows.length||b.headerScore-a.headerScore);
    const chosen=candidates[0];
    if(!chosen){
      const kind=isNumbers?'Apple Numbers (anche se il nome termina in .xlsx)':'foglio di calcolo';
      throw new Error(`Nessun giocatore riconosciuto nel ${kind}. Tabelle lette: ${(wb.SheetNames||[]).join(', ')||'nessuna'}.`);
    }
    const rows=chosen.rows;
    const ext=(file.name.split('.').pop()||'').toLowerCase();
    const sourceFormat=['csv','xls','xlsx'].includes(ext)?ext:(isNumbers?'xlsx':ext);
    const begin=await api(ENDPOINTS.list,{action:'beginListImport',sourceFilename:file.name,sourceFormat,sourceColumns:chosen.headers.filter(Boolean),referenceDate:new Date().toISOString().slice(0,10)});
    const batchId=begin?.batchId;if(!batchId)throw new Error('Impossibile iniziare l’import.');
    for(let i=0;i<rows.length;i+=80)await api(ENDPOINTS.list,{action:'appendListImport',batchId,rows:rows.slice(i,i+80)});
    const fin=await api(ENDPOINTS.list,{action:'finishListImport',batchId});
    if(!fin?.ok&&fin?.rowCount==null)throw new Error('Import non finalizzato.');
    state.v13Filters={};
    await loadList();
    msg(`Listone aggiornato: ${fin.rowCount??rows.length} giocatori · tabella ${chosen.sheetName}${isNumbers?' · sorgente Numbers':''}.`,'success');
  }
  function v13MountImport(){
    if(!state.list?.permissions?.canManageList)return;
    const row=document.querySelector('#view-list .v12-toolbar-row')||document.querySelector('#view-list .v12-toolbar');
    if(!row)return;
    let wrap=document.getElementById('v13-import-control');
    if(!wrap){
      wrap=document.createElement('span');wrap.id='v13-import-control';wrap.className='v13-import-control';
      const input=document.createElement('input');input.type='file';input.id='v13-import-file';input.accept='.csv,.xls,.xlsx,.numbers';input.hidden=true;
      const button=document.createElement('button');button.type='button';button.id='v13-import-button';button.className='secondary';button.textContent='IMPORTA CSV/XLSX';
      button.addEventListener('click',()=>{try{if(typeof input.showPicker==='function')input.showPicker();else input.click();}catch{input.click();}});
      input.addEventListener('change',async()=>{
        const file=input.files?.[0];if(!file)return;
        button.disabled=true;button.textContent='IMPORT…';
        try{await v13ImportFile(file)}catch(e){msg(e.message||'Errore import.','error')}
        finally{input.value='';button.disabled=false;button.textContent='IMPORTA CSV/XLSX';}
      });
      wrap.append(input,button);
    }
    document.querySelectorAll('#v13-import-button').forEach(el=>{if(el!==wrap.querySelector('#v13-import-button'))el.remove()});
    document.querySelectorAll('#v13-import-file').forEach(el=>{if(el!==wrap.querySelector('#v13-import-file'))el.remove()});
    if(wrap.parentElement!==row)row.appendChild(wrap);
  }

  if(typeof loadList==='function'){'''
if not pat.search(block):
    raise SystemExit('V13 import/mount block not found')
block=pat.sub(lambda _m:new,block,count=1)

s=s[:start]+block+s[end:]

# 4) Stable toolbar footprint for the single import control.
if 'v31-list-import-style' not in s:
    style='''\n<style id="v31-list-import-style">\n#view-list .v13-import-control{display:inline-flex!important;align-items:center!important;flex:0 0 auto!important}\n#view-list .v13-import-control #v13-import-button{height:28px!important;min-height:28px!important;padding:2px 7px!important;white-space:nowrap!important}\n</style>\n'''
    s=s.replace('</head>',style+'</head>',1)

p.write_text(s,encoding='utf-8')
print('V31 list import fix applied')
