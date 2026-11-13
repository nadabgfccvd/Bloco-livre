#!/usr/bin/env python3
"""Analisa strings reais do DEX (string_ids) — não ocorrências brutas de bytes."""
import struct

data = open('/tmp/dexout/classes.dex', 'rb').read()
# header: string_ids_size @56, string_ids_off @60 (little-endian u32)
n, off = struct.unpack_from('<II', data, 56)
print(f'string_ids: {n}')
strs = []
for i in range(n):
    sdo = struct.unpack_from('<I', data, off + i * 4)[0]
    # ULEB128 length em bytes
    p = sdo; l = 0; shift = 0
    while True:
        b = data[p]; p += 1
        l |= (b & 0x7f) << shift; shift += 7
        if not (b & 0x80): break
    try:
        strs.append(data[p:p + l].decode('utf-8', errors='replace'))
    except Exception:
        pass

print('total decodificadas:', len(strs))
print('--- strings com "INTERNET", "permission", "advert", "ad", "GCT", http, network, tracker ---')
sus = [s for s in strs if any(k in s.lower() for k in ['internet', 'permission', 'advert', 'gct', 'http', 'network', 'tracker', 'analytics', 'ads', ' ad ', 'flurry', 'unity', 'vungle', 'applovin', 'ironsource', 'admob', 'chartboost'])]
if sus:
    for s in sus[:40]: print(repr(s))
else:
    print('(nenhuma string suspeita)')
print('--- amostra das 12 primeiras strings ---')
for s in strs[:12]: print(repr(s[:80]))
