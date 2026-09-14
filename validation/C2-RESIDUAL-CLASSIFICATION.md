# C2 잔여 10칸 성격 분류 (2026-09-15)

`tools/completion.py check` 기준 40/50, C2(estimated/unverified) 잔여 10칸을 1칸씩
판정한다. 분류 3종 — **[종결-문헌부재]**(3회차 규칙으로 이미 종결, 재탐색해도 안 열림) /
**[전진가능]**(구체적 미시도 경로 있음) / **[구조적]**(코드가 등급을 하드코딩으로 누름,
드라이버 confidence를 읽지 않음).

작업 방식: `EVIDENCE-RULES.md` 판정표(1~28, 9-종결·22-종결·24A/B/C)와
`sim/factors.py`의 `_f_gamma`(L433)/`_f_chi`(L1034)/`_f_psi`(L1115)/`_f_delta`(L1549)를
실제로 읽고, `knowledge/params/*.yaml`의 실제 `confidence:` 필드를 grep으로 대조해
역추적했다. 판정번호·노트경로·코드경로는 전부 실제로 연 것만 기재.

## 표

| 팩터/팩 | 분류 | 근거 | 남은 경로 | 예상 난이도 |
|---|---|---|---|---|
| Γ gamma / cu_h2o2_bta<br>Γ gamma / oxide_silica<br>Γ gamma / sic_ceria_h2o2<br>Γ gamma / sti_ceria<br>Γ gamma / w_fe_oxidizer | **[종결-문헌부재]** | `_f_gamma`(sim/factors.py:433) 사유(3) 임계하중 비선형이 5팩 공통으로 `estimated` 하한을 건다(코드: L548 `f.confidence = _worst_conf(driver_conf, "estimated")` — 리터럴, 사유(3) 스코프 축소 종결이라 주석에 명시). 이 리터럴은 EVIDENCE-RULES **판정#22**(1회차 재탐색, 2026-09-14)와 **22-종결**(3회차·영구종결, 2026-09-15)이 "마모 그릿 팁 반경(R)·IC1000 항복강도(Y) 직접 실측치는 이 코퍼스로 못 낸다"를 확정한 결과를 코드에 그대로 옮긴 것이다. 사유(1)(2)는 이미 해소/조건부 하한으로 전환됐고(판정#22 본문), 사유(3)만 하한을 걸고 있다. | 없음(3회차 소진, EVIDENCE-RULES §서두 3회차 규칙상 4회차 없음). 재개 조건은 22-종결이 명시: Doddabasanagouda 2004(ISU)류가 아니라 **그릿 팁 반경 실측**(10.1149/05201.0597ecst·10.1557/proc-0991-c01-01·JJAP 2편) 또는 **IC1000 항복강도 직접값** 신규 출처가 나타나야 하며, 나오면 factors.py:548의 하드코딩 리터럴도 함께 걷어내야 코드에 반영된다(코드 변경 필요 — 사용자 승인 사항). | 해당 없음 — 종결 |
| χ chi / cu_h2o2_bta | **[전진가능]** | `_f_chi`(L1099-1101)는 `oxidizer_passivation_K`(cu 팩 전용 억제항 상수)의 confidence를 그대로 읽는다(하드코딩 아님). `knowledge/params/cu_h2o2_bta.yaml:99` `oxidizer_passivation_K.confidence: estimated`. **판정#20**(2026-09-14)이 이 상수를 K=0.8232로 확정하며 "US20110165777A1 4점에 최소자승 적합(calibration), US9200180B2 Ex.5/6/7은 비율만 정성 교차확인 — literature 문턱 미달"로 명시. 다른 드라이버(oxidizer_wt_pct=verified, slurry_ph=literature)는 이미 상한이라 병목이 아니다. | US9200180B2 TABLE 1-b Ex.5/6/7(1/2.5/5 wt% → 11.8/9.2/7.7 nm/min, 이미 확보된 1차 문헌·신규 검색 불요)에 **동일 함수형(φ+(1-φ)(1-θ)/(1-θ_ref))으로 독립 K를 재적합**해 판정#20의 K=0.8232와 정합하는지 python verify로 확인. 정합하면(같은 함수형·다른 데이터셋이 독립 검증) EVIDENCE-RULES에 새 판정을 남기고 estimated→literature 승격. | 낮음 — 신규 문헌탐색 불필요, 이미 손에 있는 데이터로 재현 검산만 하면 됨 |
| ψ psi / cu_h2o2_bta | **[종결-문헌부재]** | `_f_psi`(L1179-1181)가 `inhibitor_strength_k`·`inhibitor_ref_mM` confidence를 읽음. `knowledge/params/cu_h2o2_bta.yaml:174` `inhibitor_strength_k.confidence: unverified`. 값-경로(산성계 농도스윕 1차출처)는 **판정#17**(반증만, 값 유지)→**#24B**(1회차)→**#24C**(2회차)→**#26**(3회차·최종종결, 2026-09-15: "로컬 코퍼스 73건 0건, CN107109135A 표는 이미지 전용, 세션 도구 승인 범위 문제")로 3회차 소진. 함수형-경로(Frumkin f 물리적 근거)는 **판정#25**(3회차·영구종결, 2026-09-15: "IBM Krishnan 2024 원문이 구조적으로 리포지토리 사본 없음")로 두 칸(cu_h2o2_bta·w_fe_oxidizer) 동시 종결. 두 경로 모두 종결이라 이중으로 막혀 있다. | 없음(양쪽 다 3회차 소진). #26 노트가 남긴 재오픈 조건: 웹 도구 승인 세션에서 신규 특허검색, 또는 CN107109135A 원본 PDF(현재는 이미지 표만) 별도 확보 — 조건 충족 시 "새 근거에 의한 정상 재판정"으로만 재개 가능(이번 종결의 번복 아님). | 해당 없음 — 종결(재오픈 조건부) |
| ψ psi / sti_ceria | **[전진가능]** | `_f_psi`(L1234-1236)가 `shield_langmuir_K`/`shield_hill_n`/`shield_strength_k` confidence를 읽음. `knowledge/params/sti_ceria.yaml` 6개 `shield_*` 키 전부 `confidence: estimated`(Park 2003 JJAP Fig.3 **그림판독** + (K,n,k) 비식별, 노트 §5.5). **판정#28**은 아직 **2회차**(2026-09-15, "승격 불가로 2회차 종결" — 3회차 규칙의 마지막 1회가 남음)이며 3회차 대상을 스스로 명시했다. | 판정#28이 지정한 3회차 착수 대상: (1) 미착수 3문헌 — doi:10.1143/jjap.43.l1060, doi:10.1021/acsaelm... (노트 원문 표기 `ma2008-01/17/693`), doi:10.1149/2162-8777/ab8ffa; (2) 개별사명 특허검색 — Hitachi/Showa Denko/Samsung/SK hynix/Fujimi. | 중간 — 3회차가 마지막, 실패 시 판정#9-종결·22-종결과 동형으로 스코프 축소 종결 예정 |
| ψ psi / w_fe_oxidizer | **[종결-문헌부재]** | `_f_psi`(L1179-1181) 동일 경로, `knowledge/params/w_fe_oxidizer.yaml:277` `inhibitor_strength_k.confidence: unverified`. **판정#24A**(2026-09-14)가 원문 Fig.4b 픽셀 재판독으로 0.5wt%점을 추가 확보해 (K,k) 전 파라미터공간 반증 확정(K→0 극한도 실측 17.6% 미달) — "구조적 한계(Langmuir+exp(-kθ) 함수형)"로 승격 기각. **판정#25**(3회차·영구종결)가 Frumkin 대체 함수형의 물리적 근거(Krishnan 2024)도 구조적으로 미확보 확정, cu_h2o2_bta와 동시 종결. | 없음(값-경로는 판정#24A가 전 파라미터공간 반증, 함수형-경로는 #25가 3회차 소진). 재개하려면 Langmuir/Frumkin이 아닌 **제3의 등온식**(임계피복률 문턱 등) 1차 근거가 새로 나와야 한다 — #24A 노트가 명시. | 해당 없음 — 종결 |
| Δ delta / cu_h2o2_bta | **[전진가능]** | `_f_delta`(L1646-1648) `_worst_conf(_driver_conf, _exp_conf)`. `abrasive_d99_nm`/`abrasive_ref_d99_nm`는 2026-09-14 재승격으로 이미 `confidence: literature`(US7344988B2 알루미나 CMP 전용 특허, 화학종·용도 일치) — 병목이 **아니다**. 병목은 `damage_exponent.confidence: estimated`(`knowledge/params/cu_h2o2_bta.yaml:281`, "텅스텐→구리 전이, Cu 막질 직접 D99-스크래치 대응쌍 미확인"). **판정#27**은 **1회차**(2026-09-15)로, 3회차 규칙상 아직 2회 더 남았고 원문 3건(Basim 2000·Wei 2013·Teo 2003)을 이미 확보·배제한 뒤 다음 우선순위를 스스로 지정했다. | 판정#27이 지정한 2회차 1순위: doi:10.1149/1.2335982(알루미나+Cu 화학종 정확 일치, 최유력 후보 — 1회차는 IOP 직접만 시도, **미러 사이트 미시도**), 보조 후보 Li 2018 ECS JSS doi:10.1149/2.0101806jss(Cu barrier+콜로이달실리카, EDA 분산제 스윕). | 중간 — 1회차 소진, 2회 더 가능하나 IOP 계열 미러 사이트 봉쇄 이력(판정#24B/C 등)을 고려하면 실패 확률도 상존 |

