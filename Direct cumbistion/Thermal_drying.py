import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import cantera as ct

# --- Input Data ---
dir_path = os.path.dirname(os.path.abspath(__file__))
input_csv = os.path.join(dir_path, "mixture_results.csv")

try:
    data = pd.read_csv(input_csv)
    # Clean whitespace from headers and string columns
    data.columns = data.columns.str.strip()
    data["Stream"] = data["Stream"].astype(str).str.strip()
except FileNotFoundError:
    print(f"Error: {input_csv} not found. Please run calculate_mixture.py first.")
    exit()

# Get FINAL MIXTURE data
final_mixture_row = data[data["Stream"] == "FINAL MIXTURE"].iloc[0]
mass_total_initial = float(final_mixture_row["Mass (ton)"]) * 1000  # Convert tons to kg
moisture_initial_pct = float(final_mixture_row["Moisture (%)"])
moisture_initial = moisture_initial_pct / 100.0

# Get LHV Dry from data if available, otherwise calculate or assume
lhv_dry_initial = float(final_mixture_row["LHV (dry) (MJ/kg)"])

print(
    f"Initial State - Mass: {mass_total_initial/1000:.2f} tons, Moisture: {moisture_initial_pct:.2f}%, LHV (dry): {lhv_dry_initial:.2f} MJ/kg"
)


delta_h_evap = 2.5735 * 1e6


# --- Calculations ---
# Mass of dry solids (constant)
mass_solid = mass_total_initial * (1 - moisture_initial)

target_moistures_pct = np.linspace(0, 25, 16)  # 10% to 25% (integers)
results_list = []

print("\n--- Sensitivity Analysis ---")
print(
    f"{'Target Moisture (%)':<20} | {'Water Removed (ton)':<20} | {'Energy (GJ)':<15} | {'Energy (MWh)':<15} | {'LHV (ar) (MJ/kg)':<20} | {'Fuel Potential (MWh)':<22}"
)
print("-" * 125)

for target_pct in target_moistures_pct:
    target_moist = target_pct / 100.0

    # Mass balance: m_solid / (1 - w_target) = m_total_final
    mass_total_final = mass_solid / (1 - target_moist)
    mass_water_final = mass_total_final - mass_solid
    mass_water_initial = mass_total_initial - mass_solid  # Or just calculate once

    water_removed_kg = mass_water_initial - mass_water_final

    # Energy Calculation
    # Q = m_evap * delta_h
    energy_joules = water_removed_kg * delta_h_evap
    energy_gj = energy_joules / 1e9
    energy_mwh = energy_joules / 3.6e9

    # LHV Calculation
    # Formula: LHV_ar = LHV_dry * (1 - w) - 2.442 * w
    lhv_ar = lhv_dry_initial * (1 - target_moist) - 2.442 * target_moist

    # Fuel Potential Power (Total Energy in MWh)
    # E_fuel (MJ) = Mass (kg) * LHV_ar (MJ/kg)
    fuel_energy_mj = mass_total_final * lhv_ar
    fuel_energy_mwh = fuel_energy_mj / 3600  # 1 MWh = 3600 MJ

    results_list.append(
        {
            "Target Moisture (%)": target_pct,
            "Final Mass (ton)": mass_total_final / 1000,
            "Water Removed (ton)": water_removed_kg / 1000,
            "Energy Required (GJ)": energy_gj,
            "Energy Required (MWh)": energy_mwh,
            "LHV (ar) (MJ/kg)": lhv_ar,
            "Fuel Potential (MWh)": fuel_energy_mwh,
        }
    )

    print(
        f"{target_pct:<20.1f} | {water_removed_kg/1000:<20.2f} | {energy_gj:<15.2f} | {energy_mwh:<15.2f} | {lhv_ar:<20.2f} | {fuel_energy_mwh:<22.2f}"
    )

# --- Export Results ---
df_sensitivity = pd.DataFrame(results_list)
output_csv = os.path.join(dir_path, "drying_sensitivity_results.csv")
df_sensitivity.to_csv(output_csv, index=False)
print(f"\nDetailed results saved to {output_csv}")

# --- Plotting ---
fig, ax1 = plt.subplots(figsize=(12, 7))

# Plot Drying Energy (Left Axis)
color = "tab:red"
ax1.set_xlabel("Target Moisture Content (%)")
ax1.set_ylabel("Drying Energy Required (MWh)", color=color)
ax1.plot(
    df_sensitivity["Target Moisture (%)"],
    df_sensitivity["Energy Required (MWh)"],
    marker="o",
    linestyle="-",
    color=color,
    label="Drying Energy",
)
ax1.tick_params(axis="y", labelcolor=color)
ax1.grid(True, which="both", linestyle="--", linewidth=0.5)


# Make sure grid is visible (ax1 grid is behind ax2, so maybe add grid to ax2 or set zorder)
# Just use ax1 grid for now.

plt.title(
    f"Drying Energy & Fuel Potential vs Target Moisture\n(Initial Moisture: {moisture_initial_pct:.1f}%)"
)
plt.axvline(
    x=moisture_initial_pct, color="gray", linestyle=":", label="Initial Moisture"
)

# Add legend
lines_1, labels_1 = ax1.get_legend_handles_labels()
ax1.legend(lines_1, labels_1, loc="center right")

output_plot = os.path.join(dir_path, "drying_sensitivity_plot.png")
plt.savefig(output_plot)
print(f"Plot saved to {output_plot}")
plt.close()
