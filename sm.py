
tagNo=0

k=-1.5
dDesired=1.0
deltaT=0.1

class SM(object):
    #__metaclass__=SMMeta
    def __init__(self):
        global tagNo
        tagNo+=1
        self.startState=None
        self.inp=None
        self.out=None
        self.combinator=False
        self.classTag=self.__class__.__name__+"_"+str(tagNo)
    def start(self):
        self.state=self.startState
    def getNextValues(self,state,inp):
        nextState=self.getNextState(state,inp)
        return (nextState,nextState)
    def step(self,inp,verbose=False):
        (s,o)=self.getNextValues(self.state,inp)
        self.state=s    # memorize the necessity value for the next step
        self.inp=inp
        self.out=o
        if verbose==True:
            self.debug()
        return o    
    def transduce(self,inputs,verbose=False):
        self.start()
        if verbose==True:
            print "Start state: "+str(self.startState)
            n=len(inputs)
            for i in range(n):
                if not self.done(self.state):
                    print
                    print "Step: "+str(i) 
                    self.step(inputs[i],verbose)
        else:
            return [self.step(inp,verbose) for inp in inputs if not self.done(self.state)]
    def run(self,n=10,verbose=False): 
        return self.transduce([None]*n,verbose)
    def debug(self,indent=0):
        self.indent=indent
        print "   "*self.indent+self.classTag+" In: "+str(self.inp)+" Out: "+str(self.out)+" Next state: "+str(self.state)
    def done(self,state):
        return False

class Delay(SM):
    def __init__(self,v0):
        SM.__init__(self)
        self.startState=v0
    def getNextValues(self,state,inp):
        if inp == 'undefined':
            return (None,state)  
        return (inp,state)

class Parallel(SM):
    # 1 in 2 out
    def __init__(self,sm1,sm2):
        SM.__init__(self)
        self.combinator=True 
        self.m1=sm1
        self.m2=sm2
        self.startState=(sm1.startState,sm2.startState)
    def start(self):
        SM.start(self)
        self.m1.start()
        self.m2.start()
    def getNextValues(self,state,inp):
        (s1,s2)=state
        (newS1,o1)=self.m1.getNextValues(s1,inp)
        if isinstance(o1,list) or isinstance(o1,tuple):
            o1=o1[-1]
        (newS2,o2)=self.m2.getNextValues(s2,inp)
        if isinstance(o2,list) or isinstance(o2,tuple):
            o2=o2[-1]
        return ((newS1,newS2),(o1,o2))
    def step(self,inp,verbose=False):
        o1=self.m1.step(inp)
        o2=self.m2.step(inp)
        if verbose==True:
            self.debug()
        self.state=(o1,o2)
        return (o1,o2)
    def transduce(self,inputs,verbose=False):
        self.start()
        o=[]
        if verbose==True:
            print "Start state: "+str(self.startState)
            for i in range(len(inputs)):
                if not self.done(self.state):
                    print
                    print "Inputs["+str(i)+"]: "+str(inputs[i])
                    print " "+self.classTag 
                    o.append(self.step(inputs[i],verbose))
            return o
        else:
            return [self.step(inp,verbose) for inp in inputs  if not self.done(self.state)]
    def debug(self,indent=0):
        self.indent=indent
        if self.m1.combinator:
            print "   "*(self.indent+1)+self.m1.classTag
        self.m1.debug(self.indent+1)
        if self.m2.combinator:
            print "   "*(self.indent+1)+self.m2.classTag
        self.m2.debug(self.indent+1)
        
