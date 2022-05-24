# Audio-Processing-Functions
Group of Functions to manipulate audio files

## Contents of Each file:
* Sounds: Contains .wav files that one can mess with using the functions implemented
* Test Inputs and Test Outputs: Contains pickle objects that contain the correct files that are supposed to be created once an audio file is manipulated with the functions implemented.
* Test.py: Contains several test cases for the function to ensure they work. Takes files from test input, manipulates them with the audio functions, and then compares them with test outputs. 
* Lab.py: Contains the implementation of the functions to manipulate audio files. 

## Representing Sound
In physics, when we talk about a sound, we are talking about waves of air pressure. When a sound is generated, a sound wave consisting of alternating areas of relatively high pressure ("compressions") and relatively low air pressure ("rarefactions") moves through the air.

When we use a microphone to capture a sound digitally, we do so by making periodic measurements of an electrical signal proportional to this air pressure. Each individual measurement (often called a "sample") corresponds to the air pressure at a single moment in time; by taking repeated measurements at a constant rate (the "sampling rate," usually measured in terms of the number of samples captured per second), these measurements together form a representation of the sound by approximating how the air pressure was changing over time.

When a speaker plays back that sound, it does so by converting these measurements back into waves of alternating air pressure (by moving a diaphragm proportionally to those captured measurements). In order to faithfully represent a sound, we need to know two things: both the sampling rate and the samples that were actually captured.

For sounds recorded in mono, each sample is a positive or negative number corresponding to the air pressure at a point in time. For sounds recorded in stereo, each sample can be thought of as consisting of two values: one for the left speaker and one for the right.

## Python Representation
Our Pythonic representation of a mono sound will consist of a dictionary with two key/value pairs:

'rate': the sampling rate (as an int), in units of samples per second
'samples': a list containing samples, where each sample is a float
For example, the following is a valid sound:
```
s = {
    'rate': 8000,
    'samples': [1.00, 0.91, 0.67, 0.31, -0.10, -0.50, -0.81, -0.98, -0.98, -0.81],
}
```
## Functions Implemented
### Backwards Audio: 
This function takes in a mono sound (using the representation described above, as a dictionary) as its input and returns a new mono sound that is the reversed version of the original (but without modifying the object representing the original sound!).
### Mixing Audio: 
This function takes three inputs: two sounds (in our dictionary representation) and a "mixing parameter" $p$ (a float such that $0 \leq p \leq 1$).

The resulting sound should take $p$ times the samples in the first sound and $1-p$ times the samples in the second sound, and add them together to produce a new sound.

The two input sounds should have the same sampling rate. If you are provided with sounds of two different sampling rates, you should return `None` instead of returning a sound.

However, despite having the same sampling rate, the input sounds might have different durations. The length of the resulting sound should be the minimum of the lengths of the two input sounds, so that we are guaranteed a result where we can always hear both sounds (it would be jarring if one of the sounds cut off in the middle).

### Convolutional Filters
It turns out that a wide variety of interesting effects can be applied to audio using an operation known as convolution. By applying this operation to the samples in a sound and a "kernel" (another list of samples), we can achieve a wide variety of effects.

In its most concise mathemetical form, convolution is usually expressed in the following way:

$$ 
y[n] = (x*h)[n] = \sum^{\infty}_{m=-\infty}x[m]h[n-m]
$$

That is to say, the value $y[n]$ at sample number $n$ in the output $(y)$ can be computed using the sum on the right (where $x$ represents the samples in the input sound and $h$ represents the samples in the kernel).

For each nonzero value $h[n]$ in our kernel, we create a copy of the samples in the input sound, shifted by $n$ and scaled by $h[n]$; and adding these new lists of signals together give us our output. The total length of the output should be the length of the samples in the input sound, plus the length of the samples in the kernel, minus one.

