# No Imports Allowed!

def backwards(sound):
    return {'rate':sound['rate'], 'samples': list(reversed(sound['samples']))}


def mix(sound1, sound2, p):
    if sound1['rate'] != sound2['rate']:
        return None
    # make the mixed sound the length of the shortest one
    length = min( len(sound1['samples']), len(sound2['samples']) )
    # multiply the first sample by p, the second by (1-p) and add them
    samples = [ sound1['samples'][i]*p + sound2['samples'][i]*(1-p) for i in range(length)]
    return {'rate':sound1['rate'], 'samples':samples}

def convolve(sound, kernel):
    # first find length of each list
    length = len(sound['samples']) + len(kernel) - 1
    sound_len = len(sound['samples'])
    # create list that will hold our result
    output = [0] * length
    # then for each non-zero element in the kernel...
    for i in range(len(kernel)):
        curr_list = [0]*i + [element*kernel[i] for element in sound['samples']] + [0]*(length-sound_len-i)

        output = list(output[index] + curr_list[index] for index in range(length))
    return {'rate':sound['rate'], 'samples':output}

def echo(sound, num_echoes, delay, scale):
    sample_delay = round(delay * sound['rate'])
    # copy original sound and add additional length
    output = sound['samples'] + [0]*(num_echoes*sample_delay)
    length = len(output)
    
    # First iteration
    echo = [0]*sample_delay + output
    echo = [element*scale for element in echo]
    # add it to the output 
    print(len(echo), len(output))
    output = list(output[index] + echo[index] for index in range(length))
    # repeat numb_echoes of times
    for numb in range(num_echoes-1):
        echo = [0]*sample_delay + echo
        echo = [element*scale for element in echo]
        output = list(output[index] + echo[index] for index in range(length))
    
    return {'rate':sound['rate'], 'samples':output}


def pan(sound):
    # make copies of the left and right parts of the sound
    left = sound['left'] + []
    right = sound['right'] + []
    length = len(sound['left'])
    # for every sample...
    for i in range(length):
        # scale right and left by i/(N-1) and 1 - i/(N-1), respectively
        right[i] *= i/(length - 1)
        left[i] *= 1 - i/(length - 1)
    
    return {'rate': sound['rate'], 'left': left, 'right': right}

def remove_vocals(sound):
    # make copies of left and right parts of sound
    diff = sound['left'] + []
    right = sound['right'] + []
    # for every left and right sound...
    for i in range(len(right)):
        # subtract the right sound from the left one
        diff[i] -= right[i]
    # return a dictionary holding the difference
    return {'rate': sound['rate'], 'samples':diff}


def bass_boost_kernel(N, scale=0):
    """
    Construct a kernel that acts as a bass-boost filter.

    We start by making a low-pass filter, whose frequency response is given by
    (1/2 + 1/2cos(Omega)) ^ N

    Then we scale that piece up and add a copy of the original signal back in.
    """
    # make this a fake "sound" so that we can use the convolve function
    base = {'rate': 0, 'samples': [0.25, 0.5, 0.25]}
    kernel = {'rate': 0, 'samples': [0.25, 0.5, 0.25]}
    for i in range(N):
        kernel = convolve(kernel, base['samples'])
    kernel = kernel['samples']

    # at this point, the kernel will be acting as a low-pass filter, so we
    # scale up the values by the given scale, and add in a value in the middle
    # to get a (delayed) copy of the original
    kernel = [i * scale for i in kernel]
    kernel[len(kernel)//2] += 1

    return kernel


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds

import io
import wave
import struct

def load_wav(filename, stereo=False):
    """
    Given the filename of a WAV file, load the data from that file and return a
    Python dictionary representing that sound
    """
    f = wave.open(filename, 'r')
    chan, bd, sr, count, _, _ = f.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {'rate': sr}

    if stereo:
        left = []
        right = []
        for i in range(count):
            frame = f.readframes(1)
            if chan == 2:
                left.append(struct.unpack('<h', frame[:2])[0])
                right.append(struct.unpack('<h', frame[2:])[0])
            else:
                datum = struct.unpack('<h', frame)[0]
                left.append(datum)
                right.append(datum)

        out['left'] = [i/(2**15) for i in left]
        out['right'] = [i/(2**15) for i in right]
    else:
        samples = []
        for i in range(count):
            frame = f.readframes(1)
            if chan == 2:
                left = struct.unpack('<h', frame[:2])[0]
                right = struct.unpack('<h', frame[2:])[0]
                samples.append((left + right)/2)
            else:
                datum = struct.unpack('<h', frame)[0]
                samples.append(datum)

        out['samples'] = [i/(2**15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Given a dictionary representing a sound, and a filename, convert the given
    sound into WAV format and save it as a file with the given filename (which
    can then be opened by most audio players)
    """
    outfile = wave.open(filename, 'w')

    if 'samples' in sound:
        # mono file
        outfile.setparams((1, 2, sound['rate'], 0, 'NONE', 'not compressed'))
        out = [int(max(-1, min(1, v)) * (2**15-1)) for v in sound['samples']]
    else:
        # stereo
        outfile.setparams((2, 2, sound['rate'], 0, 'NONE', 'not compressed'))
        out = []
        for l, r in zip(sound['left'], sound['right']):
            l = int(max(-1, min(1, l)) * (2**15-1))
            r = int(max(-1, min(1, r)) * (2**15-1))
            out.append(l)
            out.append(r)

    outfile.writeframes(b''.join(struct.pack('<h', frame) for frame in out))
    outfile.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place to put your
    # code for generating and saving sounds, or any other code you write for
    # testing, etc.

    # here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file)
    # hello = load_wav('sounds/mystery.wav')
    # write_wav(backwards(hello), 'mystery_reversed.wav')
    # synth = load_wav('sounds/synth.wav')
    # water = load_wav('sounds/water.wav')
    # write_wav(mix(synth, water, 0.2), "mixed_synth_and_water.wav")
    # s = {
    # 'rate': 30,
    # 'samples': [-5, 0, 2, 3, 4],
    # }
    # k = [0, 1, 0, 0, 3]
    # print(convolve(s, k)["samples"])
    # s = load_wav("sounds\ice_and_chilli.wav")
    # k = bass_boost_kernel(1000, 1.5)
    # write_wav(convolve(s, k), "convolved_ice_and_chilli.wav")
    # s = {
    # 'rate': 8,
    # 'samples': [1, 2, 3, 4, 5],
    # }    
    # s2 = echo(s, 2, 0.4, 0.2)
    # print(s2['samples'])
    chord = load_wav("sounds/chord.wav")
    echo(chord, 5, 0.3, 0.6)
    # car = load_wav("sounds/car.wav", stereo=True)
    # write_wav(pan(car), "car_pan.wav")
    # lookout_mountain = load_wav("sounds/lookout_mountain.wav", stereo=True)
    # write_wav(remove_vocals(lookout_mountain), "no_vocals_lookout_mountain.wav")