import pandas as pd
import numpy as np

def create_latex_tables(df: pd.DataFrame, stats_file: str, effectsize_file: str):
    def format_number(x, decimals=3):
        if pd.isnull(x):
            return "-"
        if isinstance(x, (int, float, np.floating)):
            return f"{x:.{decimals}f}"
        return str(x)

    def bold_if_p(x, decimals=3):
        if pd.isnull(x):
            return "-"
        try:
            v = float(x)
        except Exception:
            return str(x)
        s = f"{v:.{decimals}f}"
        if v < 0.05:
            return f"\\textbf{{{s}}}"
        else:
            return s

    def bold_if_effsize(x, decimals=3, test_type=None):
        if pd.isnull(x):
            return "-"
        try:
            v = float(x)
        except Exception:
            return str(x)
        s = f"{v:.{decimals}f}"
        # Do not bold if test type is Fisher's exact
        if test_type == "Fisher's exact":
            return s
        if abs(v) > 0.5:
            return f"\\textbf{{{s}}}"
        else:
            return s

    # -------- Table 1: Statistics Summary --------
    def stat_row(row):
        test_type = row.get("test type", "")
        if test_type == "T-test":
            df_str = format_number(row.get("df"))
            t_str = format_number(row.get("stat_value"), 2)
            p_str = format_number(row.get("p_value"))
            s = f"$t({df_str}) = {t_str}$, $p = {p_str}$"
        elif test_type == "Fisher's exact":
            p_str = bold_if_p(row.get("p_value"))
            s = f"Fisher, $p = {p_str}$"
        else:
            u_str = row.get("stat_value", "-")
            p_str = format_number(row.get("p_value"))
            s = f"$U = {u_str}$, $p = {p_str}$"
        one_sided = row.get("one_sided", None)
        if one_sided and test_type == "T-test":
            s = s[:-1] + r"^{1}$"
        return s

    stats_summary = pd.DataFrame()
    stats_summary["Subject"] = df["word"].apply(lambda x: str(x) if pd.notnull(x) else "-")
    stats_summary["stat"] = df.apply(stat_row, axis=1)
    stats_summary["$p_{corr}$"] = df["corrected p_value"].apply(bold_if_p)
    stats_summary["Effect Size"] = df.apply(lambda r: bold_if_effsize(r.get("effsize"), test_type=r.get("test type")), axis=1)
    stats_summary["CI (95\\%)"] = df["ci"].apply(
        lambda arr: (
            f"[{arr[0]:.3f}, {arr[1]:.3f}]"
            if isinstance(arr, (list, tuple, np.ndarray)) and len(arr) == 2
            else "-"
        )
    )

    stats_summary_latex = stats_summary.to_latex(
        index=False, na_rep="-", escape=False, header=True, column_format='llllc'
    )
    stats_summary_headers = [
        "Subject", "stat", "$p_{corr}$", "Effect Size", "CI (95\\%)"
    ]
    stats_summary_header_row = " & ".join(stats_summary_headers) + " \\\\"
    summary_lines = stats_summary_latex.splitlines()
    for i, line in enumerate(summary_lines):
        if line.strip().startswith("Subject"):
            summary_lines[i] = stats_summary_header_row
            break
    summary_caption = (
        "\\caption{Comparisons of XXX across genders. Group descriptive statistics and hits are in Table \\ref{tab:} in Appendix \\ref{app:prompt_analysis}}\n"
    )
    font_size = "\\small \n\\setlength{\\tabcolsep}{3pt}\n"
    stats_table = (
            "\\begin{table}[H]\n"
            + "\\centering\n"
            + font_size
            + "\n".join(summary_lines)
            + "\n"
            + summary_caption
            + "\\end{table}\n"
    )
    with open(stats_file, "w") as f:
        f.write(stats_table)

    # -------- Table 2: Means & Hits --------
    means_hits = pd.DataFrame()
    means_hits["Subject"] = df["word"].apply(lambda x: str(x) if pd.notnull(x) else "-")
    means_hits["$M_m$($SD_m$)"] = df.apply(
        lambda r: f"{format_number(r.get('mean_m'))} ({format_number(r.get('std_m'))})", axis=1
    )
    means_hits["$M_f$($SD_f$)"] = df.apply(
        lambda r: f"{format_number(r.get('mean_f'))} ({format_number(r.get('std_f'))})", axis=1
    )
    means_hits["Hits (m;f)"] = df.apply(
        lambda r: f"{r.get('n_hits_m', '-')}; {r.get('n_hits_f', '-')}", axis=1
    )

    means_hits_latex = means_hits.to_latex(
        index=False, na_rep="-", escape=False, header=True, column_format='lllc'
    )
    means_hits_headers = [
        "Subject", "$M_m$($SD_m$)", "$M_f$($SD_f$)", "Hits (m;f)"
    ]
    means_hits_header_row = " & ".join(means_hits_headers) + " \\\\"
    hits_lines = means_hits_latex.splitlines()
    for i, line in enumerate(hits_lines):
        if line.strip().startswith("Subject"):
            hits_lines[i] = means_hits_header_row
            break
    hits_caption = "\\caption{Means (and standard deviations) for men and women, and number of hits for each group.}\n"
    means_hits_table = (
            "\\begin{table}[H]\n"
            + "\\centering\n"
            + font_size
            + "\n".join(hits_lines)
            + "\n"
            + hits_caption
            + "\\end{table}\n"
    )
    with open(effectsize_file, "w") as f:
        f.write(means_hits_table)