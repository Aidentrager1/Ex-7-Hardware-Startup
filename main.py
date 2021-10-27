import os
from threading import Thread
import kivy
os.environ['DISPLAY'] = ":0.0"
os.environ['KIVY_WINDOW'] = 'egl_rpi'
import pygame
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.slider import Slider
from pidev.MixPanel import MixPanel
from pidev.kivy.PassCodeScreen import PassCodeScreen
from pidev.kivy.PauseScreen import PauseScreen
from pidev.kivy import DPEAButton
from pidev.kivy import ImageButton
from pidev.kivy.selfupdatinglabel import SelfUpdatingLabel
from kivy.animation import Animation
from kivy.uix.widget import Widget
from pidev.Joystick import Joystick
from datetime import datetime
from time import sleep
import itertools
import spidev
import os
from time import sleep
import RPi.GPIO as GPIO
from pidev.stepper import stepper
from Slush.Devices import L6470Registers
spi = spidev.SpiDev()

# Init a 200 steps per revolution stepper on Port 0
s0 = stepper(port=0, micro_steps=32, hold_current=20, run_current=20, accel_current=20, deaccel_current=20,
             steps_per_unit=200, speed=4)


time = datetime

MIXPANEL_TOKEN = "x"
MIXPANEL = MixPanel("Project Name", MIXPANEL_TOKEN)

SCREEN_MANAGER = ScreenManager()
MAIN_SCREEN_NAME = 'main'
ADMIN_SCREEN_NAME = 'admin'
PICTURE_SCREEN_NAME = 'picture'
JOYSTICK_SCREEN_NAME = 'joystick'


class ProjectNameGUI(App):
    """
    Class to handle running the GUI Application
    """

    def build(self):
        """
        Build the application
        :return: Kivy Screen Manager instance
        """
        return SCREEN_MANAGER


Window.clearcolor = (1, 1, 1, 1)  # White


class MainScreen(Screen):
    """
    Class to handle the main screen and its associated touch events
    """
    Direction = 0
    count = 0
    motor_label = "Off"
    def pressed(self):
        """
        Function called on button touch event for button with id: testButton
        :return: None
        """
        quit()

    def pressed2(self):
        self.count += 1
        self.btn.text = str(s0.get_position_in_units())
        s0.go_until_press(0, 10000)
        print("moving motor")


    def admin_action(self):
        """
        Hidden admin button touch event. Transitions to passCodeScreen.
        This method is called from pidev/kivy/PassCodeScreen.kv
        :return: None
        """

        SCREEN_MANAGER.current = 'passCode'
    def motor_change(self):
        if self.motor_label.text == "off":
            self.motor_label.text = "on"
            s0.softStop()
            sleep(.5)
            s0.go_until_press(0, 20000)
            self.Direction = 0
        elif self.motor_label.text == "on":
            self.motor_label.text = "off"
            s0.softStop()
            sleep(.5)
            s0.goHome()
        if self.Direction == 0:
            self.Direction = 1
        else:
            self.Direction = 0
    def motor_change_direction(self):
        if self.Direction == 0:
            s0.go_until_press(1, 20000)
            self.Direction = 1
        else:
            s0.go_until_press(0, 40000)
            self.Direction = 0
    def slider_something(self):
        s0.go_until_press(0, 400*int(self.slider.value))
    def picture_action(self):
        SCREEN_MANAGER.transition.direction = 'left'
        SCREEN_MANAGER.current = 'joystick'
    def special_movements(self):
        self.motor_label_position.text = str(s0.get_position_in_units())
        print(str(s0.get_position_in_units()))
        s0.set_speed(1)
        s0.start_relative_move(15)
        while s0.isBusy():
            sleep(0.1)
        self.motor_label_position.text = str(s0.get_position_in_units())
        print(str(s0.get_position_in_units()))
        sleep(10)
        s0.set_speed(5)
        s0.start_relative_move(10)
        while s0.isBusy():
            sleep(0.1)
        self.motor_label_position.text = str(s0.get_position_in_units())
        print(str(s0.get_position_in_units()))
        sleep(8)
        s0.goHome()
        while s0.isBusy():
            sleep(0.1)
        sleep(30)
        self.motor_label_position.text = str(s0.get_position_in_units())
        print(str(s0.get_position_in_units()))
        s0.set_speed(8)
        s0.start_relative_move(-100)
        while s0.isBusy():
            sleep(0.1)
        self.motor_label_position.text = str(s0.get_position_in_units())
        print(str(s0.get_position_in_units()))
        sleep(10)
        s0.goHome()
        while s0.isBusy():
            sleep(0.1)
        self.motor_label_position.text = str(s0.get_position_in_units())
        print(str(s0.get_position_in_units()))
    def start_movement_thread(self):  # This should be inside the MainScreen Class
        Thread(target=self.special_movements).start()
