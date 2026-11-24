# -*- coding: utf-8 -*-
"""
JRA マークカード練習ゲーム（Streamlit / ブラウザ版）
起動: streamlit run streamlit_app.py
ゲーム本体はブラウザ上のJavaScriptで動くので、iPadのタッチ操作でもサクサク塗れます。
"""
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="JRA マークカード練習", layout="wide")
st.markdown("#### 🏇 JRA マークカード 塗り方練習")

HTML = r"""
<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
 body{margin:0;font-family:-apple-system,"Hiragino Sans","Noto Sans JP",sans-serif;touch-action:manipulation;background:#fff;color:#222}
 #top{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:6px}
 #task{flex:1 1 420px;background:#fffbe6;border:2px groove #ccc;padding:8px 12px;font-weight:bold;font-size:16px;white-space:pre-wrap;line-height:1.5}
 #side{display:flex;flex-direction:column;gap:4px}
 button,select{font-size:15px;padding:8px 10px;border-radius:8px;border:1px solid #888;background:#f4f4f4}
 button{font-weight:bold}
 #btns{display:grid;grid-template-columns:1fr 1fr;gap:4px}
 #result{white-space:pre-wrap;font-size:14px;padding:4px 8px;min-height:6px}
 #stat{font-size:12px;color:#666}
 svg{width:100%;height:auto;display:block;user-select:none;-webkit-user-select:none}
</style></head><body>
<div id="top">
 <div id="task"></div>
 <div id="side">
  <select id="level">
   <option value="1">レベル1 入門（単勝・複勝）</option>
   <option value="2">レベル2 初級（馬連・ワイド・枠連・馬単）</option>
   <option value="3">レベル3 中級（ボックス・3連複・馬単）</option>
   <option value="4">レベル4 上級（3連単フォーメーション等）</option>
  </select>
  <div id="btns">
   <button id="bEval">採点する</button><button id="bAns">答えを見る</button>
   <button id="bClear">塗り直す</button><button id="bNext">次の問題</button>
  </div>
  <div id="stat"></div>
 </div>
</div>
<div id="result"></div>
<svg id="svg" viewBox="0 0 1210 640" xmlns="http://www.w3.org/2000/svg"></svg>
<script>
const VENUES=["中山","東京","京都","阪神","福島","新潟","中京","小倉","札幌","函館"];
const TYPES=["単勝","複勝","枠連","馬連","馬単","ワイド","3連複","3連単"];
const UNITS=[["万円",10000],["千円",1000],["百円",100]];
const AMT_ROWS=[[30,20,10,5],[4,3,2,1]];
const AMT_VALUES=[30,20,10,5,4,3,2,1];
const CIRC="①②③④", LINES=4;
const CARD="#eaf5bd",BOX="#f4fad8",ORANGE="#e8791a",INK="#1b1b1b";

/* ============ ロジック ============ */
const rnd=n=>Math.floor(Math.random()*n);
const choice=a=>a[rnd(a.length)];
function sample(arr,n){const a=arr.slice();for(let i=a.length-1;i>0;i--){const j=rnd(i+1);[a[i],a[j]]=[a[j],a[i]];}return a.slice(0,n);}
function comb(n,k){if(k>n)return 0;let r=1;for(let i=1;i<=k;i++)r=r*(n-k+i)/i;return Math.round(r);}
const asc=s=>[...s].sort((a,b)=>a-b);
const fmt=s=>asc(s).join("・");
const eqSet=(a,b)=>a.size===b.size&&[...a].every(x=>b.has(x));

function countPoints(ty,mode,bl){
  const [A,B,C]=bl;
  if(ty==="3連単"){let c=0;for(const a of A)for(const b of B)for(const d of C)if(new Set([a,b,d]).size===3)c++;return c;}
  if(ty==="馬単"){let c=0;for(const a of A)for(const b of B)if(a!==b)c++;return c;}
  if(ty==="馬連"||ty==="ワイド")return mode==="ボックス"?comb(A.size,2):1;
  if(ty==="3連複"){if(mode==="ボックス")return comb(A.size,3);if(mode==="軸1頭ながし")return comb(B.size,2);return 1;}
  return 1;
}
function makeLine(ty,mode,heads){
  const pool=[...Array(heads).keys()].map(i=>i+1);
  const pick=(n,ex=new Set())=>new Set(sample(pool.filter(x=>!ex.has(x)),n));
  let A=new Set(),B=new Set(),C=new Set();
  if(ty==="単勝"||ty==="複勝")A=pick(1);
  else if(ty==="枠連")A=new Set(sample([1,2,3,4,5,6,7,8],2));
  else if(ty==="馬連"||ty==="ワイド")A=mode==="通常"?pick(2):pick(choice([3,4]));
  else if(ty==="馬単"){
    if(mode==="通常"){A=pick(1);B=pick(1,A);}
    else{A=pick(choice([1,1,2]));B=pick(choice([1,2,3]),A);}
  }else if(ty==="3連複"){
    if(mode==="通常")A=pick(3);
    else if(mode==="ボックス")A=pick(choice([4,4,5]));
    else{A=pick(1);B=pick(choice([2,3,4]),A);}
  }else if(ty==="3連単"){
    A=pick(choice([1,1,2]));
    B=pick(choice([2,2,3]),Math.random()<0.35?new Set():A);
    C=pick(choice([2,3,4]),Math.random()<0.35?new Set():new Set([...A,...B]));
  }
  return [A,B,C];
}
function genTask(level){
  const venue=rnd(10),race=1+rnd(12),heads=8+rnd(11);
  let ty,mode,nl,amounts;
  if(level==1){ty=choice(["単勝","複勝"]);mode="通常";nl=1;amounts=[100,200,300,500];}
  else if(level==2){ty=choice(["馬連","ワイド","枠連","馬単"]);mode="通常";nl=choice([1,2]);amounts=[100,200,300,500,1000];}
  else if(level==3){
    ty=choice(["馬連","ワイド","3連複","馬単"]);
    mode=ty==="馬単"?"フォーメーション":ty==="3連複"?choice(["通常","ボックス","軸1頭ながし"]):choice(["通常","ボックス"]);
    nl=choice([1,2,3]);amounts=[100,200,300,500,1000];
  }else{
    ty=choice(["3連単","3連単","3連単","3連複","馬単"]);
    mode=ty==="3連複"?choice(["ボックス","軸1頭ながし"]):"フォーメーション";
    nl=choice([2,3,4]);amounts=[100,200,300,500,1000,1500,2000];
  }
  const lines=[],seen=new Set();let tries=0;
  while(lines.length<nl&&tries<200){
    tries++;
    const bl=makeLine(ty,mode,heads),pts=countPoints(ty,mode,bl);
    if(pts<1||pts>12)continue;
    const key=JSON.stringify(bl.map(asc));
    if(seen.has(key))continue;
    seen.add(key);
    lines.push({blocks:bl,amount:choice(amounts),points:pts});
  }
  return {level,venue,race,type:ty,mode,prev:level>=2&&Math.random()<0.15,lines};
}
function describeLine(ty,mode,bl){
  const [A,B,C]=bl;
  if(ty==="単勝"||ty==="複勝")return fmt(A)+"番";
  if(ty==="枠連"){const [a,b]=asc(A);return a+"枠 - "+b+"枠";}
  if(ty==="馬連"||ty==="ワイド")return mode==="ボックス"?"ボックス "+fmt(A):asc(A).join("-");
  if(ty==="馬単")return "1着 "+fmt(A)+" → 2着 "+fmt(B);
  if(ty==="3連複"){
    if(mode==="通常")return asc(A).join("-");
    if(mode==="ボックス")return "ボックス "+fmt(A);
    return "軸 "+fmt(A)+" ― 相手 "+fmt(B);
  }
  return "1着 "+fmt(A)+" → 2着 "+fmt(B)+" → 3着 "+fmt(C);
}
function howTo(ty,mode){
  if(ty==="単勝"||ty==="複勝")return "1着欄に馬番を1つ塗る";
  if(ty==="枠連")return "1着欄に枠番を2つ塗る（枠番は1〜8）";
  if(ty==="馬連"||ty==="ワイド"||(ty==="3連複"&&mode==="通常"))return "1着欄に馬番をまとめて塗る";
  if(mode==="ボックス")return "1着欄にボックスの馬番を全部塗る";
  if(ty==="3連複")return "1着欄＝軸馬、2着欄＝相手馬を塗る";
  if(ty==="馬単")return "1着欄＝1着の馬、2着欄＝2着の馬を塗る";
  return "着順ごとに1着欄・2着欄・3着欄へ塗る";
}
function taskText(t){
  let head="【指示】"+VENUES[t.venue]+" "+t.race+"レース　"+t.type+(t.mode!=="通常"?"（"+t.mode+"）":"")+(t.prev?"　※前日発売":"");
  const rows=[head];let total=0;
  t.lines.forEach((ln,i)=>{
    rows.push(" "+CIRC[i]+" "+describeLine(t.type,t.mode,ln.blocks)+"　各"+ln.amount.toLocaleString()+"円（"+ln.points+"通り）");
    total+=ln.amount*ln.points;
  });
  rows.push("　　合計 "+total.toLocaleString()+"円　／　塗り方: "+howTo(t.type,t.mode));
  return rows.join("\n");
}
function canonAmount(a){
  let u=100;
  for(const [,m] of UNITS){if(a%m===0&&a/m<=30){u=m;break;}}
  let v=a/u;const digits=[];
  for(const d of AMT_VALUES){while(v>=d){digits.push(d);v-=d;}}
  return [u,digits];
}
const parse=k=>{const p=k.split("|");return [p[0],...p.slice(1).map(x=>(x!==""&&!isNaN(x))?Number(x):x)];};
function markedAmount(on,L){
  const units=[],digits=[];
  for(const k of on){const p=parse(k);if(p[1]===L){if(p[0]==="unit")units.push(p[2]);if(p[0]==="amt")digits.push(p[2]);}}
  if(units.length!==1||!digits.length)return null;
  return digits.reduce((a,b)=>a+b,0)*units[0];
}
function fullExpected(t){
  const ks=new Set(["venue|"+t.venue,"race|"+t.race,"type|"+t.type]);
  if(t.prev)ks.add("prev");
  t.lines.forEach((ln,L)=>{
    for(let b=0;b<3;b++)for(const n of ln.blocks[b])ks.add(`h|${L}|${b}|${n}`);
    const [u,digits]=canonAmount(ln.amount);
    ks.add(`unit|${L}|${u}`);digits.forEach(d=>ks.add(`amt|${L}|${d}`));
  });
  return ks;
}
function diffKeys(t,on){
  const exp=fullExpected(t),ok={};
  t.lines.forEach((ln,L)=>{ok[L]=markedAmount(on,L)===ln.amount;});
  const missing=new Set(),extra=new Set();
  for(const k of exp)if(!on.has(k)){const p=parse(k);if((p[0]==="unit"||p[0]==="amt")&&ok[p[1]])continue;missing.add(k);}
  for(const k of on)if(!exp.has(k)){const p=parse(k);if((p[0]==="unit"||p[0]==="amt")&&ok[p[1]])continue;extra.add(k);}
  return [missing,extra];
}
function amtExample(a){
  const [u,d]=canonAmount(a);
  return d.join("＋")+" と "+({10000:"万円",1000:"千円",100:"百円"})[u];
}
function checkMarks(t,on){
  const res=[],ps=[...on].map(parse);
  const got=p=>new Set(ps.filter(x=>x[0]===p).map(x=>x[1]));
  res.push(["場名",eqSet(got("venue"),new Set([t.venue])),VENUES[t.venue]+"を1つ塗る"]);
  res.push(["レース番号",eqSet(got("race"),new Set([t.race])),t.race+"を1つ塗る"]);
  res.push(["式別",eqSet(got("type"),new Set([t.type])),t.type+"を1つ塗る"]);
  res.push(["前日発売",on.has("prev")===t.prev,t.prev?"前日発売を塗る":"前日発売は塗らない"]);
  const n=t.lines.length;
  for(let L=0;L<n;L++){
    const ln=t.lines[L];let ok=true;
    for(let b=0;b<3;b++){
      const g=new Set(ps.filter(x=>x[0]==="h"&&x[1]===L&&x[2]===b).map(x=>x[3]));
      if(!eqSet(g,ln.blocks[b]))ok=false;
    }
    const exp=[0,1,2].filter(b=>ln.blocks[b].size).map(b=>["1着","2着","3着"][b]+"欄: "+fmt(ln.blocks[b])).join(" / ");
    res.push([CIRC[L]+"行 馬番",ok,exp]);
    res.push([CIRC[L]+"行 金額",markedAmount(on,L)===ln.amount,ln.amount.toLocaleString()+"円（例: "+amtExample(ln.amount)+"）"]);
  }
  if(n<LINES){
    const stray=ps.some(x=>["h","amt","unit","ura"].includes(x[0])&&x[1]>=n);
    res.push(["使わない行",!stray,CIRC[n]+"行目以降は空欄のまま"]);
  }
  res.push(["ウラ",!ps.some(x=>x[0]==="ura"),"今回ウラは塗らない"]);
  return res;
}
// ==UI==
/* ============ 画面 ============ */
const $=id=>document.getElementById(id);
const NS="http://www.w3.org/2000/svg";
const svg=$("svg");
function el(tag,attrs,parent){const e=document.createElementNS(NS,tag);for(const k in attrs)e.setAttribute(k,attrs[k]);(parent||svg).appendChild(e);return e;}
function txt(x,y,s,size,bold,anchor){
  const lines=String(s).split("\n"),n=lines.length;
  const t=el("text",{x,y,"text-anchor":anchor||"middle","font-size":size,"font-weight":bold?"bold":"normal",fill:INK});
  lines.forEach((l,i)=>{const sp=el("tspan",{x,dy:i===0?(size*0.35-(n-1)*size*0.55):size*1.1},t);sp.textContent=l;});
  return t;
}
const items={};let on=new Set();let task=null,t0=0,peeked=false,played=0,perfect=0,streak=0;
function mark(key,cx,cy,label,w,h,size){
  w=w||24;h=h||34;size=size||11;
  const g=el("g",{style:"cursor:pointer"});
  const o=el("ellipse",{cx,cy,rx:w/2,ry:h/2,fill:CARD,stroke:ORANGE,"stroke-width":2},g);
  const t=txt(cx,cy,label||"",size,true);g.appendChild(t);t.setAttribute("fill",ORANGE);t.style.pointerEvents="none";
  g.addEventListener("click",()=>toggle(key));
  items[key]={o,t,cx,cy,w,h};
}
function rect(x,y,w,h,fill,stroke,sw){el("rect",{x,y,width:w,height:h,fill:fill||"none",stroke:stroke||"none","stroke-width":sw||1});}
function drawCard(){
  rect(2,2,1206,636,CARD,"#555",2);
  rect(10,8,86,120,BOX,"#555");txt(53,30,"前日\n発売",11,true);mark("prev",53,88,"",26,40);
  rect(100,8,550,120,BOX,"#555");txt(375,22,"場　名",12,true);
  VENUES.forEach((v,i)=>{const cx=127+54*i;txt(cx,56,v,12,true);mark("venue|"+i,cx,96);});
  rect(660,8,282,120,BOX,"#555");txt(801,22,"レース番号",12,true);
  for(let n=1;n<=12;n++){const r=Math.floor((n-1)/6),c=(n-1)%6;mark("race|"+n,683+46*c,58+44*r,String(n),26,32,12);}
  rect(950,8,254,120,BOX,"#555");txt(1077,17,"式　別",12,true);
  TYPES.forEach((v,i)=>{const r=Math.floor(i/4),c=i%4,cx=981+62*c;txt(cx,40+46*r,v,11,true);mark("type|"+v,cx,64+46*r,"",24,26);});
  for(let b=0;b<3;b++)txt(14+b*300+138,146,(b+1)+"着・"+(b+1)+"頭目",11,true);
  txt(915,146,"ウラ",10,true);txt(1004,146,"金額",11,true);txt(1126,146,"単位",11,true);
  for(let L=0;L<LINES;L++){
    const y0=158+L*120;
    rect(6,y0,1198,114,BOX,"#888");txt(10,y0+9,CIRC[L],10,true,"start");
    for(let b=0;b<3;b++){
      const bx=14+b*300;rect(bx,y0+4,280,106,"none","#bbb");
      for(let n=1;n<=18;n++){const r=Math.floor((n-1)/9),c=(n-1)%9;mark(`h|${L}|${b}|${n}`,bx+18+c*30,y0+32+r*48,String(n),24,34,10);}
    }
    mark("ura|"+L,915,y0+57,"ウ\nラ",28,52,10);
    AMT_ROWS.forEach((row,r)=>row.forEach((v,c)=>mark(`amt|${L}|${v}`,950+c*36,y0+32+r*48,String(v),28,34,10)));
    UNITS.forEach(([name,m],c)=>mark(`unit|${L}|${m}`,1090+c*36,y0+57,name[0]+"\n円",28,52,10));
  }
}
function paint(k){const it=items[k],v=on.has(k);it.o.setAttribute("fill",v?INK:CARD);it.t.setAttribute("fill",v?"#cfcfcf":ORANGE);}
function clearFb(){svg.querySelectorAll(".fb").forEach(e=>e.remove());}
function toggle(k){clearFb();if(on.has(k))on.delete(k);else on.add(k);paint(k);}
function clearMarks(){clearFb();const ks=[...on];on.clear();ks.forEach(paint);$("result").textContent="";}
function ring(k,color,dash){
  const it=items[k];if(!it)return;
  const e=el("ellipse",{cx:it.cx,cy:it.cy,rx:it.w/2+6,ry:it.h/2+6,fill:"none",stroke:color,"stroke-width":3,class:"fb"});
  if(dash)e.setAttribute("stroke-dasharray","5 4");e.style.pointerEvents="none";
}
function updateStat(){$("stat").textContent="全問正解 "+perfect+"/"+played+"問　連続 "+streak;}
function newTask(){clearMarks();task=genTask(Number($("level").value));$("task").textContent=taskText(task);t0=Date.now();peeked=false;updateStat();}
function showAnswer(){
  clearFb();peeked=true;fullExpected(task).forEach(k=>ring(k,"#1f6fe0",true));
  const r=$("result");r.style.color="#1f6fe0";
  r.textContent="青い点線が正解の位置です。塗ってから「採点する」を押してみましょう（答えを見た問題は成績に数えません）";
}
function evaluate(){
  clearFb();
  const res=checkMarks(task,on),ok=res.filter(x=>x[1]).length,total=res.length,sec=Math.round((Date.now()-t0)/1000);
  const [missing,extra]=diffKeys(task,on);
  missing.forEach(k=>ring(k,"#1f6fe0",true));extra.forEach(k=>ring(k,"#e02020",false));
  const r=$("result");
  if(ok===total){r.textContent="🎉 全問正解！  "+ok+"/"+total+"項目　所要時間 "+sec+"秒";r.style.color="#168a2e";}
  else{
    r.textContent="採点 "+ok+"/"+total+"項目　所要時間 "+sec+"秒\n"+res.filter(x=>!x[1]).map(x=>"✗ "+x[0]+": "+x[2]).join("\n")+"\n（赤い輪＝余計に塗った所／青い点線＝塗り忘れ）";
    r.style.color="#c03030";
  }
  if(!peeked){played++;if(ok===total){perfect++;streak++;}else streak=0;updateStat();peeked=true;}
}
$("bEval").onclick=evaluate;$("bAns").onclick=showAnswer;$("bClear").onclick=clearMarks;$("bNext").onclick=newTask;$("level").onchange=newTask;
drawCard();newTask();
</script></body></html>
"""

components.html(HTML, height=1050, scrolling=True)
st.caption("カードの丸をタップして塗ります。レベルは右上のメニューで切り替え。")
