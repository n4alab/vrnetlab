#!/usr/bin/env python3

import datetime
import logging
import os
import signal
import sys

import vrnetlab


def handle_SIGCHLD(signal, frame):
    os.waitpid(-1, os.WNOHANG)


def handle_SIGTERM(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, handle_SIGTERM)
signal.signal(signal.SIGTERM, handle_SIGTERM)
signal.signal(signal.SIGCHLD, handle_SIGCHLD)

TRACE_LEVEL_NUM = 9
logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")


def trace(self, message, *args, **kws):
    if self.isEnabledFor(TRACE_LEVEL_NUM):
        self._log(TRACE_LEVEL_NUM, message, args, **kws)


logging.Logger.trace = trace


class FlinosVM(vrnetlab.VM):
    def __init__(self, hostname, username, password, data_nics, conn_mode):
        super().__init__(
            username,
            password,
            disk_image="/installed.qcow2",
            ram=4096,
            driveif="virtio",
            smp="2",
            data_intf_prefix="eth",
        )
        self.hostname = hostname
        self.conn_mode = conn_mode
        self.nic_type = "virtio-net-pci"
        self.num_nics = data_nics

    def bootstrap_spin(self):
        if self.spins > 600:
            self.stop()
            self.start()
            return

        ridx, match, res = self.tn.expect([b"FLiNOS login:", b"login:", b"Login:", b"#", b">"], 1)
        if match:
            self.logger.debug("matched readiness pattern %s", ridx)
            self.running = True
            self.tn.close()
            startup_time = datetime.datetime.now() - self.start_time
            self.logger.info("Startup complete in: %s", startup_time)
            return

        if res:
            self.logger.trace("OUTPUT: %s", res.decode(errors="replace"))
            self.spins = 0

        if self.spins >= 30:
            self.running = True
            self.tn.close()
            startup_time = datetime.datetime.now() - self.start_time
            self.logger.info("Startup complete in: %s", startup_time)
            return

        self.spins += 1


class Flinos(vrnetlab.VR):
    def __init__(self, hostname, username, password, data_nics, conn_mode):
        super().__init__(username, password)
        self.vms = [FlinosVM(hostname, username, password, data_nics, conn_mode)]


if __name__ == "__main__":
    import argparse

    for src, dst in (("RAM", "QEMU_MEMORY"), ("VCPU", "QEMU_SMP")):
        if src in os.environ and dst not in os.environ:
            os.environ[dst] = os.environ[src]

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--trace", action="store_true", help="enable trace level logging")
    parser.add_argument("--username", default="admin", help="Username")
    parser.add_argument("--password", default="admin", help="Password")
    parser.add_argument("--hostname", default="flinos", help="VM hostname")
    parser.add_argument("--nics", type=int, default=8, help="Number of data NICs")
    parser.add_argument(
        "--connection-mode",
        default="tc",
        help="Connection mode to use in the datapath",
    )
    args = parser.parse_args()

    logging.basicConfig(format="%(asctime)s: %(module)-10s %(levelname)-8s %(message)s")
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    if args.trace:
        logger.setLevel(1)

    vr = Flinos(
        args.hostname,
        args.username,
        args.password,
        args.nics,
        args.connection_mode,
    )
    vr.start()
