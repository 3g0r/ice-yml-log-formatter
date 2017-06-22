import logging
import re
import traceback
from collections import ChainMap

from yaml import safe_dump

try:
    from yaml import CDumper as Dumper, CSafeDumper as SafeDumper
except ImportError:
    from yaml import Dumper, SafeDumper

import Ice

regxp = re.compile(r'^(.+)$', re.MULTILINE | re.UNICODE)


def indentation(text, space_size=2):
    space = ' ' * space_size
    return regxp.sub(rf'{space}\1', text)


def to_plain_objects(any_value, depth=0):
    if any_value is Ice.Unset:
        return ''

    if isinstance(any_value, Ice.Identity):
        return Ice.identityToString(any_value)

    if isinstance(any_value, Ice.Object):
        return dict(ChainMap({'ice_id': any_value.ice_id()},
                             {k: to_plain_objects(v, depth + 1)
                              for k, v in any_value.__dict__.items()}))

    if depth >= 2:
        return any_value

    if isinstance(any_value, list):
        return [to_plain_objects(v, depth) for v in any_value]

    if type(any_value) is dict:
        return {k: to_plain_objects(v, depth + 1)
                for k, v in any_value.items()}

    return any_value


def get_request_context(current):
    if not current:
        return {}

    return dict(
        iceRequestId=current.requestId,
        iceOperation=current.operation,
        iceIdentity=Ice.identityToString(current.id),
    )


def get_context_string(record):
    context = get_request_context(record.get('ice_current', None))

    if record.get('context'):
        context = {**context,
                   'context': dict(record.get('context', {}))}

    if context:
        return safe_dump(
            to_plain_objects(context),
            default_flow_style=False,
            allow_unicode=True)


class YAMLLogFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        logging.Formatter.__init__(self, *args, **kwargs)

    def formatException(self, ei):
        """
        Format and return the specified exception information as a string.

        This default implementation just uses
        traceback.print_exception()
        """
        if ei == (None, None, None):
            return ''

        exc_type, exc_value, exc_traceback = ei

        exc_traceback = traceback.extract_tb(exc_traceback)

        message = ''
        if isinstance(exc_value, Ice.Exception):
            exc_type = exc_value.ice_name()
            message = vars(exc_value).get('message')
            if message is Ice.Unset:
                message = ''
        elif isinstance(exc_value, Exception):
            exc_type = exc_type.__name__
            message = str(exc_value)

        if message:
            message = f': {message}'

        error_data = {key: value
                      for key, value in vars(exc_value).items()
                      if key != 'message'}

        if error_data:
            info = indentation(
                safe_dump(
                    {'error_data': to_plain_objects(error_data)},
                    default_flow_style=False,
                    allow_unicode=True))
        else:
            info = ''

        return (f'Error: {exc_type}{message}\n' +
                info +
                indentation('stack_trace:\n') +
                indentation('\n'.join(exc_traceback.format()), 4))

    def formatMessage(self, record):
        return self.record_to_string(record)

    def format(self, record):
        """Formats a log record and serializes to YAML"""
        return self.record_to_string(record)

    def record_to_string(self, record):
        message = self._style.format(record)
        context = None
        try:
            context = get_context_string(vars(record))
        except Exception as e:
            print(e)
            print(traceback.extract_tb(e.__traceback__).format())

        if context:
            info = f'\n{indentation(context)}'
        else:
            info = ''

        s = f'{message}{info}'

        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            if s[-1:] != "\n":
                s += "\n"
            s += indentation(record.exc_text)

        if record.stack_info:
            if s[-1:] != "\n":
                s += "\n"
            s += indentation(self.formatStack(record.stack_info))

        return s
