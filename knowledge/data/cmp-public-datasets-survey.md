# CMP 공개 데이터셋 조사 — 논문 부록·SEMATECH·대학 공개 데이터에 무엇이 있고 무엇이 없는가 (cmp-data-engineer Lv1-1)

> 에이전트: cmp-data-engineer Lv1-1 | 작성일: 2026-09-09
> 관련: [[abrasive-size-concentration-ph-K-additive-mrr-quantitative]] (본 노트가 "표에서 수기 추출"이라 지목하는 대상), [[inline-virtual-metrology-sampling-optimization]] (VM·샘플링 문헌의 정량값 출처), [[cu-dishing-erosion-density-step-height-model-tugbawa]] (MIT Boning 그룹 문헌의 대표 사례)
> 범위: 웹 검색(2026-09-09 시점)으로 확인 가능한 CMP 관련 공개 데이터를 "실제 다운로드 가능한 구조화 데이터셋"과 "논문 본문/부록의 표·그림"으로 구분해 정리한다. 동진 사내 데이터·관행은 다루지 않는다(문헌만).

## 1. 존재하는 것 — 2016 PHM Data Challenge CMP 데이터셋

현재까지 확인된 것 중 유일하게 **실제 CMP 툴에서 수집된, 다운로드 가능한 구조화 데이터셋**은 PHM Society(Prognostics and Health Management Society)가 주관한 2016년 데이터 챌린지의 CMP 데이터셋이다. PHM Society 공식 페이지(phmsociety.org)에 압축파일 링크가 걸려 있고, 이를 사용한 후속 연구가 다수 존재한다(가장 상세히 확인한 것은 Li, Wu, Yu, "Prediction of Material Removal Rate for Chemical Mechanical Planarization Using Decision Tree-Based Ensemble Learning," *Journal of Manufacturing Science and Engineering* 141(3), 031003, 2019, DOI: 10.1115/1.4042051 — 저자 소속 UCF 홈페이지에 호스팅된 원문 PDF를 fitz로 직접 열어 본문을 확인).

### 1.1 데이터 구조 (Li et al. 2019 §4.1, 원문 확인)

- 4개 CMP 툴에서 지정된 웨이퍼들을 다양한 런(run)에 걸쳐 모니터링한 시계열 신호.
- 컬럼: 실시간 상태 모니터링 변수(패드 백킹필름·드레서·폴리싱테이블·드레서테이블·멤브레인·캐리어시트 사용량·드레싱워터 상태 등) **19개** + 압력·슬러리 유량·웨이퍼 회전속도·스테이지·헤드 등 사전설정 파라미터 **6개** = 총 **25개**(x1~x25). PHM Society 페이지 자체도 "25 columns"라고 표기해 이 숫자와 일치한다.
- 학습 데이터: **웨이퍼 1981개**, 스테이지 A/B 두 조건, 총 **672,744개 트레이스**(시계열 샘플), **185개 CSV 파일**로 분할(스테이지 A에서 이상치 4건 제거). 검증 데이터 **144,148 트레이스**, 테스트 데이터 **156,262 트레이스**. 전체 용량 약 187 MB.
- 목표변수: `AVG_REMOVAL_RATE` — CMP 전후 두께 측정으로 산출한 평균 제거율(MRR, nm/min 단위로 보고됨). 웨이퍼ID·STAGE별로 라벨이 붙는다.
- 파일명 패턴(PHM Society 페이지 확인): `CMP-training-*.csv`(시계열), `CMP-training-removalrate.csv`(라벨), `CMP-test-*.csv`.

### 1.2 이 데이터로 무엇을 재현할 수 있는가

