import streamlit as st
from datetime import datetime
import physics

# ============================================================
# Настройка страницы
# ============================================================
st.set_page_config(
    page_title="Калькулятор по термодинамике",
    page_icon="🌡️",
    layout="centered"
)

# ============================================================
# Инициализация истории расчётов
# ============================================================
if "history" not in st.session_state:
    st.session_state.history = []


def add_history(process: str, result: str):
    st.session_state.history.insert(0, f"{process} → {result}")
    st.session_state.history = st.session_state.history[:20]


# ============================================================
# Отчёт и скачивание
# ============================================================
def make_report(process: str, inputs: dict, result: str) -> str:
    lines = [
        "=" * 50,
        "ОТЧЁТ О РАСЧЁТЕ",
        f"Раздел: {process}",
        f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        "=" * 50,
        "",
        "Исходные данные:",
    ]
    for name, value in inputs.items():
        lines.append(f"  {name} = {value}")
    lines += ["", "Результат:", f"  {result}", "=" * 50,
              "Калькулятор по термодинамике · учебный проект"]
    return "\n".join(lines)


def show_download(process: str, inputs: dict, result: str, key: str):
    report = make_report(process, inputs, result)
    st.download_button(
        label="💾 Скачать отчёт (.txt)",
        data=report,
        file_name=f"thermo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain",
        key=key
    )


# ============================================================
# Перевод единиц в СИ
# ============================================================
PRESSURE_UNITS = {
    "Па": 1.0, "кПа": 1000.0, "МПа": 1_000_000.0,
    "атм": 101_325.0, "мм рт. ст.": 133.322,
}
VOLUME_UNITS = {"м³": 1.0, "л": 0.001, "см³": 0.000001}


def to_si(value: float, unit: str, kind: str) -> float:
    if kind == "pressure":
        return value * PRESSURE_UNITS[unit]
    if kind == "volume":
        return value * VOLUME_UNITS[unit]
    if kind == "temperature":
        return value + 273.15 if unit == "°C" else value
    return value


# ============================================================
# Заголовок и Вкладки
# ============================================================
st.title("🌡️ Интерактивный калькулятор по термодинамике")
st.caption("Учебный проект · Python + Streamlit")

tab1, tab2, tab3, tab4 = st.tabs([
    "pV = νRT", "Первое начало", "КПД", "Справочник"
])

# ============================================================
# ВКЛАДКА 1 — Уравнение Менделеева–Клапейрона
# ============================================================
with tab1:
    st.subheader("Уравнение состояния идеального газа")
    st.latex(r"pV = \nu R T")
    st.write("Введите известные параметры. Поле нужной величины оставьте равным 0.")

    col1, col2 = st.columns(2)
    with col1:
        nu1 = st.number_input("ν, моль", min_value=0.0, value=1.0,
                              step=0.1, key="nu1")
        T1_val = st.number_input("T", min_value=0.0, value=273.0,
                                 step=1.0, key="T1_val")
        T1_unit = st.selectbox("Ед. температуры", ["К", "°C"], key="T1_unit")
        T1 = to_si(T1_val, T1_unit, "temperature")
    with col2:
        V1_val = st.number_input("V", min_value=0.0, value=22.4,
                                 step=0.1, key="V1_val")
        V1_unit = st.selectbox("Ед. объёма", list(VOLUME_UNITS.keys()),
                               index=1, key="V1_unit")
        V1 = to_si(V1_val, V1_unit, "volume")

        p1_val = st.number_input("p", min_value=0.0, value=0.0,
                                 step=1.0, key="p1_val")
        p1_unit = st.selectbox("Ед. давления", list(PRESSURE_UNITS.keys()),
                               index=1, key="p1_unit")
        p1 = to_si(p1_val, p1_unit, "pressure")

    if st.button("Рассчитать", key="btn1"):
        try:
            if p1 == 0:
                p = physics.ideal_gas_pressure(nu1, T1, V1)
                p_out = p / PRESSURE_UNITS[p1_unit]
                result = f"p = {p_out:.3f} {p1_unit}"
                st.success(f"**{result}**")
                add_history("pV=νRT: p", result)
                show_download("Давление", {"ν": nu1, "T": T1, "V": V1}, result, "dl_p")

            elif V1 == 0:
                V = physics.ideal_gas_volume(nu1, T1, p1)
                V_out = V / VOLUME_UNITS[V1_unit]
                result = f"V = {V_out:.3f} {V1_unit}"
                st.success(f"**{result}**")
                add_history("pV=νRT: V", result)
                show_download("Объём", {"ν": nu1, "T": T1, "p": p1}, result, "dl_V")

            elif T1 == 0:
                T = physics.ideal_gas_temperature(p1, V1, nu1)
                T_out = T - 273.15 if T1_unit == "°C" else T
                result = f"T = {T_out:.2f} {T1_unit}"
                st.success(f"**{result}**")
                add_history("pV=νRT: T", result)
                show_download("Температура", {"ν": nu1, "p": p1, "V": V1}, result, "dl_T")

            else:
                st.info("Все поля заполнены — обнулите то, что нужно найти.")
        except ValueError as e:
            st.error(f"Ошибка: {e}")

