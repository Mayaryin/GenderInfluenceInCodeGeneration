import numpy as np
from scipy import stats


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


def compare_genders(df, dependent_variable, prt=False):
    female = df[df['gender'] == 'Woman (cisgender)'][dependent_variable].dropna()
    male = df[df['gender'] == 'Man (cisgender)'][dependent_variable].dropna()

    nonzero_female = (female != 0).sum()
    nonzero_male = (male != 0).sum()

    female_var = np.var(female, ddof=1)
    male_var = np.var(male, ddof=1)
    n_female = len(female)
    n_male = len(male)

    if (prt):
        print(f"{dependent_variable}:")
        print(f"  Female: n={n_female}, variance={female_var:.4f}")
        print(f"  Male:   n={n_male}, variance={male_var:.4f}")

    p_value = 0
    if shapiro_wilk(female, male, dependent_variable):
        t_stat, p_value = stats.ttest_ind(male, female, equal_var=False)
        if (prt):
            print(f"  T-statistic: {t_stat:.4f}, p-value: {p_value:.4f}")
        return  t_stat, p_value, 'T-test', female_var, male_var, nonzero_female, nonzero_male
    else:
        stat, p_value = stats.mannwhitneyu(male, female, alternative='two-sided')
        if (prt):
            print(f"Mann-Whitney U test: stat={stat:.4f}, p-value={p_value:.4f}")
        return  stat, p_value, 'U-test', female_var, male_var, nonzero_female, nonzero_male


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
