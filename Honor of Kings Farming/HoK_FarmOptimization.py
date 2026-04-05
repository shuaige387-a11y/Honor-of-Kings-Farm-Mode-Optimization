import math
from pyomo.environ import (
    ConcreteModel, Var, Objective, Constraint,
    Binary, maximize, SolverFactory, value, NonNegativeReals, Set
)

# -----------------------------------------
# 1. Configuration
# -----------------------------------------
TOTAL_PLOTS = 11
HORIZON = 168  
WEEKEND_START = 120

plants_data = {
    'Wheat':         {'time': 1/120, 'cost': 0,   'revenue': 3},
    'Carrot':        {'time': 1/30,  'cost': 1,   'revenue': 10},
    'Tomato':        {'time': 1/12,  'cost': 2,   'revenue': 25},
    'Mushroom':      {'time': 1/3,   'cost': 11,  'revenue': 140},
    'Potato':        {'time': 1,     'cost': 35,  'revenue': 460},
    'Corn':          {'time': 8,     'cost': 266, 'revenue': 3420},
    'Strawberry':    {'time': 16,    'cost': 457, 'revenue': 5860},
    'Sunflower':     {'time': 1,     'cost': 36,  'revenue': 480},
    'Green Pepper':  {'time': 8,     'cost': 274, 'revenue': 3525},
    'Garlic':        {'time': 16,    'cost': 453, 'revenue': 6030},
}

# Define sleeping intervals (start_hour, end_hour)
# Users can define their sleep schedule accordingly
sleep_intervals = [(0, 7), (24, 31), (48, 55), (72, 79), (96, 103), (120, 127), (144, 151)]

def is_awake(t):
    for start, end in sleep_intervals:
        if start <= t < end:
            return False
    return True

# -----------------------------------------
# 2. Model Construction
# -----------------------------------------
model = ConcreteModel()

# Sets
model.P = Set(initialize=plants_data.keys())
model.T = Set(initialize=range(HORIZON))

# Variables
# x[p, t] = number of plots starting plant p at hour t
model.x = Var(model.P, model.T, domain=NonNegativeReals)

# -----------------------------------------
# 3. Objective: Maximize Profit
# -----------------------------------------
def obj_rule(model):
    total_profit = 0
    for p in model.P:
        duration = plants_data[p]['time']
        cost = plants_data[p]['cost']
        base_rev = plants_data[p]['revenue']
        
        for t in model.T:
            harvest_time = t + duration
            if harvest_time <= HORIZON:
                # Determine multiplier (Weekend bonus)
                multiplier = 2 if harvest_time >= WEEKEND_START else 1
                profit_per_unit = (base_rev * multiplier) - cost
                total_profit += model.x[p, t] * profit_per_unit
    return total_profit

model.profit = Objective(rule=obj_rule, sense=maximize)

# -----------------------------------------
# 4. Constraints
# -----------------------------------------

# Constraint 1: Land Capacity
# At any time t, the sum of all ongoing crops must not exceed TOTAL_PLOTS
def capacity_rule(model, t_check):
    ongoing_crops = 0
    for p in model.P:
        duration = plants_data[p]['time']
        # A plant started at 't' occupies the land until it's harvested AND picked up
        # We need to find the actual pickup time based on sleep schedule
        for t in model.T:
            harvest_time = t + duration
            
            # Find actual pickup time (first awake time >= harvest_time)
            pickup_time = harvest_time
            while pickup_time < HORIZON and not is_awake(math.floor(pickup_time)):
                pickup_time += 1
            
            # If t_check falls within [t, pickup_time), the plot is occupied
            if t <= t_check < pickup_time:
                ongoing_crops += model.x[p, t]
                
    return ongoing_crops <= TOTAL_PLOTS

model.cap_cons = Constraint(model.T, rule=capacity_rule)

# Constraint 2: Harvest Visibility
# Plants can only be harvested (and land freed) when player is awake
def awake_harvest_rule(model, p, t):
    duration = plants_data[p]['time']
    harvest_time = t + duration
    
    if harvest_time > HORIZON:
        return model.x[p, t] == 0
    
    # Optional: If you want to strictly forbid starting a crop that matures while sleeping
    # (Though the capacity rule already handles land blockage)
    return Constraint.Skip

model.harvest_cons = Constraint(model.P, model.T, rule=awake_harvest_rule)

# -----------------------------------------
# 5. Solve
# -----------------------------------------
solver = SolverFactory('appsi_highs') 
results = solver.solve(model)

# -----------------------------------------
# 6. Output Results
# -----------------------------------------
print(f"Maximum Weekly Profit: {value(model.profit):.2f}")
print("-" * 30)
for t in sorted(model.T):
    for p in model.P:
        val = value(model.x[p, t])
        if val > 0.01:
            print(f"Hour {t:3}: Start planting {val:4.1f} units of {p:12}")