class Cascade(SM):
    def __init__(self,sm1,sm2):
        SM.__init__(self)
        self.combinator=True
        self.m1=sm1
        self.m2=sm2
        self.startState=(self.m1.startState,self.m2.startState)
    def start(self):
        SM.start(self)
        self.m1.start()
        self.m2.start()
    def getNextValues(self,state,inp):
        s1,o1=self.m1.getNextValues(state[0],inp)      
        if isinstance(o1,list) or isinstance(o1,tuple):
            o1=o1[-1]
        s2,o2=self.m2.getNextValues(state[1],o1)
        if isinstance(o2,list) or isinstance(o2,tuple):
            o2=o2[-1]
        return ((s1,s2),o2)
    def step(self,inp,verbose=False):
        (s,_)=self.getNextValues(self.state,inp)
        o1=self.m1.step(inp)
        o2=self.m2.step(o1)            
        if verbose==True:
            self.debug()
        self.state=s
        return o2
    def transduce(self,inputs,verbose=False):
        self.start()
        o=[]
        if verbose==True:
            print "Start state: "+str(self.startState)
            for i in range(len(inputs)):
                if not self.done(self.state):
                    print
                    print "Inputs["+str(i)+"]: "+str(inputs[i])
                    print " "+self.classTag 
                    o.append(self.step(inputs[i],verbose))
            return o
        else:
            return [self.step(inp,verbose) for inp in inputs  if not self.done(self.state)]
    def debug(self,indent=0):
        self.indent=indent
        if self.m1.combinator:
            print "   "*(self.indent+1)+self.m1.classTag
        self.m1.debug(self.indent+1)
        if self.m2.combinator:
            print "   "*(self.indent+1)+self.m2.classTag
        self.m2.debug(self.indent+1)
    def run(self,n=10,verbose=False):
        self.start()
        if verbose==True:
            print "Start state: "+str(self.startState)
            for i in range(n):
                if not self.done(self.state):
                    print
                    print "Step: "+str(i)
                    print " "+self.classTag 
                    self.step(None,verbose)
        else:
            return [self.step(inp,verbose) for inp in [None]*n  if not self.done(self.state)]

class Feedback(SM):
    def __init__(self,sm):
        SM.__init__(self)
        self.combinator=True
        self.m=sm
        self.startState=self.m.startState
    def getNextValues(self,state,inp):
        (_,o)=self.m.getNextValues(state,'undefined')
        if isinstance(o,list) or isinstance(o,tuple):
            o=o[-1]
        (newS,_)=self.m.getNextValues(state,o)
        if isinstance(o,list) or isinstance(o,tuple):
            o=o[-1]
        return (newS,o)
    def step(self,inp,verbose=False):
        (s,o)=self.getNextValues(self.state,inp)    
        self.m.step(o)         # feedback input                    
        self.state=s
        if verbose==True:
            self.debug()
        return o
    def debug(self,indent=0):
        self.indent=indent
        if self.m.combinator:
            print "   "*(self.indent+1)+self.m.classTag
        self.m.debug(self.indent+1)
    def start(self):
        SM.start(self)
        self.m.start()
    def run(self,n=10,verbose=False):
        self.start()
        if verbose==True:
            print "Start state: "+str(self.startState)
            for i in range(n):
                if not self.done(self.state):
                    print
                    print "Step: "+str(i)
                    print " "+self.classTag 
                    self.step(None,verbose)
        else:
            return [self.step(inp,verbose) for inp in [None]*n]

class Feedback2(Feedback):
    def getNextValues(self,state,inp):
        (_,o)=self.m.getNextValues(state,(inp,'undefined'))
        if isinstance(o,list) or isinstance(o,tuple):
            o=o[-1]
        (newS,_)=self.m.getNextValues(state,(inp,o))
        if isinstance(o,list) or isinstance(o,tuple):
            o=o[-1]
        return (newS,o)
    def step(self,inp,verbose=False):
        (s,o)=self.getNextValues(self.state,inp)    
        self.m.step(inp)                         
        self.state=s
        if verbose==True:
            self.debug()
        return o

class Wire(SM):
    def __init__(self):
        SM.__init__(self)
        self.startState=0
    def getNextState(self,state,inp):
        if inp=='undefined':
            return self.state
        return inp

