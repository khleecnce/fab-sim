"""새 팩 하나를 추가하는 실제 비용은 얼마인가.

질문: 공개 특허는 수만 건인데 왜 팩이 5개뿐인가?
가설 A: 데이터가 없어서 → 특허가 많으니 거짓일 가능성
가설 B: 팩 하나 만드는 비용이 비싸서 → 이걸 실측한다

측정 방법: 팩의 자기선언 파라미터를 하나씩 빼 보고, 빼면 시뮬레이션이
깨지는 것(=필수)과 빠져도 도는 것(=선택)을 가른다.
필수만이 진짜 비용이다.
"""
import sys
import pathlib
import warnings
import copy

warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np                               # noqa: E402
from sim.engine import Recipe, simulate          # noqa: E402
from sim.params import load_pack                 # noqa: E402
import sim.models                                # noqa: E402,F401


def mrr(pack_name, drop=None):
    """해당 키를 뺀 채로 시뮬레이션. 깨지면 예외.

    ⚠ sim.params.load_pack 을 monkeypatch 해도 소용없다 —
      sim.engine 이 `from sim.params import load_pack` 으로 **이름을 직접
      바인딩**했기 때문에 모듈 속성을 바꿔도 엔진은 원본을 계속 본다.
      (이 실수로 "모든 파라미터가 무영향"이라는 거짓 결과가 나왔다.)
      실제로 파일을 지운 임시 디렉토리를 만들어 FABSIM_PACK_DIR 로 가리킨다.
    """
    import os, shutil, tempfile, subprocess, json
    src = ROOT / "knowledge" / "params"
    with tempfile.TemporaryDirectory() as td:
        dst = pathlib.Path(td) / "params"
        shutil.copytree(src, dst)
        if drop:
            f = dst / f"{pack_name}.yaml"
            lines = f.read_text(encoding="utf-8").splitlines(keepends=True)
            out, skip = [], False
            for ln in lines:
                if ln.startswith(f"  {drop}:"):
                    skip = True
                    continue
                if skip:
                    # 하위 들여쓰기(4칸 이상)면 그 키의 블록이다
                    if ln.strip() and not ln.startswith("    "):
                        skip = False
                    else:
                        continue
                out.append(ln)
            f.write_text("".join(out), encoding="utf-8")
        env = dict(os.environ)
        env["FABSIM_PACK_DIR"] = str(dst)
        env["PYTHONWARNINGS"] = "ignore"
        code = (
            "import numpy as np, json;"
            "from sim.engine import Recipe, simulate;"
            "import sim.models;"
            f"r=simulate(Recipe(pack='{pack_name}'));"
            "print(json.dumps(float(np.mean(np.asarray(r.mrr_nm_per_min,dtype=float)))))"
        )
        p = subprocess.run([sys.executable, "-c", code], cwd=str(ROOT),
                           capture_output=True, text=True, env=env)
        if p.returncode != 0:
            raise RuntimeError((p.stderr or "").strip()[-200:])
        return json.loads(p.stdout.strip().splitlines()[-1])


PACKS = ["oxide_silica", "sti_ceria", "cu_h2o2_bta",
         "w_fe_oxidizer", "sic_ceria_h2o2"]

print("=" * 76)
print("새 팩 하나의 실제 비용 — 필수 파라미터만 세어 본다")
print("=" * 76)

totals = {"필수": [], "영향있음": [], "무영향": []}

for pack in PACKS:
    pk = load_pack(pack)
    own = [k for k in pk.params if pk.has_own(k)]
    base = mrr(pack)
    req, infl, noop = [], [], []
    for key in own:
        try:
            v = mrr(pack, drop=key)
        except Exception:
            req.append(key)
            continue
        if abs(v - base) / max(base, 1e-9) > 1e-6:
            infl.append(key)
        else:
            noop.append(key)
    totals["필수"].append(len(req))
    totals["영향있음"].append(len(infl))
    totals["무영향"].append(len(noop))
    print(f"\n── {pack}  (자기선언 {len(own)}개)")
    print(f"   필수   {len(req):2d}개 — 없으면 시뮬레이션이 안 돈다")
    if req:
        print(f"          {', '.join(sorted(req)[:8])}")
    print(f"   영향   {len(infl):2d}개 — 없어도 돌지만 결과가 바뀐다")
    print(f"   무영향 {len(noop):2d}개 — 빼도 결과가 같다 (이 팩에서 미사용)")
    if noop:
        print(f"          {', '.join(sorted(noop)[:8])}")

print()
print("=" * 76)
print(f"평균: 필수 {np.mean(totals['필수']):.1f}개 / "
      f"영향 {np.mean(totals['영향있음']):.1f}개 / "
      f"무영향 {np.mean(totals['무영향']):.1f}개")
print()
print("→ '필수' 개수가 새 팩 하나의 최소 비용이다.")
print("  이 숫자가 크면 팩 확장이 병목이고, 작으면 병목은 다른 데 있다.")
