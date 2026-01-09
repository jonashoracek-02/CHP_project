import pandas as pd
import numpy as np

# --- Input Data ---
# Masses in tons
mass_s1_ar = 800
mass_s2_ar = 400
mass_s3_ar = 1000

# Composition Data (from samples.csv / Pretreatment_computations.py)
# Moisture is in % wt, converted to fraction 0-1
# LHV_dry is in MJ/kg

samples = {
    "Sample1": {
        "moisture_ar": 9.650497 / 100,
        "LHV_dry": 16.74396,
        "Ash_dry": 13.21269,  # Added for completeness if needed
    },
    "Sample2": {
        "moisture_ar": 74.20339 / 100,
        "LHV_dry": 19.99935,
        "Ash_dry": 11.30681,
    },
    "Sample3": {
        "moisture_ar": 85.60128 / 100,
        "LHV_dry": 17.39563,
        "Ash_dry": 9.777355,
    },
}

target_moisture = 0.60  # 60% for Sample 2 and 3

# --- Calculations ---


def perform_drying(mass_ar, moist_ar, target_moist):
    """
    Calculates mass after drying to target moisture.
    If current moisture <= target, no drying occurs.
    """
    if moist_ar <= target_moist:
        return mass_ar, moist_ar

    mass_solid = mass_ar * (1 - moist_ar)
    # mass_final = mass_solid + mass_water_final
    # mass_water_final / mass_final = target_moist
    # mass_water_final = target_moist * mass_final
    # mass_final = mass_solid + target_moist * mass_final
    # mass_final * (1 - target_moist) = mass_solid
    mass_final = mass_solid / (1 - target_moist)
    return mass_final, target_moist


# 1. Process Sample 2
mass_s2_final, moist_s2_final = perform_drying(
    mass_s2_ar, samples["Sample2"]["moisture_ar"], target_moisture
)

# 2. Process Sample 3
mass_s3_final, moist_s3_final = perform_drying(
    mass_s3_ar, samples["Sample3"]["moisture_ar"], target_moisture
)

# 3. Process Sample 1 (No drying)
mass_s1_final = mass_s1_ar
moist_s1_final = samples["Sample1"]["moisture_ar"]

# --- Mixing ---

# Calculate Dry Masses (Solids)
dry_s1 = mass_s1_final * (1 - moist_s1_final)
dry_s2 = mass_s2_final * (1 - moist_s2_final)
dry_s3 = mass_s3_final * (1 - moist_s3_final)

total_dry_mass = dry_s1 + dry_s2 + dry_s3
total_wet_mass = mass_s1_final + mass_s2_final + mass_s3_final
total_water_mass = total_wet_mass - total_dry_mass

final_mixture_moisture = total_water_mass / total_wet_mass

# Calculate Weighted Average properties on DRY basis
# LHV_dry_mix = sum(mi_dry * LHV_dry_i) / sum(mi_dry)
lhv_dry_mix = (
    dry_s1 * samples["Sample1"]["LHV_dry"]
    + dry_s2 * samples["Sample2"]["LHV_dry"]
    + dry_s3 * samples["Sample3"]["LHV_dry"]
) / total_dry_mass

ash_dry_mix = (
    dry_s1 * samples["Sample1"]["Ash_dry"]
    + dry_s2 * samples["Sample2"]["Ash_dry"]
    + dry_s3 * samples["Sample3"]["Ash_dry"]
) / total_dry_mass


# Convert LHV Dry Mix to LHV AR Mix
# Formula: LHV_ar = LHV_dry * (1 - w) - 2.442 * w
# w is moisture fraction
lhv_ar_mix = lhv_dry_mix * (1 - final_mixture_moisture) - 2.442 * final_mixture_moisture

# --- Output Results ---

print("----------------------------------------------------------------")
print(
    f"{'Stream':<15} | {'Mass (ton)':<15} | {'Moisture (%)':<15} | {'LHV (MJ/kg)':<15}"
)
print("----------------------------------------------------------------")
print(
    f"{'Sample 1 (AR)':<15} | {mass_s1_ar:<15.2f} | {samples['Sample1']['moisture_ar']*100:<15.2f} | {samples['Sample1']['LHV_dry'] * (1-samples['Sample1']['moisture_ar']) - 2.442*samples['Sample1']['moisture_ar']:<15.2f}"
)
print(
    f"{'Sample 2 (Dry)':<15} | {mass_s2_final:<15.2f} | {moist_s2_final*100:<15.2f} | -"
)
print(
    f"{'Sample 3 (Dry)':<15} | {mass_s3_final:<15.2f} | {moist_s3_final*100:<15.2f} | -"
)
print("----------------------------------------------------------------")
print(" FINAL MIXTURE ")
print("----------------------------------------------------------------")
print(f"Total Mass:      {total_wet_mass:.2f} tons")
print(f"Moisture:        {final_mixture_moisture*100:.2f} %")
print(f"LHV (AR):        {lhv_ar_mix:.2f} MJ/kg")
print(f"LHV (Dry):       {lhv_dry_mix:.2f} MJ/kg")
print(f"Ash (Dry):       {ash_dry_mix:.2f} %")
print("----------------------------------------------------------------")

# --- Export to CSV ---
results_data = {
    "Stream": ["Sample 1 (AR)", "Sample 2 (Dry)", "Sample 3 (Dry)", "FINAL MIXTURE"],
    "Mass (ton)": [mass_s1_ar, mass_s2_final, mass_s3_final, total_wet_mass],
    "Moisture (%)": [
        samples["Sample1"]["moisture_ar"] * 100,
        moist_s2_final * 100,
        moist_s3_final * 100,
        final_mixture_moisture * 100,
    ],
    "LHV (ar) (MJ/kg)": [
        samples["Sample1"]["LHV_dry"] * (1 - samples["Sample1"]["moisture_ar"])
        - 2.442 * samples["Sample1"]["moisture_ar"],
        "-",
        "-",
        lhv_ar_mix,
    ],
    "LHV (dry) (MJ/kg)": [
        samples["Sample1"]["LHV_dry"],
        samples["Sample2"]["LHV_dry"],
        samples["Sample3"]["LHV_dry"],
        lhv_dry_mix,
    ],
    "Ash (dry) (%)": [
        samples["Sample1"]["Ash_dry"],
        samples["Sample2"]["Ash_dry"],
        samples["Sample3"]["Ash_dry"],
        ash_dry_mix,
    ],
}

df_results = pd.DataFrame(results_data)
csv_filename = "mixture_results.csv"
df_results.to_csv(csv_filename, index=False)
print(f"\nResults saved to {csv_filename}")
