# state-machines
Pls refer to mit open-course 6.01sc. No src available, so I wrote mine.


example:
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
