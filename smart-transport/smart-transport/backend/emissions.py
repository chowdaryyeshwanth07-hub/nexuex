"""
Emissions and Environmental Impact Calculation Module
Computes estimated CO2 emissions (in kg) and environmental savings
for private vehicles vs public/multimodal transit modes.
"""

# Emission factors in kg CO2 per passenger-kilometer (average Indian urban transport benchmarks)
EMISSION_FACTORS = {
    'car': 0.160,       # 160g CO2/km (Single occupancy petrol/diesel car)
    'cab': 0.145,       # 145g CO2/km (Ride-share cab)
    'bike': 0.065,      # 65g CO2/km (Motorcycle/scooter)
    'bus': 0.038,       # 38g CO2/passenger-km (Average occupancy urban public bus)
    'metro': 0.018,     # 18g CO2/passenger-km (Grid powered electric mass rapid transit)
    'bus_metro': 0.024, # 24g CO2/passenger-km (Combined feeder bus + metro)
    'walk': 0.000,      # Zero emission
    'cycle': 0.000      # Zero emission
}

# Average operating cost factors in INR per km
COST_FACTORS = {
    'car': 11.5,        # Fuel + maintenance + tolls (~₹11.5/km) + parking added separately
    'bike': 3.5,        # Fuel + maintenance
    'bus': 1.5,         # Flat/tiered public fare rate ~ ₹20-₹35 average
    'metro': 2.2,       # Metro ticket rate ~ ₹20-₹40 average
    'bus_metro': 1.8,   # Combined fare
    'walk': 0.0
}

def calculate_emissions(distance_km, mode):
    """
    Calculate total CO2 emissions in kg for a given distance and mode.
    """
    mode_key = mode.lower().replace(' ', '_').replace('+', '_')
    factor = EMISSION_FACTORS.get(mode_key, EMISSION_FACTORS.get('car', 0.160))
    emissions = round(distance_km * factor, 2)
    return emissions

def calculate_savings(distance_km, chosen_mode_emissions, chosen_mode_cost, car_cost_base=None):
    """
    Calculate CO2 and money savings compared to driving a private car.
    """
    car_emissions = calculate_emissions(distance_km, 'car')
    co2_saved = round(max(0.0, car_emissions - chosen_mode_emissions), 2)
    
    if car_cost_base is None:
        # Default car cost: distance * per_km + ₹40 parking fee
        car_cost_base = (distance_km * COST_FACTORS['car']) + 40.0
    
    money_saved = round(max(0.0, car_cost_base - chosen_mode_cost), 1)
    
    # Trees equivalent offset: ~21.7 kg CO2 absorbed per mature tree per year
    trees_equivalent = round((co2_saved * 365) / 21.7, 1)

    return {
        'car_baseline_emissions_kg': car_emissions,
        'car_baseline_cost_inr': round(car_cost_base, 1),
        'co2_saved_kg': co2_saved,
        'money_saved_inr': money_saved,
        'co2_reduction_percentage': round(((co2_saved / max(0.01, car_emissions)) * 100), 1),
        'trees_offset_per_year_equiv': trees_equivalent
    }
