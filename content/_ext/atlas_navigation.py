"""Render the complete textbook sidebar from its authored TOC once per build.

The theme's generic resolver repeatedly copies the global Docutils tree for
each of the hundreds of pages. The Atlas already has an explicit ordered TOC;
reuse that tree and let the theme retain the current page's own heading TOC.
"""
from __future__ import annotations

from pathlib import Path
import yaml


def _sidebar_context(app, pagename, templatename, context, doctree):
    source = Path(app.srcdir)
    if not hasattr(app, '_atlas_sidebar'):
        app._atlas_sidebar = yaml.safe_load((source/'_toc.yml').read_text(encoding='utf-8'))
    toc = app._atlas_sidebar

    def item(node):
        document = node['file']
        title = node.get('title')
        if not title:
            title_node = app.env.titles.get(document)
            title = title_node.astext() if title_node is not None else document
        children = [item(child) for child in node.get('sections', [])]
        return {'file': document, 'title': title.replace('`', ''),
                'current': document == pagename,
                'active': document == pagename or any(child['active'] for child in children),
                'children': children}

    context['atlas_sidebar_root'] = toc['root']
    context['atlas_sidebar_parts'] = [
        {'caption': part['caption'], 'chapters': [item(node) for node in part['chapters']]}
        for part in toc['parts']
    ]


def setup(app):
    app.connect('html-page-context', _sidebar_context)
    return {'version': '1.0', 'parallel_read_safe': True, 'parallel_write_safe': True}
