import numpy as np
from scipy import stats
from statsmodels.stats.weightstats import ttest_ind



def run_t_test_on_gender(df, dependent_variable, prt=False):
    female = df[df['gender'] == 'Woman (cisgender)'][dependent_variable].dropna()
    male = df[df['gender'] == 'Man (cisgender)'][dependent_variable].dropna()

    t_stat, p_value = stats.ttest_ind(male, female, equal_var=False)

    female_var = np.var(female, ddof=1)
    male_var = np.var(male, ddof=1)
    n_female = len(female)
    n_male = len(male)

    if(prt):
        print(f"{dependent_variable}:")
        print(f"  T-statistic: {t_stat:.4f}, p-value: {p_value:.4f}")
        print(f"  Female: n={n_female}, variance={female_var:.4f}")
        print(f"  Male:   n={n_male}, variance={male_var:.4f}")


import pingouin as pg

def compare_genders(df, dependent_variable, prt=False, one_sided=False, direction="greater"):
    """
    direction: 'greater', 'less', or 'two-sided', passed to scipy.stats functions as 'alternative'
        - 'greater': tests if mean of male > mean of female
        - 'less': tests if mean of male < mean of female
        - 'two-sided': regular two-sided test

    one_sided controls if test is one-sided (True) or two-sided (False).
    If one_sided is True, you must specify 'greater' or 'less' in direction.
    """
    female = df[df['gender'] == 'Woman (cisgender)'][dependent_variable].dropna()
    male = df[df['gender'] == 'Man (cisgender)'][dependent_variable].dropna()

    mean_female = np.mean(female)
    mean_male = np.mean(male)
    median_female = np.median(female)
    median_male = np.median(male)
    std_female = np.std(female, ddof=1)
    std_male = np.std(male, ddof=1)
    female_var = np.var(female, ddof=1)
    male_var = np.var(male, ddof=1)
    n_female = len(female)
    n_male = len(male)
    nonzero_female = (female != 0).sum()
    nonzero_male = (male != 0).sum()

    # Use Fisher's exact test if either group is very small
    if nonzero_female <= 5 and nonzero_male <= 5:
        from scipy.stats import fisher_exact

        # Create a 2x2 table: rows = gender, columns = nonzero/zero
        zero_female = n_female - nonzero_female
        zero_male = n_male - nonzero_male
        table = [[nonzero_female, zero_female], [nonzero_male, zero_male]]

        # Set alternative
        alt_map = {"greater": "greater", "less": "less", "two-sided": "two-sided"}
        alternative = alt_map.get(direction, "two-sided")
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
            'm_female': None,
            'm_male': None,
            'std_female': None,
            'std_male': None,
            'n_female': None,
            'n_male': None,
            'hits_female': nonzero_female,
            'hits_male': nonzero_male,
            'effect_size': oddsratio,
            'effect_size_type': "Odds ratio",
            'effect_size_CI': None
        }

    if prt:
        print(f"{dependent_variable}:")
        print(f"  Female: n={n_female}, variance={female_var:.4f}")
        print(f"  Male:   n={n_male}, variance={male_var:.4f}")

    if shapiro_wilk(female, male, dependent_variable):
        if one_sided:
            t_stat, p_value, df_ = ttest_ind(male, female, usevar='unequal', alternative=direction)
        else:
            t_stat, p_value, df_ = ttest_ind(male, female, usevar='unequal')
            direction = "two-sided"
        # Compute Cohen's d
        effsize = pg.compute_effsize(male, female, eftype='cohen')
        ci = pg.compute_bootci(male, female, func='cohen', n_boot=1000, confidence=0.95)

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
            'm_female': mean_female,
            'm_male': mean_male,
            'std_female': std_female,
            'std_male': std_male,
            'n_female': n_female,
            'n_male': n_male,
            'hits_female': nonzero_female,
            'hits_male': nonzero_male,
            'effect_size': effsize,
            'effect_size_type': 'Cohen\'s d',
            'effect_size_CI': ci
        }

    else:
        direction = "less" if direction == "smaller" else "greater"
        alternative = direction if one_sided else "two-sided"
        result = pg.mwu(x=male, y=female, alternative=alternative)

        # result is a one-row DataFrame; extract the values
        row = result.iloc[0]
        effsize = row['RBC']

        # define custom function for ci bootstrapping
        def rbc_stat(x, y):
            result = pg.mwu(x=x, y=y, alternative=alternative)
            row = result.iloc[0]
            return row['RBC']

        #determine cis
        ci = pg.compute_bootci(male, female, func=rbc_stat, n_boot=1000, confidence=0.95)

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
            'm_female': median_female,
            'm_male': median_male,
            'std_female': std_female,
            'std_male': std_male,
            'n_female': n_female,
            'n_male': n_male,
            'hits_female': nonzero_female,
            'hits_male': nonzero_male,
            'effect_size': effsize,
            'effect_size_type': "RBC",
            'effect_size_CI': ci     # [lower, upper]
        }

def shapiro_wilk(female, male, dependent_variable, prt=False):
    stat_female, p_female = stats.shapiro(female)
    stat_male, p_male = stats.shapiro(male)

    if (prt):
        print(f"Normality test (Shapiro-Wilk) for {dependent_variable}:")
        print(f"  Female: stat={stat_female:.4f}, p-value={p_female:.4f} " +
              ("(normal)" if p_female > 0.05 else "(not normal)"))
        print(f"  Male:   stat={stat_male:.4f}, p-value={p_male:.4f} " +
              ("(normal)" if p_male > 0.05 else "(not normal)"))

    if p_female > 0.05 and p_male > 0.05:
        if(prt):
            print("Both distributions are normal, so we can run a t-test.")
        return True
    else:
        if (prt):
            print("At least one of the distributions is not normal, so we cannot run a t-test.")
        return False