class FeedbackAdd(SM):
    def __init__(self,sm1,sm2):
        SM.__init__(self)
        self.combinator=True
        self.m1=sm1
        self.m2=sm2
        self.startState=(sm1.startState,sm2.startState)
    def getNextValues(self,state,inp):
        (_,o1)=self.m1.getNextValues(state[0],'undefined')
        if isinstance(o1,list) or isinstance(o1,tuple):
            o1=o1[-1]
        (_,o2)=self.m2.getNextValues(state[1],o1)
        if isinstance(o2,list) or isinstance(o2,tuple):
            o2=o2[-1]
        o2+=inp           # Add
        (newS1,o)=self.m1.getNextValues(state[0],o2)
        (newS2,_)=self.m2.getNextValues(state[1],o)
        return ((newS1,newS2),(o1,o2))
    def step(self,inp,verbose=False):
        (s,o)=self.getNextValues(self.state,inp)
        self.m2.step(o[0])
        self.m1.step(o[1])                             
        self.state=s
        if verbose==True:
            self.debug()
        return o[1]
    def debug(self,indent=0):
        self.indent=indent
        if self.m1.combinator:
            print "   "*(self.indent+1)+self.m1.classTag
        self.m1.debug(self.indent+1)
        if self.m2.combinator:
            print "   "*(self.indent+1)+self.m2.classTag
        self.m2.debug(self.indent+1)
    def start(self):
        SM.start(self)
        self.m1.start()
        self.m2.start()
    def transduce(self,inputs,verbose=False):
        self.start()
        o=[]
        if verbose==True:
            print "Start state: "+str(self.startState)
            for i in range(len(inputs)):
                if not self.done(self.state):
                    print
                    print "Inputs["+str(i)+"]: "+str(inputs[i])
                    print " "+self.classTag 
                    o.append(self.step(inputs[i],verbose))
            return o
        else:
            return [self.step(inp,verbose) for inp in inputs  if not self.done(self.state)]

class WallController(SM):
    def __init__(self):
        SM.__init__(self)
        self.startState=0
    def getNextState(self,state,inp):
        if inp=='undefined': 
            return state
        else:
            return k*(dDesired-inp)


class WallWorld(SM):
    def __init__(self):
        SM.__init__(self)
        self.startState=5
    def getNextValues(self,state,inp):
        return (state-deltaT*inp,state)

class Multiplier(SM):
    def getNextState(self,state,inp):
        (i1,i2)=inp
        if i2 == 'undefined':   
            if state==None:
                state=1    
            return state*i1
        else:
            return i1*i2

class Switch(SM):
    def __init__(self,condition,sm1,sm2):
        SM.__init__(self)
        self.m1=sm1
        self.m2=sm2
        self.condition=condition
        self.startState=(self.m1.startState,self.m2.startState)
        self.combinator=True
        self.case=None
    def getNextValues(self,state,inp):
        (s1,s2)=state
        if self.condition(inp):
            self.case=1
            (ns1,o)=self.m1.getNextValues(s1,inp)
            if isinstance(o,list) or isinstance(o,tuple):
                o=o[-1]
            return ((ns1,s2),o)
        else:
            self.case=2
            (ns2,o)=self.m1.getNextValues(s2,inp)
            if isinstance(o,list) or isinstance(o,tuple):
                o=o[-1]
            return ((s1,ns2),o)
    def step(self,inp,verbose=False):
        (s,o)=self.getNextValues(self.state,inp)
        self.state=s
        if self.case==1:
            self.m1.step(inp)  
        elif self.case==2:
            self.m2.step(inp)            
        if verbose==True:
            self.debug()
        return o
    def debug(self,indent=0):
        self.indent=indent
        if self.case==1:
            if self.m1.combinator:
                print "   "*(self.indent+1)+self.m1.classTag
            self.m1.debug(self.indent+1)
        elif self.case==2:
            if self.m2.combinator:
                print "   "*(self.indent+1)+self.m2.classTag
            self.m2.debug(self.indent+1)
    def start(self):
        SM.start(self)
        self.m1.start()
        self.m2.start()
    def transduce(self,inputs,verbose=False):
        self.start()
        if verbose==True:
            print "Start state: "+str(self.startState)
            print " "+self.classTag
        return [self.step(inp,verbose) for inp in [None]*n  if not self.done(self.state)]
        