Li et al.(2019)은 원신호에서 시간영역 4종(표준편차·3차중심모멘트·왜도·첨도) + 주파수영역 3종(최대진폭·주파수중심·첨도) = 특징 85개를 추출하고, RF 중요도 기준 상위 35개를 선택했을 때 GBT/RF 모두 R²=0.917, 잔차 표준편차 8.317 nm/min(GBT, 35특징, 검증셋)을 문헌값으로 보고한다. 이는 "슬러리 조성→MRR" 같은 화학·기계 모델이 아니라 **FDC(장비 상태 신호)→MRR 가상계측(VM)** 문제이며, [[inline-virtual-metrology-sampling-optimization]]에서 다룬 VM 역할 분담과 정확히 같은 카테고리의 데이터다.

```python verify
# PHM 2016 CMP 데이터셋 구조 재현 — Li, Wu, Yu (2019) ASME JMSE 141(3):031003
# DOI: 10.1115/1.4042051, §4.1 Data Description 수치를 그대로 assert로 옮긴다.
n_measurement_vars = 19
n_extra_params = 6
assert n_measurement_vars + n_extra_params == 25, "x1..x25 총 25컬럼 문헌값과 불일치"

n_traj_train, n_traj_valid, n_traj_test = 672744, 144148, 156262
total_traj = n_traj_train + n_traj_valid + n_traj_test
assert total_traj == 973154, "학습/검증/테스트 트레이스 합계가 문헌값과 다르다"

n_files_train = 185
n_wafers_train = 1981
assert n_files_train == 185 and n_wafers_train == 1981

# UCI SECOM 클래스 불균형 재현 — McCann & Johnston (2008), archive.ics.uci.edu/dataset/179
n_total, n_fail = 1567, 104
n_pass = n_total - n_fail
assert n_pass == 1463
ratio = n_pass / n_fail
assert 14.0 < ratio < 14.1, f"불균형비 {ratio:.2f}가 문헌 서술(약 14:1)과 어긋남"

print("PHM2016 컬럼/트레이스 수, SECOM 클래스 비율 모두 문헌값과 대조 일치")
```

## 2. 존재하지만 CMP 전용이 아닌 것 — UCI SECOM

UCI Machine Learning Repository의 SECOM 데이터셋(McCann & Johnston, 2008; CC BY 4.0 라이선스, archive.ics.uci.edu/dataset/179)은 인스턴스 1,567개, 컬럼 591개(특징 590 + pass/fail 라벨 1)로 반도체 제조 공정의 센서·계측 신호를 담고 있다. 그러나 **어느 공정 단계인지 명시되지 않는다** — 페이지 설명 자체가 "반도체 제조 공정"이라고만 하고 CMP를 특정하지 않는다. 특징도 익명화되어 있어 CMP 파라미터(압력·유량·pH 등)로 되짚을 수 없다. 라벨은 불량 104건 vs 정상 1463건(약 14:1 불균형)으로, 조성·MRR 같은 회귀 문제가 아니라 공정 이상 분류(FDC) 문제다. 결론: **CMP 스키마 설계에 직접 재사용은 불가**하지만, "익명 다변량 FDC + 불균형 이진 라벨"이라는 데이터 형태 자체는 [[inline-virtual-metrology-sampling-optimization]]에서 다룬 VM 입력 구조와 유사하므로 스키마의 "일반 FDC 엔터티" 설계 참고용으로는 쓸 수 있다.

## 3. 논문 본문·부록에만 있는 CMP 데이터 — 다운로드 가능한 "데이터셋"은 아니다