# Prints the value of get_position_in_units to a label on the kivy screen
# 15 turns revolutions clockwise at 1 revolution / sec.
# Then prints the value of get_position_in_units to a label on the kivy screen
# Stops 10 seconds then turns clockwise for 10 revolutions at 5 rev / sec.
# Then prints the value of get_position_in_units to a label on the kivy screen
# Stops for 8 seconds.
# Then goes home and stops for 30 seconds.
# Then prints the value of get_position_in_units to a label on the kivy screen
# Then turns counter clockwise for 100 revolutions at 8 rev / sec.
# Then prints the value of get_position_in_units to a label on the kivy screen
# Then stops for 10 seconds and
# then goes home and
# Then prints the value of get_position_in_units to a label on the kivy screen
class PictureScreen(Screen):
    def picture_action(self):
        SCREEN_MANAGER.transition.direction = 'right'
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME
    def animation(self):
        anim = Animation(x=50,y=100, size=(800, 800), t='in_quad')
        anim.start(self.imagebutton1)
class AdminScreen(Screen):
    """
    Class to handle the AdminScreen and its functionality
    """

    def __init__(self, **kwargs):
        """
        Load the AdminScreen.kv file. Set the necessary names of the screens for the PassCodeScreen to transition to.
        Lastly super Screen's __init__
        :param kwargs: Normal kivy.uix.screenmanager.Screen attributes
        """
        Builder.load_file('AdminScreen.kv')

        PassCodeScreen.set_admin_events_screen(ADMIN_SCREEN_NAME)  # Specify screen name to transition to after correct password
        PassCodeScreen.set_transition_back_screen(MAIN_SCREEN_NAME)  # set screen name to transition to if "Back to Game is pressed"

        super(AdminScreen, self).__init__(**kwargs)

    @staticmethod
    def transition_back():
        """
        Transition back to the main screen
        :return:
        """
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    @staticmethod
    def shutdown():
        """
        Shutdown the system. This should free all steppers and do any cleanup necessary
        :return: None
        """
        os.system("sudo shutdown now")

    @staticmethod
    def exit_program():
        """
        Quit the program. This should free all steppers and do any cleanup necessary
        :return: None
        """
        quit()
class JoystickScreen(Screen):
    def start_joy_thread(self):  # This should be inside the MainScreen Class
        Thread(target=self.updatelabel).start()
    buttons = [0, 1, 2, 3 ,4, 5, 6, 7, 8, 9, 10]
    joystick1 = Joystick(0, False)
    def updatelabel (self):
        while True:
            # for x in self.buttons:
            #     if self.joystick1.get_button_state(x) == 1:
            #         for y in self.buttons:
            #             if self.joystick1.get_button_state(y) == 1:
            #                 self.joystick_pressed.text = "pressed"
            #                 break
            #
            #
            #     else:
            #         self.joystick_pressed.text = "not pressed"
            # sleep(.1)
            for combo in itertools.combinations(self.buttons, 3):
                if self.joystick1.button_combo_check(combo):
                            self.joystick_pressed.text = "pressed"
                            break
                else:
                    self.joystick_pressed.text = "not pressed"
            sleep(.1)
            self.joystick_x.text = str(self.joystick1.get_both_axes()[0])
            self.joystick_y.text = str(self.joystick1.get_both_axes()[1])
            self.joystick_x.center_x += self.joystick1.get_both_axes()[0] * 100
            self.joystick_y.center_y += self.joystick1.get_both_axes()[1] * 100
            sleep(.1)
    pass





"""
Widget additions
"""

Builder.load_file('main.kv')
Builder.load_file('PictureScreen.kv')
Builder.load_file('JoystickScreen.kv')
SCREEN_MANAGER.add_widget(MainScreen(name=MAIN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(PictureScreen(name=PICTURE_SCREEN_NAME))
SCREEN_MANAGER.add_widget(JoystickScreen(name=JOYSTICK_SCREEN_NAME))
SCREEN_MANAGER.add_widget(PassCodeScreen(name='passCode'))
SCREEN_MANAGER.add_widget(PauseScreen(name='pauseScene'))
SCREEN_MANAGER.add_widget(AdminScreen(name=ADMIN_SCREEN_NAME))

"""
MixPanel
"""


def send_event(event_name):
    """
    Send an event to MixPanel without properties
    :param event_name: Name of the event
    :return: None
    """
    global MIXPANEL

    MIXPANEL.set_event_name(event_name)
    MIXPANEL.send_event()


if __name__ == "__main__":
    # send_event("Project Initialized")
    # Window.fullscreen = 'auto'
    ProjectNameGUI().run()
