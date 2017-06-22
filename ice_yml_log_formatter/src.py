import logging
import re
import traceback

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


def to_plain_objects(any_value):
    if isinstance(any_value, Ice.Identity):
        return Ice.identityToString(any_value)

    return any_value


def get_request_context(current):
    if not current:
        return {}

    return dict(
        iceRequestId=current.requestId,
        iceOperation=current.operation,
        iceIdentity=Ice.identityToString(current.id),
    )


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
        context = dict(vars(record).get('context', {}))
        info_data = get_request_context(vars(record).get('ice_current', None))
        if context:
            info_data = {**info_data, 'context': context}

        if info_data:
            info = ("\n" +
                    indentation(
                        safe_dump(
                            to_plain_objects(info_data),
                            default_flow_style=False,
                            allow_unicode=True)))
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
