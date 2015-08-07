import kid_readout.equipment.lockin_controller
import fts_motor
from scipy.constants import c
import numpy as np
import time

li = kid_readout.equipment.lockin_controller.lockinController(serial_port='COM4')

motor = fts_motor.FtsMotorController(port='COM5')

motor.go_to_position(0)

counts_per_mm = 2000.0

freq_resolution_GHz = 2.0
max_freq_GHz = 2000.0
step_size_mm = c*1000 / (max_freq_GHz*1e9*2)
start_mm = -10.0
end_mm = 1.2 * c * 1000 / (freq_resolution_GHz*1e9*2)

start_counts = int(np.round(start_mm*counts_per_mm))
end_counts = int(np.round(end_mm*counts_per_mm))
step_counts = int(np.round(step_size_mm*counts_per_mm))

print "step_size: %.3f mm, %d counts" % (step_size_mm,step_counts)
print "start: %.3f mm, %d counts" % (start_mm, start_counts)
print "end: %.3f mm, %d counts" % (end_mm, end_counts)

positions = range(start_counts,end_counts,step_counts)
print "number of steps:", len(positions)

observed_positions = []
r_data = []
theta_data = []
import sys
for position in positions:
    try:
        print "moving to", -position
        sys.stdout.flush()
        motor.go_to_position(-position)
        print "sleeping"
        sys.stdout.flush()
        time.sleep(0.2)
        print "getting data"
        sys.stdout.flush()
        x,y,r,theta = li.get_data()
        print "got data"
        sys.stdout.flush()
        r_data.append(r)
        theta_data.append(theta)
        observed_positions.append(position)
    except KeyboardInterrupt:
        break
    except Exception,e:
        print "error",e

filename = '/home/data/fts/%s' % (time.strftime('%Y-%m-%d_%H-%M-%S'))
filename += '_blue_and_green_input_filter_10_dB_pad_no_output_filter'
np.savez(filename, position=np.array(observed_positions), r=np.array(r_data), theta=np.array(theta_data))

motor.send_position_command(0)