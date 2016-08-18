import os, sys
from subprocess import Popen, call, DEVNULL
from PIL import Image
import shutil
from string import digits, ascii_lowercase, ascii_uppercase
import traceback

arr62 = digits + ascii_lowercase + ascii_uppercase

def getsz(w, h):
    minpad = 10000000
    bestSz = 25
    # i : how many we tile with
    for i in range(25,75):
        rw = i * ((w + i - 1) // i)
        rh = i * ((h + i - 1) // i)
        if rw*rh - w*h <= minpad:
            minpad = rw*rh - w*h
            bestSz = i
    rw = bestSz * ((w + bestSz - 1) // bestSz)
    rh = bestSz * ((h + bestSz - 1) // bestSz)
    return (bestSz, rw, rh)

def ffCall(inf, outf, filters, sync=False):
    print(filters)
    # make less verbose, silently overwrite
    baseSettings = ['ffmpeg', '-hide_banner', '-y', '-loglevel', 'panic']
    # set input video, add video filter param
    allArgs = baseSettings + ['-i', inf, '-filter:v', filters, outf]

    try:
        if sync:
            call(allArgs, stdin=DEVNULL, stdout=DEVNULL)
        else:
            Popen(allArgs, stdin=DEVNULL, stdout=DEVNULL)
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        lStr = ''.join('!! ' + line for line in lines)
        with open('log.txt', 'a+') as log:
            log.write(lStr)

if __name__ == '__main__':
    print(sys.argv)
    if len(sys.argv) == 1 or not os.path.isdir(sys.argv[1]) or not \
            os.path.isfile(sys.argv[1] + '/' + sys.argv[1] + '.gif'):
        print("Invalid .gif argument")
        exit()
    f = sys.argv[1]
    os.chdir(f)
    gif = f + '.gif'
    dim = Image.open(gif).size
    print(dim)
    sz, w, h = getsz(dim[0], dim[1])
    print(sz, str(w) + "x" + str(h))

    uf = '__' + f + '__'
    ffCall(gif, '__' + gif, "pad={}:{}:0:0:white".format(w, h), True)
    os.remove(gif)
    for i in range(w // sz):
        for j in range(h // sz):
            ffCall('__' + gif, uf + arr62[i] + arr62[j] + '.gif',
                    "crop={}:{}:{}:{}".format(sz, sz, sz*i, sz*j), True)
    os.remove('__' + gif)
