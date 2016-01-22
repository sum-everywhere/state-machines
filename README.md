# state-machines
Pls refer to mit open-course 6.01sc. No src available, so I wrote mine.


example 1:

import sys

sys.path.append(".")

from sm import SM,Parallel,Cascade,Delay,Feedback,FeedbackAdd,Wire, \
     Feedback2,WallController,WallWorld,Accumulator,Switch,Mux,ConsumeFiveValues, \
     Repeat,Sequence,RepeatUntil,Until,Wire,CountingStateMachine,Multiplier, \
     ParallelAdd,Gain,Diff,Adder

# Y/X=(1-R**2)(R**3)
m=Cascade(ParallelAdd(Wire(),Cascade(Gain(-1),Delay(2))),Delay(3)) 

m.transduce([1,0,0,0],verbose=True)

# fibonacci
fib=Feedback(Cascade(Parallel(Delay(1),Cascade(Delay(1),Delay(0))),Adder()))

fib.run(verbose=True)


example 2:
'''
from matplotlib import pyplot as plt

import math

sys.path.append(".")

from sm import SM,Parallel,Cascade,Delay,Feedback,FeedbackAdd,Wire, \
     Feedback2,WallController,WallWorld,Accumulator,Switch,Mux,ConsumeFiveValues, \
     Repeat,Sequence,RepeatUntil,Until,Wire,CountingStateMachine,Multiplier, \
     ParallelAdd,Gain,Diff,Adder

def delta(x):
    if x==0:
        return 1
    return 0
class Delta(SM):
    def __init__(self):
        SM.__init__(self)
        self.startState=0
    def getNextValues(self,state,inp):
        state=delta(inp)
        if inp=='undefined':
            if state==-1:
                return (None,1)
            else:
                return (None,0)
        return (state,state)
X=range(-1,40)
plt.axis('auto')
plt.axvline(x=0)
plt.axhline(y=0)
# p=r*e**(j*omega)
p=0.85*(math.e**(1j*math.pi/4))  
# Y/X=1/((1-p)R)
m=Cascade(Delta(),Cascade(FeedbackAdd(Delay(0),Gain(p)),Gain(1)))
Y=m.transduce(X)
A=[y.real for y in Y]
B=[y.imag for y in Y]
plt.plot(A,B,'bo')
plt.show
'''