class Mux(Switch):
    def getNextValues(self,state,inp):
        (s1,s2)=state
        (ns1,o1)=self.m1.getNextValues(s1,inp)
        (ns2,o2)=self.m2.getNextValues(s2,inp)
        if self.condition(inp):
            self.case=1    
            return ((ns1,ns2),o1)
        else:
            self.case=2
            return ((ns1,ns2),o2)
    def step(self,inp,verbose=False):
        (s,o)=self.getNextValues(self.state,inp)
        self.state=s
        self.m1.step(inp)  
        self.m2.step(inp)            
        if verbose==True:
            self.debug()
        return o

    
class Accumulator(SM):
    def __init__(self,initialValue=0):
        SM.__init__(self)
        self.startState=initialValue
    def getNextValues(self,state,inp):
        if inp=='undefined': 
            return state,state
        return state+inp,state+inp

class If(SM):
    def __init__(self,initialValue=0):
        SM.__init__(self,condition,sm1,sm2)
        self.combinator=True
        self.startState=('start',None)
        self.m1=sm1
        self.m2=sm2
        self.condition=contition
        self.case=None
    def getFirstRealState(self,inp):
        if self.condition(inp):
            return ('runningM1',self.m1.startState)
        else:
            return ('runningM2',self.m2.startState)
    def getNextValues(self,state,inp):
        (ifState,smState)=state
        if ifState=='start':     
            (ifState,smState)=self.getFirstRealState(inp)
        if ifState=='runningM1':
            self.case=1
            (newS,o)=self.m1.getNextValues(state,inp)
            if isinstance(o,list) or isinstance(o,tuple):
                o=o[-1]
            return(('runningM1',newS),o)
        else:
            self.case=2
            (newS,o)=self.m2.getNextValues(state,inp)
            if isinstance(o,list) or isinstance(o,tuple):
                o=o[-1]
            return(('runningM2',newS),o)
    def step(self,inp,verbose=False):
        (s,o)=self.getNextValues(self.state,inp)
        self.state=s
        if s[0]=='runningM1': 
            self.m1.step(inp)
        else:
            self.m2.step(inp)            
        if verbose==True:
            self.debug()
        return o
    def debug(self,indent=0):
        self.indent=indent
        if self.case==1:
            if self.m1.combinator:
                print "   "*(self.indent+1)+self.m1.classTag
            self.m1.debug(self.indent+1)
        elif self.case==2:
            if self.m2.combinator:
                print "   "*(self.indent+1)+self.m2.classTag
            self.m2.debug(self.indent+1)

class ConsumeFiveValues(SM):
    def __init__(self):
        SM.__init__(self)
        self.startState=(0,0)
    def getNextValues(self,state,inp):
        (count,total)=state
        if count==4:
            return ((count+1,total+inp),total+inp)
        else:
            return ((count+1,total+inp),None)
    def done(self,state):
        (count,total)=state
        return count==5
    def transduce(self,inputs,verbose=False):
        self.start()
        if verbose==True:
            print "Start state: "+str(self.startState)
        return [self.step(inp,verbose) for inp in inputs if not self.done(self.state)]

