"""논문 원문 텍스트를 **필요할 때 만들어** 돌려준다.

왜 필요한가 (2026-09-16)
────────────────────────
지식노트의 `python verify` 블록 여럿이 `papers/<이름>.pdf.txt` 를 직접 열어
원문 문구를 대조한다. 그런데 `papers/*.txt` 는 .gitignore 대상이라 저장소에
없고, 로컬에서 지워지면 그 블록이

    FileNotFoundError: papers/basim2000-...pdf.txt

로 죽는다. 그러면 검증기가 "검증 코드 실패"를 신고하는데, 실제로는 **주장이
틀린 것이 아니라 원문 사본이 없는 것**이다. 둘은 완전히 다른 사건인데
같은 얼굴로 나온다 — 다음 회차가 멀쩡한 노트를 뜯어고치러 간다.

규칙
────
1. `.txt` 사이드카가 있으면 그대로 쓴다.
2. 없고 **PDF 가 있으면 그 자리에서 추출**해 캐시한다(재현 가능).
3. 둘 다 없으면 `PaperTextMissing` 을 낸다 — 조용히 빈 문자열을 돌려주지
   않는다. 빈 문자열을 돌려주면 `assert "구절" not in text` 류가 **통과**해
   버려서, 원문이 없는데 "확인했다"가 된다. 그게 가장 나쁜 실패다.
"""
from __future__ import annotations

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAPERS = ROOT / "papers"


class PaperTextMissing(FileNotFoundError):
    """원문 사본이 이 기계에 없다 — 주장이 틀렸다는 뜻이 아니다."""


def paper_text(name: str) -> str:
    """`name` 은 'basim2000-....pdf' 또는 'basim2000-....pdf.txt' 둘 다 허용."""
    stem = name[:-4] if name.endswith(".pdf.txt") else name
    if not stem.endswith(".pdf"):
        stem += ".pdf"
    pdf = PAPERS / stem
    txt = PAPERS / (stem + ".txt")

    if txt.exists():
        return txt.read_text(encoding="utf-8", errors="ignore")

    if pdf.exists():
        try:
            import fitz                      # PyMuPDF
        except ImportError as e:             # pragma: no cover
            raise PaperTextMissing(
                f"{stem} 의 텍스트 사이드카가 없고 PyMuPDF 도 없어 추출 불가") from e
        with fitz.open(pdf) as doc:
            body = "\n".join(page.get_text() for page in doc)
        try:
            txt.write_text(body, encoding="utf-8")   # 캐시(.gitignore 대상)
        except OSError:
            pass
        return body

    raise PaperTextMissing(
        f"papers/{stem} 이 이 기계에 없다. papers/*.pdf 는 저작권상 커밋하지 "
        "않으므로 새 clone 에서는 원문을 다시 확보해야 한다 "
        "(tools/find_open_access.py --title \"<제목>\"). "
        "⚠ 이것은 '주장이 틀렸다'가 아니라 '이 기계에서 확인할 수 없다'는 뜻이다.")
