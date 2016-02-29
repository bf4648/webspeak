#!/usr/bin/env python3

import argparse
import aiohttp
import aiohttp.server
import aiohttp.websocket
import asyncio
import json
import logging
import os
import subprocess


LOG = logging.getLogger()


# This is hacky, but only support one set of global variables for
# simplicity right now
WS_WRITER = None
ARGS = None


def set_volume(percent):
    subprocess.call(['pactl', '--', 'set-sink-volume', '0', '%i%%' % percent])


def play_sound(sound):
    if os.path.exists(sound):
        subprocess.call(['paplay', '--volume=32768', sound])
    else:
        LOG.error('Unable to find sound file `%s`' % sound)


class Handler(aiohttp.server.ServerHttpProtocol):
    def _get_static(self, message):
        fn = message.path.split('/')[-1]
        fn = os.path.join('static', fn)
        try:
            with open(fn) as f:
                resp = aiohttp.Response(self.writer, 200)
                resp.send_headers()
                resp.write(f.read().encode())
                LOG.debug('200 GET %s' % fn)
        except FileNotFoundError:
            resp = aiohttp.Response(self.writer, 404)
            resp.send_headers()
            LOG.error('404 GET %s' % fn)
        return resp

    @asyncio.coroutine
    def _do_websocket(self, message, payload):
        global WS_WRITER

        status, headers, parser, writer, protocol = \
            aiohttp.websocket.do_handshake(message.method,
                                           message.headers,
                                           self.transport)
        resp = aiohttp.Response(self.writer, status,
                                http_version=message.version)
        resp.add_headers(*headers)
        resp.send_headers()

        dataqueue = self.reader.set_parser(parser)

        LOG.debug('New websocket connection')

        if WS_WRITER:
            LOG.warning('Warning, another client was listening!')
        WS_WRITER = writer

        while True:
            try:
                msg = yield from dataqueue.read()
            except:
                break

            if msg.tp == aiohttp.websocket.MSG_PING:
                writer.pong()
            elif msg.tp == aiohttp.websocket.MSG_TEXT:
                # Ignore
                pass
            elif msg.tp == aiohttp.websocket.MSG_CLOSE:
                break

        WS_WRITER = None
        LOG.debug('Disconnected')

    @asyncio.coroutine
    def _do_say(self, message, payload):
        text = yield from payload.read()
        event = {'speak': text.decode()}
        if WS_WRITER:
            if ARGS.tone:
                play_sound(ARGS.tone)
            WS_WRITER.send(json.dumps(event).encode())
            LOG.debug('Queued %r' % text)
            resp = aiohttp.Response(self.writer, 200)
        else:
            LOG.error('No waiting speaker!')
            resp = aiohttp.Response(self.writer, 500)
        resp.send_headers()
        return resp

    @asyncio.coroutine
    def handle_request(self, message, payload):
        upgrade = 'websocket' in message.headers.get('upgrade', '').lower()
        if upgrade:
            yield from self._do_websocket(message, payload)
            return
        elif message.path.startswith('/static/'):
            resp = self._get_static(message)
        elif message.path.startswith('/say'):
            resp = yield from self._do_say(message, payload)
        else:
            resp = aiohttp.Response(self.writer, 302)
            resp.add_header('Location', '/static/index.html')
            resp.send_headers()
            LOG.debug('302 GET %s' % message.path)
        yield from resp.write_eof()


def main():
    global ARGS
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('--listen', default='0.0.0.0',
                        help='Address to listen on')
    parser.add_argument('--port', default=5010,
                        type=int,
                        help='Port to listen on')
    parser.add_argument('--tone', default=None,
                        help='Play this sound before speaking')
    parser.add_argument('--pulseaudio', default=False,
                        action='store_const', const=True,
                        help='Use pulseaudio to adjust volume and play tone')
    ARGS = parser.parse_args()

    if ARGS.pulseaudio:
        LOG.info('Setting volume to 60%')
        set_volume(60)

    loop = asyncio.get_event_loop()
    f = loop.create_server(Handler, ARGS.listen, ARGS.port)
    server = loop.run_until_complete(f)
    loop.run_forever()


if __name__ == '__main__':
    import sys
    sys.exit(main())
