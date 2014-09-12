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
		"Do something"
			
		"Talk to someone"
			#To whom will you speak?
				"Tell me what you're doing"
					#get details on the current activity
				"Stop what you're doing"
					#continue the conversation
				"When you've finished what you're doing, I want you to..."
					#identify a step and add it
					
		
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
			self.quality = newquality #Let's rank these things out of 100.
			self.units = newunits
		
		def canuse(amount):
		    return (self.quantity >= amount)
		   
		def use(amount):
			self.quantity -= amount
			
		def endofturn:
			return
			
	class InfiniteIngredient(Ingredient):
	    def canuse(amount):
			return True
			
		def use(amount):
			return
			
			
	class Tool(Ingredient):
		def __init__(self, newname = 'Unnamed tool', newquantity = 0, newquality = 0):
			Ingredient.__init__(self, newname, newquantity, newquality)
			self.beingused = 0
	
		def canuse(amount):
			return ((self.quantity - self.beingused) >= amount)
			
		def use(amount):
			self.beingused += amount
			
		def endofturn:
			self.beingused = 0
			
	class Oven(Tool):
		def __init__(self, newname = 'Oven',1)
			Tool.__init__(self, newname)
			self.timeremaining = 0
			
		def use(amount):
			self.beingused = 1
			self.timeremaining = amount
			
		def endofturn:
			if self.timeremaining > 0:
				self.timeremaining -= 1
				if self.timereamining = 0:
					self.beingused = 0
			
	def InitBasicIngredients:
		water = new InfiniteIngredient('Reclaimed Water', 10000000, 30, 'ml')
		salt = new Ingredient('Salt', 1000, 100, 'mg')
		flour = new Ingredient('Plain Flour', 5000, 100, 'g')
		sourdough = new InfiniteIngredient('Leftover dough', 200, 100, 'g')
		yeast = new Ingredient('Yeast', 200, 100, 'g')
		mixingbowl = new Tool('Mixing bowl', 1, 100)
		rollingpin = new Tool('Rolling pin', 1, 100)
		oven = new Oven()
			
			
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
		def __init__(self)
			self.name = 'Undefined baking action'
			self.skillsneeded = []	
	
	class BakingStep(Step):
		def __init__(self):

			self.ingredientsneeded = []
			self.productname = 'Undefined baking product'
			
	class Recipe(BakingAction):
		def __init__(self)
			self.steps = []