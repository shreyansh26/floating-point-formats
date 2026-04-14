import math


BIAS = 15


def decode_fp16(bits: int) -> float:
    sign = -1.0 if (bits >> 15) & 0x1 else 1.0
    exponent = (bits >> 10) & 0x1F
    mantissa = bits & 0x3FF

    if exponent == 0:
        if mantissa == 0:
            return math.copysign(0.0, sign)
        return sign * (mantissa / 1024.0) * (2.0 ** (1 - BIAS))

    if exponent == 0x1F:
        if mantissa == 0:
            return math.copysign(math.inf, sign)
        return math.nan

    return sign * (1.0 + mantissa / 1024.0) * (2.0 ** (exponent - BIAS))


decoded = [decode_fp16(bits) for bits in range(1 << 16)]
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
