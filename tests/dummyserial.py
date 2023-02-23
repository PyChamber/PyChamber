"""
Forked from https://github.com/ampledata/dummyserial/ which has been abandoned.
Updated to be compatible with PySerial 3.4, and made into one file

Dummy Serial Class Definitions
"""

import logging
import logging.handlers
import time

from serial.serialutil import PortNotOpenError, SerialBase, SerialException

LOG_LEVEL = logging.DEBUG
LOG_FORMAT = logging.Formatter("%(asctime)s dummyserial %(levelname)s %(name)s.%(funcName)s:%(lineno)d - %(message)s")

DEFAULT_TIMEOUT = 2
DEFAULT_BAUDRATE = 9600
# Response when no matching message (key) is found in the look-up dictionary.
# * Should not be an empty string, as that is interpreted as
#   "no data available on port".
DEFAULT_RESPONSE = b"NONE"
NO_DATA_PRESENT = b""


class DSIOError(IOError):
    """Dummy Serial Wrapper for IOError Exception."""

    pass


class DSTypeError(TypeError):
    """Dummy Serial Wrapper for TypeError Exception."""

    pass


class Serial(SerialBase):
    """
    Dummy (mock) serial port for testing purposes.
    Mimics the behavior of a serial port as defined by the PySerial module
    Args:
        * port:
        * baudrate:
        * bytesize:
        * parity:
        * stopbits:
        * timeout:
        * xonxoff:
        * rtscts:
        * write_timeout:
        * dsrdtr:
        * inter_byte_timeout:
        * exclusive
        * expected_responses:
        * raise_on_unrecognized:
    Note:
    As the portname argument not is used properly, only one port on
    :mod:`dummyserial` can be used simultaneously.
    """

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(LOG_LEVEL)
        _console_handler.setFormatter(LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def __init__(self, *args, **kwargs):
        self._logger.debug("args=%s", args)
        self._logger.debug("kwargs=%s", kwargs)

        self.expected_responses = kwargs.pop("expected_responses", {})
        self.raise_on_unrecognized = kwargs.pop("raise_on_unrecognized", False)

        super().__init__(*args, **kwargs)

        self._input_buffer = NO_DATA_PRESENT
        self._output_buffer = NO_DATA_PRESENT

    def open(self):  # noqa: A003
        """Open a (previously initialized) port."""
        self._logger.debug("Opening port")

        if self._port is None:
            raise SerialException("Port must be configured before it can be used.")
        if self.is_open:
            raise SerialException("Port is already open.")

        self.is_open = True

    def close(self):
        """Close a port on dummy_serial."""
        self._logger.debug("Closing port")
        if self.is_open:
            self.is_open = False

    def write(self, data: bytes):
        """
        Write to a port on dummy_serial.
        Args:
            data (string/bytes): data for sending to the port on
            dummy_serial. Will affect the response for subsequent read
            operations.
        """
        self._logger.debug(f'Writing ({len(data)}): "{data}"')

        if not self.is_open:
            raise PortNotOpenError

        if not isinstance(data, bytes):
            raise DSTypeError("The input must be type bytes. Given:" + repr(data))

        # Look up which data that should be waiting for subsequent read
        # commands.
        self._output_buffer = self.expected_responses.get(data)
        if not self._output_buffer:
            if self.raise_on_unrecognized:
                raise KeyError(f"Unrecognized command: {str(data)}. Add to expected_responses dict.")
            self._output_buffer = NO_DATA_PRESENT
        self._logger.debug(f"{self._output_buffer=}")

    def read(self, size=1):
        """
        Read size bytes from the Dummy Serial Responses.
        The response is dependent on what was written last to the port on
        dummyserial, and what is defined in the :data:`RESPONSES` dictionary.
        Args:
            size (int): For compability with the real function.
        If the response is shorter than size, it will sleep for timeout.
        If the response is longer than size, it will return only size bytes.
        """
        self._logger.debug("Reading %s bytes.", size)

        if not self.is_open:
            raise PortNotOpenError

        if size < 0:
            raise DSIOError(f"The size to read must not be negative. Given: {size:!r}")

        # Do the actual reading from the waiting data, and simulate the
        # influence of size.
        if self._output_buffer == DEFAULT_RESPONSE:
            return_val = self._output_buffer
        elif size == len(self._output_buffer):
            return_val = self._output_buffer
            self._output_buffer = NO_DATA_PRESENT
        elif size < len(self._output_buffer):
            self._logger.debug(
                f"The size to read ({size}) is smaller than the available data ({len(self._output_buffer)}:"
                f' "{self._output_buffer}"). Some bytes will be kept for later.'
            )

            return_val = self._output_buffer[:size]
            self._output_buffer = self._output_buffer[size:]
        else:  # Wait for timeout - we asked for more data than available!
            self._logger.debug(
                f"The size to read ({size}) is larger than the available data({len(self._output_buffer)}:"
                f' "{self._output_buffer}"). Will sleep until timeout.'
            )

            time.sleep(self.timeout)
            return_val = self._output_buffer
            self._output_buffer = NO_DATA_PRESENT

        self._logger.debug(f'Read ({len(return_val)}): "{return_val}"')

        return return_val

    def in_waiting(self):
        """Returns length of waiting input data."""
        return len(self._input_buffer)

    def out_waiting(self):
        """Returns length of waiting output data."""
        return len(self._output_buffer)

    def reset_input_buffer(self):
        self._input_buffer = NO_DATA_PRESENT

    def reset_output_buffer(self):
        self._output_buffer = NO_DATA_PRESENT
