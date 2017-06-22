ZeroC Ice logging utils
=======================

logging.conf example
^^^^^^^^^^^^^^^^^^^^

.. code::

  # https://docs.python.org/3.6/library/logging.config.html
  #
  # Level	        Numeric value
  # CRITICAL      50
  # ERROR         40
  # WARNING       30
  # INFO          20
  # DEBUG         10
  # NOTSET        0
  # higher level - less logs

  [loggers]
  keys=root

  [handlers]
  keys=consoleHandler

  [logger_root]
  level=DEBUG
  handlers=consoleHandler

  [handler_consoleHandler]
  class=StreamHandler
  level=DEBUG
  formatter=consoleFormatter
  args=(sys.stdout,)

  [formatter_consoleFormatter]
  class=ice_yml_log_formatter.YAMLLogFormatter
  format=[%(levelname)s] %(name)s: %(msg)s
  datefmt=

simple usage example
^^^^^^^^^^^^^^^^^^^^
.. code:: python

  import os
  import logging.config
  import logging

  from ice_yml_log_formatter import get_request_context

  logging.getLogger()
  logging.config.fileConfig('./logging.conf')

  #....
  #....
  # in your ice servant method
  try:
    raise Exception('Any cause')
  except:
    logging.exception('Oops!',
                      extra={
                        'ice_current': current,
                        'context': {
                          'any_info_key': 'any info value',
                        },
                      })

Use ``ice_current`` for ice request metatada print, and ``context`` for extra structured information.

log example
^^^^^^^^^^^
.. code::

  [DEBUG] services.fun - Dispatch
    iceIdentity: ZeroC/Fun
    iceOperation: something
    iceRequestId: 1

  [ERROR] services.fun - Unexpected error
    iceIdentity: ZeroC/Fun
    iceOperation: something
    iceRequestId: 1
    context:
      any_info_key: any info value
    Error: Fun::ExampleException
      error_data:
        some_prop: 1
      stack_trace:
          File "path-to-source/fun.py", line 71, in wrapped
            return method(self, *args, **kwargs)

          File "path-to-source/fun.py", line 123, in something
            raise Fun.ExampleException(some_prop=1)
