import math


BIAS = 127


def decode_e8m0(bits: int) -> float:
    if bits == 0xFF:
        return math.nan

    return 2.0 ** (bits - BIAS)


decoded = [decode_e8m0(bits) for bits in range(1 << 8)]
finite_values = sorted({value for value in decoded if math.isfinite(value)})
nan_count = sum(1 for value in decoded if math.isnan(value))

print("total encodings:", len(decoded))
print("unique finite values:", len(finite_values))
print("min finite:", finite_values[0])
print("max finite:", finite_values[-1])
print("first 16 finite values:", finite_values[:16])
print("last 16 finite values:", finite_values[-16:])
print("special encodings:")
print("  NaN :", nan_count)
