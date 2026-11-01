R = 8.314  # универсальная газовая постоянная, Дж/(моль·К)


def ideal_gas_pressure(nu, T, V):
    """p = νRT / V. V в м³, T в К, ν в моль."""
    if V <= 0 or T <= 0 or nu <= 0:
        raise ValueError("ν, T и V должны быть положительными")
    return nu * R * T / V


def ideal_gas_volume(nu, T, p):
    """V = νRT / p."""
    if p <= 0 or T <= 0 or nu <= 0:
        raise ValueError("ν, T и p должны быть положительными")
    return nu * R * T / p


def ideal_gas_temperature(p, V, nu):
    """T = pV / (νR)."""
    if nu <= 0:
        raise ValueError("ν должно быть положительным")
    return p * V / (nu * R)


def internal_energy_change(nu, dT, i=3):
    """ΔU = (i/2)·νR·ΔT. i — число степеней свободы (3 — одноатомный, 5 — двухатомный)."""
    return i / 2 * nu * R * dT


def work_isobaric(p, dV):
    """A = p·ΔV при постоянном давлении."""
    return p * dV


def work_isothermal(nu, T, V1, V2):
    """A = νRT·ln(V2/V1)."""
    import math
    if V1 <= 0 or V2 <= 0 or T <= 0:
        raise ValueError("Объёмы и температура должны быть положительными")
    return nu * R * T * math.log(V2 / V1)


def heat_capacity_q(c, m, dT):
    """Q = c·m·ΔT (удельная теплоёмкость)."""
    return c * m * dT


def heat_capacity_molar_q(C, nu, dT):
    """Q = C·ν·ΔT (молярная теплоёмкость)."""
    return C * nu * dT


def efficiency_heat_engine(Q1, Q2):
    """η = (Q1 − Q2)/Q1."""
    if Q1 <= 0:
        raise ValueError("Q1 должно быть положительным")
    return (Q1 - Q2) / Q1


def efficiency_carnot(T1, T2):
    """η = 1 − T2/T1 (T в К)."""
    if T1 <= 0 or T2 <= 0 or T2 >= T1:
        raise ValueError("Нужно T1 > T2 > 0")
    return 1 - T2 / T1
