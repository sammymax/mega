import os, sys
from subprocess import Popen, call, DEVNULL
import shutil
from string import digits, ascii_lowercase, ascii_uppercase
import traceback
import emojinator.upload as uploader

arr62 = digits + ascii_lowercase + ascii_uppercase

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

# python cut.py [gif name without file extension] [team name] [session cookie] [sz] [w] [h]
if __name__ == '__main__':
    print(sys.argv)
    if len(sys.argv) != 7 or not os.path.isdir(sys.argv[1]) or not \
            os.path.isfile(sys.argv[1] + '/' + sys.argv[1] + '.gif'):
        print("Bad arguments")
        exit()
    f = sys.argv[1]
    os.chdir(f)
    gif = f + '.gif'
    sz, w, h = int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
    print(sz, str(w) + "x" + str(h))

    uf = '__' + f + '__'
    ffCall(gif, '__' + gif, "pad={}:{}:0:0:white".format(w, h), True)
    os.remove(gif)
    for i in range(w // sz):
        for j in range(h // sz):
            ffCall('__' + gif, uf + arr62[i] + arr62[j] + '.gif',
                    "crop={}:{}:{}:{}".format(sz, sz, sz*i, sz*j), True)
    os.remove('__' + gif)
    os.chdir('..')
    gifArgs = [f + '/' + d for d in os.listdir(f)]
    uploader.main(sys.argv[2], sys.argv[3], gifArgs)
    shutil.rmtree(f)
