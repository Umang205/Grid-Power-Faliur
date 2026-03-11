import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Create sample data
np.random.seed(42)
n_samples = 1000

# Generate dates
base_date = datetime(2023, 1, 1)
start_times = [base_date + timedelta(hours=x) for x in range(n_samples)]
durations = np.random.randint(1, 24, n_samples)
end_times = [start + timedelta(hours=dur) for start, dur in zip(start_times, durations)]

# Create areas and power plants
areas = ['North Region', 'South Region', 'East Region', 'West Region']
power_plants = ['Plant A', 'Plant B', 'Plant C', 'Plant D']
reasons = ['Equipment failure', 'Maintenance', 'Weather rainstorm', 'Overload', 'Animal intervention']

data = {
    'start_time': start_times,
    'end_time': end_times,
    'area': np.random.choice(areas, n_samples),
    'power_plant': np.random.choice(power_plants, n_samples),
    'reason': np.random.choice(reasons, n_samples)
}

# Create DataFrame and save to Excel
df = pd.DataFrame(data)
df.to_excel('outage_data.xlsx', index=False)
print("Sample dataset created successfully!") 