class Repeat(SM):
    def __init__(self,sm,n=None):
        SM.__init__(self)
        self.combinator=True
        self.m=sm
        self.startState=(0,self.m.startState)
        self.n=n
    def advanceIfDone(self,counter,smState):
        while self.m.done(smState) and not self.done((counter,smState)):
            counter+=1
            smState=self.m.startState
        return (counter,smState)
    def getNextValues(self,state,inp):
        (counter,smState)=state
        (smState,o)=self.m.getNextValues(smState,inp)
        if isinstance(o,list) or isinstance(o,tuple):
            o=o[-1]
        (counter,smState)=self.advanceIfDone(counter,smState)
        return ((counter,smState),o)
    def step(self,inp,verbose=False):
        (s,o)=self.getNextValues(self.state,inp)    
        self.m.step(inp)                      
        self.state=s
        self.m.state=s[1] 
        self.inp=inp
        self.out=o
        if verbose==True:
            self.debug()
        return o
    def start(self):
        SM.start(self)
        self.m.start()
    def done(self,state):
        (counter,smState)=state
        return counter==self.n
    def transduce(self,inputs,verbose=False):
        self.start()
        if verbose==True:
            print "Start state: "+str(self.startState)
            n=len(inputs)
            for i in range(n):
                if not self.done(self.state):
                    print
                    print "Step: "+str(i)
                    #print " "+self.classTag 
                    self.step(inputs[i],verbose)
        else:
            return [self.step(inp,verbose) for inp in inputs if not self.done(self.state)]

class Sequence(SM): 
    def __init__(self,smList):
        SM.__init__(self)
        self.combinator=True
        self.smList=smList
        self.startState=(0,self.smList[0].startState)
        self.n=len(smList)
    def advanceIfDone(self,counter,smState):
        while self.smList[counter].done(smState) and counter+1<self.n:
            counter+=1
            smState=self.smList[counter].startState
        return (counter,smState)
    def getNextValues(self,state,inp):
        (counter,smState)=state
        (smState,o)=self.smList[counter].getNextValues(smState,inp) 
        if isinstance(o,list) or isinstance(o,tuple):
            o=o[-1]
        (counter,smState)=self.advanceIfDone(counter,smState)       
        return ((counter,smState),o)
    def step(self,inp,verbose=False):
        self.smList[self.state[0]].step(inp)   # current step
        (s,o)=self.getNextValues(self.state,inp)
        self.state=s       
        self.smList[s[0]].state=s[1]
        self.inp=inp
        self.out=o
        #print " "+self.classTag+" "+"Next State: "+str(s)
        if verbose==True:
            self.debug()
        return o
    def done(self,state):
        (counter,smState)=state
        return self.smList[counter].done(smState)
    def start(self):
        SM.start(self)
        self.smList[self.state[0]].start()
    def transduce(self,inputs,verbose=False):
        self.start()
        if verbose==True:
            print "Start state: "+str(self.startState)
            n=len(inputs)
            for i in range(n):
                if not self.done(self.state):
                    print
                    print "Step: "+str(i)
                    #print " "+self.classTag 
                    self.step(inputs[i],verbose)
        else:
            return [self.step(inp,verbose) for inp in inputs if not self.done(self.state)]

class RepeatUntil(SM):
    #Test condition on input
    def __init__(self,condition,sm):
        SM.__init__(self)
        self.combinator=True
        self.m=sm
        self.condition=condition
        self.startState=(False,self.m.startState)
    def getNextValues(self,state,inp):
        (condTrue,smState)=state
        (smState,o)=self.m.getNextValues(smState,inp)
        if isinstance(o,list) or isinstance(o,tuple):
            o=o[-1]
        condTrue=self.condition(inp)
        if self.m.done(smState) and not condTrue:
            smState=self.m.startState
        return ((condTrue,smState),o)
    def done(self,state):
        (condTrue,smState)=state
        return self.m.done(smState) and condTrue
    def start(self):
        SM.start(self)
        self.m.start()
    def step(self,inp,verbose=False):
        (s,o)=self.getNextValues(self.state,inp)
        self.m.step(inp)                      
        self.state=s
        self.m.state=s[1]   
        self.inp=inp
        self.out=o
        if verbose==True:
            self.debug()
        return o
    def transduce(self,inputs,verbose=False):
        self.start()
        if verbose==True:
            print "Start state: "+str(self.startState)
            n=len(inputs)
            for i in range(n):
                if not self.done(self.state):
                    print
                    print "Step: "+str(i)
                    #print " "+self.classTag 
                    self.step(inputs[i],verbose)
        else:
            return [self.step(inp,verbose) for inp in inputs if not self.done(self.state)]

