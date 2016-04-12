#!/usr/bin/env python

import ConfigParser
import logging
import threading
import subprocess
import time
import os

try:
    import rrb3
except:
    import rrb3mock as rrb3

CONFIG_FILE = 'config.ini'


class Rover(threading.Thread):

    def __init__(self, config):
        threading.Thread.__init__(self)

        self.config = config
        self.rate = float(self.config.get('rover', 'rate'))
        battery_voltage = self.config.get('hw', 'battery_voltage')
        motor_voltage = self.config.get('hw', 'motor_voltage')
        logging.info('Initializing rrb3...')
        self.rr = rrb3.RRB3(battery_voltage, motor_voltage)
        self.rr.set_led1(0)
        self.rr.set_led1(1)
        logging.info('Initialized rrb3')
        self.is_running = True

    def stop(self):
        self.rr.stop()
        self.rr.cleanup()
        self.is_running = False

    def shutdown(self):
        self.stop()
        self._run_shell_cmd('/sbin/shutdown -h now')

    def reboot(self):
        self.stop()
        self._run_shell_cmd('/sbin/reboot')

    def update(self):
        self._run_shell_cmd('git pull')

    def run(self):
        while (self.is_running):
            time.sleep(self.rate)

    def get_range(self):
        distance = self.rr.get_distance()
        logging.debug('Range: {}'.format(distance))
        return distance

    def set_motors(self, left, right):
        l = abs(left)
        r = abs(right)
        left_dir = 0 if left < 0 else 1
        right_dir = 0 if right < 0 else 1
        logging.debug('set_motors({}, {}, {}, {})'.format(l, left_dir, r, right_dir))
        self.rr.set_motors(l, left_dir, r, right_dir)

    def _run_shell_cmd(self, command):
        logging.info('Running shell command: {}'.format(command))
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output = process.communicate()[0]
        logging.info(output)

def main():
    config = ConfigParser.ConfigParser()
    config.read(CONFIG_FILE)
    Rover(config).start()

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    logging.basicConfig(format='[%(levelname)-5s] %(message)s')
    main()
