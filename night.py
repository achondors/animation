from __future__ import division

import math
import numpy as np
import matplotlib as mpl

from matplotlib import cm
from matplotlib import pyplot as plt
from matplotlib import animation

""" A snowy night animation

Note that everything is based on virtual seconds passed from 00:00
(something like epoch() in Linux).

Since we want our animation to start at 20:00, we add an offset
to the timer (i.e. MyTime()) during initialization. The animation
ends at 06:00 in the morning, that is 10 "virtual" hours. Our
animation should last 35 seconds. To have a nice animation we choose
frame interval of 100 msec.

Note that the animation is done with MyDay() object that re-draws
all matplotlib's components upon each tick (frame); it cleans up
old before adding new.

The components used are:

  * Timer (text)
  * Stars (scatter)
  * Snow (scatter)
  * Messages (text)

"""

# NOTE: Workaround for issue
# https://github.com/matplotlib/matplotlib/issues/1008/
# so that we should not patch
# /usr/share/pyshare/matplotlib/figure.py...
mpl.rcParams["savefig.facecolor"] = "black"
mpl.rcParams["savefig.edgecolor"] = "black"

# Size related constants
FIGSIZE = 10, 5  # inches
XMIN, XMAX = 0, 20
YMIN, YMAX = 0, 10
XCENTER, YCENTER = 10, 5

# Time related constants
REAL_DURATION = 15  # seconds of our final animation
VIRTUAL_DURATION = 60 * 60 * 6  # From 20:00 to 02:00
INTERVAL = 100 # msec between frames
FRAMES = (REAL_DURATION * 1000) // INTERVAL  # total frames of our final animation
FPS = FRAMES // REAL_DURATION

# for each frame how many virtual seconds have passed
VIRTUAL_SECS_PER_FRAME = VIRTUAL_DURATION / REAL_DURATION * INTERVAL / 1000

# Events during the day(in seconds)
MSG_TIMESTAMP = 82800  # 23:00

STARS = 50

class MyTime(object):
    def __init__(self, offset=0):
        self.ticks = 0
        self._seconds = float(offset)

    def tick(self):
        """Invoked for every frame."""
        print "Tick...", self.ticks, self._seconds, self.seconds
        self.ticks += 1
        self._seconds += VIRTUAL_SECS_PER_FRAME  # Virtual seconds added

    @property
    def seconds(self):
        """Virtual seconds passed after epoch (00:00)."""
        return int(self._seconds)

    def __str__(self):
        seconds = self.seconds
        h = (seconds // 3600) % 24  # Find the hour of the day
        m = seconds % 3600 // 60
        s = seconds % 60
        return "%02d:%02d:%02d" % (h, m, s)


class MyDay(object):
    def __init__(self, time):
        self.time = time
        self.timer = None
        self.msg = None
        self.snowfall = None
        self.snow = None
        self.stars = None
        self.add_stars()

    @property
    def now(self):
        return self.time.seconds

    def refresh(self):
        self.cleanup()
        self.add_timer()
        self.add_msg()
        self.add_snow()

    def cleanup(self):
        """Cleanup only those that are not static."""
        if self.timer:
            print "Cleanup timer..."
            self.timer.remove()
            self.timer = None
        if self.snowfall:
            print "Cleanup snow..."
            self.snowfall.remove()
            self.snowfall = None

    def add_timer(self):
        print "Adding timer %s..." % str(self.time)
        self.timer = plt.text(XMAX - 1, YMAX - 0.5,
                              str(self.time),
                              fontsize=20, color="white",
                              horizontalalignment='center',
                              verticalalignment='center')

    def add_msg(self):
        if self.now < MSG_TIMESTAMP:
            return

        self.msg = plt.text(XCENTER, YCENTER,
                            "Look! It's snowing!!!",
                            fontsize=40, color="yellow",
                            horizontalalignment='center',
                            verticalalignment='center')

    def add_stars(self):
        """Do not re-add stars as they are not moving"""
        print "Adding stars..."
        xpos = np.random.uniform(XMIN, XMAX, STARS)
        ypos = np.random.uniform(YCENTER, YMAX, STARS)
        sizes = np.random.uniform(10, 50, STARS)
        self.stars = plt.scatter(xpos, ypos, s=sizes, marker="*",
                                 facecolor="silver", edgecolor="silver")

    def add_snow(self):
        """Always remove snowfall but not snow on the ground."""
        print "Adding snowfall..."
        flakes = np.random.randint(1, 20)
        xpos = np.random.uniform(XMIN, XMAX, flakes)
        ypos = np.random.uniform(YMIN, YMAX, flakes)
        self.snowfall = plt.scatter(xpos, ypos, s=10, marker="*",
                                    facecolor="snow", edgecolor="snow")

        print "Adding snow..."
        xpos = np.random.uniform(XMIN, XMAX, 10)
        ypos = np.random.uniform(YMIN, 0.3, 10)
        self.snow = plt.scatter(xpos, ypos, s=10, marker="*",
                                facecolor="snow", edgecolor="snow")


# First set up the figure, the axis, and the plot element we want to animate
fig = plt.figure(figsize=FIGSIZE, facecolor="black", edgecolor="black")
fig.set_figheight(10)
fig.set_figwidth(20)


# First argument is [left, bottom, width, height] in normalized (0, 1) units
ax = plt.axes([0, 0, 1, 1], xlim=(XMIN, XMAX), ylim=(YMIN, YMAX), frameon=False)

# Initialize global variables
# We initialize our timer at 20:00
time = MyTime(offset=72000)
day = MyDay(time)

# Animation function. This is called sequentially for every singl frame;
# that is for every second of our day!
def animate(i):
    time.tick()
    day.refresh()
    return []

# Call the animator. blit=True means only re-draw the parts that have changed.
# Here we redraw everything...
print "Start animation with %s frames and %s interval" % (FRAMES, INTERVAL)
anim = animation.FuncAnimation(fig, animate, repeat=False, blit=False,
                               frames=FRAMES, interval=INTERVAL)

#plt.show()

print "Saving it with fps=%s..." % FPS
anim.save("night.mp4", fps=FPS)
