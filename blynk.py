import blynklib
import random

BLYNK_AUTH = 'BpyikgI4yxzrwf9ZzZVMFXgPpq8J5fnM'

# initialize blynk
blynk = blynklib.Blynk(BLYNK_AUTH)
values = ['2','3','4','5']
A_VPIN = 11
H_VPIN = 10
L_VPIN = 9
T_VPIN = 8
V_VPIN = 12
# register handler for virtual pin V11 reading
@blynk.handle_event('read V{}'.format(A_VPIN))
def read_handler(vpin):
    global values
   # print('pressure={} altitude={}'.format('20','23.4'))
    blynk.virtual_write(T_VPIN, values[3])
    blynk.virtual_write(H_VPIN, values[2])
    blynk.virtual_write(L_VPIN, values[4])
    blynk.virtual_write(V_VPIN, values[6])
    blynk.virtual_write(A_VPIN, values[5])


def run_blynk(data):
   global values
   values = data.split(' ')
   blynk.run()
###########################################################
# infinite loop that waits for event
###########################################################
def main():
        while True:
            blynk.run()


if __name__ == "__main__":
    # Make sure the GPIO is stopped correctly
    try:
        while True:
	   main()
    except KeyboardInterrupt:
        print("Exiting gracefully")
        # Turn off your GPIOs here
    except Exception as e:
        #print("Some other error occurred")
        print(e.message)




