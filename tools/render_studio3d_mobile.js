/* 폰 폭(360px 컨테이너 → 342 CSS px)에서 실제로 렌더링해 읽히는지 확인한다.
   데스크톱 620px 과 나란히 뽑아 비교 시트를 만든다. */
const { createCanvas } = require("/tmp/node_modules/canvas");
const fs = require("fs");

let HOST_W = 360;                 // 컨테이너 clientWidth
let DPR = 2;                      // 폰 레티나
const canvases = {}, els = {};

function mkEl(id){
  if(els[id]) return els[id];
  if(id.startsWith("cv-")){
    const c = createCanvas(10,10);
    c.dataset = { h: {"cv-padsec":230,"cv-padasp":300,"cv-padlife":210,
                      "cv-diskgrit":300,"cv-diskpcr":230}[id] || 230 };
    c.style = {};
    c.parentElement = { clientWidth: HOST_W };
    canvases[id] = c; els[id] = c; return c;
  }
  els[id] = { id, innerHTML:"", textContent:"", style:{}, dataset:{}, querySelectorAll:()=>[] };
  return els[id];
}
const PRESENT = new Set(["pidBox","cap-sds","cv-padsec","cap-padsec","cv-padasp","cap-padasp",
  "cv-padlife","cap-padlife","cv-diskgrit","cap-diskgrit","cv-diskpcr","cap-diskpcr",
  "foupGrid","cap-foup"]);
global.window = { devicePixelRatio: DPR };
global.document = {
  getElementById:(id)=> PRESENT.has(id) ? mkEl(id) : null,
  querySelectorAll:()=>[], createElement:()=>createCanvas(64,64),
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
  cond_sweep_cpm:10, cond_duty_pct:100, cond_downforce_lbf:6,
  center_offset_m:0.20, wafer_radius_m:0.15,
};
function num(k,d){ return PACKVALS[k] ?? d; }
function boot(){} function run(){} function drawPanel(){}

const src = fs.readFileSync("/tmp/s3d_1.mjs","utf8");
const start = src.indexOf("const VC = {fg:");
const end   = src.indexOf("/* ─────────────────────────────────────────── Performance factors");
eval(src.slice(start, end));

function renderAt(hostW, dpr, tag){
  HOST_W = hostW; DPR = dpr; global.window.devicePixelRatio = dpr;
  for(const k of Object.keys(canvases)){
    canvases[k].parentElement.clientWidth = hostW;
    delete canvases[k];  // 새로 만들게
    delete els[k];
  }
  drawViz();
  const order = ["cv-padsec","cv-padasp","cv-padlife","cv-diskgrit","cv-diskpcr"];
  const TITLES = {
    "cv-padsec":"Pad — groove cross-section + eta",
    "cv-padasp":"Pad — asperity stats (geometry check)",
    "cv-padlife":"Pad — life / glazing",
    "cv-diskgrit":"Disk — grit map + axes",
    "cv-diskpcr":"Disk — PCR sweep vs wafer track",
  };
  // 논리 크기(css px)로 시트 구성
  const cssW = Math.max(hostW-18, 280);
  let totH = 0;
  for(const id of order) totH += (+canvases[id].style.height.replace("px","")) + 26;
  const sheet = createCanvas(cssW*dpr, (totH+10)*dpr);
  const sg = sheet.getContext("2d");
  sg.scale(dpr,dpr);
  sg.fillStyle="#0b0f14"; sg.fillRect(0,0,cssW,totH+10);
  let y = 6;
  for(const id of order){
    sg.fillStyle="#4da3ff"; sg.font="bold 10px sans-serif";
    sg.fillText(TITLES[id], 4, y+10);
    y += 18;
    const hh = +canvases[id].style.height.replace("px","");
    sg.drawImage(canvases[id], 0, y, cssW, hh);
    y += hh + 8;
  }
  const out = `/tmp/viz/SHEET_${tag}.png`;
  fs.writeFileSync(out, sheet.toBuffer("image/png"));
  console.log(`${tag}: hostW=${hostW} cssW=${cssW} dpr=${dpr} -> ${out} (${sheet.width}x${sheet.height}px)`);
  // 캔버스별 실제 논리 크기 보고
  for(const id of order){
    console.log(`   ${id}: css ${canvases[id].style.width} x ${canvases[id].style.height}, bitmap ${canvases[id].width}x${canvases[id].height}`);
  }
  return out;
}

renderAt(360, 2, "phone");
renderAt(620, 1, "desktop");
console.log("\nFOUP grid on phone:", (els["foupGrid"].innerHTML||"").slice(0,120));
