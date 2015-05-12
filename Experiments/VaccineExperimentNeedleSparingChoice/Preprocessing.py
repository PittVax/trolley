# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

!out=dat/2005_2009_ver2_11_age_counts; echo 'count,age' > $out; \
    (for f in dat/2005_2009_ver2_11_synth_*.txt; do tail -n +2 $f | cut -d ',' -f 5; done;) \
        | sort -n | uniq -c | perl -p -e 's/^ +//; s/ +/,/g;' >> $out

# <codecell>

import pandas as pd
import numpy as np
import math
import intervals

# <codecell>

age_by_year=pd.read_csv('dat/2005_2009_ver2_11_age_counts')

# <codecell>

def interpolate_months(df):
    for i, r in df.iterrows():
        base_age_in_months = r['age'] * 12
        count = float(r['count']) / 12.0
        for remainder in range(12):
            age_months = base_age_in_months + remainder
            yield dict(age_years=round(float(age_months)/12.0, 4),
                       age_months=age_months, count=count)

age_by_month = pd.DataFrame(interpolate_months(age_by_year))
age_by_month.to_csv('dat/2005_2009_ver2_11_population_by_month.csv', index=False)

# <codecell>

age_intervals = [
    '[0.5, 2)',
    '[2,5)',
    '[5,9)',
    '[9,18)',
    '[18,50)',
    '[50,65)',
    '[65,106)'
]

def aggregate_intervals(age_intervals, age_by_month):
    for ivl in [intervals.FloatInterval(i) for i in age_intervals]:
        assert(ivl.upper_inc is False)
        assert(ivl.lower_inc is True)
        d = age_by_month
        yield dict(
            count = d[(d.age_years < ivl.upper) 
                & (d.age_years >= ivl.lower)]['count'].sum(),
            age_interval = ivl.__str__()
        )
    

# <codecell>

age_interval_counts = pd.DataFrame(aggregate_intervals(age_intervals, age_by_month))
age_interval_counts.to_csv('dat/2005_2009_ver2_11_age_interval_counts.csv', index=False)

# <codecell>


