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
    std_female = np.std(female, ddof=1)
    std_male = np.std(male, ddof=1)
    female_var = np.var(female, ddof=1)
    male_var = np.var(male, ddof=1)
    n_female = len(female)
    n_male = len(male)
    nonzero_female = (female != 0).sum()
    nonzero_male = (male != 0).sum()

    if prt:
        print(f"{dependent_variable}:")
        print(f"  Female: n={n_female}, variance={female_var:.4f}")
        print(f"  Male:   n={n_male}, variance={male_var:.4f}")

    if shapiro_wilk(female, male, dependent_variable):
        if one_sided:
            t_stat, p_value, df = ttest_ind(male, female, usevar='unequal', alternative=direction)
        else:
            t_stat, p_value, df = ttest_ind(male, female, usevar='unequal')  # default 'two-sided'
            direction = "two-sided"
        if prt:
            print(f"  T-statistic: {t_stat:.4f}, p-value: {p_value:.4f} ({direction})")

        return {
            'test_statistic': t_stat,
            'df': df,
            'p_value': p_value,
            'test_type': 'T-test',
            'mean_female': mean_female,
            'mean_male': mean_male,
            'std_female': std_female,
            'std_male': std_male,
            'n_female': n_female,
            'n_male': n_male,
            'hits_female': nonzero_female,
            'hits_male': nonzero_male,
        }

    else:
        alternative = direction if one_sided else "two-sided"
        stat, p_value = stats.mannwhitneyu(male, female, alternative=alternative)
        if prt:
            print(f"Mann-Whitney U test: stat={stat:.4f}, p-value={p_value:.4f} ({alternative})")
        return {
            'test_statistic': stat,
            'df': None,
            'p_value': p_value,
            'test_type': 'U-test',
            'mean_female': mean_female,
            'mean_male': mean_male,
            'std_female': std_female,
            'std_male': std_male,
            'n_female': n_female,
            'n_male': n_male,
            'hits_female': nonzero_female,
            'hits_male': nonzero_male,
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
