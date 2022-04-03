import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

SOUTH = "north"
NORTH = "south"
NCARS = 20

class Monitor():
    def __init__(self):
        self.mutex = Lock()
        self.lim = Value('i',0)
        self.north_waiting = Value('i',0) #Número de coches que vienen del norte esperando
        self.south_waiting = Value('i',0)
        self.south_passed = Value('i',0) #Número de coches que vienen del sur que han pasado
        self.north_passed = Value('i',0)
        self.south_inside = Value('i',0)
        self.north_inside = Value('i',0) #Número de coches que vienen del norte dentro del tunel
        self.free_tunnel_north = Condition(self.mutex)
        self.free_tunnel_south = Condition(self.mutex)

    def is_free_tunnel_north(self): #Comprueba que hayan pasado los coches que esperaban o no haya nadie esperando en el sur, y que ningun coche venga del sur
        return (self.north_passed.value <= self.lim.value or self.south_waiting.value == 0) and self.south_inside.value == 0
 
    def is_free_tunnel_south(self):
        return (self.south_passed.value <= self.lim.value or self.north_waiting.value == 0) and self.north_inside.value == 0

    def wants_enter(self, direction):
        self.mutex.acquire()
        if direction == NORTH:
            self.north_waiting.value +=1
            self.free_tunnel_north.wait_for(self.is_free_tunnel_north)
            self.north_waiting.value -=1
            self.north_inside.value += 1
            self.north_passed.value += 1
            self.mutex.release()
        else:
            self.south_waiting.value +=1
            self.free_tunnel_south.wait_for(self.is_free_tunnel_south)
            self.south_waiting.value -=1
            self.south_inside.value += 1 
            self.south_passed.value += 1
            self.mutex.release()

    def leaves_tunnel(self, direction):
        self.mutex.acquire()
        if direction == NORTH:
            self.north_inside.value -= 1  
            self.south_passed.value = 0 #Reinciamos los coches que han pasado del otro sentido
            if self.north_passed.value == 1: #Cuando cambia el sentido cambiamos lim
                self.lim.value = self.north_waiting.value + 1
            if self.north_passed.value <= self.lim.value or self.south_waiting.value == 0 :
                self.free_tunnel_north.notify_all()
            else:
                self.free_tunnel_south.notify_all()
            self.mutex.release()
        else:
            self.south_inside.value -= 1
            self.north_passed.value = 0
            if self.south_passed.value == 1:
                self.lim.value = self.south_waiting.value + 1 
            if self.south_passed.value <= self.lim.value or self.north_waiting.value == 0 :
                self.free_tunnel_south.notify_all()
            else:
                self.free_tunnel_north.notify_all()
            self.mutex.release()

def delay(n=3):
    time.sleep(random.random()*n)


def car(cid, direction, monitor):
    print(f"car {cid} direction {direction} created")
    delay(6)
    print(f"car {cid} heading {direction} wants to enter")
    monitor.wants_enter(direction)
    print(f"car {cid} heading {direction} enters the tunnel")
    delay(3)
    print(f"car {cid} heading {direction} leaving the tunnel")
    monitor.leaves_tunnel(direction)
    print(f"car {cid} heading {direction} out of the tunnel")



def main():
    monitor = Monitor()
    cid = 0
    for _ in range(NCARS):
        direction = NORTH if random.randint(0,8)==1  else SOUTH
        cid += 1
        p = Process(target=car, args=(cid, direction, monitor))
        p.start()
        time.sleep(random.expovariate(1/0.5)) # a new car enters each 0.5s

if __name__ == '__main__':    
    main()