# E2M1: 1 sign bit, 2 exponent bits, 1 fraction bits.

import math


BIAS = 1


def decode_e2m1(bits: int) -> float:
    sign = -1.0 if (bits >> 3) & 0x1 else 1.0
    exponent = (bits >> 1) & 0x3
    mantissa = bits & 0x1

    if exponent == 0:
        if mantissa == 0:
            return math.copysign(0.0, sign)
        return sign * (mantissa / 2.0) * (2.0 ** (1 - BIAS))

    # OCP/ML E2M1 reserves no encodings for Inf/NaN, so exponent == 0x3
    # still decodes as a normal finite value and gives the top magnitudes 4 and 6.
    return sign * (1.0 + mantissa / 2.0) * (2.0 ** (exponent - BIAS))


decoded = [decode_e2m1(bits) for bits in range(1 << 4)]
finite_values = sorted({value for value in decoded if math.isfinite(value)})
pos_inf_count = sum(1 for value in decoded if value == math.inf)
neg_inf_count = sum(1 for value in decoded if value == -math.inf)
nan_count = sum(1 for value in decoded if math.isnan(value))

print("total encodings:", len(decoded))
print("unique finite values:", len(finite_values))
print(finite_values)
print("special encodings:")
print("  -inf:", neg_inf_count)
print("  +inf:", pos_inf_count)
print("  NaN :", nan_count)