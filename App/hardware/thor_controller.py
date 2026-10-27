import os
import time
import clr

homedir = os.getcwd()
clr.AddReference(homedir + r"\hardware\DLLs\Kinesis\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference(homedir + r"\hardware\DLLs\Kinesis\Thorlabs.MotionControl.KCube.InertialMotorCLI.dll")
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.KCube.InertialMotorCLI import *
from System import Decimal  # necessary for real world units

class ThorController:
    def __init__(self, serial_num):
        self.serial_num = serial_num
        self.x = 0
        self.y = 0
        self.z = 0
        self.angle = 0
        self.xy_step_var = 1000

        self.velocity = 2600
        self.acceleration = 134442

        self.z_velocity = 500
        self.z_acceleration = 10000

        self.xy_step_size = 1000
        self.z_step_size = 500

        try:
            DeviceManagerCLI.BuildDeviceList()
            # create new device
            
            self.device = KCubeInertialMotor.CreateKCubeInertialMotor(self.serial_num)

            # Connect
            self.device.Connect(self.serial_num)
            time.sleep(0.25)

            # Ensure that the self.device settings have been initialized
            if not self.device.IsSettingsInitialized():
                self.device.WaitForSettingsInitialized(10000)  # 10 second timeout
                assert self.device.IsSettingsInitialized() is True

            # Get self.device Information and display description
            device_info = self.device.GetDeviceInfo()
            print(device_info.Description)
            # Start polling and enable channel
            self.device.StartPolling(250)  #250ms polling rate
            time.sleep(0.25)
            self.device.EnableDevice()
            time.sleep(0.25)  # Wait for self.device to enable

            # Load any configuration settings needed by the controller/stage
            inertial_motor_config = self.device.GetInertialMotorConfiguration(self.serial_num)

            # Get parameters related to homing/zeroing/moving
            self.device_settings = ThorlabsInertialMotorSettings.GetSettings(inertial_motor_config)

            # Step parameters for an intertial motor channel
            self.x_motor = InertialMotorStatus.MotorChannels.Channel1  # enum chan ident
            self.xy_velocity = self.device_settings.Drive.Channel(self.x_motor).StepRate
            self.xy_acceleration = self.device_settings.Drive.Channel(self.x_motor).StepAcceleration

            self.y_motor = InertialMotorStatus.MotorChannels.Channel2  # enum chan ident
            self.device_settings.Drive.Channel(self.y_motor).StepRate = self.xy_velocity
            self.device_settings.Drive.Channel(self.y_motor).StepAcceleration = self.xy_acceleration

            self.z_motor = InertialMotorStatus.MotorChannels.Channel3  # enum chan ident
            self.z_velocity = self.device_settings.Drive.Channel(self.z_motor).StepRate
            self.z_acceleration = self.device_settings.Drive.Channel(self.z_motor).StepAcceleration

            self.angle_motor = InertialMotorStatus.MotorChannels.Channel4 # enum chan ident
            self.angle_velocity = self.device_settings.Drive.Channel(self.angle_motor).StepRate
            self.angle_acceleration = self.device_settings.Drive.Channel(self.angle_motor).StepAcceleration

            # Send settings to the self.device
            self.device.SetSettings(self.device_settings, True, True)

            print("Zeroing self.device")
            self.set_origin()
            
            print("Setting Jog parameters")
            self.x_jogParams = self.device.GetJogParameters(self.x_motor)
            self.x_jogParams.JogRate = self.xy_velocity
            self.x_jogParams.JogAcceleration = self.xy_acceleration
            self.x_jogParams.JogMode = InertialMotorJogMode.Continuous
            self.device.SetJogParameters(self.x_motor, self.x_jogParams)

            self.y_jogParams = self.device.GetJogParameters(self.y_motor)
            self.y_jogParams.JogRate = self.xy_velocity
            self.y_jogParams.JogAcceleration = self.xy_acceleration
            self.y_jogParams.JogMode = InertialMotorJogMode.Continuous
            self.device.SetJogParameters(self.y_motor, self.y_jogParams)

            self.z_jogParams = self.device.GetJogParameters(self.z_motor)
            self.z_jogParams.JogRate = self.z_velocity
            self.z_jogParams.JogAcceleration = self.z_acceleration
            self.z_jogParams.JogMode = InertialMotorJogMode.Continuous
            self.device.SetJogParameters(self.z_motor, self.z_jogParams)

            self.angle_jogParams = self.device.GetJogParameters(self.angle_motor)
            self.angle_jogParams.JogRate = self.angle_velocity
            self.angle_jogParams.JogAcceleration = self.angle_acceleration
            self.angle_jogParams.JogMode = InertialMotorJogMode.Continuous
            self.device.SetJogParameters(self.angle_motor, self.angle_jogParams)


        except Exception as e:
            print(e)

    def set_origin(self):
        try:
            self.device.SetPositionAs(self.x_motor, 0)
            self.device.SetPositionAs(self.y_motor, 0)
            self.device.SetPositionAs(self.z_motor, 0)
            self.device.SetPositionAs(self.angle_motor, 0)
            
        except Exception as e:
            print(e)

    def set_z_zero(self):
        try: 
            self.device.SetPositionAs(self.z_motor, 0)
        except Exception as e:
            print(e)
    
    def go_to_Xpos(self, new_x):
        try:
            self.device.MoveTo(self.x_motor, new_x, 1000)
            self.x = new_x
        except Exception as e:
            print(e)

    def go_to_Ypos(self, new_y):
        try:
            self.device.MoveTo(self.y_motor, new_y, 1000)
            self.y = new_y
        except Exception as e:
            print(e)
            
    def go_to_xypos(self, new_x, new_y):
        try:
            self.device.MoveTo(self.x_motor, new_x, 1000)
            self.x = new_x
            self.device.MoveTo(self.y_motor, new_y, 1000)
            self.y = new_y
        except Exception as e:
            print(e)

    def go_to_Zpos(self, new_z):
        try:
            self.device.MoveTo(self.z_motor, new_z, 1000)
            self.z = new_z
        except Exception as e:
            print(e)

    def go_to_Angle(self, new_angle):
        try:
            self.device.MoveTo(self.angle_motor, new_angle, 1000)
            self.angle = new_angle
        except Exception as e:
            print(e)

    def set_xy_velocity(self, velocity):
        self.xy_velocity = velocity
        self.device_settings.Drive.Channel(self.x_motor).StepRate = velocity
        self.device_settings.Drive.Channel(self.y_motor).StepRate = velocity
        self.x_jogParams.JogRate = self.xy_velocity
        self.y_jogParams.JogRate = self.xy_velocity
        self.device.SetJogParameters(self.x_motor, self.x_jogParams)
        self.device.SetJogParameters(self.y_motor, self.y_jogParams)

    def set_z_velocity(self, velocity):
        self.z_velocity = velocity
        self.device_settings.Drive.Channel(self.z_motor).StepRate = velocity
        self.z_jogParams.JogRate = self.z_velocity
        self.device.SetJogParameters(self.z_motor, self.z_jogParams)

    def set_angle_velocity(self, velocity):
        self.angle_velocity = velocity
        self.device_settings.Drive.Channel(self.angle_motor).StepRate = velocity
        self.angle_jogParams.JogRate = self.angle_velocity
        self.device.SetJogParameters(self.angle_motor, self.angle_jogParams)

    def set_xy_acceleration(self, acceleration):
        self.xy_acceleration = acceleration
        self.device_settings.Drive.Channel(self.x_motor).StepAcceleration = acceleration
        self.device_settings.Drive.Channel(self.y_motor).StepAcceleration = acceleration
        self.x_jogParams.JogAcceleration = self.xy_acceleration
        self.y_jogParams.JogAcceleration = self.xy_acceleration
        self.device.SetJogParameters(self.x_motor, self.x_jogParams)
        self.device.SetJogParameters(self.y_motor, self.y_jogParams)

    def set_z_acceleration(self, acceleration):
        self.z_accleration = acceleration
        self.device_settings.Drive.Channel(self.z_motor).StepAcceleration = acceleration
        self.z_jogParams.JogAcceleration = self.z_acceleration
        self.device.SetJogParameters(self.z_motor, self.z_jogParams)

    def set_Angle_acceleration(self, acceleration):
        self.angle_acceleration = acceleration
        self.device_settings.Drive.Channel(self.angle_motor).StepAcceleration = acceleration
        self.angle_jogParams.JogAcceleration = self.angle_acceleration
        self.device.SetJogParameters(self.angle_motor, self.angle_jogParams)

    def get_xy_velocity(self):
        return self.xy_velocity

    def get_z_velocity(self):
        return self.z_velocity
    
    def get_angle_velocity(self):
        return self.angle_velocity

    def get_xy_acceleration(self):
        return self.xy_acceleration
    
    def get_z_acceleration(self):
        return self.z_accleration
    
    def get_angle_acceleration(self):
        return self.angle_acceleration

    def start_forward_x_motor(self):
        self.device.Jog(self.x_motor, InertialMotorJogDirection.Increase, 0)
    def start_backward_x_motor(self):
        self.device.Jog(self.x_motor, InertialMotorJogDirection.Decrease, 0)
    def stop_x_motor(self):
        self.device.Stop(self.x_motor)
    def get_x_pos(self):
        return self.device.GetPosition(self.x_motor)

    def start_forward_y_motor(self):
        self.device.Jog(self.y_motor, InertialMotorJogDirection.Increase, 0)
    def start_backward_y_motor(self):
        self.device.Jog(self.y_motor, InertialMotorJogDirection.Decrease, 0)
    def stop_y_motor(self):
        self.device.Stop(self.y_motor)
    def get_y_pos(self):
        return self.device.GetPosition(self.y_motor)

    def start_forward_z_motor(self):
        self.device.Jog(self.z_motor, InertialMotorJogDirection.Increase, 0)
    def start_backward_z_motor(self):
        self.device.Jog(self.z_motor, InertialMotorJogDirection.Decrease, 0)
    def stop_z_motor(self):
        self.device.Stop(self.z_motor)
    def get_z_pos(self):
        return self.device.GetPosition(self.z_motor)
    
    def start_forward_angle_motor(self):
        self.device.Jog(self.angle_motor, InertialMotorJogDirection.Increase, 0)
    def start_backward_angle_motor(self):
        self.device.Jog(self.angle_motor, InertialMotorJogDirection.Decrease, 0)
    def stop_angle_motor(self):
        self.device.Stop(self.angle_motor)
    def get_angle_pos(self):
        return self.device.GetPosition(self.angle_motor)

    def get_position(self):
        self.x = self.get_x_pos()
        self.y = self.get_y_pos()
        self.z = self.get_z_pos()
        self.angle = self.get_angle_pos() 
        return self.x, self.y, self.z, self.angle

    def stop_all(self):
        self.stop_x_motor()
        self.stop_y_motor()
        self.stop_z_motor()
        self.stop_angle_motor()

    def step_forward(self):
        self.get_position()
        return self.go_to_xypos(self.x, self.y - self.xy_step_size)

    def step_backward(self):
        self.get_position()
        return self.go_to_xypos(self.x, self.y + self.xy_step_size)

    def step_left(self):
        self.get_position()
        return self.go_to_xypos(self.x + self.xy_step_size, self.y)

    def step_right(self):
        self.get_position()
        return self.go_to_xypos(self.x - self.xy_step_size, self.y)


    def disconnect(self):
        try:
            self.device.StopPolling()
            self.device.Disconnect()
        except Exception as e:
            print(e)