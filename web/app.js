const $ = (id)=>document.getElementById(id);
const fmt = (n)=>Math.round(Number(n)||0).toLocaleString('en-US');
const safe = (s)=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
const state={tab:'pulse', syndrome:'dengue', district:'All Districts', reduction:25};
const titles={pulse:['POPULATION HEALTH · INTELLIGENCE WORKSPACE','The health pulse, at a glance.','Explore simulated sentinel patterns and investigate emerging signals.'],
 alerts:['WATCH · EARLY WARNING ENGINE','Spot the unusual before the obvious.','Explore local anomalies, rolling momentum and explainable detection rules.'],
 forecast:['MODEL · WEEKLY OUTLOOK','Anticipate the next eight weeks.','Compare a seasonal count model against an out-of-time baseline.'],
 scenario:['PLANNING · COUNTERFACTUAL SANDBOX','Model possibilities, not promises.','Test transparent hypothetical reductions across projected cases.'],
 quality:['DATA · QUALITY & PROVENANCE','Know where every number came from.','Reproducible simulated data, validation rules and API access.']};
async function api(path){const response=await fetch('/api/'+path);if(!response.ok)throw new Error('API error '+response.status);return await response.json()}
function query(obj){return new URLSearchParams(obj).toString()}
function drawLine(container, datasets, opts={}){
 const el=$(container), width=760,height=270,padL=50,padR=17,padT=23,padB=34;
 const items=datasets.flatMap(d=>d.values.filter(v=>v!==null&&Number.isFinite(v)));
 if(!items.length){el.innerHTML='<p class="muted">No chart data found</p>';return;}
 const lo=0, hi=Math.max(...items)*1.17+1, total=Math.max(...datasets.map(d=>d.values.length));
 const X=i=>padL+(width-padL-padR)*(i/Math.max(1,total-1));
 const Y=v=>height-padB-(height-padB-padT)*(v-lo)/(hi-lo);
 let svg=`<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Synthetic surveillance time series">`;
 for(let k=0;k<=4;k++){let y=padT+(height-padB-padT)*k/4;let v=hi*(1-k/4);
 svg+=`<line x1="${padL}" x2="${width-padR}" y1="${y}" y2="${y}" stroke="#eef1f8" stroke-width="1"/><text x="${padL-12}" y="${y+4}" text-anchor="end">${fmt(v)}</text>`;}
 if(opts.band){const u=opts.band.upper,l=opts.band.lower,from=opts.band.start;
 const nodes=u.map((v,i)=>`${X(from+i)},${Y(v)}`).concat(l.map((v,i)=>`${X(from+l.length-1-i)},${Y(l[l.length-1-i])}`)).join(' ');
 svg+=`<polygon points="${nodes}" fill="#9ae5de" fill-opacity=".34"/>`;}
 datasets.forEach((d,k)=>{
 const p=d.values.map((v,i)=>v===null?null:`${X(i).toFixed(1)},${Y(v).toFixed(1)}`);
 let pieces=[],segment=[];for(const point of p){if(point===null){if(segment.length)pieces.push(segment.join(' '));segment=[];}else segment.push(point);}if(segment.length)pieces.push(segment.join(' '));
 for(const points of pieces)svg+=`<polyline points="${points}" fill="none" stroke="${d.color||'#655de0'}" stroke-width="${d.width||3}" stroke-linecap="round" stroke-linejoin="round" ${d.dash?'stroke-dasharray="7 6"':''}/>`;
 });
 const labels=opts.labels||[];
 for(let i=0;i<total;i+=Math.max(1,Math.ceil(total/6))){let label=labels[i]||('W'+(i+1));svg+=`<text x="${X(i)}" y="${height-9}" text-anchor="middle">${safe(label.slice(5))}</text>`;}
 svg+='</svg>';el.innerHTML=svg;
}
function tag(level){return `<span class="level ${safe(level)}">${safe(level)}</span>`}
function alertRows(items,number){return items.slice(0,number).map(x=>`<div class="alertrow"><b>${safe(x.district)}</b>${tag(x.level)}</div>`).join('')}
async function pulse(){const d=await api('overview?'+query({syndrome:state.syndrome}));
 $('m-cases').textContent=fmt(d.recent_four_week_cases);
 $('m-change').textContent=(d.percent_change>0?'+':'')+d.percent_change+'% vs preceding 4 weeks';
 $('m-positivity').textContent=d.positivity_pct+'%';
 $('m-alerts').textContent=d.high_alerts+d.watch_alerts;
 $('m-weeks').textContent=d.weeks;
 $('mini-alerts').innerHTML=alertRows(d.districts,8);
 drawLine('pulse-chart',[{values:d.recent_weeks.map(x=>x.cases),color:'#6e66e9'}],{labels:d.recent_weeks.map(x=>x.week_start)});
}
async function signals(){const d=await api('signals?'+query({syndrome:state.syndrome}));
 $('alerts-table').innerHTML=`<table class="signal-table"><thead><tr><th>AREA</th><th>STATUS</th><th>4-WEEK CASES</th><th>ANOMALY z</th><th>MOMENTUM</th><th>EWMA</th></tr></thead><tbody>`+
 d.alerts.map(x=>`<tr><td>${safe(x.district)}</td><td>${tag(x.level)}</td><td>${fmt(x.recent_four_week_cases)}</td><td>${x.z_score.toFixed(2)}</td><td>${x.four_week_change_pct>0?'+':''}${x.four_week_change_pct}%</td><td>${fmt(x.ewma_cases)}</td></tr>`).join('')+'</tbody></table>';
}
async function forecast(){const d=await api('forecast?'+query({syndrome:state.syndrome,district:state.district,weeks:8}));
 const recent=d.recent.map(x=>x.cases), pred=d.forecast.map(x=>x.cases);
 const total=recent.length+pred.length;
 drawLine('forecast-chart',[
  {values:[...recent,...Array(pred.length).fill(null)],color:'#6259d6'},
  {values:[...Array(recent.length-1).fill(null),recent[recent.length-1],...pred],color:'#20b6aa',dash:true}],
  {labels:[...d.recent.map(x=>x.week_start),...d.forecast.map(x=>x.week_start)],
   band:{start:recent.length,upper:d.forecast.map(x=>x.upper),lower:d.forecast.map(x=>x.lower)}});
 const b=d.backtest;
 $('validation').innerHTML=`<div class="metricline"><small>MODEL MAE · 12-WEEK HOLDOUT</small><b>${b.model_mae}</b></div><div class="metricline"><small>SEASONAL NAIVE MAE</small><b>${b.seasonal_naive_mae}</b></div><div class="metricline"><small>EMPIRICAL RESIDUAL BAND COVERAGE</small><b>${Math.round(b.empirical_holdout_80_band_coverage*100)}%</b></div><p class="muted">A lower MAE is better. The model is not guaranteed to outperform the baseline. Bands are illustrative.</p>`;
}
async function scenario(){const d=await api('scenario?'+query({syndrome:state.syndrome,district:state.district,reduction_pct:state.reduction,weeks:8}));
 drawLine('scenario-chart',[{values:d.series.map(x=>x.baseline),color:'#705fe1'},
 {values:d.series.map(x=>x.hypothetical),color:'#21b6ab'}],{labels:d.series.map(x=>x.week_start)});
 $('scenario-summary').innerHTML=`<div class="muted">Simulated difference over eight weeks</div><div class="big-difference">${fmt(d.difference_total)}</div><div class="muted">Fewer *hypothetical* cases under this assumption</div><div class="impact-row">Baseline total <b>${fmt(d.baseline_total)}</b></div><div class="impact-row">Hypothetical total <b>${fmt(d.hypothetical_total)}</b></div><div class="ideas"><strong>Potential activities to discuss:</strong><br>${d.planning_ideas.map(s=>'• '+safe(s)).join('<br>')}<p>Not a causal efficacy model.</p></div>`;
}
async function quality(){const d=await api('quality');
 const entries=[['SIMULATED RECORDS',fmt(d.rows)],['DISTRICTS',d.districts],['SYNDROME TYPES',d.syndromes],['WEEKS OBSERVED',d.weeks],['DUPLICATE KEYS',d.duplicates],['MISSING COMBINATIONS',d.missing_combinations],['VALIDATION ERRORS',d.validation_errors.length],['FIRST WEEK',d.date_min],['LAST WEEK',d.date_max]];
 $('quality-grid').innerHTML=entries.map(([l,v])=>`<div class="quality-tile"><small>${safe(l)}</small><b>${safe(v)}</b></div>`).join('');
 $('csv-link').href='/api/export?syndrome='+encodeURIComponent(state.syndrome);
}
async function refresh(){const handlers={pulse,alerts:signals,forecast,scenario,quality};
 try{await handlers[state.tab]()}catch(error){console.error(error);document.querySelector('#panel-'+state.tab).insertAdjacentHTML('beforeend',`<p class="muted">Unable to load: ${safe(error.message)}. Check that the local API is running.</p>`)} }
function tab(name){state.tab=name;document.querySelectorAll('.tabs button').forEach(b=>b.classList.toggle('active',b.dataset.tab===name));
 document.querySelectorAll('.panel').forEach(x=>x.classList.toggle('active',x.id==='panel-'+name));
 const [k,t,s]=titles[name];$('kicker').textContent=k;$('title').textContent=t;$('subtitle').textContent=s;refresh();}
document.querySelectorAll('.tabs button').forEach(b=>b.addEventListener('click',()=>tab(b.dataset.tab)));
$('syndrome').addEventListener('change',e=>{state.syndrome=e.target.value;refresh()});
$('district').addEventListener('change',e=>{state.district=e.target.value;refresh()});
$('reduction').addEventListener('input',e=>{state.reduction=Number(e.target.value);$('reduction-label').textContent=state.reduction+'%';if(state.tab==='scenario')refresh()});
api('meta').then(d=>{$('district').innerHTML=d.districts.map(x=>`<option>${safe(x)}</option>`).join('');refresh()}).catch(()=>refresh());
