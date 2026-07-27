"""Self-contained, cinematic-yet-readable HTML report for an MSAI Report.

Design intent: the 3D hero makes you *feel* the result (the measurements are a
particle field that clusters tightly when the judges agree), and the data section
below is calm and readable so a non-metrologist can act on it. Built per the
project's design-engineering philosophy: real volumetric bloom (not a CSS glow),
a refined green (agreement) / amber (anomaly) palette on warm charcoal, mono
numerals, generous space, motion only where it earns its place.
"""
from __future__ import annotations
import json

_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MSAI report · __TITLE__</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600&family=Geist+Mono:wght@400;500&display=swap');
:root{
  --bg: oklch(0.165 0.012 155);
  --bg2: oklch(0.205 0.013 155);
  --ink: oklch(0.955 0.006 150);
  --dim: oklch(0.72 0.01 150);
  --faint: oklch(0.52 0.01 150);
  --line: oklch(0.30 0.012 155);
  --good: oklch(0.82 0.15 156);
  --good-soft: oklch(0.62 0.10 156);
  --warn: oklch(0.80 0.135 72);
  --ease: cubic-bezier(0.23,1,0.32,1);
  --mono: 'Geist Mono', ui-monospace, monospace;
  --sans: 'Geist', ui-sans-serif, system-ui, sans-serif;
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--ink);font-family:var(--sans);font-weight:400;
  line-height:1.6;-webkit-font-smoothing:antialiased;overflow-x:hidden}
.num{font-family:var(--mono);font-feature-settings:"tnum"}

/* ---------- hero ---------- */
.hero{position:relative;min-height:100dvh;width:100%;overflow:hidden}
#scene{position:absolute;inset:0;width:100%;height:100%;display:block}
.no3d #scene{display:none}
.hero::after{content:"";position:absolute;inset:0;pointer-events:none;
  background:linear-gradient(to bottom, transparent 55%, var(--bg) 99%)}
.hero-in{position:absolute;left:clamp(20px,6vw,84px);bottom:clamp(40px,9vh,96px);
  max-width:min(640px,86vw);z-index:2}
.eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.22em;text-transform:uppercase;
  color:var(--good-soft);margin-bottom:22px}
.alpha{font-family:var(--mono);font-weight:500;font-size:clamp(68px,13vw,148px);
  line-height:.9;letter-spacing:-.03em;color:var(--ink)}
.alpha .ci{display:block;font-size:clamp(13px,1.4vw,15px);color:var(--faint);
  letter-spacing:0;margin-top:14px;font-weight:400}
.alpha-label{font-size:clamp(15px,1.9vw,19px);color:var(--dim);margin-top:6px}
.lede{font-size:clamp(17px,2.1vw,21px);color:var(--ink);margin-top:26px;line-height:1.5;
  max-width:34ch}
.scrollcue{position:absolute;left:clamp(20px,6vw,84px);bottom:18px;font-family:var(--mono);
  font-size:11px;letter-spacing:.18em;color:var(--faint);text-transform:uppercase;z-index:2}

/* ---------- report body ---------- */
main{max-width:1080px;margin:0 auto;padding:clamp(60px,11vh,128px) clamp(20px,6vw,84px) 120px}
section{padding-top:clamp(54px,9vh,104px)}
section + section{border-top:1px solid var(--line);margin-top:clamp(54px,9vh,104px)}
.kicker{font-family:var(--mono);font-size:12px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--good-soft);margin-bottom:18px}
h2{font-size:clamp(24px,3.4vw,34px);font-weight:500;letter-spacing:-.02em;line-height:1.15;
  margin-bottom:18px;max-width:22ch}
.body{color:var(--dim);max-width:64ch;font-size:clamp(15px,1.7vw,17px)}
.body strong{color:var(--ink);font-weight:500}
.reveal{opacity:0;transform:translateY(14px);transition:opacity .7s var(--ease),transform .7s var(--ease)}
.reveal.in{opacity:1;transform:none}

