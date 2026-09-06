/* V8 strategic center + Mantra 2026/27 */
'use strict';
(()=>{
 if(window.__FANTA_V8_STRATEGY__)return;window.__FANTA_V8_STRATEGY__=1;
 ENDPOINTS.strategy=`${SUPABASE_URL}/functions/v1/strategy-api`;
 const MOD={
 '3-4-3':[['Por'],['Dc'],['Dc'],['Dc','B'],['E'],['M','C'],['C'],['E'],['W','A'],['W','A'],['A','Pc']],
 '3-4-1-2':[['Por'],['Dc'],['Dc'],['Dc','B'],['E'],['M','C'],['C'],['E'],['T'],['A','Pc'],['A','Pc']],
 '3-4-2-1':[['Por'],['Dc'],['Dc'],['Dc','B'],['M'],['E'],['M','C'],['E','W'],['T'],['T','A'],['A','Pc']],
 '3-5-2':[['Por'],['Dc'],['Dc'],['Dc','B'],['M'],['E'],['M','C'],['C'],['E','W'],['A','Pc'],['A','Pc']],
 '3-5-1-1':[['Por'],['Dc'],['Dc'],['Dc','B'],['M'],['M'],['C'],['E','W'],['E','W'],['T','A'],['A','Pc']],
 '4-3-3':[['Por'],['Dd'],['Dc'],['Dc'],['Ds'],['M','C'],['M'],['C'],['W','A'],['W','A'],['A','Pc']],
 '4-3-1-2':[['Por'],['Dd'],['Dc'],['Dc'],['Ds'],['M','C'],['M'],['C'],['T'],['T','A','Pc'],['A','Pc']],
 '4-4-2':[['Por'],['Dd'],['Dc'],['Dc'],['Ds'],['M','C'],['C'],['E','W'],['E'],['A','Pc'],['A','Pc']],
 '4-1-4-1':[['Por'],['Dd'],['Dc'],['Dc'],['Ds'],['M'],['C','T'],['T'],['E','W'],['W'],['A','Pc']],
 '4-M-1-1':[['Por'],['Dd'],['Dc'],['Dc'],['Ds'],['M'],['C'],['E','W'],['E','W'],['T','A'],['A','Pc']],
 '4-2-3-1':[['Por'],['Dd'],['Dc'],['Dc'],['Ds'],['M'],['M','C'],['W','T'],['T'],['W','A'],['A','Pc']]};
 Object.assign(state,{v8Profile:state.v8Profile||{preferred_modules:[],profile:'balanced',role_budgets:{},notes:''},v8Modules:state.v8Modules||MOD,v8Features:state.v8Features||new Map(),v8League:'',v8Busy:false,v8Moment:null,v8MomentCtx:'',v8MetricKey:'',v8Metric:null});
 const cl=(v,a,b)=>Math.max(a,Math.min(b,v)),num=v=>Number.isFinite(Number(v))?Number(v):null,fmt=(v,d=2)=>num(v)===null?'—':Number(v).toFixed(d).replace('.',','),pop=v=>{let n=0;for(v>>>=0;v;v&=v-1)n++;return n};
 const sapi=p=>api(ENDPOINTS.strategy,p,{quiet:true});
 const pref=p=>state.v7Preferences?.get(String(p?.source_player_id||p?.id||''))||null;
 const feat=p=>p?.strategic_features||state.v8Features.get(String(p?.id||''))||state.v8Features.get(String(p?.source_player_id||''))||{};
 const fm=p=>num(feat(p).forecast_fantasy_avg)??num(p?.expected_fantasy_avg)??0;
 const prs=p=>{let v=num(feat(p).forecast_presence)??num(p?.expected_titolarity)??50;if(v<=1)v*=100;return cl(v,0,100)};
 const vol=p=>cl(num(feat(p).volatility)??.25,0,1),trend=p=>cl(num(feat(p).trend_age_adjusted)??0,-1,1);
