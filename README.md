# Google Chrome TTS Engine

This is a somewhat roundabout way to get the excellent Google TTS
engine to be available to me for general use. Since Chrome makes this
available, willing to read lots of text for free, this project aims to
make it possible to use Chrome externally to generate high-quality
text-to-speech.

I use this on a computer connected to an amplifier which drives
overhead speakers to make household announcements in response to Home
Automation events.

## Setup

In order to use this you need python3 and aiohttp. On most systems:

```bash
 $ pip3 install aiohttp
```

Now you need to run the server side app. The simplest way is:

```bash
 $ python3 webspeak.py
```

Next, point a Chrome browser at `http://localhost:5010`, if you are on
the same machine as `webspeak.py`. If not, use the IP address or
hostname of that box in the URL instead.

In chrome, you should see:

```
Status: Waiting for first request
```

Now, you're ready to ask for something to be spoken. The simplest way
to do this is with `curl` like this:

```bash
 $ curl -d "Say this for me" http://localhost:5010/say
```

If it works, you should see a response in your chrome browser and hear
it speak what you asked for.

## Integrating this to run all the time

For my setup, I run this in a headless VNC session on a dedicated
computer which has an audio output connected to an amplifier that
drives my speakers. Once it's running you can leave chrome in the
background and never have to look at it, but continue to feed it
things to say.