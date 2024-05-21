#!/usr/bin/env python3
"""Pymodbus asynchronous Server Example.

An example of a multi threaded asynchronous server.

usage::

    server_async.py [-h] [--comm {tcp,udp,serial,tls}]
                    [--framer {ascii,rtu,socket,tls}]
                    [--log {critical,error,warning,info,debug}]
                    [--port PORT] [--store {sequential,sparse,factory,none}]
                    [--slaves SLAVES]

    -h, --help
        show this help message and exit
    -c, --comm {tcp,udp,serial,tls}
        set communication, default is tcp
    -f, --framer {ascii,rtu,socket,tls}
        set framer, default depends on --comm
    -l, --log {critical,error,warning,info,debug}
        set log level, default is info
    -p, --port PORT
        set port
        set serial device baud rate
    --store {sequential,sparse,factory,none}
        set datastore type
    --slaves SLAVES
        set number of slaves to respond to

The corresponding client can be started as:

    python3 client_sync.py

"""
import asyncio
import logging
import sys


try:
    import helper
except ImportError:
    print("*** ERROR --> THIS EXAMPLE needs the example directory, please see \n\
          https://pymodbus.readthedocs.io/en/latest/source/examples.html\n\
          for more information.")
    sys.exit(-1)

from pymodbus import __version__ as pymodbus_version
from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSimulatorContext,
    ModbusSlaveContext,
    ModbusSparseDataBlock,
    ModbusSimulatorContext
)
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server import (
    StartAsyncSerialServer,
    StartAsyncTcpServer,
    StartAsyncTlsServer,
    StartAsyncUdpServer,
)


_logger = logging.getLogger(__file__)
_logger.setLevel(logging.INFO)

demo_config = {
    "setup": {
        "co size": 100,
        "di size": 150,
        "hr size": 200,
        "ir size": 250,
        "shared blocks": True,
        "type exception": False,
        "defaults": {
            "value": {
                "bits": 0x0708,
                "uint16": 1,
                "uint32": 45000,
                "float32": 127.4,
                "string": "X",
            },
            "action": {
                "bits": None,
                "uint16": None,
                "uint32": None,
                "float32": None,
                "string": None,
            },
        },
    },
    "invalid": [
        1,
        [6, 6],
    ],
    "write": [
        3,
        [7, 8],
        [16, 18],
        [21, 26],
        [31, 36],
    ],
    "bits": [
        [7, 9],
        {"addr": 2, "value": 0x81},
        {"addr": 3, "value": 17},
        {"addr": 4, "value": 17},
        {"addr": 5, "value": 17},
        {"addr": 10, "value": 0x81},
        {"addr": [11, 12], "value": 0x04342},
        {"addr": 13, "action": "reset"},
        {"addr": 14, "value": 15, "action": "reset"},
    ],
    "uint16": [
        {"addr": 16, "value": 3124},
        {"addr": [17, 18], "value": 5678},
        {"addr": [19, 20], "value": 14661, "action": "random"},
    ],
    "uint32": [
        {"addr": [21, 22], "value": 3124},
        {"addr": [23, 26], "value": 5678},
        {"addr": [27, 30], "value": 345000, "action": "increment"},
    ],
    "float32": [
        {"addr": [31, 32], "value": 3124.17},
        {"addr": [33, 36], "value": 5678.19},
        {"addr": [37, 40], "value": 345000.18, "action": "increment"},
    ],
    "string": [
        {"addr": [41, 42], "value": "Str"},
        {"addr": [43, 44], "value": "Strx"},
    ],
    "repeat": [{"addr": [0, 45], "to": [46, 138]}],
}

def setup_server(description=None, context=None, cmdline=None):
    """Run server setup."""
    args = helper.get_commandline(server=True, description=description, cmdline=cmdline)
    if context:
        args.context = context
    if not args.context:
        _logger.info("### Create datastore")
        # The datastores only respond to the addresses that are initialized
        # If you initialize a DataBlock to addresses of 0x00 to 0xFF, a request to
        # 0x100 will respond with an invalid address exception.
        # This is because many devices exhibit this kind of behavior (but not all)
        print(args.store)
        if args.store == "sequential":
            # Continuing, use a sequential block without gaps.
            datablock = lambda : ModbusSequentialDataBlock(0x00, [17] * 100)  # pylint: disable=unnecessary-lambda-assignment
        elif args.store == "sparse":
            # Continuing, or use a sparse DataBlock which can have gaps
            datablock = lambda : ModbusSparseDataBlock({0x00: 0, 0x05: 1})  # pylint: disable=unnecessary-lambda-assignment
        elif args.store == "factory":
            # Alternately, use the factory methods to initialize the DataBlocks
            # or simply do not pass them to have them initialized to 0x00 on the
            # full address range::
            datablock = lambda : ModbusSequentialDataBlock.create()  # pylint: disable=unnecessary-lambda-assignment,unnecessary-lambda

        if args.slaves:
            # The server then makes use of a server context that allows the server
            # to respond with different slave contexts for different slave ids.
            # By default it will return the same context for every slave id supplied
            # (broadcast mode).
            # However, this can be overloaded by setting the single flag to False and
            # then supplying a dictionary of slave id to context mapping::
            #
            # The slave context can also be initialized in zero_mode which means
            # that a request to address(0-7) will map to the address (0-7).
            # The default is False which is based on section 4.4 of the
            # specification, so address(0-7) will map to (1-8)::
            context = {
                0x01: ModbusSlaveContext(
                    di=datablock(),
                    co=datablock(),
                    hr=datablock(),
                    ir=datablock(),
                ),
                0x02: ModbusSlaveContext(
                    di=datablock(),
                    co=datablock(),
                    hr=datablock(),
                    ir=datablock(),
                ),
                0x03: ModbusSlaveContext(
                    di=datablock(),
                    co=datablock(),
                    hr=datablock(),
                    ir=datablock(),
                    zero_mode=True,
                ),
            }
            single = False
            print("here instead")
        else:
            # context = ModbusSlaveContext(
            #     di=datablock(), co=datablock(), hr=datablock(), ir=datablock()
            # )
            single = True
            lol_context = ModbusSimulatorContext(context)

            print("correct")
        # Build data storage
        args.context = ModbusServerContext(slaves=lol_context, single=single)
        # args.context = ModbusSimulatorContext(context)

    # ----------------------------------------------------------------------- #
    # initialize the server information
    # ----------------------------------------------------------------------- #
    # If you don't set this or any fields, they are defaulted to empty strings.
    # ----------------------------------------------------------------------- #
    args.identity = ModbusDeviceIdentification(
        info_name={
            "VendorName": "Pymodbus",
            "ProductCode": "PM",
            "VendorUrl": "https://github.com/pymodbus-dev/pymodbus/",
            "ProductName": "Pymodbus Server",
            "ModelName": "Pymodbus Server",
            "MajorMinorRevision": pymodbus_version,
        }
    )
    return args


