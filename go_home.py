__author__ = 'gjones'
import fts_motor
motor = fts_motor.FtsMotorController(port='COM5')

motor.go_to_position(0)
