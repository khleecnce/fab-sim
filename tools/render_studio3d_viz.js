/* 실제 node-canvas 로 시각화를 렌더링해 PNG 로 떨어뜨린다.
   목적: "예외 없이 돈다"를 넘어 **그림이 실제로 읽히는가**를 눈으로 확인. */
const { createCanvas } = require("/tmp/node_modules/canvas");
const fs = require("fs");

const canvases = {};
const els = {};
function el(id){
  if(els[id]) return els[id];
  if(id.startsWith("cv-")){
    const spec = {
      "cv-padsec":[640,230], "cv-padasp":[640,250], "cv-padlife":[640,210],
      "cv-diskgrit":[640,300], "cv-diskpcr":[640,230],
    }[id] || [640,260];
    const c = createCanvas(spec[0], spec[1]);
    canvases[id] = c;
    els[id] = c;           // node-canvas 객체가 getContext/width/height 를 그대로 제공
    return els[id];
  }
  els[id] = { id, innerHTML:"", textContent:"", style:{}, dataset:{}, querySelectorAll:()=>[] };
  return els[id];
}
const PRESENT = new Set(["pidBox","cap-sds","cv-padsec","cap-padsec","cv-padasp","cap-padasp",
  "cv-padlife","cap-padlife","cv-diskgrit","cap-diskgrit","cv-diskpcr","cap-diskpcr",
  "foupGrid","cap-foup"]);
global.document = {
  getElementById:(id)=> PRESENT.has(id) ? el(id) : null,
  querySelectorAll:()=>[],
  createElement:()=>createCanvas(64,64),
};

const state = {
  pack:"oxide_silica", wafer:"NPW", time_s:60,
  recorded:{ diw_flow_ml_min:0, filter_rating_um:1.0, pump_type:"diaphragm", blend_tank_l:200 },
  initial_thickness_nm:1000, overrides:{}, base:{}, packs:[],
  foup:{ sel:0, slots:Array.from({length:25},(_,i)=> i<3?{wafer:i?"PTW":"NPW",pack:"oxide_silica",thick:1000,ttv:0}:null) },
};
const PACKVALS = {
  sfr_ml_min:200, abrasive_size_nm:50, abrasive_d99_nm:250, abrasive_wt_pct:10,
  groove_pitch_mm:3.05, groove_depth_mm:0.76, groove_width_um:600, pad_porosity_pct:30,
  asperity_density_per_m2:1e11, pad_asperity_radius_m:5e-6,
  cond_sweep_cpm:10, cond_duty_pct:100, cond_downforce_lbf:6, center_offset_m:0.20, wafer_radius_m:0.15,
};
function num(k,d){ return PACKVALS[k] ?? d; }
function boot(){} function run(){} function drawPanel(){}

const src = fs.readFileSync("/tmp/s3d_1.mjs","utf8");
const start = src.indexOf("const VC = {fg:");
const end   = src.indexOf("/* ─────────────────────────────────────────── Performance factors");
eval(src.slice(start, end));

drawViz();

/* 각 캔버스를 PNG 로, 그리고 캡션은 텍스트로 */
const OUT = "/tmp/viz";
fs.mkdirSync(OUT, {recursive:true});
for(const [id, c] of Object.entries(canvases)){
  fs.writeFileSync(`${OUT}/${id}.png`, c.toBuffer("image/png"));
  console.log("wrote", `${OUT}/${id}.png`, c.width+"x"+c.height);
}

/* 하나의 세로 시트로 합쳐 한 번에 보기 */
const order = ["cv-padsec","cv-padasp","cv-padlife","cv-diskgrit","cv-diskpcr"];
const TITLES = {
  "cv-padsec":"④ Pad — Groove Cross-section (+ eta curve, Mu 2016)",
  "cv-padasp":"④ Pad — Asperity statistics (GW): geometry check + eta candidates",
  "cv-padlife":"④ Pad — Life / glazing (Jeong 2024), clamped outside 1-10 min",
  "cv-diskgrit":"⑤ Disk — Grit map + which axis is which",
  "cv-diskpcr":"⑤ Disk — Pad cut-rate profile: sweep dwell vs wafer track",
};
const GAP = 30, W = 640;
let totH = 0;
for(const id of order) totH += canvases[id].height + GAP;
const sheet = createCanvas(W, totH + 14);
const sg = sheet.getContext("2d");
sg.fillStyle = "#0b0f14"; sg.fillRect(0,0,W,totH+14);
let y = 8;
for(const id of order){
  sg.fillStyle = "#4da3ff"; sg.font = "bold 11px sans-serif";
  sg.fillText(TITLES[id], 8, y+12);
  y += 20;
  sg.drawImage(canvases[id], 0, y);
  y += canvases[id].height + 10;
}
fs.writeFileSync("/tmp/viz/SHEET.png", sheet.toBuffer("image/png"));
console.log("wrote /tmp/viz/SHEET.png", W+"x"+(totH+14));

console.log("\n=== P&ID HTML ===");
console.log(els["pidBox"].innerHTML.replace(/\s+/g," ").slice(0,600));
console.log("\n=== FOUP grid (first 3 slots) ===");
console.log(els["foupGrid"].innerHTML.replace(/\s+/g," ").slice(0,420));
