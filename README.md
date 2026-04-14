# Floating-Point Format Notes

This directory contains small scripts that enumerate and decode several low-precision floating-point formats:

- `e8m0.py`
- `fp4.py`
- `fp8.py`
- `fp16.py`
- `bf16.py`

Each script iterates over every possible bit pattern for the format, decodes it to a Python `float`, and prints a summary.

## Bit Layout

For a format with:

- 1 sign bit
- `e` exponent bits
- `m` fraction bits

the stored bit pattern is:

```text
sign | exponent | mantissa
```

where:

- `S` is the sign bit
- `E` is the exponent field interpreted as an unsigned integer
- `M` is the mantissa/fraction field interpreted as an unsigned integer
- `bias` is usually `2^(e - 1) - 1`

`E8M0` is the notable exception in this folder:

- it has no sign bit
- it has 8 exponent bits
- it has 0 mantissa bits
- it is primarily used as a scale type in MX formats

## Decode Formula

### Normal numbers

When the exponent field is nonzero and not reserved for specials:

```text
value = (-1)^S * 2^(E - bias) * (1 + M / 2^m)
```

The term `1 + M / 2^m` is the significand. The leading `1` is implicit.

### Subnormal numbers

When the exponent field is zero and the mantissa is nonzero:

```text
value = (-1)^S * 2^(1 - bias) * (M / 2^m)
```

Subnormals do not have the implicit leading `1`.

### Zero

When `E = 0` and `M = 0`:

```text
+0.0 or -0.0
```

The sign bit is still preserved, so both `+0.0` and `-0.0` exist as distinct encodings.

### Infinities and NaNs

For IEEE-style formats, the all-ones exponent field is special:

```text
E = max_exponent, M = 0   -> +/-inf
E = max_exponent, M != 0  -> NaN
```

Not every ML format uses this convention. Some low-precision ML formats reserve no encodings for `Inf` or `NaN`.

## `E8M0`

`E8M0` is not a conventional signed floating-point data type.

It is an unsigned exponent-only format:

- 8 exponent bits
- 0 mantissa bits
- no sign bit
- bias `127`

For the OCP MX scale type used in microscaling formats:

- `0xFF` is reserved for `NaN`
- there is no zero encoding
- there is no infinity encoding
- all other encodings represent powers of two

So the decode rule is:

```text
bits = 255      -> NaN
bits = 0..254   -> 2^(bits - 127)
```

This means the supported finite exponent range is:

```text
-127 .. 127
```

and the finite values are:

```text
2^-127, 2^-126, ..., 2^126, 2^127
```

Because `E8M0` has no sign bit and no mantissa, there are no subnormals.

## Why `mantissa / 2^m`?

The mantissa field stores the fractional part of the significand.

If there are `m` mantissa bits, then:

```text
M / 2^m
```

converts the stored integer field into its binary fraction value.

Examples:

- 1 mantissa bit  -> divide by `2`
- 3 mantissa bits -> divide by `8`
- 7 mantissa bits -> divide by `128`
- 10 mantissa bits -> divide by `1024`

## Field Extraction

The scripts extract fields by shifting down and masking:

```python
sign = (bits >> shift) & sign_mask
exponent = (bits >> mantissa_bits) & exponent_mask
mantissa = bits & mantissa_mask
```

Example for FP16:

```python
sign = (bits >> 15) & 0x1
exponent = (bits >> 10) & 0x1F
mantissa = bits & 0x3FF
```

The mask is always all ones across the width of the field:

```text
n-bit mask = (1 << n) - 1
```

## Formats In This Folder

### `e8m0.py`

- Format: `E8M0`
- Bits: 8 exponent, 0 mantissa, no sign
- Bias: `127`
- Interpretation in this repo: OCP MX scale type

Important details:

- `0xFF` is the single `NaN` encoding
- `0x00` is not zero; it decodes to `2^-127`
- there are no subnormals
- there are no infinities
- every finite value is an exact power of two

So:

```text
decode(bits) = 2^(bits - 127), for bits in 0..254
```

This is the scale format used by MX formats such as `MXFP4`, `MXFP6`, and `MXFP8`.

### `fp4.py`

- Format: `E2M1`
- Bits: 1 sign, 2 exponent, 1 mantissa
- Bias: `1`
- Interpretation in this repo: OCP/ML-style `FP4`

Important detail:

- `fp4.py` does **not** reserve encodings for `Inf` or `NaN`
- `exponent == 0b11` is still a normal finite exponent

So the positive finite values are:

```text
0, 0.5, 1, 1.5, 2, 3, 4, 6
```

This matches the OCP MX `FP4 (E2M1)` element encoding used inside microscaled formats such as `MXFP4`.

### `fp8.py`

- Format: `E4M3`
- Bits: 1 sign, 4 exponent, 3 mantissa
- Bias: `7`
- Interpretation in this repo: IEEE-style special handling in the script

Current script behavior:

- `E = 0` -> zero/subnormal
- `E = 15, M = 0` -> `Inf`
- `E = 15, M != 0` -> `NaN`

Note:

- Many ML stacks use `E4M3` variants such as `E4M3FN` or `E4M3FNUZ`
- those are not always identical to naive IEEE-style `Inf`/`NaN` decoding

### `fp16.py`

- Format: IEEE binary16
- Bits: 1 sign, 5 exponent, 10 mantissa
- Bias: `15`
- Special values: yes (`Inf`, `NaN`)

Normal decode:

```text
(-1)^S * 2^(E - 15) * (1 + M / 1024)
```

Subnormal decode:

```text
(-1)^S * 2^(-14) * (M / 1024)
```

### `bf16.py`

- Format: bfloat16
- Bits: 1 sign, 8 exponent, 7 mantissa
- Bias: `127`
- Special values: yes (`Inf`, `NaN`)

Normal decode:

```text
(-1)^S * 2^(E - 127) * (1 + M / 128)
```

Subnormal decode:

```text
(-1)^S * 2^(-126) * (M / 128)
```

`bf16` has the same exponent width as IEEE `float32`, but fewer mantissa bits.

## About The Printed Counts

Some scripts print:

- `total encodings`
- `unique finite values`
- special counts

`unique finite values` is computed via a Python `set`, so duplicate numeric values are collapsed.

This especially matters for signed zero:

```python
finite_values = sorted({value for value in decoded if math.isfinite(value)})
```

In Python:

```python
-0.0 == 0.0
```

so `+0.0` and `-0.0` count as two distinct encodings but only one unique numeric value in the printed set.

## MXFP4 vs Raw FP4

`MXFP4` is not just a scalar 4-bit dtype.

It is a microscaled block format:

- element type: `FP4 (E2M1)`
- scale type: `E8M0`
- block size: `32`

Conceptually:

```text
decoded_value_i = shared_block_scale * decoded_fp4_element_i
```

So `fp4.py` models the raw element encoding, not the full microscaled block format.