class Until(RepeatUntil):
    def getNextValues(self,state,inp):
        (condTrue,smState)=state
        (smState,o)=self.m.getNextValues(smState,inp)
        condTrue=self.condition(inp)
        return ((condTrue,smState),o)
    def done(self,state):        
        (condTrue,smState)=state
        return self.m.done(smState) or condTrue
    def step(self,inp,verbose=False):
        (s,o)=self.getNextValues(self.state,inp)    
        self.m.step(inp)
        self.state=s
        #self.m.state=s[1]    Done is done.
        self.inp=inp
        self.out=o
        if verbose==True:
            self.debug()
        return o

class CountingStateMachine(SM):
    def __init__(self):
        SM.__init__(self)
        self.startState=0
    def getNextValues(self,state,inp):
        return (state+1,self.getOutput(state,inp))
    def getOutput(self,state,inp):
        return state

class ParallelAdd(Parallel):
    def getNextValues(self,state,inp):
        (s1,s2)=state
        (newS1,o1)=self.m1.getNextValues(s1,inp)
        if isinstance(o1,list) or isinstance(o1,tuple):
            o1=o1[-1]
        (newS2,o2)=self.m2.getNextValues(s2,inp)
        if isinstance(o2,list) or isinstance(o2,tuple):
            o2=o2[-1]
        return ((newS1,newS2),o1+o2)
    def step(self,inp,verbose=False):
        (s,o)=self.getNextValues(self.state,inp)
        self.m1.step(inp)
        self.m2.step(inp)
        self.state=s
        self.inp=inp
        self.out=o
        if verbose==True:
            self.debug()
        return o
    def transduce(self,inputs,verbose=False):
        self.start()
        o=[]
        if verbose==True:
            print "Start state: "+str(self.startState)
            for i in range(len(inputs)):
                if not self.done(self.state):
                    print
                    print "Inputs["+str(i)+"]: "+str(inputs[i])
                    print " "+self.classTag 
                    o.append(self.step(inputs[i],verbose))
            return o
        else:
            return [self.step(inp,verbose) for inp in inputs  if not self.done(self.state)]
    def debug(self,indent=0):
        self.indent=indent
        if self.m1.combinator:
            print "   "*(self.indent+1)+self.m1.classTag
        self.m1.debug(self.indent+1)
        if self.m2.combinator:
            print "   "*(self.indent+1)+self.m2.classTag
        self.m2.debug(self.indent+1)
        print "   "*(self.indent+1)+"(out: "+str(self.out)+")"        
        
class Gain(SM):
    # state=o[t]
    def __init__(self,gain):
        SM.__init__(self)
        self.startState=gain
    def getNextValues(self,state,inp):
        o=self.state*inp
        return (self.state,o)

class Diff(SM):
    # state=i[t]
    def __init__(self,previousInput):
        SM.__init__(self)
        self.startState=previousInput 
    def getNextValues(self,state,inp):
        return (inp,inp-state)

class Adder(SM):
    def getNextState(self,state,inp):
        if inp == 'undefined':
            return state
        (i1,i2)=inp
        return i1+i2

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

class LTISM(SM):
    def __init__(self,dCoeffs,cCoeffs):
        SM.__init__(self)
        j=len(dCoeffs)-1
        k=len(cCoeffs)

        self.cCoeffs=cCoeffs
        self.dCoeffs=dCoeffs
        self.startState=([0.0]*j,[0.0]*k)

    def getNextValues(self,state,inp):
        (inputs,outputs)=state
        inputs=[inp]+inputs
        currentOutput=sum([a*b for (a,b) in zip(self.dCoeffs,inputs)])+ \
                       sum([a*b for (a,b) in zip(self.cCoeffs,outputs)])
        return ((inputs[:-1],[currentOutput]+outputs[:-1]),currentOutput)
