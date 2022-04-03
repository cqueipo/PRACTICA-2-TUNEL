#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  3 13:19:49 2022

@author: mat
"""


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
        self.north_waiting = Value('i',0) #Número de coches que vienen del norte esperando
        self.south_waiting = Value('i',0)
        self.south_inside = Value('i',0)
        self.north_inside = Value('i',0) #Número de coches que vienen del norte dentro del túnel
        self.free_tunnel_north=Condition(self.mutex)
        self.free_tunnel_south= Condition(self.mutex)

    def is_free_tunnel_north(self): #Pasan coches si esperan más en el norte que en el sur, si no pasan coches del sur
        return self.north_waiting.value >= self.south_waiting.value and self.south_inside.value == 0

    def is_free_tunnel_south(self):
        return self.south_waiting.value >= self.north_waiting.value and self.north_inside.value == 0

    def wants_enter(self, direction):
        self.mutex.acquire()
        if direction == NORTH:
            self.north_waiting.value += 1
            self.free_tunnel_north.wait_for(self.is_free_tunnel_north)
            self.north_inside.value += 1 #Aumentamos el valor de coches dentro del túnel
            self.north_waiting.value -= 1
            self.mutex.release()
        else:
            self.south_waiting.value += 1
            self.free_tunnel_south.wait_for(self.is_free_tunnel_south)
            self.south_inside.value += 1 
            self.south_waiting.value -= 1
            self.mutex.release()

    def leaves_tunnel(self, direction):
        self.mutex.acquire()
        if direction == NORTH:
            self.north_inside.value -= 1   
            self.free_tunnel_north.notify_all()
            self.free_tunnel_south.notify_all()
            self.mutex.release()
        else:
            self.south_inside.value -= 1
            self.free_tunnel_south.notify_all()  
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
        direction = NORTH if random.randint(0,9)==1  else SOUTH
        cid += 1
        p = Process(target=car, args=(cid, direction, monitor))
        p.start()
        time.sleep(random.expovariate(1/0.5)) # a new car enters each 0.5s

if __name__ == '__main__':    
    main()