# ============================================================
# ВКЛАДКА 2 — Первое начало термодинамики
# ============================================================
with tab2:
    st.subheader("Первое начало термодинамики")
    st.markdown("**Изменение внутренней энергии**")
    st.latex(r"\Delta U = \frac{i}{2}\,\nu R\,\Delta T")

    col1, col2, col3 = st.columns(3)
    with col1:
        nu2 = st.number_input("ν, моль", min_value=0.0, value=1.0, step=0.1, key="nu2")
    with col2:
        dT2 = st.number_input("ΔT, К", value=10.0, step=1.0, key="dT2")
    with col3:
        i2 = st.selectbox("Газ", [3, 5, 6],
                          format_func=lambda x:
                          {3: "одноатомный (i=3)", 5: "двухатомный (i=5)", 6: "многоатомный (i=6)"}[x],
                          key="i2")

    if st.button("Найти ΔU", key="btn2"):
        try:
            du = physics.internal_energy_change(nu2, dT2, i2)
            result = f"ΔU = {du:.2f} Дж"
            st.success(f"**{result}**")
            add_history("ΔU", result)
            show_download("Внутренняя энергия", {"ν": nu2, "ΔT": dT2, "i": i2}, result, "dl_du")
        except ValueError as e:
            st.error(f"Ошибка: {e}")

    st.divider()
    st.markdown("**Работа газа**")
    work_type = st.radio("Процесс:", ["Изобарный", "Изотермический"], horizontal=True, key="work_type")

    if work_type == "Изобарный":
        st.latex(r"A = p\,\Delta V")
        col1, col2 = st.columns(2)
        with col1:
            p_w = st.number_input("p, Па", min_value=0.0, value=101325.0, step=100.0, key="p_w")
        with col2:
            dV_w = st.number_input("ΔV, м³", value=0.001, step=0.001, format="%.4f", key="dV_w")
        if st.button("Найти A", key="btnA1"):
            A = physics.work_isobaric(p_w, dV_w)
            result = f"A = {A:.2f} Дж"
            st.success(f"**{result}**")
            add_history("A (изобара)", result)
            show_download("Работа (изобара)", {"p": p_w, "ΔV": dV_w}, result, "dl_A1")
    else:
        st.latex(r"A = \nu R T \ln\frac{V_2}{V_1}")
        st.caption("R = 8.314 Дж/(моль·К)")
        col1, col2 = st.columns(2)
        with col1:
            nu_w = st.number_input("ν, моль", min_value=0.0, value=1.0, step=0.1, key="nu_w")
            V1w = st.number_input("V₁, м³", min_value=0.0, value=0.01, step=0.001, format="%.4f", key="V1w")
        with col2:
            T_w = st.number_input("T, К", min_value=0.0, value=300.0, step=1.0, key="T_w")
            V2w = st.number_input("V₂, м³", min_value=0.0, value=0.02, step=0.001, format="%.4f", key="V2w")
        if st.button("Найти A", key="btnA2"):
            try:
                A = physics.work_isothermal(nu_w, T_w, V1w, V2w)
                result = f"A = {A:.2f} Дж"
                st.success(f"**{result}**")
                add_history("A (изотерма)", result)
                show_download("Работа (изотерма)", {"ν": nu_w, "T": T_w, "V₁": V1w, "V₂": V2w}, result, "dl_A2")
            except ValueError as e:
                st.error(f"Ошибка: {e}")

    st.divider()
    st.markdown("**Количество теплоты**")
    mode = st.radio("Способ:", ["через удельную теплоёмкость", "через молярную теплоёмкость"], horizontal=True,
                    key="q_mode")

    if mode == "через удельную теплоёмкость":
        st.latex(r"Q = c\,m\,\Delta T")
    else:
        st.latex(r"Q = C\,\nu\,\Delta T")

    col1, col2, col3 = st.columns(3)
    with col1:
        if mode == "через удельную теплоёмкость":
            c_q = st.number_input("c, Дж/(кг·К)", min_value=0.0, value=4200.0, step=10.0, key="c_q")
        else:
            c_q = st.number_input("C, Дж/(моль·К)", min_value=0.0, value=20.8, step=0.1, key="C_q")
    with col2:
        if mode == "через удельную теплоёмкость":
            m_q = st.number_input("m, кг", min_value=0.0, value=1.0, step=0.1, key="m_q")
        else:
            m_q = st.number_input("ν, моль", min_value=0.0, value=1.0, step=0.1, key="nu_q")
    with col3:
        dT_q = st.number_input("ΔT, К", value=10.0, step=1.0, key="dT_q")

    if st.button("Найти Q", key="btnQ"):
        if mode == "через удельную теплоёмкость":
            Q = physics.heat_capacity_q(c_q, m_q, dT_q)
        else:
            Q = physics.heat_capacity_molar_q(c_q, m_q, dT_q)
        result = f"Q = {Q:.2f} Дж ({Q / 1000:.3f} кДж)"
        st.success(f"**{result}**")
        add_history("Q", result)
        show_download("Теплота", {"c/C": c_q, "m/ν": m_q, "ΔT": dT_q}, result, "dl_Q")

