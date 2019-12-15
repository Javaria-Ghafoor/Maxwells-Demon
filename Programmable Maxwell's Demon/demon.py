from random import random
from math import exp, sqrt, pi, floor, cos, sin
from numpy.ma import arange
from vpython import scene, cylinder, color, box, compound, vector, vertex, quad, rate


def gaussian(x, sigma=1.0, meu=0.0):
    return exp(-0.5 * (x - meu / sigma) ** 2) / (sigma * sqrt(2 * pi))


dx = 0.001
N = 100
i = 1
xmax = 3
xlast = -xmax
integral = 0
bins = []
iterno = []

for x in arange(-xmax, dx / 2, dx):
    integral += gaussian(x, xmax/3, 0) * dx    # xmax lies within 3*sigma
    if integral >= i / N:
        k = (x - xlast) / 10
        for j in range(1, 11):
            bins.append(xlast + j * k)
        xlast = x
        i += 1
    iterno.append(x)
# print(len(iter))

# print(bins)
lbin = len(bins)    # 490 entries

for i in range(lbin - 1, -1, -1):  # to make sure average value of bins==meu==0 (adding symmetric values about 0)
    bins.append(-bins[i])

lbin = len(bins)    # 980 entries


def choose():  # returns a number between -3 and 3 (-3 and 3 sigma), gaussian distribution
    r = floor(lbin * random())  # random() gets the next random number in the range [0.0, 1.0).
    return bins[r]

scene.forward = vector(-0.15, -0.3, -1)
scene.range = 1

Dia_axle = 0.03  # diameter of axle
Dia_paddle = 0.05  # diameter of paddle bearing
R = 1  # radius of demon
H = 0.1  # height of demon
dr = R / 100  # thickness of demon cylinder, blade, and paddle
paddle_color = vector(0.8, 1, 0.8)
Len_paddle = 0.4 * R
h = H / 5
d = 1.5 * Dia_paddle



"""
Axes in VPython:
x-axis: left
y-axis: up
z-axis: out
"""


def make_paddle():
    vcyl = cylinder(pos=vector(0, -H / 2, 0), size=vector(H, Dia_paddle, Dia_paddle), axis=vector(0, 1, 0),
                    color=paddle_color, theta=0, omega=0)
    #   size is always set as if our axis is the default axis
    hcyl = cylinder(size=vector(R - dr / 2 - Len_paddle, Dia_paddle / 3, Dia_paddle / 3), color=color.white, theta=0,
                    omega=0)
    #   default pos=(0, 0, 0), axis=(1, 0, 0)
    blade = box(pos=vector(R - dr / 2 - Len_paddle / 2, 0, 0), size=vector(Len_paddle, H, dr), color=paddle_color,
                theta=0, omega=0)
    offset = 0.51 * H
    bearing1 = cylinder(pos=vector(0, offset, 0), size=vector(h, d, d), axis=vector(0, 1, 0), color=color.white,
                        theta=0, omega=0)
    bearing2 = cylinder(pos=vector(0, -offset, 0), size=vector(h, d, d), axis=vector(0, -1, 0), color=color.white,
                        theta=0, omega=0)
    paddle = compound([vcyl, hcyl, blade, bearing1, bearing2])
    paddle.rotate(angle=pi / 2, axis=vector(0, 1, 0), origin=vector(0, 0, 0))
    paddle.theta = 0
    paddle.omega = 0
    return paddle


make_paddle()


