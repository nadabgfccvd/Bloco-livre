#!/usr/bin/env python3
"""Star crown geometry: place the 14 big gold components on the ellipse.
Claim: 12 gold stars + 1 major star on ellipse rx=3*cell, ry=2.6*cell around board center.
Cell ~84.5 px. rx=253.5, ry=219.7. Board center: x=358, y=(190+866)/2=528.
Check each star's angular position relative to center, and radii.
Also check the 'major star' (biggest component 15634 = the horizontal arc? that's likely the banner text or the arc).
"""
import sys, math
sys.path.insert(0, '/home/z/my-project/scripts')

stars = [
 (354,437,15634),(232,338,1929),(486,719,1929),(359,372,1469),(486,338,1271),
 (232,719,1268),(579,638,1265),(140,655,1208),(139,412,1189),(359,748,746),
 (359,308,743),(628,527,138),(90,526,96),(579,386,72)
]
cx, cy = 358, 528
print(f'{"star":>14} size {"dx":>5} {"dy":>5} {"r":>6} {"angle":>7}')
for (x,y,s) in sorted(stars, key=lambda s: -s[2]):
    dx, dy = x-cx, y-cy
    r = math.hypot(dx,dy)
    a = math.degrees(math.atan2(-dy, dx)) % 360
    print(f'({x:4d},{y:4d}) {s:6d} {dx:5d} {dy:5d} {r:6.0f} {a:6.1f}')
print()
print('claimed rx=253.5 ry=219.7: ellipse r at angle a = ', end='')
for a in [0, 30, 60, 90, 120, 150, 180]:
    rr = 1/math.sqrt((math.cos(math.radians(a))/253.5)**2 + (math.sin(math.radians(a))/219.7)**2)
    print(f'{a}deg:{rr:.0f}', end=' ')
print()
