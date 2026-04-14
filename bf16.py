# E8M7: 1 sign bit, 8 exponent bits, 7 fraction bits.

import math


BIAS = 127


def decode_bf16(bits: int) -> float:
    sign = -1.0 if (bits >> 15) & 0x1 else 1.0
    exponent = (bits >> 7) & 0xFF
    mantissa = bits & 0x7F

    if exponent == 0:
        if mantissa == 0:
            return math.copysign(0.0, sign)
        return sign * (mantissa / 128.0) * (2.0 ** (1 - BIAS))

    if exponent == 0xFF:
        if mantissa == 0:
            return math.copysign(math.inf, sign)
        return math.nan

    return sign * (1.0 + mantissa / 128.0) * (2.0 ** (exponent - BIAS))


decoded = [decode_bf16(bits) for bits in range(1 << 16)]
finite_values = sorted({value for value in decoded if math.isfinite(value)})
pos_inf_count = sum(1 for value in decoded if value == math.inf)
neg_inf_count = sum(1 for value in decoded if value == -math.inf)
nan_count = sum(1 for value in decoded if math.isnan(value))

print("total encodings:", len(decoded))
print("unique finite values:", len(finite_values))
print("min finite:", finite_values[0])
print("max finite:", finite_values[-1])
print("first 32 finite values:", finite_values[:32])
print("last 32 finite values:", finite_values[-32:])
print("special encodings:")
print("  -inf:", neg_inf_count)
print("  +inf:", pos_inf_count)
print("  NaN :", nan_count)
