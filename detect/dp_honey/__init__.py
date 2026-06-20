"""DP-HONEY: synthetic, non-functional honeytoken generator.

.. warning::

   Every value this package emits is **synthetic** and **shape-only**. Outputs
   are format-compatible with real secrets (they "look like" AWS keys, JWTs,
   GitHub tokens, and so on) but are **never** provider-valid, signed,
   decryptable, authenticated, or usable credentials. Do not treat any output
   as a real secret, and never train this package on real credentials.

The public API is expanded in :mod:`detect.dp_honey` as the package is built.
"""

__version__ = "0.1.0"
