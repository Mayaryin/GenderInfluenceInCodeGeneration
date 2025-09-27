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

    # ---------- Statistics Table ----------
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

    stats_out = pd.DataFrame()
    stats_out["Subject"] = df["word"].apply(lambda x: str(x) if pd.notnull(x) else "-")
    stats_out["stat"] = df.apply(stat_row, axis=1)
    stats_out["corr. p"] = df["corrected p_value"].apply(bold_if_p)
    stats_out["M(SD) m"] = df.apply(
        lambda r: f"{format_number(r.get('mean_m'))} ({format_number(r.get('std_m'))})", axis=1
    )
    stats_out["M(SD) f"] = df.apply(
        lambda r: f"{format_number(r.get('mean_f'))} ({format_number(r.get('std_f'))})", axis=1
    )
    stats_out["Hits (m;f)"] = df.apply(
        lambda r: f"{r.get('n_hits_m', '-')}; {r.get('n_hits_f', '-')}", axis=1
    )
    # Pass test type to the bold effect size function
    stats_out["eff. size"] = df.apply(lambda r: bold_if_effsize(r.get("effsize"), test_type=r.get("test type")), axis=1)

    stats_latex = stats_out.to_latex(index=False, na_rep="-", escape=False, header=True, column_format='lllllcrl')
    stats_headers = [
        "subject", "statistic", "$p_{corr}$", "$M_m$($SD_m$)", "$M_f$($SD_f$)",
        "Hits (m;f)", "$d$/$r$/OR"
    ]
    stats_bold_headers = " & ".join([f"\\textbf{{{h}}}" for h in stats_headers]) + " \\\\"
    lines = stats_latex.splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith("Subject"):
            lines[i] = stats_bold_headers
            break
    stats_caption = (
        "\\caption{Significant corrected effects ($p < 0.05$). The superscript ¹ denotes a one-sided t-test.}\n"
    )
    font_size = "\\scriptsize \n\\setlength{\\tabcolsep}{3pt} \n"
    stats_table = "\\begin{table}\n" + font_size + "\n".join(lines) + stats_caption + "\n\\end{table}"

    with open(stats_file, "w") as f:
        f.write(stats_table)

    # ---------- Effect Size Table ----------
    eff_out = pd.DataFrame()
    eff_out["Subject"] = df["word"].apply(lambda x: str(x) if pd.notnull(x) else "-")
    # Pass test type to bold_if_effsize, so Fisher's exact never gets bold
    eff_out["eff size"] = df.apply(lambda r: bold_if_effsize(r.get("effsize"), test_type=r.get("test type")), axis=1)
    eff_out["CI (95\\%)"] = df["ci"].apply(
        lambda arr: (
            f"[{arr[0]:.3f}, {arr[1]:.3f}]"
            if isinstance(arr, (list, tuple, np.ndarray)) and len(arr) == 2
            else "-"
        )
    )

    eff_latex = eff_out.to_latex(index=False, na_rep="-", escape=False, header=True, column_format='lll')
    eff_headers = ["subject", "eff. size", "CI (95\\%)"]
    eff_bold_headers = " & ".join([f"\\textbf{{{h}}}" for h in eff_headers]) + " \\\\"
    eff_lines = eff_latex.splitlines()
    for i, line in enumerate(eff_lines):
        if line.strip().startswith("Subject"):
            eff_lines[i] = eff_bold_headers
            break
    eff_caption = (
        "\\caption{Effect sizes and their bootstrapped 95\\% confidence intervals. "
        "Noticeable effect sizes ($> 0.5$) are marked in bold}\n"
    )
    eff_table = "\\begin{table}\n" + font_size + "\n".join(eff_lines) + eff_caption + "\n\\end{table}"

    with open(effectsize_file, "w") as f:
        f.write(eff_table)