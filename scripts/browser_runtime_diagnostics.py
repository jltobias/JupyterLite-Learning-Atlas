"""Private, credential-free diagnostics and executed-cell completion detection."""
import re
from urllib.parse import urlsplit, urlunsplit


def sanitized_url(value):
    try:
        parts=urlsplit(value)
        if parts.scheme not in {'http','https'}:return parts.scheme+':[redacted]' if parts.scheme else '[relative URL]'
        host=parts.hostname or ''
        if ':' in host:host='['+host+']'
        if parts.port:host+=':'+str(parts.port)
        return urlunsplit((parts.scheme,host,parts.path,'',''))
    except (TypeError,ValueError):return '[invalid URL]'


def sanitized_text(value):
    text=re.sub(r'https?://[^\s<>\"\')]+',lambda m:sanitized_url(m[0]),str(value))
    text=re.sub(r'(?i)\b(authorization|api[_-]?key|access[_-]?token|token|password|secret|credentials?)\s*[:=]\s*(?:bearer\s+)?[^\s,;]+',r'\1=[redacted]',text)
    return re.sub(r'(?i)\bbearer\s+[^\s,;]+','Bearer [redacted]',text)[:5000]


def attach_diagnostics(context):
    diagnostics={'failed_requests':[],'http_errors':[],'console':[],'page_errors':[]}
    def append(key,value):
        if len(diagnostics[key])<200:diagnostics[key].append(value)
    context.on('requestfailed',lambda request:append('failed_requests',{
        'url':sanitized_url(request.url),'method':request.method,'resource_type':request.resource_type,
        'failure':sanitized_text(request.failure)}))
    context.on('response',lambda response:append('http_errors',{'url':sanitized_url(response.url),'status':response.status}) if response.status>=400 else None)
    def console(message):
        text=message.text
        if message.type in {'error','warning'} or re.search(r'(?i)piplite|micropip|pyodide|\.whl|failed to load|\bloading\b|\bloaded\b|ATLAS_PACKAGE',text):
            location=message.location
            append('console',{'type':message.type,'text':sanitized_text(text),'url':sanitized_url(location.get('url','')),'line':location.get('lineNumber')})
    context.on('console',console)
    context.on('weberror',lambda error:append('page_errors',sanitized_text(error.error)))
    return diagnostics


EXECUTION_STATE_JS=r'''({cell, marker, errorMarker}) => {
    const outputs=[...cell.querySelectorAll('.jp-OutputArea-output')];
    for (const output of outputs) {
        const text=output.innerText || output.textContent || '';
        if (text.includes(errorMarker)) return {status:'error',text,mime:output.getAttribute('data-mime-type')};
    }
    for (const output of outputs) {
        const mime=output.getAttribute('data-mime-type') || '';
        const text=output.innerText || output.textContent || '';
        if (mime==='application/vnd.jupyter.error' || output.classList.contains('jp-mod-error') ||
            (mime==='application/vnd.jupyter.stderr' && /Traceback\s*\(\s*most\s*recent\s*call\s*last\s*\)/.test(text)))
            return {status:'error',text,mime};
    }
    return outputs.some(output=>(output.innerText || output.textContent || '').includes(marker)) ? {status:'passed'} : false;
}'''


def guarded_execution(source,error_marker):
    import textwrap
    return ('try:\n'+textwrap.indent(source,'    ')+
        '\nexcept BaseException as _atlas_execution_error:\n'+
        f'    print({error_marker!r} + " " + type(_atlas_execution_error).__name__ + ": " + str(_atlas_execution_error), flush=True)\n'+
        '    raise\n')
