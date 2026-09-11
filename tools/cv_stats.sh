cd ~/fab-sim
echo "tier1: $(ls sim/tier1_empirical/*.py | grep -v __init__ | wc -l)"
echo "tier2: $(ls sim/tier2_physics/*.py | grep -v __init__ | wc -l)"
echo "integration: $(ls sim/integration/*.py 2>/dev/null | grep -v __init__ | wc -l)"
echo "metrics: $(ls sim/metrics/*.py | grep -v __init__ | wc -l)"
echo "calib: $(ls sim/calibration/*.py | grep -v __init__ | wc -l)"
echo "notes: $(find knowledge -name '*.md' | wc -l)"
echo "datasets: $(ls validation/datasets/*.yaml | grep -v TEMPLATE | wc -l)"
echo "papers: $(ls papers/*.pdf 2>/dev/null | wc -l)"
echo "pyLOC: $(find sim tools -name '*.py' | xargs cat | wc -l)"
echo "commits: $(git rev-list --count HEAD)"
echo "agents: $(ls -d agents/*/ | wc -l)"
python3 -c "
import json
d=json.load(open('validation/patent_corpus.json'))
print('patent_corpus_type', type(d), len(d) if hasattr(d,'__len__') else '')
if isinstance(d,dict): print(list(d)[:6])
"