CMP 슬러리 조성(입자크기·농도·pH·K⁺·분산제)과 MRR의 관계를 다루는 문헌은 많지만, 이들은 **논문 본문 표(Table)나 그림(Figure)의 형태로만 존재**하고 별도의 CSV/부록 데이터파일로 공개된 경우를 찾지 못했다. 예컨대 이 저장소의 [[abrasive-size-concentration-ph-K-additive-mrr-quantitative]] 노트 자체가 여러 논문의 본문 표·그래프에서 수치를 **수기로 옮겨 재구성**한 것이지, 저자가 배포한 구조화 데이터를 내려받은 것이 아니다. MIT Boning 그룹(예: Tugbawa 박사논문, [[cu-dishing-erosion-density-step-height-model-tugbawa]]에서 다룬 dishing/erosion 모델)도 mtlsites.mit.edu·boning.mit.edu에 논문 PDF는 다수 공개하지만, 이번 조사에서 별도의 다운로드 가능한 실험 데이터 저장소(데이터베이스·CSV·SI 파일)는 찾지 못했다 — 논문 부록의 DOE 표는 PDF 본문 안에 이미지/텍스트로만 존재한다. 이 부재는 "없다"를 확정 증명한 것이 아니라 **이번 검색 범위에서 확인하지 못했다는 뜻**이며, 향후 학위논문 리포지토리(DSpace 등)를 개별 논문 단위로 더 뒤지면 원자료 첨부물이 나올 가능성은 남아 있다(미검증).

## 4. 조사했지만 존재를 확인하지 못한 것

- **SEMATECH/SEMI 공개 데이터셋**: SEMATECH가 CMP를 핵심 기술로 지정하고 Applied Materials 등과 컨소시엄 프로젝트(Cu CMP 컨소시어블 평가 등)를 운영했다는 기록은 다수 확인되나, 회원사 외부에 공개된 정량 데이터셋(슬러리 조성표, 툴 성능 로그 등)은 이번 검색에서 찾지 못했다. SEMATECH 활동은 대부분 회원제 컨소시엄 보고서 형태였고, 공개 아카이브에 남은 것은 특허·2차 보도자료뿐이었다.
- **Figshare/Zenodo의 CMP 데이터셋**: "chemical mechanical polishing/planarization CMP dataset"으로 두 저장소를 검색했으나 관련 데이터셋을 확인하지 못했다(검색 시점 2026-09-09 기준 — 두 플랫폼은 계속 업데이트되므로 이후 등록될 수 있다).
- **Kaggle의 CMP 전용 데이터셋**: PHM2016 데이터셋이 커뮤니티에 의해 노트북 형태로 재사용된 사례는 있으나(예: virtual metrology 리뷰 논문의 언급), Kaggle에 독립적으로 게시된 CMP 전용 데이터셋은 확인하지 못했다. Kaggle에서 실제로 찾을 수 있었던 것은 SECOM 미러(§2, CMP 특정 아님)뿐이다.
- **MIT Boning 그룹의 구조화 데이터 저장소**: §3 참조. 논문 PDF 저장소는 있으나 데이터 저장소는 확인 못 함.

## 5. cmp-data-engineer 스키마 설계에 대한 시사점

이번 조사 결과가 Lv1-2(통합 스키마 설계)에 주는 함의는 두 갈래다. 첫째, PHM2016류의 **FDC 시계열형** 데이터(웨이퍼ID·스테이지·다변량 센서 트레이스·목표 MRR)는 실측 공개 데이터가 존재하므로, 스키마의 "장비 상태 모니터링" 엔터티는 이 데이터의 필드 구조(1.1절)를 참고해 설계할 수 있다. 둘째, **조성-성능형**(슬러리 파라미터→MRR, 패턴밀도→dishing/erosion 등) 데이터는 공개 구조화 데이터셋이 전무하고 전량 "논문 표 수기 추출"에 의존하므로, 스키마는 이 추출 과정 자체를 1급 시민으로 다뤄야 한다 — 즉 각 레코드에 출처(DOI/논문 Table 번호)를 강제하는 필드가 없으면 [[abrasive-size-concentration-ph-K-additive-mrr-quantitative]] 같은 노트들이 향후 재검증 불가능한 상태로 쌓이게 된다. 이 두 데이터 성격(시계열형 vs 표형)은 단일 스키마로 억지로 합치기보다 별도 엔터티로 두고 공통 키(웨이퍼/로트/공정단계)로만 조인하는 편이 안전하다는 것이 이번 조사에서 얻은 잠정 결론이다(설계 자체는 Lv1-2에서 다룬다 — 이 노트의 범위 밖).
