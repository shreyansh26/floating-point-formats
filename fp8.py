# E4M3: 1 sign bit, 4 exponent bits, 3 fraction bits.

import math


BIAS = 7


def decode_e4m3(bits: int) -> float:
    sign = -1.0 if (bits >> 7) & 0x1 else 1.0
    exponent = (bits >> 3) & 0xF
    mantissa = bits & 0x7

    if exponent == 0:
        if mantissa == 0:
            return math.copysign(0.0, sign)
        return sign * (mantissa / 8.0) * (2.0 ** (1 - BIAS))

    if exponent == 0xF:
        if mantissa == 0:
            return math.copysign(math.inf, sign)
        return math.nan

    return sign * (1.0 + mantissa / 8.0) * (2.0 ** (exponent - BIAS))


decoded = [decode_e4m3(bits) for bits in range(256)]
finite_values = sorted({value for value in decoded if math.isfinite(value)})
pos_inf_count = sum(1 for value in decoded if value == math.inf)
neg_inf_count = sum(1 for value in decoded if value == -math.inf)
nan_count = sum(1 for value in decoded if math.isnan(value))

print("total encodings:", len(decoded))
print("unique finite values:", len(finite_values))
print("min finite:", finite_values[0])
print("max finite:", finite_values[-1])
print(finite_values)
print("special encodings:")
print("  -inf:", neg_inf_count)
print("  +inf:", pos_inf_count)
print("  NaN :", nan_count)