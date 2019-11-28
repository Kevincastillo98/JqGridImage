# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1574946505.6483376
_enable_loop = True
_template_filename = '/home/kevin/Documentos/Jqgrid/myprojectname/myprojectname/templates/data.mak'
_template_uri = '/home/kevin/Documentos/Jqgrid/myprojectname/myprojectname/templates/data.mak'
_source_encoding = 'utf-8'
from markupsafe import escape_silent as escape
_exports = ['title']


def _mako_get_namespace(context, name):
    try:
        return context.namespaces[(__name__, name)]
    except KeyError:
        _mako_generate_namespaces(context)
        return context.namespaces[(__name__, name)]
def _mako_generate_namespaces(context):
    pass
def _mako_inherit(template, context):
    _mako_generate_namespaces(context)
    return runtime._inherit_from(context, 'local:templates.master', _template_uri)
def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        __M_writer = context.writer()
        __M_writer('\n\n')
        __M_writer('\n\n\n\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        __M_writer('\nPeticiones al API del clima\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"filename": "/home/kevin/Documentos/Jqgrid/myprojectname/myprojectname/templates/data.mak", "uri": "/home/kevin/Documentos/Jqgrid/myprojectname/myprojectname/templates/data.mak", "source_encoding": "utf-8", "line_map": {"28": 0, "33": 1, "34": 5, "40": 3, "44": 3, "50": 44}}
__M_END_METADATA
"""
