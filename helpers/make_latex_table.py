import pandas as pd
import numpy as np

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

def bold_if_effsize(x, decimals=3):
    if pd.isnull(x):
        return "-"
    try:
        v = float(x)
    except Exception:
        return str(x)
    s = f"{v:.{decimals}f}"
    if abs(v) > 0.5:
        return f"\\textbf{{{s}}}"
    else:
        return s



def create_latex_table_from_stats(df: pd.DataFrame, file_name: str):
    # Helper columns
    def stat_row(row):
        if row["test type"] == "T-test":
            df_str = format_number(row["df"])
            t_str = format_number(row["stat_value"], 2)
            p_str = format_number(row["p_value"])
            s = f"$t({df_str}) = {t_str}$, $p = {p_str}$"
        else:
            u_str = row["stat_value"]
            p_str = format_number(row["p_value"])
            s = f"$U = {u_str}$, $p = {p_str}$"
        # Add superscript 1 if direction is not NaN, empty or blank
        one_sided = row.get("one_sided", None)
        if one_sided:
            s = s[:-1] + r"^{1}$"
        return s


    # Prepare columns
    out = pd.DataFrame()
    out["Subject"] = df["word"].apply(lambda x: str(x) if pd.notnull(x) else "-")
    out["stat"] = df.apply(stat_row, axis=1)
    out["corr. p"] = df["corrected p_value"].apply(bold_if_p)
    out["M(SD) m"] = df.apply(
        lambda r: f"{format_number(r['mean_m'])} ({format_number(r['std_m'])})", axis=1
    )
    out["M(SD) f"] = df.apply(
        lambda r: f"{format_number(r['mean_f'])} ({format_number(r['std_f'])})", axis=1
    )
    out["Hits (m;f)"] = df.apply(
        lambda r: f"{r['n_hits_m']}; {r['n_hits_f']}", axis=1
    )
    out["eff. size"] = df["effsize"].apply(bold_if_effsize)

    # Format to LaTeX
    latex_body = out.to_latex(index=False, na_rep="-", escape=False, header=True, column_format='lllllcrl')

    # Bold headers manually for latex:
    headers = [
        "subject", "statistic", "$p_{corrected}$", "$M_m$($SD_m$)", "$M_f$($SD_f$)",
        "Hits (m;f)", "$d$/$r$"
    ]
    bold_headers = " & ".join([f"\\textbf{{{h}}}" for h in headers]) + " \\\\"
    lines = latex_body.splitlines()
    # Replace header line with bolded one
    for i, line in enumerate(lines):
        if line.strip().startswith("Subject"):
            lines[i] = bold_headers
            break

    # Assemble table with caption and superscript note
    caption = (
        """\\caption{Significant corrected effects ($p < 0.05$) and noticeable effect sizes ($> 0.5$) are marked in bold. Effect sizes (Cohen's d for t-test and Rank-Biserial Correlation for U-Test) are reported for completeness; 
        however, when group data contain many zeros, effect size estimates may be unstable and should be interpreted with caution. The superscript ¹ denotes a one-sided t-test.}\n"""
    )

    font_size = """\\scriptsize \n\\setlength{\\tabcolsep}{3pt} \n"""
    latex_table = "\\begin{table}\n" + font_size + "\n".join(lines) + caption + "\n\\end{table}"

    with open(file_name, "w") as f:
        f.write(latex_table)