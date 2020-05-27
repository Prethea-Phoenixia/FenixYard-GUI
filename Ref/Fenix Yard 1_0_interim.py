import math

import xlwings as xw

R = 8.314472
Na = 6.022e23
h = 6.626e-34
k = 2.1e-7


def cube(x):
    if x >= 0:
        return x ** (1 / 3)
    elif x < 0:
        return -(abs(x) ** (1 / 3))


def same_sign(a, b):
    return a * b > 0


def brents(f, x0, x1, max_iter=150, tolerance=1e-5):
    fx0 = f(x0)
    fx1 = f(x1)

    assert (fx0 * fx1) <= 0, "Root not bracketed"

    if abs(fx0) < abs(fx1):
        x0, x1 = x1, x0
        fx0, fx1 = fx1, fx0

    x2, fx2 = x0, fx0

    mflag = True
    steps_taken = 0

    while steps_taken < max_iter and abs(x1 - x0) > tolerance:
        fx0 = f(x0)
        fx1 = f(x1)
        fx2 = f(x2)

        if fx0 != fx2 and fx1 != fx2:
            L0 = (x0 * fx1 * fx2) / ((fx0 - fx1) * (fx0 - fx2))
            L1 = (x1 * fx0 * fx2) / ((fx1 - fx0) * (fx1 - fx2))
            L2 = (x2 * fx1 * fx0) / ((fx2 - fx0) * (fx2 - fx1))
            new = L0 + L1 + L2

        else:
            new = x1 - ((fx1 * (x1 - x0)) / (fx1 - fx0))

        if (
            (new < ((3 * x0 + x1) / 4) or new > x1)
            or (mflag == True and (abs(new - x1)) >= (abs(x1 - x2) / 2))
            or (mflag == False and (abs(new - x1)) >= (abs(x2 - d) / 2))
            or (mflag == True and (abs(x1 - x2)) < tolerance)
            or (mflag == False and (abs(x2 - d)) < tolerance)
        ):
            new = (x0 + x1) / 2
            mflag = True

        else:
            mflag = False

        fnew = f(new)
        d, x2 = x2, x1

        if (fx0 * fnew) < 0:
            x1 = new
        else:
            x0 = new

        if abs(fx0) < abs(fx1):
            x0, x1 = x1, x0

        steps_taken += 1

    return x1, steps_taken


def secant_method(f, x0, x1, max_iter=100, tolerance=1e-5):
    steps_taken = 1
    while steps_taken < max_iter and abs(x1 - x0) > tolerance:
        x2 = x1 - ((f(x1) * (x1 - x0)) / (f(x1) - f(x0)))
        x1, x0 = x2, x1
        steps_taken += 1
    return x2, steps_taken


def solve_cubic_depressed(p, q):
    x = cube(-q / 2 + math.sqrt(q ** 2 / 4 + p ** 3 / 27)) + cube(
        -q / 2 - math.sqrt(q ** 2 / 4 + p ** 3 / 27)
    )

    return x


@xw.func
def solve_for_mach(T, Tb, T0, P0, rho, Hv, Mmol, gamma):
    def f(mach):
        P = 1e5 * math.e ** (Hv * Mmol * (1 / Tb - 1 / T) / R)
        rhos = P * Mmol / (R * T)
        m = mach * math.sqrt(gamma / 2)
        q = math.sqrt(math.pi) * (m / 2) * ((gamma - 1) / (gamma + 1))
        Tv = T * (math.sqrt(1 + q ** 2) - q) ** 2
        rhov = rhos * (
            math.sqrt(T / Tv)
            * (
                (m ** 2 + 0.5) * math.e ** (m ** 2) * math.erfc(m)
                - m / math.sqrt(math.pi)
            )
            + 0.5
            * (T / Tv)
            * (1 - math.sqrt(math.pi) * m * math.e ** (m ** 2) * math.erfc(m))
        )
        c0 = math.sqrt(1.4 * R * T0 / 0.0288)
        cv = math.sqrt(gamma * R * Tv / Mmol)
        r = ((gamma + 1) / 4) * mach * (cv / c0)
        bv = (
            (P / P0) * (Tv / T) * (rhov / rho)
            - 1
            - gamma * mach * (cv / c0) * (r + math.sqrt(1 + r ** 2))
        )

        return bv

    cache = []
    result, step = secant_method(f, 0, 1)
    cache.append(result)

    def f_n(x):
        return f(x) / (x - result)

    try:
        result, step = secant_method(f_n, 0, 1)
        cache.append(result)
    finally:
        for i in cache:
            if 0 <= i <= 1:
                return i
        if min(cache) > 1:
            return 1
        if max(cache) < 0:
            return 0
        return 0