def make_demon():
    # VPython 6 has an extrusion object unlike VPython 7 (which we're using)
    n = 4 * 90
    dtheta = 2 * pi / n
    theta = 0
    demon_color = vector(0.67, 0.86, 1)
    quads = []
    # subscript i: inside, o: outside
    vilower = []
    viupper = []
    volower = []
    voupper = []
    vibottom = []
    vitop = []
    vobottom = []
    votop = []
    while theta < 2*pi-dtheta/2:
        ray1i = R * vector(cos(theta), 0, sin(theta))
        ray2i = R * vector(cos(theta + dtheta), 0, sin(theta + dtheta))
        ray1o = (R + dr) * vector(cos(theta), 0, sin(theta))
        ray2o = (R + dr) * vector(cos(theta + dtheta), 0, sin(theta + dtheta))

        vilower.append(vertex(pos=ray1i + vector(0, -0.5 * H, 0), normal=-ray1i, color=demon_color))
        viupper.append(vertex(pos=ray1i + vector(0, 0.5 * H, 0), normal=-ray1i, color=demon_color))
        volower.append(vertex(pos=ray2o + vector(0, -0.5 * H, 0), normal=ray1o, color=demon_color))
        voupper.append(vertex(pos=ray2o + vector(0, 0.5 * H, 0), normal=ray1o, color=demon_color))

        vibottom.append(vertex(pos=ray1i + vector(0, -0.5 * H, 0), normal=vector(0, -1, 0), color=demon_color))
        vitop.append(vertex(pos=ray1i + vector(0, 0.5 * H, 0), normal=vector(0, 1, 0), color=demon_color))
        vobottom.append(vertex(pos=ray2o + vector(0, -0.5 * H, 0), normal=vector(0, -1, 0), color=demon_color))
        votop.append(vertex(pos=ray2o + vector(0, 0.5 * H, 0), normal=vector(0, 1, 0), color=demon_color))

        theta += dtheta
    vilower.append(vilower[0])
    viupper.append(viupper[0])
    volower.append(volower[0])
    voupper.append(voupper[0])
    vibottom.append(vibottom[0])
    vitop.append(vitop[0])
    vobottom.append(vobottom[0])
    votop.append(votop[0])
    for n in range(n):
        quads.append(quad(v0=vilower[n], v1=viupper[n], v2=viupper[n + 1], v3=vilower[n + 1]))
        quads.append(quad(v0=volower[n], v3=voupper[n], v2=voupper[n + 1], v1=volower[n + 1]))
        quads.append(quad(v0=vibottom[n], v1=vobottom[n], v2=vobottom[n + 1], v3=vibottom[n + 1]))
        quads.append(quad(v0=vitop[n], v1=votop[n], v2=votop[n + 1], v3=vitop[n + 1]))
    quads.append(box(pos=vector(0, 0, -(R - Len_paddle / 2)), size=vector(dr, H, Len_paddle), color=color.orange))
    box(pos=vector(0, -H / 2 - dr / 2, 0), size=vector(2.2 * R, dr, 2.2 * R), color=color.white, opacity=0.7)
    obj = compound(quads)
    obj.omega = 0
    obj.theta = 0
    return obj


demon = make_demon()
Demon_theta = [3 * pi / 2]     # x-z plane
demon_theta0 = Demon_theta[0]
demon_omega0 = 0
demon.theta = demon_theta0
demon.omega = demon_omega0
demon.rotate(angle=demon.theta, axis=vector(0, 1, 0), origin=vector(0, 0, 0))

# make the rods and axle

c = color.gray(0.9)
w = 0.05 * R
# rod = cylinder(pos=vector(0, -4, -0.55 * R), radius=Dia_axle / 2, axis=vector(0, 8, 0), color=color.red)
rodupperVo = cylinder(pos=vector(0, 1.5 * H, -0.55 * R), radius=Dia_axle / 2, axis=vector(0, 4, 0), color=color.red)
rodupperHo = cylinder(pos=vector(0, 1.5 * H + Dia_axle / 2, -0.55 * R), radius=Dia_axle / 2,
                       axis=vector(0, 0, 0.45 * R), color=color.red)
rodlowerVo = cylinder(pos=vector(0, -1.5 * H, -0.55 * R), radius=Dia_axle / 2, axis=vector(0, -4, 0), color=color.red)
rodlowerHo = cylinder(pos=vector(0, -1.5 * H - Dia_axle / 2, -0.55 * R), radius=Dia_axle / 2,
                     axis=vector(0, 0, 0.45 * R), color=color.red)
rodupperVpi = cylinder(pos=vector(0, 1.5 * H, 0.55 * R), radius=Dia_axle / 2, axis=vector(0, 4, 0), color=color.red)
rodupperHpi = cylinder(pos=vector(0, 1.5 * H + Dia_axle / 2, 0.55 * R), radius=Dia_axle / 2,
                       axis=vector(0, 0, -0.45 * R), color=color.red)
rodlowerVpi = cylinder(pos=vector(0, -1.5 * H, 0.55 * R), radius=Dia_axle / 2, axis=vector(0, -4, 0), color=color.red)
rodlowerHpi = cylinder(pos=vector(0, -1.5 * H - Dia_axle / 2, 0.55 * R), radius=Dia_axle / 2,
                     axis=vector(0, 0, -0.45 * R), color=color.red)
axle = cylinder(pos=vector(0, -4, 0), radius=Dia_axle / 2, axis=vector(0, 8, 0), color=color.white)

# make the binary-reference sequence

def make_bit(b:bool):
    if b == False:
        barH = box(pos=vector(H / 2 + dr, H / 2 + H / 3, 0), size=vector(H, H / 4, dr), color=paddle_color)
        barV = box(pos=vector(H, H / 3, 0), size=vector(H / 4, -H, dr))
        bitbar = compound([barH, barV])
    elif b == True:
        barH = box(size=vector(-H / 2, H / 2 + H / 3, 0), color=paddle_color)
        barV = box(pos=vector(-H, H / 3, 0), size=vector(-H / 4, -H, dr))
        bitbar = compound([barH, barV])
    return bitbar


