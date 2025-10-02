import numpy as np
from scipy import stats
from statsmodels.stats.weightstats import ttest_ind
import pingouin as pg

def compare_groups(
    df, dependent_variable,
    group_column, group_x, group_y,
    prt=False, one_sided=False, direction="greater"
):
    """
    direction: 'greater', 'less', or 'two-sided'
        - 'greater': tests if mean of group_x > mean of group_y
        - 'less': tests if mean of group_x < mean of group_y
        - 'two-sided': regular two-sided test
    """
    x_group = df[df[group_column] == group_x][dependent_variable].dropna()
    y_group = df[df[group_column] == group_y][dependent_variable].dropna()

    mean_x = np.mean(x_group)
    mean_y = np.mean(y_group)
    median_x = np.median(x_group)
    median_y = np.median(y_group)
    std_x = np.std(x_group, ddof=1)
    std_y = np.std(y_group, ddof=1)
    var_x = np.var(x_group, ddof=1)
    var_y = np.var(y_group, ddof=1)
    n_x = len(x_group)
    n_y = len(y_group)
    nonzero_x = (x_group != 0).sum()
    nonzero_y = (y_group != 0).sum()

    # Use Fisher's exact test if both have very few nonzero
    if nonzero_x <= 5 and nonzero_y <= 5:
        from scipy.stats import fisher_exact
        zero_x = n_x - nonzero_x
        zero_y = n_y - nonzero_y
        table = [[nonzero_x, zero_x], [nonzero_y, zero_y]]

        alternative = {"greater": "greater", "less": "less", "two-sided": "two-sided"}.get(direction, "two-sided")
        oddsratio, p_value = fisher_exact(table, alternative=alternative)
        if prt:
            print(f"  Fisher's exact test table: {table}")
            print(f"  Odds ratio: {oddsratio:.4f}, p-value: {p_value:.4f} ({direction})")
        return {
            'test_statistic': oddsratio,
            'direction': direction,
            'one_sided': one_sided,
            'df': None,
            'p_value': p_value,
            'test_type': "Fisher's exact",
            'mean_x': None,
            'mean_y': None,
            'std_x': None,
            'std_y': None,
            'n_x': None,
            'n_y': None,
            'hits_x': nonzero_x,
            'hits_y': nonzero_y,
            'effect_size': oddsratio,
            'effect_size_type': "Odds ratio",
            'effect_size_CI': None
        }

    if prt:
        print(f"{dependent_variable}:")
        print(f"  {group_x}: n={n_x}, variance={var_x:.4f}")
        print(f"  {group_y}: n={n_y}, variance={var_y:.4f}")

    if shapiro_wilk(x_group, y_group, dependent_variable):
        if one_sided:
            t_stat, p_value, df_ = ttest_ind(x_group, y_group, usevar='unequal', alternative=direction)
        else:
            t_stat, p_value, df_ = ttest_ind(x_group, y_group, usevar='unequal')
            direction = "two-sided"
        effsize = pg.compute_effsize(x_group, y_group, eftype='cohen')
        ci = pg.compute_bootci(x_group, y_group, func='cohen', n_boot=1000, confidence=0.95)
        if prt:
            print(f"  T-statistic: {t_stat:.4f}, p-value: {p_value:.4f} ({direction})")
            print(f"  Effect size (Cohen's d): {effsize:.4f} (95% CI: [{ci[0]:.3f}, {ci[1]:.3f}])")
        return {
            'test_statistic': t_stat,
            'one_sided': one_sided,
            'direction': direction,
            'df': df_,
            'p_value': p_value,
            'test_type': 'T-test',
            'mean_x': mean_x,
            'mean_y': mean_y,
            'std_x': std_x,
            'std_y': std_y,
            'n_x': n_x,
            'n_y': n_y,
            'hits_x': nonzero_x,
            'hits_y': nonzero_y,
            'effect_size': effsize,
            'effect_size_type': "Cohen's d",
            'effect_size_CI': ci
        }
    else:
        # Mann-Whitney U (for non-normal distributions)
        alternative = direction if one_sided else "two-sided"
        result = pg.mwu(x=x_group, y=y_group, alternative=alternative)
        row = result.iloc[0]
        effsize = row['RBC']
        def rbc_stat(x, y):
            result = pg.mwu(x=x, y=y, alternative=alternative)
            return result.iloc[0]['RBC']
        ci = pg.compute_bootci(x_group, y_group, func=rbc_stat, n_boot=1000, confidence=0.95)
        if prt:
            print(f"  U-statistic: {row['U-val']:.4f}, z-value: {row['z-val']:.4f}, p-value: {row['p-val']:.4f}")
            print(f"  Effect size (RBC/r): {effsize:.4f} (95% CI: [{ci[0]:.3f}, {ci[1]:.3f}])")
        return {
            'test_statistic': row['U-val'],
            'direction': direction,
            'one_sided': one_sided,
            'df': None,
            'p_value': row['p-val'],
            'test_type': 'Mann-Whitney U',
            'mean_x': median_x,
            'mean_y': median_y,
            'std_x': std_x,
            'std_y': std_y,
            'n_x': n_x,
            'n_y': n_y,
            'hits_x': nonzero_x,
            'hits_y': nonzero_y,
            'effect_size': effsize,
            'effect_size_type': "RBC",
            'effect_size_CI': ci
        }

def shapiro_wilk(group_x, group_y, dependent_variable, prt=False):
    stat_x, p_x = stats.shapiro(group_x)
    stat_y, p_y = stats.shapiro(group_y)
    if prt:
        print(f"Normality test (Shapiro-Wilk) for {dependent_variable}:")
        print(f"  First group:  stat={stat_x:.4f}, p-value={p_x:.4f} {'(normal)' if p_x > 0.05 else '(not normal)'}")
        print(f"  Second group: stat={stat_y:.4f}, p-value={p_y:.4f} {'(normal)' if p_y > 0.05 else '(not normal)'}")
    if p_x > 0.05 and p_y > 0.05:
        if prt:
            print("Both distributions are normal, so we can run a t-test.")
        return True
    else:
        if prt:
            print("At least one of the distributions is not normal, so we cannot run a t-test.")
        return False