/* by judge */
.judges{margin-top:30px;display:flex;flex-direction:column;gap:18px;max-width:680px}
.jrow{display:grid;grid-template-columns:160px 1fr 92px;align-items:center;gap:16px}
.jname{color:var(--dim);font-size:14px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.jtrack{height:8px;background:var(--bg2);border-radius:99px;overflow:hidden}
.jfill{height:100%;background:var(--good);border-radius:99px;transform-origin:left;
  transform:scaleX(0);transition:transform 1s var(--ease)}
.in .jfill{transform:scaleX(var(--v))}
.jval{font-family:var(--mono);font-size:15px;text-align:right;color:var(--ink)}
.jsub{font-family:var(--mono);font-size:12px;color:var(--faint)}

/* heatmap */
.hm-wrap{margin-top:30px;overflow-x:auto;padding-bottom:8px}
.hm{display:grid;gap:4px;min-width:560px}
.hm-row{display:grid;grid-template-columns:128px 1fr;align-items:center;gap:10px}
.hm-name{font-family:var(--mono);font-size:11px;color:var(--faint);text-align:right;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.hm-cells{display:grid;gap:4px}
.cell{aspect-ratio:1;border-radius:3px;background:var(--good);transition:transform .15s var(--ease)}
.cell.off{background:var(--warn)}
.cell.na{background:var(--bg2);box-shadow:inset 0 0 0 1px var(--line)}
.cell:hover{transform:scale(1.18)}
.hm-axis{display:grid;grid-template-columns:128px 1fr;gap:10px;margin-top:6px}
.hm-ticks{display:grid;gap:4px}
.tick{font-family:var(--mono);font-size:9px;color:var(--faint);text-align:center;
  overflow:hidden;white-space:nowrap}
.legend{display:flex;gap:22px;margin-top:22px;font-size:13px;color:var(--dim);flex-wrap:wrap}
.legend span{display:inline-flex;align-items:center;gap:8px}
.sw{width:12px;height:12px;border-radius:3px;display:inline-block}

/* limits */
.limits{margin-top:28px;display:flex;flex-direction:column;gap:22px;max-width:64ch}
.limit{display:grid;grid-template-columns:auto 1fr;gap:14px;align-items:start}
.limit .n{font-family:var(--mono);font-size:13px;color:var(--warn);padding-top:2px}
.limit p{color:var(--dim);font-size:clamp(14px,1.6vw,16px)}
.limit b{color:var(--ink);font-weight:500}

footer{max-width:1080px;margin:0 auto;padding:0 clamp(20px,6vw,84px) 80px;
  color:var(--faint);font-size:13px;font-family:var(--mono);border-top:1px solid var(--line);
  padding-top:30px}
@media (prefers-reduced-motion: reduce){
  .reveal{transition:opacity .4s ease}.reveal{transform:none}
  .jfill{transition:none}html{scroll-behavior:auto}
}
</style>
</head>
<body>
<header class="hero">
  <canvas id="scene"></canvas>
  <div class="hero-in">
    <div class="eyebrow">MSAI · measurement reliability</div>
    <div class="alpha num" id="alpha">—<span class="ci" id="ci"></span></div>
    <div class="alpha-label" id="albl">judge agreement</div>
    <p class="lede" id="lede"></p>
  </div>
  <div class="scrollcue">scroll for the data</div>
</header>

<main>
  <section class="reveal">
    <div class="kicker">What this says</div>
    <h2 id="verdict-h">Read in one line</h2>
    <p class="body" id="verdict"></p>
  </section>

  <section class="reveal">
    <div class="kicker" id="bj-kicker">By judge</div>
    <h2>How each grader did</h2>
    <p class="body" id="bj-body"></p>
    <div class="judges" id="judges"></div>
  </section>

  <section class="reveal">
    <div class="kicker">Every measurement</div>
    <h2>One square per grade, nothing hidden</h2>
    <p class="body" id="hm-body"></p>
    <div class="hm-wrap"><div class="hm" id="hm"></div>
      <div class="hm-axis"><div></div><div class="hm-ticks" id="ticks"></div></div>
    </div>
    <div class="legend">
      <span><i class="sw" style="background:var(--good)"></i> in agreement / correct</span>
      <span><i class="sw" style="background:var(--warn)"></i> off</span>
      <span><i class="sw" style="background:var(--bg2);box-shadow:inset 0 0 0 1px var(--line)"></i> no answer</span>
    </div>
    <p class="body" id="hm-caption" style="margin-top:22px"></p>
  </section>

  <section class="reveal">
    <div class="kicker">What this does NOT tell you</div>
    <h2>The honest boundaries</h2>
    <div class="limits">
      <div class="limit"><span class="n">01</span><p><b>Agreement is not safety.</b> A grader can be perfectly consistent and consistently wrong. This measures whether your measurement is stable, not whether your model is good.</p></div>
      <div class="limit"><span class="n">02</span><p><b>The instrument moves.</b> An AI judge is not a steel gauge; it shifts with model and prompt changes. Re-run whenever the judge or prompt changes.</p></div>
      <div class="limit"><span class="n">03</span><p><b>Accuracy is only as good as your reference.</b> Any correctness number is conformance to the key you supplied. It inherits that key's weakness, and judge consensus is not a valid key.</p></div>
    </div>
  </section>
</main>
<footer id="foot"></footer>

<script type="importmap">
{"imports":{
  "three":"https://unpkg.com/three@0.160.0/build/three.module.js",
  "three/addons/":"https://unpkg.com/three@0.160.0/examples/jsm/"
}}
</script>
<script>window.__MSAI__ = __MSAI_DATA_JSON__;</script>

<script type="module">
const D = window.__MSAI__;
const fmt = (x,n=3)=> (x==null||Number.isNaN(x)) ? "n/a" : Number(x).toFixed(n);
const pct = x => (x==null||Number.isNaN(x)) ? "n/a" : Math.round(x*100)+"%";

/* ---- derive numbers from the data ---- */
const det = D.detail || {};
const grid = det.grid || [];
const judges = det.judges || [];
const items = det.items || [];
let good=0, off=0, na=0;
grid.forEach(r=>r.forEach(c=>{ if(c===1)good++; else if(c===0)off++; else na++; }));
const graded = good+off;
const acc = D.accuracy;
const hasRef = det.graded_against === "reference" && !!acc;
const agreePct = items.length ? items.map((_,i)=>{
  const col = judges.map((_,j)=> (grid[j]||[])[i]).filter(v=>v!==null&&v!==undefined);
  return col.length ? (col.filter(v=>v===1).length===col.length?1:0) : null;
}).filter(v=>v!==null) : [];
const fullAgreeItems = agreePct.filter(v=>v===1).length;

/* ---- hero overlay ---- */
const a = D.krippendorff_alpha;
document.getElementById("alpha").firstChild.textContent = (a==null||Number.isNaN(a))?"n/a":fmt(a);
const ci = D.alpha_ci||[];
document.getElementById("ci").textContent = (ci[0]==null)?"":`95% CI ${fmt(ci[0],2)} to ${fmt(ci[1],2)} · Krippendorff α (${D.alpha_level})`;
document.getElementById("albl").textContent = "judge agreement";
const ledeEl = document.getElementById("lede");
ledeEl.textContent = a>=0.8
  ? `Your ${D.n_judges} graders land on the same answer almost every time. The measurement is reproducible.`
  : a>=0.667
  ? `Your ${D.n_judges} graders agree on the easy cases but split on the rest. Read before you trust.`
  : `Your ${D.n_judges} graders often disagree. The noise may be in the rubric, not the models.`;

/* ---- verdict ---- */
let v = `You used <strong>${D.n_judges} AI models</strong> to grade the same <strong>${D.n_items} items</strong>, ${D.n_trials_max} time${D.n_trials_max===1?"":"s"} each. `;
v += `They fully agreed on <strong>${fullAgreeItems} of ${agreePct.length}</strong> items`;
if(hasRef) v += `, and matched your reference key on <strong>${pct(acc.overall_accuracy)}</strong> of graded picks`;
if(hasRef && acc.accuracy_label) v += ` — but ${acc.accuracy_label} (reference fitness: ${acc.fitness})`;
v += `. `;
if(off>0){
  // REV-014: only say "concentrated" if the off-picks actually cluster on one item (>=60% of them),
  // instead of asserting concentration whenever ANY single item has an off pick.
  const offByItem = items.map((_,i)=> judges.reduce((s,_,j)=> s + (((grid[j]||[])[i]===0)?1:0), 0));
  const topOff = Math.max(...offByItem);
  const topItem = items[offByItem.indexOf(topOff)];
  const conc = topOff/off;
  if(conc >= 0.6){
    v += `The disagreement is concentrated: <strong>${Math.round(conc*100)}%</strong> of the off picks land on item <strong>${topItem}</strong>. `;
  } else {
    v += `The disagreement is spread across items, not concentrated on one. `;
  }
} else {
  v += `Nothing landed off. `;
}
v += `Agreement like this means your eval is <strong>reproducible</strong>. It does not, by itself, mean the grades are correct.`;
document.getElementById("verdict").innerHTML = v;

/* ---- by judge ---- */
const bjBody = document.getElementById("bj-body");
bjBody.textContent = hasRef
  ? "Each bar is how often that grader matched your reference key."
  : "Each bar is how often that grader matched the panel's answer (no reference supplied, so this is agreement, not correctness).";
document.getElementById("bj-kicker").textContent = hasRef ? "Accuracy by judge" : "Agreement by judge";
const jwrap = document.getElementById("judges");
judges.forEach((jg,j)=>{
  const cells = (grid[j]||[]).filter(c=>c!==null&&c!==undefined);
  // prefer the official per-trial accuracy ledger; fall back to the modal grid
  let rate, denom, mae="";
  if(hasRef && acc.by_judge[jg]){
    rate = acc.by_judge[jg].accuracy; denom = acc.by_judge[jg].n;
    if(acc.by_judge[jg].mae!=null) mae = `  MAE ${fmt(acc.by_judge[jg].mae,2)}`;
  } else {
    denom = cells.length; rate = cells.length ? cells.filter(c=>c===1).length/cells.length : 0;
  }
  const row = document.createElement("div"); row.className="jrow";
  row.innerHTML = `<div class="jname" title="${jg}">${jg}</div>
    <div class="jtrack"><div class="jfill" style="--v:${rate}"></div></div>
    <div><span class="jval">${Math.round(rate*100)}%</span> <span class="jsub">/${denom}${mae}</span></div>`;
  jwrap.appendChild(row);
});

/* ---- heatmap ---- */
document.getElementById("hm-body").textContent =
  `Rows are graders, columns are items. ${graded} graded picks in total. Hover any square.`;
const hm = document.getElementById("hm");
const cols = items.length;
judges.forEach((jg,j)=>{
  const row = document.createElement("div"); row.className="hm-row";
  const cellsEl = document.createElement("div"); cellsEl.className="hm-cells";
  cellsEl.style.gridTemplateColumns = `repeat(${cols},1fr)`;
  items.forEach((it,i)=>{
    const c = (grid[j]||[])[i];
    const d = document.createElement("div");
    d.className = "cell" + (c===0?" off":c==null?" na":"");
    d.title = `${jg} · ${it} · ${c===1?"correct/agrees":c===0?"OFF":"no answer"}`;
    cellsEl.appendChild(d);
  });
  row.innerHTML = `<div class="hm-name" title="${jg}">${jg}</div>`;
  row.appendChild(cellsEl); hm.appendChild(row);
});
const ticks = document.getElementById("ticks");
ticks.style.gridTemplateColumns = `repeat(${cols},1fr)`;
items.forEach(it=>{ const t=document.createElement("div"); t.className="tick"; t.textContent=it.replace(/[^0-9]/g,"")||it; ticks.appendChild(t); });
document.getElementById("hm-caption").innerHTML = off>0
  ? `<strong>${good} of ${graded} squares are green.</strong> The remaining off picks mark where graders diverge — read those items before trusting them, rather than assuming a broken grader.`
  : `<strong>Every graded square is green.</strong> On this set, the graders were both consistent and aligned with your key.`;

/* ---- footer ---- */
document.getElementById("foot").textContent =
  `Generated by MSAI (msai-eval). Agreement measures reproducibility; accuracy (if shown) is conformance to your supplied reference. No safety claim is implied.`;

/* ---- scroll reveal (stagger) ---- */
const io = new IntersectionObserver((es)=>es.forEach((e,k)=>{
  if(e.isIntersecting){ e.target.style.transitionDelay=(e.target.dataset.d||0)+"ms"; e.target.classList.add("in"); io.unobserve(e.target); }
}),{threshold:.18,rootMargin:"-40px"});
document.querySelectorAll(".reveal").forEach((el,i)=>{ el.dataset.d=Math.min(i*60,180); io.observe(el); });

/* ============ 3D HERO ============ */
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
try{
  const THREE = await import("three");
  const {EffectComposer} = await import("three/addons/postprocessing/EffectComposer.js");
  const {RenderPass} = await import("three/addons/postprocessing/RenderPass.js");
  const {UnrealBloomPass} = await import("three/addons/postprocessing/UnrealBloomPass.js");
  const {Reflector} = await import("three/addons/objects/Reflector.js");
  const {MarchingCubes} = await import("three/addons/objects/MarchingCubes.js");

  const BG=0x141a16, GREEN=new THREE.Color(0xaef06a), AMBER=new THREE.Color(0xe8c486), CORE=new THREE.Color(0xd9ffe9);
  const canvas=document.getElementById("scene");
  const renderer=new THREE.WebGLRenderer({canvas,antialias:true,powerPreference:"high-performance"});
  renderer.setPixelRatio(Math.min(devicePixelRatio,2));
  const scene=new THREE.Scene();
  scene.fog=new THREE.FogExp2(BG,0.072);
  const W=()=>innerWidth, H=()=>innerHeight;
  const camera=new THREE.PerspectiveCamera(46,W()/H(),0.1,100);
  camera.position.set(0,1.25,7.2); camera.lookAt(0,0.35,0);
  renderer.setSize(W(),H());

  const group=new THREE.Group(); group.position.y=0.5; scene.add(group);

  // central reference: a morphing green plasma blob (the "true value"),
  // displaced by 3D simplex noise in the vertex shader (Xbox-boot energy).
  const SNOISE = `
    vec4 permute(vec4 x){return mod(((x*34.0)+1.0)*x,289.0);}
    vec4 taylorInvSqrt(vec4 r){return 1.79284291400159-0.85373472095314*r;}
    float snoise(vec3 v){
      const vec2 C=vec2(1.0/6.0,1.0/3.0); const vec4 D=vec4(0.0,0.5,1.0,2.0);
      vec3 i=floor(v+dot(v,C.yyy)); vec3 x0=v-i+dot(i,C.xxx);
      vec3 g=step(x0.yzx,x0.xyz); vec3 l=1.0-g; vec3 i1=min(g.xyz,l.zxy); vec3 i2=max(g.xyz,l.zxy);
      vec3 x1=x0-i1+C.xxx; vec3 x2=x0-i2+2.0*C.xxx; vec3 x3=x0-1.0+3.0*C.xxx;
      i=mod(i,289.0);
      vec4 p=permute(permute(permute(i.z+vec4(0.0,i1.z,i2.z,1.0))+i.y+vec4(0.0,i1.y,i2.y,1.0))+i.x+vec4(0.0,i1.x,i2.x,1.0));
      float n_=1.0/7.0; vec3 ns=n_*D.wyz-D.xzx;
      vec4 j=p-49.0*floor(p*ns.z*ns.z);
      vec4 x_=floor(j*ns.z); vec4 y_=floor(j-7.0*x_);
      vec4 x=x_*ns.x+ns.yyyy; vec4 y=y_*ns.x+ns.yyyy; vec4 h=1.0-abs(x)-abs(y);
      vec4 b0=vec4(x.xy,y.xy); vec4 b1=vec4(x.zw,y.zw);
      vec4 s0=floor(b0)*2.0+1.0; vec4 s1=floor(b1)*2.0+1.0; vec4 sh=-step(h,vec4(0.0));
      vec4 a0=b0.xzyw+s0.xzyw*sh.xxyy; vec4 a1=b1.xzyw+s1.xzyw*sh.zzww;
      vec3 p0=vec3(a0.xy,h.x); vec3 p1=vec3(a0.zw,h.y); vec3 p2=vec3(a1.xy,h.z); vec3 p3=vec3(a1.zw,h.w);
      vec4 norm=taylorInvSqrt(vec4(dot(p0,p0),dot(p1,p1),dot(p2,p2),dot(p3,p3)));
      p0*=norm.x;p1*=norm.y;p2*=norm.z;p3*=norm.w;
      vec4 m=max(0.6-vec4(dot(x0,x0),dot(x1,x1),dot(x2,x2),dot(x3,x3)),0.0); m=m*m;
      return 42.0*dot(m*m,vec4(dot(p0,x0),dot(p1,x1),dot(p2,x2),dot(p3,x3)));
    }`;
  // shader: dense white-hot center -> lime body -> green rim, hotspots drift over time
  const mcMat=new THREE.ShaderMaterial({
    uniforms:{uTime:{value:0.0},
      uCore:{value:new THREE.Color(0xf4ffd6)}, uBody:{value:new THREE.Color(0x8fd62a)},
      uDeep:{value:new THREE.Color(0x205f10)}},
    vertexShader:`
      varying vec3 vLoc; varying vec3 vNrm; varying vec3 vView; varying vec3 vWorld;
      void main(){
        vLoc=position; vNrm=normalize(normalMatrix*normal);
        vWorld=(modelMatrix*vec4(position,1.0)).xyz;
        vec4 mv=modelViewMatrix*vec4(position,1.0); vView=normalize(-mv.xyz);
        gl_Position=projectionMatrix*mv;
      }`,
    fragmentShader: SNOISE + `
      uniform float uTime; uniform vec3 uCore; uniform vec3 uBody; uniform vec3 uDeep;
      varying vec3 vLoc; varying vec3 vNrm; varying vec3 vView; varying vec3 vWorld;
      void main(){
        float d = clamp(length(vLoc), 0.0, 1.0);
        float fres = pow(1.0 - max(dot(vNrm,vView),0.0), 1.5);
        float hot = smoothstep(0.5, 0.03, d);                  // dense center glows white
        float nz = snoise(vWorld*1.25 + vec3(0.0,uTime*0.55,0.0))*0.5+0.5;  // drifting variation
        vec3 col = mix(uDeep, uBody, smoothstep(0.05,0.6,nz));
        col = mix(col, uCore, clamp(hot*(0.42+0.5*nz),0.0,1.0));
        col += fres * uBody * 0.55;
        gl_FragColor = vec4(col,1.0);
      }`
  });
  // MarchingCubes metaballs: a main mass plus droplets that pinch off and merge back
  const mc=new MarchingCubes(48, mcMat, false, false, 90000);
  mc.isolation=70; mc.scale.set(1.55,1.55,1.55); mc.position.y=0.0;
  group.add(mc);
  function buildField(tt){
    mc.reset();
    mc.addBall(0.5,0.5,0.5,0.62,12);
    for(let k=0;k<4;k++){ const ph=k/4*6.2832; const rad=0.13+0.085*Math.sin(tt*0.55+k*1.9);
      mc.addBall(0.5+Math.cos(tt*0.5+ph)*rad, 0.5+Math.sin(tt*0.42+ph*1.3)*rad*0.85,
                 0.5+Math.sin(tt*0.5+ph)*rad, 0.30, 12); }
    mc.update();
  }
  buildField(0.0);

  // particle field: every grade is a point. tight shell when agreement is high.
  const N=820, alpha=(a==null||Number.isNaN(a))?0.6:Math.max(0,Math.min(1,a));
  const spread=THREE.MathUtils.lerp(1.3,0.34,alpha);          // tightness encodes agreement
  const offFrac=graded>0?Math.min(0.5,off/graded):0.02;
  const pos=new Float32Array(N*3), col=new Float32Array(N*3);
  for(let i=0;i<N;i++){
    let x=Math.random()*2-1,y=Math.random()*2-1,z=Math.random()*2-1; const L=Math.hypot(x,y,z)||1;
    const isOff = i/N < offFrac;
    const r = 2.0 + (Math.random()-.5)*spread + (isOff? 0.7+Math.random()*0.6 : 0);
    x=x/L*r; y=y/L*r*0.78; z=z/L*r;
    pos[i*3]=x; pos[i*3+1]=y; pos[i*3+2]=z;
    const c=isOff?AMBER:GREEN; col[i*3]=c.r; col[i*3+1]=c.g; col[i*3+2]=c.b;
  }
  const pg=new THREE.BufferGeometry();
  pg.setAttribute("position",new THREE.BufferAttribute(pos,3));
  pg.setAttribute("color",new THREE.BufferAttribute(col,3));
  // soft round sprite so motes read as light dust, not hard pixels
  const dotTex=(()=>{const c=document.createElement("canvas");c.width=c.height=64;
    const g=c.getContext("2d");const grd=g.createRadialGradient(32,32,0,32,32,32);
    grd.addColorStop(0,"rgba(255,255,255,1)");grd.addColorStop(0.35,"rgba(255,255,255,0.5)");
    grd.addColorStop(1,"rgba(255,255,255,0)");g.fillStyle=grd;g.fillRect(0,0,64,64);
    const t=new THREE.CanvasTexture(c);return t;})();
  const points=new THREE.Points(pg,new THREE.PointsMaterial({
    map:dotTex,size:0.17,vertexColors:true,transparent:true,opacity:0.5,sizeAttenuation:true,
    blending:THREE.AdditiveBlending,depthWrite:false}));
  group.add(points);

  // ambient feathered dust spread across the whole frame (big, very faint motes)
  const AN=260, apos=new Float32Array(AN*3), acol=new Float32Array(AN*3);
  for(let i=0;i<AN;i++){
    apos[i*3]=(Math.random()*2-1)*8; apos[i*3+1]=(Math.random()*2-1)*4.5; apos[i*3+2]=(Math.random()*2-1)*5-1.5;
    const g=0.65+Math.random()*0.35; acol[i*3]=g*0.62; acol[i*3+1]=g; acol[i*3+2]=g*0.32;
  }
  const ag=new THREE.BufferGeometry();
  ag.setAttribute("position",new THREE.BufferAttribute(apos,3));
  ag.setAttribute("color",new THREE.BufferAttribute(acol,3));
  const ambient=new THREE.Points(ag,new THREE.PointsMaterial({
    map:dotTex,size:0.55,vertexColors:true,transparent:true,opacity:0.15,sizeAttenuation:true,
    blending:THREE.AdditiveBlending,depthWrite:false}));
  scene.add(ambient);

  // wet-floor mirror
  const mirror=new Reflector(new THREE.PlaneGeometry(60,60),{
    clipBias:0.003,textureWidth:W()*devicePixelRatio,textureHeight:H()*devicePixelRatio,color:0x0a0f0c});
  mirror.rotation.x=-Math.PI/2; mirror.position.y=-2.0; scene.add(mirror);

  // bloom
  const composer=new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene,camera));
  const bloom=new UnrealBloomPass(new THREE.Vector2(W(),H()),0.62,0.5,0.22);
  composer.addPass(bloom);
  composer.setSize(W(),H()); composer.setPixelRatio(Math.min(devicePixelRatio,2));

  addEventListener("resize",()=>{
    camera.aspect=W()/H(); camera.updateProjectionMatrix();
    renderer.setSize(W(),H()); composer.setSize(W(),H());
  },{passive:true});

  let t=0;
  function loop(){
    t+=0.016;
    mcMat.uniforms.uTime.value=t;
    if(!reduce){
      buildField(t);
      group.rotation.y+=0.0010; points.rotation.y-=0.0005;
      points.scale.setScalar(1.0+Math.sin(t*0.5)*0.02);
      ambient.rotation.y-=0.0003;
      camera.position.y=1.25+Math.sin(t*0.4)*0.1; camera.lookAt(0,0.35,0);
    }
    composer.render();
    requestAnimationFrame(loop);
  }
  loop();
  if(reduce){ composer.render(); }
}catch(err){
  document.body.classList.add("no3d");
  console.warn("3D hero unavailable, falling back to readable layout:",err);
}
</script>
</body>
</html>"""


def render(data: dict, path: str, title: str = "LLM-judge reliability") -> str:
    html = (_TEMPLATE
            .replace("__TITLE__", str(title))
            .replace("__MSAI_DATA_JSON__", json.dumps(data, default=str)))
    with open(path, "w", encoding="utf-8") as f:   # the HTML contains Δ/σ/× — never crash on cp1252
        f.write(html)
    return path
