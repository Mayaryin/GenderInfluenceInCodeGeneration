import os

from helpers.statistical_tests import compare_genders
from statsmodels.stats.multitest import multipletests
import tempfile
import subprocess
import re
from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze

def run_pylint_on_code(code):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
        tmp.write(code)
        tmp_path = tmp.name
    try:
        result = subprocess.run(
            ['pylint', '--score=y', '--output-format=text', '--rcfile=.pylintrc', tmp_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output = result.stdout
        errors = result.stderr
        # Extract score from output
        score_line = [line for line in output.split('\n') if 'Your code has been rated at' in line]
        if score_line:
            # Example: "Your code has been rated at 8.00/10"
            score = float(score_line[0].split(' ')[6].split('/')[0])
        else:
            score = None

        # Extract pylint codes using regex, e.g. W0611, C0114, etc.
        code_pattern = re.compile(r': ([A-Z]\d{4}):')
        pylint_codes = code_pattern.findall(output)

        # Save the full pylint output and stderr (just in case)
        messages = output.strip() + '\n' + errors.strip()
    finally:
        os.remove(tmp_path)  # Always clean up
    return score, messages, pylint_codes


def calc_radon_metrics(code):
    # Complexity
    try:
        complexity_data = cc_visit(code)
        cc_scores = [block.complexity for block in complexity_data] if complexity_data else [0]
        radon_complexity = float(sum(cc_scores) / len(cc_scores))
    except Exception:
        radon_complexity = None

    # MI index
    try:
        radon_maintainability_index = float(mi_visit(code, False))
    except Exception:
        radon_maintainability_index = None

    # Raw metrics
    try:
        raw = analyze(code)
        radon_loc = raw.loc
        radon_sloc = raw.sloc
        radon_lloc = raw.lloc
        radon_comments = raw.comments
    except Exception:
        radon_loc = radon_sloc = radon_lloc = radon_comments = None

    # Halstead metrics: volume, difficulty, effort, time required to program, bugs cannot be computed on this type of code since its only function calls

    return (radon_complexity, radon_maintainability_index, radon_loc, radon_sloc, radon_lloc, radon_comments)