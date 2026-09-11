/* drawViz() 계열 함수를 jsdom 없이 단독 실행해 검증한다.
   목적: 캔버스 그리기 코드가 실제로 예외 없이 돌고, 숫자가 의도대로 나오는지.
   three.js·DOM 전체를 띄우지 않고, 함수가 쓰는 최소 표면만 스텁으로 만든다. */

const calls = [];
function mkCtx(){
  const noop = ()=>{};
  return new Proxy({}, {
    get(_, k){
      if(k==="canvas") return {width:640, height:260};
      if(k==="measureText") return ()=>({width:40});
      if(k==="save"||k==="restore") return noop;
      if(typeof k === "string") return (...a)=>{ calls.push(k); return undefined; };
      return noop;
    },
    set(){ return true; }
  });
}

const els = {};
function el(id){
  if(!els[id]){
    els[id] = {
      id, innerHTML:"", textContent:"", style:{},
      width:640, height:260,
      getContext:()=>mkCtx(),
      querySelectorAll:()=>[],
      dataset:{},
    };
  }
  return els[id];
}

// 테스트할 id 목록 — 없는 것은 null 을 돌려 "조용히 통과"를 확인한다
const PRESENT = new Set(["pidBox","cap-sds","cv-padsec","cap-padsec","cv-padasp","cap-padasp",
  "cv-padlife","cap-padlife","cv-diskgrit","cap-diskgrit","cv-diskpcr","cap-diskpcr",
  "foupGrid","cap-foup"]);

global.document = {
  getElementById:(id)=> PRESENT.has(id) ? el(id) : null,
  querySelectorAll:()=>[],
  createElement:()=>({ width:0, height:0, getContext:()=>mkCtx() }),
};
global.console.warn = (...a)=>{ throw new Error("drawViz threw: "+a.join(" ")); };

/* 함수들이 의존하는 전역 */
const state = {
  pack:"oxide_silica", wafer:"NPW", time_s:60,
  recorded:{ diw_flow_ml_min:0, filter_rating_um:1.0, pump_type:"diaphragm", blend_tank_l:200 },
  initial_thickness_nm:1000, overrides:{}, base:{}, packs:[],
  foup:{ sel:0, slots:Array.from({length:25},(_,i)=> i===0?{wafer:"NPW",pack:"oxide_silica",thick:1000,ttv:0}:null) },
};
const PACKVALS = {
  sfr_ml_min:200, abrasive_size_nm:50, abrasive_d99_nm:250, abrasive_wt_pct:10,
  groove_pitch_mm:3.05, groove_depth_mm:0.76, groove_width_um:600, pad_porosity_pct:30,
  asperity_density_per_m2:1e11, pad_asperity_radius_m:5e-6,
  cond_sweep_cpm:10, cond_duty_pct:100, cond_downforce_lbf:6, center_offset_m:0.20, wafer_radius_m:0.15,
};
function num(k, d){ return PACKVALS[k] ?? d; }
function boot(){}
function run(){}
function drawPanel(){}

/* studio3d.html 에서 시각화 블록만 잘라 온다 */
const fs = require("fs");
const src = fs.readFileSync("/tmp/s3d_1.mjs","utf8");
const start = src.indexOf("const VC = {fg:");
const end   = src.indexOf("/* ─────────────────────────────────────────── Performance factors");
if(start<0 || end<0){ console.error("블록 경계를 못 찾음", start, end); process.exit(2); }
const block = src.slice(start, end);
console.log("extracted viz block:", block.length, "chars");

eval(block);

/* ── 실행 ── */
const checks = [];
function chk(name, fn){
  calls.length = 0;
  try{ fn(); checks.push([name, true, calls.length]); }
  catch(e){ checks.push([name, false, e.message]); }
}
chk("drawSDS", drawSDS);
chk("drawPadSection", drawPadSection);
chk("drawPadAsperity", drawPadAsperity);
chk("drawPadLife", drawPadLife);
chk("drawDiskGrit", drawDiskGrit);
chk("drawDiskPCR", drawDiskPCR);
chk("drawFoup", drawFoup);
chk("drawViz(all)", drawViz);

let bad = 0;
for(const [n, ok, info] of checks){
  console.log(ok ? `  OK    ${n}  (${info} canvas ops)` : `  FAIL  ${n}: ${info}`);
  if(!ok) bad++;
}

/* 내용 검증 — 그림이 '그려졌다'만이 아니라 '맞는 말을 하는가' */
console.log("\n--- content checks ---");
function has(id, needle, label){
  const t = els[id] ? (els[id].innerHTML||"") : "";
  const ok = t.includes(needle);
  console.log(ok?`  OK    ${label}`:`  FAIL  ${label} (missing "${needle}")`);
  if(!ok) bad++;
}
// P&ID: 필터가 dead 로 표시되고, D99 250nm < 1.0µm 이므로 "nothing to retain"
has("pidBox", 'class="nd dead"', "P&ID marks recorded-only nodes dashed");
has("cap-sds", "nothing to retain", "filter vs D99 verdict correct (250nm < 1.0um)");
// asperity: 1e11 은 기하 반증에 걸려야 한다
has("cap-padasp", "fails the geometric check", "eta=1e11 flagged as geometrically impossible");
// FOUP: 1/25 적재
has("cap-foup", "1/25 slots loaded", "FOUP reports 1/25 loaded");
has("foupGrid", 'data-slot="24"', "FOUP renders all 25 slots");
has("foupGrid", 'class="sl on npw"', "slot 1 selected + NPW");
// 패드 단면: width 만 wired
has("cap-padsec", "Width is the only groove dimension wired", "pad section states depth/pitch are dead");

/* D99 를 필터보다 크게 만들어 경고로 뒤집히는지 */
console.log("\n--- filter cut flip (D99 2000nm vs 1.0um filter) ---");
PACKVALS.abrasive_d99_nm = 2000;
els["cap-sds"].innerHTML = "";
drawSDS();
has("cap-sds", "a real POU filter would cut it", "coarse tail now warns");

/* eta 를 2.0e8 로 내리면 기하 검사를 통과해야 한다 */
console.log("\n--- eta 2.0e8 geometric check ---");
PACKVALS.asperity_density_per_m2 = 2.0e8;
els["cap-padasp"].innerHTML = "";
drawPadAsperity();
const t = els["cap-padasp"].innerHTML;
const passed = !t.includes("fails the geometric check");
console.log(passed?"  OK    eta=2.0e8 passes the geometric check"
                 :"  FAIL  eta=2.0e8 still flagged");
if(!passed) bad++;

console.log(bad ? `\n${bad} FAILURE(S)` : "\nALL PASS");
process.exit(bad?1:0);
