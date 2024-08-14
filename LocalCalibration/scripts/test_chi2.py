from scipy.stats import chi2
import numpy as np
df = 5
beta = 0.9
alpha = 1-beta
chi2_lower = chi2.ppf(alpha / 2, df)
chi2_upper = chi2.ppf(1 - alpha / 2, df)
print(chi2_lower)
print(chi2_upper)
sample_std = 0.3746
lower_bound_variance = (df * (sample_std)**2) / chi2_upper
upper_bound_variance = (df * (sample_std)**2) / chi2_lower
lower_bound_std = np.sqrt(lower_bound_variance)
upper_bound_std = np.sqrt(upper_bound_variance)
print(lower_bound_std)
print(upper_bound_std)