async def run_async_server(args):
    """Run server."""
    txt = f"### start ASYNC server, listening on {args.port} - {args.comm}"
    args.comm="serial"
    _logger.info(txt)
    if args.comm == "tcp":
        address = (args.host if args.host else "", args.port if args.port else None)
        server = await StartAsyncTcpServer(
            context=args.context,  # Data storage
            identity=args.identity,  # server identify
            # TBD host=
            # TBD port=
            address=address,  # listen address
            # custom_functions=[],  # allow custom handling
            framer=args.framer,  # The framer strategy to use
            # ignore_missing_slaves=True,  # ignore request to a missing slave
            # broadcast_enable=False,  # treat slave_id 0 as broadcast address,
            # timeout=1,  # waiting time for request to complete
        )
    elif args.comm == "udp":
        address = (
            args.host if args.host else "127.0.0.1",
            args.port if args.port else None,
        )
        server = await StartAsyncUdpServer(
            context=args.context,  # Data storage
            identity=args.identity,  # server identify
            address=address,  # listen address
            # custom_functions=[],  # allow custom handling
            framer=framer,  # The framer strategy to use
            # ignore_missing_slaves=True,  # ignore request to a missing slave
            # broadcast_enable=False,  # treat slave_id 0 as broadcast address,
            # timeout=1,  # waiting time for request to complete
        )
    elif args.comm == "serial":
        # socat -d -d PTY,link=/tmp/ptyp0,raw,echo=0,ispeed=9600
        #             PTY,link=/tmp/ttyp0,raw,echo=0,ospeed=9600
        server = await StartAsyncSerialServer(
            context=args.context,  # Data storage
            identity=args.identity,  # server identify
            # timeout=1,  # waiting time for request to complete
            port="/dev/pts/2",  # serial port
            # custom_functions=[],  # allow custom handling
            framer="rtu",  # The framer strategy to use
            stopbits=1,  # The number of stop bits to use
            bytesize=8,  # The bytesize of the serial messages
            parity="N",  # Which kind of parity to use
            baudrate=9600,  # The baud rate to use for the serial device
            # handle_local_echo=False,  # Handle local echo of the USB-to-RS485 adaptor
            # ignore_missing_slaves=True,  # ignore request to a missing slave
            # broadcast_enable=False,  # treat slave_id 0 as broadcast address,
            # strict=True,  # use strict timing, t1.5 for Modbus RTU
        )
    elif args.comm == "tls":
        address = (args.host if args.host else "", args.port if args.port else None)
        server = await StartAsyncTlsServer(
            context=args.context,  # Data storage
            host="localhost",  # define tcp address where to connect to.
            # port=port,  # on which port
            identity=args.identity,  # server identify
            # custom_functions=[],  # allow custom handling
            address=address,  # listen address
            framer=args.framer,  # The framer strategy to use
            certfile=helper.get_certificate(
                "crt"
            ),  # The cert file path for TLS (used if sslctx is None)
            # sslctx=sslctx,  # The SSLContext to use for TLS (default None and auto create)
            keyfile=helper.get_certificate(
                "key"
            ),  # The key file path for TLS (used if sslctx is None)
            # password="none",  # The password for for decrypting the private key file
            # ignore_missing_slaves=True,  # ignore request to a missing slave
            # broadcast_enable=False,  # treat slave_id 0 as broadcast address,
            # timeout=1,  # waiting time for request to complete
        )
    return server


async def async_helper():
    """Combine setup and run."""
    _logger.info("Starting...")
    run_args = setup_server(description="Run asynchronous server.", context=demo_config)
    await run_async_server(run_args)


if __name__ == "__main__":
    asyncio.run(async_helper(), debug=True)
