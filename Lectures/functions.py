import numpy as np
from matplotlib import pyplot as plt

# @ 1_Liquid_vapor_example


def plot_T_s(fluid):
    T_low = fluid.min_temp - 273.15  # [°C]
    T_cr = fluid.critical_temperature - 273.15  # [°C]

    fluid.TQ = 273.16, 0
    s1 = fluid.entropy_mass
    h1 = fluid.enthalpy_mass

    fluid.TQ = 273.17, 0
    s2 = fluid.entropy_mass
    h2 = fluid.enthalpy_mass

    s0 = s1 - (s2 - s1)
    h0 = h1 - (h2 - h1)

    # temperature range

    T_min = T_low + 0.01  # [°C]
    T_max = T_cr - 0.01  # [°C]

    # n of points
    n_p = 2000

    T = np.linspace(T_min, T_max, n_p)
    T_K = T + 273.15  # [K]

    P_sv = np.zeros(len(T))
    s_sv = np.zeros(len(T))

    P_sl = np.zeros(len(T))
    s_sl = np.zeros(len(T))

    for i, T_i in enumerate(T_K):
        # set the state for saturated vapor
        fluid.TQ = T_i, 1
        P_sv[i] = fluid.P
        s_sv[i] = fluid.entropy_mass

        # set the state for saturated liquid
        fluid.TQ = T_i, 0
        P_sl[i] = fluid.P
        s_sl[i] = fluid.entropy_mass

    fig, ax = plt.subplots(figsize=(15 / 2, 5))
    ax.plot((s_sl - s0) / 1e3, T, label="Saturated liquid")
    ax.plot((s_sv - s0) / 1e3, T, label="Saturated vapor")
    plt.fill_between((s_sv - s0) / 1e3, T, color="r", alpha=0.1, edgecolor=None)
    plt.fill_between((s_sl - s0) / 1e3, T, color="r", alpha=0.1, edgecolor=None)
    ax.set_xlabel("Specific entropy [kJ/(kg K)]")
    ax.set_ylabel("Temperature [°C]")
    ax.legend()
    return fig, ax


def constant_T_transformation(fluid, T_set=300):
    """
    Function related to 1_Liquid_vapor_example.
    returns v_tot and P_tot given T_set.
    """
    # specific volume range
    fluid.TQ = T_set + 273.15, 0
    v_sl_T_set = 1 / fluid.density
    v_min = 0.5 * v_sl_T_set

    fluid.TQ = T_set + 273.15, 1
    v_sv_T_set = 1 / fluid.density
    v_max = 10 * v_sv_T_set

    n_p = 1000

    v_l = np.linspace(v_min, v_sl_T_set, n_p)
    v_v = np.linspace(v_sv_T_set, v_max, n_p)
    P = np.zeros((len(v_l), 2))

    for i, (l, v) in enumerate(zip(v_l, v_v)):
        fluid.TD = T_set + 273.15, 1 / l
        P[i, 0] = fluid.P
        fluid.TD = T_set + 273.15, 1 / v
        P[i, 1] = fluid.P

    v_tot = np.concatenate([v_l, v_v])
    P_tot = np.concatenate([P[:, 0], P[:, 1]])

    return v_tot, P_tot