## 자체 검증 — 판정번호 실존 확인

```
$ grep -oE '판정#[0-9]+[A-Z]?|판정 ?#[0-9]+-종결' validation/C2-RESIDUAL-CLASSIFICATION.md | sort -u
```
사용된 판정번호: #17, #20, #22, #22-종결, #24A, #25, #26, #27, #28 — 전부 `EVIDENCE-RULES.md`
표(라인 50-89)에 실존 확인(각 번호로 grep해 1건 이상 매치, 아래 "완료 기준 1" 섹션 참조).

## 집계

- **[종결-문헌부재]**: 7칸 — Γ×5(판정#22/22-종결) + ψ/cu_h2o2_bta(판정#17·#24B·#24C·#26·#25) + ψ/w_fe_oxidizer(판정#24A·#25)
- **[전진가능]**: 3칸 — χ/cu_h2o2_bta(판정#20 후속) + ψ/sti_ceria(판정#28, 3회차 남음) + Δ/cu_h2o2_bta(판정#27, 2·3회차 남음)
- **[구조적]**: 0칸 — Γ의 `_worst_conf(driver_conf, "estimated")` 리터럴(factors.py:548)이 κ(S48)와 같은 **코드 패턴**이긴 하나, κ와 달리 이것은 **판정#22/22-종결이 이미 3회차로 종결한 문헌부재 사실을 코드에 그대로 인코딩**한 것이다(모델 함수형의 미확정·식별불가가 원인인 κ·판정#19 유형과는 원인이 다르다). 따라서 "코드 구조 자체가 원인"인 별도 [구조적] 칸으로 세지 않고 [종결-문헌부재]에 포함시켰다 — 단, 이 하드코딩 리터럴 자체가 향후 재탐색 성공 시 **함께 걷어내야 할 코드 변경 지점**이라는 점은 Γ 행에 명시해 뒀다. `_f_chi`/`_f_psi`는 감사 결과 하드코딩 리터럴 없이 팩 YAML의 실제 `confidence:` 값을 그대로 읽는다(L1099-1101, L1179-1181, L1234-1236) — κ식 구조적 캡이 존재하지 않음을 코드로 확인했다.