# ============================================================
# ВКЛАДКА 3 — КПД
# ============================================================
with tab3:
    st.subheader("КПД теплового двигателя")
    engine_type = st.radio("Тип расчёта:", ["По теплотам Q₁, Q₂", "Цикл Карно (по температурам)"], horizontal=True,
                           key="eta_type")

    if engine_type == "По теплотам Q₁, Q₂":
        st.latex(r"\eta = \frac{Q_1 - Q_2}{Q_1}")
        col1, col2 = st.columns(2)
        with col1:
            Q1 = st.number_input("Q₁, Дж (от нагревателя)", min_value=0.0, value=1000.0, step=10.0, key="Q1")
        with col2:
            Q2 = st.number_input("Q₂, Дж (холодильнику)", min_value=0.0, value=600.0, step=10.0, key="Q2")
        if st.button("Рассчитать КПД", key="btnE1"):
            try:
                eta = physics.efficiency_heat_engine(Q1, Q2)
                result = f"η = {eta * 100:.1f} %"
                st.success(f"**η = {eta:.3f} = {result}**")
                st.info(f"Работа за цикл: A = Q₁ − Q₂ = **{Q1 - Q2:.1f} Дж**")
                add_history("η (по Q)", result)
                show_download("КПД по теплотам", {"Q₁": Q1, "Q₂": Q2}, result, "dl_eta1")
            except ValueError as e:
                st.error(f"Ошибка: {e}")
    else:
        st.latex(r"\eta = 1 - \frac{T_2}{T_1}")
        col1, col2 = st.columns(2)
        with col1:
            T1c = st.number_input("T₁ (нагреватель), К", min_value=0.0, value=600.0, step=1.0, key="T1c")
        with col2:
            T2c = st.number_input("T₂ (холодильник), К", min_value=0.0, value=300.0, step=1.0, key="T2c")
        if st.button("Рассчитать КПД Карно", key="btnE2"):
            try:
                eta = physics.efficiency_carnot(T1c, T2c)
                result = f"η = {eta * 100:.1f} %"
                st.success(f"**η = {eta:.3f} = {result}**")
                add_history("η (Карно)", result)
                show_download("КПД Карно", {"T₁": T1c, "T₂": T2c}, result, "dl_eta2")
            except ValueError as e:
                st.error(f"Ошибка: {e}")