@xw.func
def solve_for_t(
    Ia,
    Tb,
    Tm,
    T0,
    Tc,
    P0,
    rho,
    rhoq,
    Hf,
    Hv,
    Mmol,
    gamma,
    Cp,
    S,
    chi,
    emissivity,
    search_limit,
):
    def f_t(T):
        def consider_E_melt_ejection():
            V = Mmol / rhoq  # Molar Volume
            # estimating mu: M:molar mass
            mu = Na * h / V * math.exp(3.8 * Tb / T)
            mu = max(mu, 0)
            # estimating lamda (Eotvos)
            lamda = k * (Tc - 6 - T) / V ** (2 / 3)
            Pst = max(4 * lamda / S, 0)
            # quartic equation:
            a = 4 * (P - P0 - Pst) / (3 * rho * mu * S ** 2)
            c = vi
            d = -chi * math.log((T - T0 + Hf / Cp) / (Tm - T0), math.e)
            Dm = solve_cubic_depressed(c / a, d / a)
            vm = a * Dm ** 3
            return vm * rho * (T - Tm) * Cp

        mach = solve_for_mach(T, Tb, T0, P0, rho, Hv, Mmol, gamma)

        P = 1e5 * math.e ** (Hv * Mmol * (1 / Tb - 1 / T) / R)
        rhos = P * Mmol / (R * T)
        m = mach * math.sqrt(gamma / 2)
        q = math.sqrt(math.pi) * (m / 2) * ((gamma - 1) / (gamma + 1))
        Tv = T * (math.sqrt(1 + q ** 2) - q) ** 2
        rhov = rhos * (
            math.sqrt(T / Tv)
            * (
                (m ** 2 + 0.5) * math.e ** (m ** 2) * math.erfc(m)
                - m / math.sqrt(math.pi)
            )
            + 0.5
            * (T / Tv)
            * (1 - math.sqrt(math.pi) * m * math.e ** (m ** 2) * math.erfc(m))
        )
        cv = math.sqrt(gamma * R * Tv / Mmol)
        pv = rhov * R * Tv / Mmol
        vv = cv * mach
        vi = vv * rhov / rho
        be = (
            Ia
            - emissivity * 5.67e-8 * T ** 2
            - rho * vi * (Hf + (T - T0) * Cp)
            + rho * vi * (vi ** 2 / 2 - Hv)
            + rhov * vv * (gamma * R * (T - Tv) / Mmol - vv ** 2 / 2)
        )
        if rhoq != 0:
            be -= consider_E_melt_ejection()

        return be

    result, step = brents(f_t, Tm, search_limit)
    return result


@xw.func
def kinetic_ciws(theta, vel, acc, dt, r_max, r_min, s, muz_vel, volume):
    r = r_max
    P_miss = 1
    while r >= r_min:
        FCE = min(
            volume / (((r / muz_vel) ** 2 * acc / 2) ** 3 * math.pi * 4 / 3 * 1 / 2), 1
        )
        P_hit_r = min(s / (math.pi * (theta * r / 2) ** 2) * FCE, 1)
        P_miss_r = 1 - P_hit_r
        P_miss *= P_miss_r
        vel += acc * dt
        r -= vel * dt + 1 / 2 * acc * dt ** 2
    P_hit = 1 - P_miss
    return P_hit


@xw.func
def ablationNuke(v, Mp, Ep, z, R, Ha, rhoa, Opmod, C):

    assert Ha > 0, "Heat of Vaporization not provided."

    sigma = 5.67e-8

    def integrate(test_x):
        def outer(y):

            beta = math.atan(y / z)

            r = z / math.cos(beta)

            tr = r / v

            def inner(t):
                def P():
                    ans = (
                        2
                        * Ep
                        / (math.pi ** (3 / 2) * r ** 3)
                        * (tr / t) ** 5
                        * math.exp(-1 * (tr / t) ** 2)
                    )
                    return ans

                def Ts():
                    ans = (
                        Ep
                        * v
                        / (math.pi ** (3 / 2) * sigma * r ** 3)
                        * (tr / t) ** 6
                        * math.exp(-1 * (tr / t) ** 2)
                    )

                    ans = ans ** (1 / 4)
                    return max(0, ans)

                def rho():
                    ans = (
                        2
                        * Ep
                        / (math.pi ** (3 / 2) * r ** 3 * v ** 2)
                        * (tr / t) ** 3
                        * math.exp(-(tr / t))
                    )
                    return ans

                def absorp():
                    # Uranium opacity
                    stagP = P() + 1 / 2 * rho() * (r/t) ** 2
                    pressAtm = stagP / 101325
                    tempR = (Ts() - 273.15) * 0.8
                    if tempR > 1e4:
                        k = (
                            8370 * (pressAtm / 500) * (72000 / tempR) ** 2.39
                        )  # unit in inverse feet
                        aR = 1 / ((1 / k) * 0.3048)
                    else:
                        aR = 1e64
                    aR *= Opmod
                    return aR

                def eDot():
                    tz = z/v
                    ans = (
                        Ep
                        * v
                        / (math.pi ** (3 / 2) * z ** 3)
                        * (tz / t) ** 6
                        * math.exp(-(tz / (t * math.cos(beta)))**2)
                    )
                    ans *= C
                    return ans

                return eDot() / Ha * math.exp(-1 * absorp() * test_x)

            cumulative = 0

            delta_t = tr / 25

            curr_t = delta_t

            for i in range(0, 50):

                cumulative += inner(curr_t) * delta_t
                curr_t += delta_t

            return cumulative

        delta_R = R / 25
        curr_R = delta_R
        result = 0
        for i in range(0, 24):
            result += outer(curr_R) * curr_R * delta_R
            curr_R += delta_R

        result *= 2 * math.pi
        result_x = result / rhoa / (math.pi * R ** 2)
        return result, result_x

    def layerDepth(x):
        ans, result_x = integrate(x)
        balance = result_x - x
        return balance

    ans_x, steps = brents(layerDepth, 0, 1, 150, 1e-5)
    assert steps < 150
    ans = integrate(ans_x)

    return ans
