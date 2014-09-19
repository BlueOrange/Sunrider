#Blue's crafting framework and bakery mod.

label bakery_welcome:
    "This is a very early pre-alpha of the bakery!"
    #set current location = back of house
    #draw bakery background
    #characters to their starting places
    #if first day, go with first day dialogue and first day plan selection method
        #If 'do what you usually do', then load the pre-existing plan.  Else set all plans to None.
        jump bakery_turn_loop
    #if second day, go with second day dialogue, else present default welcome
    #present plan selection choices
    jump bakery_turn_loop  #Yeah, I know, not strictly required.
    
    
label bakery_turn_loop:
    call bakery_status_here
    $bakery_action_chosen = False
    call bakery_action_menu
    if bakery_action_chosen
        call bakery_events_here
        time += 1
        if time >= bakery_closing_time then
            jump bakery_closed
    jump bakery_turn_loop
    
label bakery_satus_here:
    python:
        foreach baker in bakery.bakers
            if baker.location == bakery_here
                renpy.say(baker.statusmessage)
        
    
    
label bakery_action_menu:
    menu:
        "Make something" (in back of house)
        "Serve customers" (in front of house)
        "Buy ingredients" (in spaceport)
        "Sell products" (in spaceport)
                        
            
        "Talk to someone"
            #To whom will you speak?
                "Tell me what you're doing"
                    #get details on the current activity
                "Stop what you're doing"
                    #continue the conversation
                "Before you keep going, I want you to..."
                    #identify a step and stack it
                "When you've finished what you're doing, I want you to..."
                    #identify a step and queue it
                    
        
        "Watch something"
        
        "Go somewhere"
            "Go to spaceport"
            "Go to back of house"
            "Go to front of house"



python:

    class Ingredient(store.object):
       
        def __init__(self, newname = 'Unnamed ingredient', newquantity = 0, newquality = 0, newunits = ''):
            self.quantity = newquantity
            self.name = newname
            self.quality = newquality #Neutral quality is zero.  Higher is good, lower is bad
            self.units = newunits
        
        def canuse(self, amount):
            return (self.quantity >= amount)
           
        def use(self, amount):
            self.quantity -= amount
            
        def endofturn:
            return
            
    class InfiniteIngredient(Ingredient):
        def canuse(self, amount):
            return True
            
        def use(self, amount):
            return
            
            
    class Tool(Ingredient):  #For items that are used briefly.  Amount used is ignored, you're always using 1.  Set it to zero so that you don't get multiples listed if you use the same tool more than once
        def __init__(self, newname = 'Unnamed tool', newquantity = 1, newquality = 0):
            Ingredient.__init__(self, newname, newquantity, newquality)
            self.beingused = 0
    
        def canuse(self, amount):  
            return ((self.quantity - self.beingused) > 0)
            
        def use(self, amount):
            self.beingused += 1
            
        def endofturn(self):
            self.beingused = 0
            
    class Facility(Tool):  #For unique items that are used for long periods of time.  Amount used reflects the amount of time you use it for
        def __init__(self, newname = 'Oven',1)
            Tool.__init__(self, newname)
            self.timeremaining = 0
            
        def use(amount):
            self.beingused = 1
            self.timeremaining = amount
            
        def endofturn(self):
            if self.timeremaining > 0:
                self.timeremaining -= 1
                if self.timereamining = 0:
                    self.beingused = 0
            
    def InitBasicIngredients:
        water = new InfiniteIngredient('Reclaimed Water', 10000000, -30, 'ml')
        salt = new Ingredient('Salt', 1000, 0, 'mg')
        flour = new Ingredient('Plain Flour', 5000, 0, 'g')
        sourdough = new InfiniteIngredient('Leftover dough', 200, 0, 'g')
        yeast = new Ingredient('Yeast', 200, 0, 'g')
        mixingbowl = new Tool('Mixing bowl', 1, 0)
        rollingpin = new Tool('Rolling pin', 1, 0)
        oven = new Facility('Oven')
            
            
    class Product(Ingredient):
        def __init__(self, newmaker = DefaultBaker, newingredients = [])
            BakingIngredient.__init__(self)
            self.maker =newmaker
            self.quantity = 1
            self.quality = newquality
            self.insidepoints = 0
            self.outsidepoints = 0
            self.flavourpoints = 0
            
    class Skill(store.object):
        def __init__(self):
            self.name = 'Undefined skill'
            self.level = 0
            
    class Baker(store.object):
        def __init__(self):
            self.name = 'Unnamed baker'
            self.skills = []
            self.plansknown = []
            self.currentplan = None
            
    class Step(store.object):
        def __init__(self, newactor = None, newname = 'Unnamed step')
            self.name = newname
            self.skillsneeded = []    
            self.actor = newactor
            self.report = ''
            
        def assignactor(newactor)
            self.actor = newactor
        def perform():
            if actor == None:
                self.report = 'Nobody was assigned to ' + self.name
                return False
            else:
                self.report = self.actor.name + ' completed ' + self.name
                return True
            
    class Move(Step):
        def __init__(self, newactor = None, newdestination = None)
            Step.__init__(self, newactor, 'go to ' + newdestination)
            self.destination = newdestination
            
        def perform():  #Yeah, in theory we should check if they /can/ go there.  This mini-game is complicated enough.
            if not Step.perform():
                return False
            if self.actor.location == 'spaceport':
                self.actor.setintransit(self.destination)
            elif self.destination == 'spaceport':
                self.actor.setintransit('spaceport_actual')
            elif self.destination == 'spaceport_actual':
                self.actor.location = 'spaceport'
            else:
                self.actor.location = self.destination 
            self.report = self.actor.name + ' went to ' + self.destination
            return True
    
    class MakingStep(Step):
        def __init__(self, newactor = None, newname = 'Unnamed making step', newingredientsneeded = [], newproductname = 'Undefined product', newquantity = 1):
            Step.__init__(self, newactor, newname)
            self.ingredientsneeded = newingredientsneeded
            self.productname = newproductname
            self.quantity = 1
            self.output = None
            
        def perform(self):
            if not Step.perform():
                return False
            if self.checkperformance():
                self.createoutput()
                self.useingredients()
                
        def checkperformance(self):#asks "are we in the right place, with the right ingredients, and the right skills?"
            return True 
            
        def createoutput(self): #makes skill rolls, inspects ingredient objects and sets self.output to a Product object
    
    class Plan(Step):
        def __init__(self, newactor = None, newname = 'Unnamed plan',  newsteps = [], newcurrentstep = 0)
            Step.__init__(self, newactor, newname)
            self.steps = []
            self.currentstep = 0
            
        def perform():
            if self.steps(self.currentstep).perform:
                self.currentstep += 1
            else:
                self.report = self.actor + ' was unable to ' + self.name + ' because '+ self.steps(self.currentstep).report            
            
    class Recipe(Plan, MakingStep):
        

        def requiredingredients(self):
            result = []
            foreach step in self.steps
                addingredients(result, self.steps.requiredingredients)

            
        