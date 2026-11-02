"""Serve assembled output at the real project prefix, safely within _site."""
from __future__ import annotations
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit,unquote

ROOT=Path(__file__).resolve().parents[1]
PREFIX='/JupyterLite-Learning-Atlas/'


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if urlsplit(self.path).path=='/':
            self.send_response(302);self.send_header('Location',PREFIX);self.end_headers();return
        if not urlsplit(self.path).path.startswith(PREFIX):self.send_error(404,'Use the project subpath');return
        super().do_GET()
    def translate_path(self,path):
        raw=unquote(urlsplit(path).path)
        relative=raw[len(PREFIX):] if raw.startswith(PREFIX) else ''
        target=(ROOT/'_site'/relative).resolve()
        if not target.is_relative_to(ROOT/'_site'):return str(ROOT/'_site/__not_found__')
        return str(target)


def main():
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8000);args=p.parse_args()
    assert (ROOT/'_site/index.html').exists(),'Run python scripts/build.py first'
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    print(f'Preview http://localhost:{args.port}{PREFIX}',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()


if __name__=='__main__':main()