For example, consider the following sound:
```
s = {
  'rate': 20,
  'samples': [2, 5, 0, 3]
}
```
and consider convolving this signal with the following kernel:
```
kernel = [3, -2]
```
Here, we'll walk through the process of computing the result of `convolve(s, kernel)`, using the process described above. We know that our output is eventually going to have 5 samples in it (the length of the samples, plus the length of the kernel, minus 1).

The `3` at index `0` contributes values to our output samples like a version of the input samples scaled by `3` and shifted by `0`: `[6, 15, 0, 9, 0]`

The `-2` at index `1` contributes values to our output samples like a version of the input samples scaled by `-2` and shifted by `1`: `[0, -4, -10, 0, -6]`.

Adding those together, we get our overall result: `[6, 11, -10, 9, -6]`. These represent the samples of our output sound (which should have the same rate as the input).

### Echo

Next, we'll implement a classic effect: an echo filter. We simulate an echo by starting with our original sound, and adding one or more additional copies of the sound, each delayed by some amount and scaled down so as to be quieter.

We implemented this filter as a function called 'echo(sound, num_echoes, delay, scale)'. This function should take the following arguments:

* `sound`: a dictionary representing the original sound
* `num_echoes`: the number of additional copies of the sound to add
* `delay`: the amount (in **seconds**) by which each "echo" should be delayed
* `scale`: the amount by which each echo's samples should be scaled

First, we determine how many samples each copy should be delayed by. We used Python's `round` function: `sample_delay = round(delay * sound['rate'])`

We should add in a delayed and scaled-down copy of the sound's samples (scaled by the given `scale` value and offset by `sample_delay` samples). Note that each new copy should be scaled down more than the one preceding it (the first should be multiplied by `scale`, the second by a total of `scale**2`, the third by a total of `scale**3`, and so on).

All told, the output is `num_echoes * sample_delay` samples longer than the input in order to avoid cutting off any of the echoes.

## Stereo Effects
For the last two audio effects, we focused on stereo sounds (files that have separate lists of samples for the left and right speakers.

Our Pythonic representation of a stereo sound consisted of a dictionary with three key/value pairs:

* `'rate'`: the sampling rate (as an int), in units of samples per second
* `'left'`: a list containing samples for the left speaker
* `'right'`: a list containing samples for the right spearker

For example, the following is a valid stereo sound:
```
s = {
    'rate': 8000,
    'left': [0.00, 0.59, 0.95, 0.95, 0.59, 0.00, -0.59, -0.95, -0.95, -0.59],
    'right': [1.00, 0.91, 0.67, 0.31, -0.10, -0.50, -0.81, -0.98, -0.98, -0.81],
}
```

### Pan
We achieve this effect by adjusting the volume in the left and right channels separately, so that the left channel starts out at full volume and ends at 0 volume (and vice versa for the right channel).

In particular, if our sound is N samples long, then we scale the first sample in the right channel by 0, the second by $\frac{1}{N-1}$, the third by $\frac{2}{N-1}$,... and the last by 1. At the same time, we scale the first sample in the left channel by 1, the second by $1 - \frac{1}{N-1}$, the third by $1 - \frac{2}{N-1}$,... and the last by 0.

### Removing Vocal from Music
For each sample in the (stereo) input sound, we compute (left-right), i.e., the difference between the left and right channels at that point in time, and use the result as the corresponding sample in the (mono) output sound.

Indeed, it seems weird that subtracting the left and right channels should remove vocals! So how does this work? And why does it only work on certain songs? Well, it comes down to a little bit of a trick of the way songs tend to be recorded. Typically, many instruments are recorded so that they favor one side of the stereo track over the other (for example, the guitar track might be slightly off to one side, the bass slightly off to the other, and various drums at various "positions" as well). By contrast, vocals are often recorded mono and played equally in both channels. When we subtract the two, we are removing everything that is the same in both channels, which often includes the main vocal track (and often not much else). However, there are certainly exceptions to this rule; and, beyond differences in recording technique, certain vocal effects like reverb tend to introduce differences between the two channels that make this technique less effective.