# ============================================================
# ВКЛАДКА 4 — Справочник и Проверка
# ============================================================
with tab4:
    st.subheader("Справочник и проверка")

    mode4 = st.radio("Выберите режим:", ["📖 Справочник формул", "✅ Проверка ответа"], horizontal=True, key="tab4_mode")

    if mode4 == "📖 Справочник формул":
        st.write("Выберите нужный раздел, чтобы вспомнить формулу:")

        with st.expander("1. Уравнение Менделеева-Клапейрона"):
            st.latex(r"pV = \nu R T")
            st.write("Связывает давление, объём и температуру идеального газа.")

        with st.expander("2. Первое начало термодинамики"):
            st.latex(r"Q = \Delta U + A")
            st.write(
                "Количество теплоты, переданное газу, идёт на изменение его внутренней энергии и работу против внешних сил.")

        with st.expander("3. Внутренняя энергия идеального газа"):
            st.latex(r"\Delta U = \frac{i}{2}\,\nu R\,\Delta T")
            st.write(
                "Зависит только от изменения температуры. i — число степеней свободы (3 для одноатомного, 5 для двухатомного).")

        with st.expander("4. Работа газа"):
            st.write("**Изобарный процесс (p = const):**")
            st.latex(r"A = p\,\Delta V")
            st.write("**Изотермический процесс (T = const):**")
            st.latex(r"A = \nu R T \ln\frac{V_2}{V_1}")

        with st.expander("5. КПД теплового двигателя"):
            st.latex(r"\eta = \frac{Q_1 - Q_2}{Q_1} = \frac{A}{Q_1}")
            st.write("Отношение полезной работы к затраченной энергии.")

        with st.expander("6. КПД цикла Карно (идеальная машина)"):
            st.latex(r"\eta = 1 - \frac{T_2}{T_1}")
            st.write("Максимально возможный КПД для данных температур нагревателя (T₁) и холодильника (T₂).")

    else:
        st.write("Решите задачу на бумаге, введите свой ответ, и калькулятор проверит его.")
        st.info("Пример: найдите давление 1 моль газа при 273 К и объёме 22.4 л. Введите ответ в кПа.")

        col1, col2, col3 = st.columns(3)
        with col1:
            nu_ch = st.number_input("ν, моль", min_value=0.0, value=1.0, step=0.1, key="ch_nu")
        with col2:
            T_ch = st.number_input("T, К", min_value=0.0, value=273.0, step=1.0, key="ch_T")
        with col3:
            V_ch = st.number_input("V, л", min_value=0.0, value=22.4, step=0.1, key="ch_V")

        user_answer = st.number_input("Ваш ответ: p, кПа", value=0.0, step=1.0, key="ch_ans")

        if st.button("Проверить ответ", key="btn_check"):
            # Считаем правильный ответ в кПа
            p_pa = physics.ideal_gas_pressure(nu_ch, T_ch, V_ch / 1000)
            p_kpa = p_pa / 1000

            # Сравниваем с погрешностью 1% (на случай погрешности округления)
            if abs(user_answer - p_kpa) <= p_kpa * 0.01:
                st.success(f"✅ **Верно!** Правильный ответ: {p_kpa:.2f} кПа")
            else:
                st.error(f"❌ **Ошибка.** Правильный ответ: {p_kpa:.2f} кПа")

# ============================================================
# История и подвал
# ============================================================
if st.session_state.get("history"):
    with st.expander(f"📜 История расчётов ({len(st.session_state.history)})", expanded=False):
        for i, item in enumerate(st.session_state.history, 1):
            st.write(f"{i}. {item}")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📥 Скачать всю историю",
                data="\n".join(st.session_state.history),
                file_name=f"history_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                key="dl_all"
            )
        with col2:
            if st.button("🗑️ Очистить историю", key="clear_hist"):
                st.session_state.history = []
                st.rerun()

st.divider()
st.caption("© Учебный проект по физике · 2026")
