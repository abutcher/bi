from util import *
import numpy
import math

class QuadrantTree:
	
	#@print_timing
	def __init__(self, instances, lives=False, numlives=3):
		minx, miny = sys.maxint, sys.maxint
		maxx, maxy = -sys.maxint, -sys.maxint
		for instance in instances:
			if instance.coord.x < minx:
				minx = instance.coord.x
			if instance.coord.x > maxx:
				maxx = instance.coord.x
			if instance.coord.y < miny:
				miny = instance.coord.y
			if instance.coord.y > maxy:
				maxy = instance.coord.y
		self.root = Quadrant(minx, maxx, miny, maxy, instances)
		self.minsize = math.sqrt(len(instances))
		self.max_variance = 0.0
		self.got = 0.0

		def grow(quadrant):
			if len(quadrant.instances) > self.minsize:
				quadrant.children = quadrant.split()
				for child in quadrant.children:
					if len(child.instances) == 0:
						quadrant.children.remove(child)
				for child in quadrant.children:
					grow(child)

		def grow_lives(quadrant, numlives):
			if len(quadrant.instances) > self.minsize and numlives > 0:
				quadrant.children = quadrant.split()
				for child in quadrant.children:
					if len(child.datums()) == 0:
						quadrant.children.remove(child)
						continue
					if variance(child.datums()) > variance(quadrant.datums()):
						grow_lives(child, numlives-1)
					else:
						grow_lives(child, numlives)
		if lives:			
			grow_lives(self.root, numlives)
		else:
			grow(self.root)

		#self.maxv()
			
	def leaves(self):
		leaves = []
		def collect_leaves(quadrant):
			if quadrant.children == []:
				leaves.append(quadrant)
			else:
				for child in quadrant.children:
					collect_leaves(child)
		collect_leaves(self.root)
		return leaves

	def maxv(self):
		def keep_searching(quadrant):
			if quadrant.qvariance() > self.max_variance:
				self.max_variance = quadrant.qvariance()
			for child in quadrant.children:
				if len(child.instances) == 0:
					quadrant.children.remove(child)
			if quadrant.children != []:
				for child in quadrant.children:
					keep_searching(child)
		keep_searching(self.root)
		return self.max_variance

	def classify(self, inst):
		self.got = 0.0
		def keep_searching(quadrant):
			#print quadrant.qvariance()
			#print quadrant.weighted_variance()
			if quadrant.qvariance() < 1.5 * quadrant.weighted_variance():
				self.got = quadrant.qmedian()
			else:
				if quadrant.children != []:
					minq = None
					minv = sys.maxint
					for child in quadrant.children:
						if child.qvariance() < minv:
							minv = child.qvariance()
							minq = child
					keep_searching(minq)
		keep_searching(self.root)
		if self.got == 0.0:
			self.got = self.root.qmedian()
		return self.got

	def prune(self, alpha, beta):
		maxv = self.max_variance
		def keep_cutting(quadrant, level=0):
			if level > 3:
				if quadrant.children != []:
					for child in quadrant.children:
						if len(child.instances) == 0:
							quadrant.children.remove(child)
					for child in quadrant.children:
						if alpha*quadrant.qvariance() < child.qvariance() or beta*maxv < child.qvariance():
							quadrant.children.remove(child)
					if quadrant.children != []:
						for child in quadrant.children:
							keep_cutting(child, level + 1)
		keep_cutting(self.root)
	
class Quadrant:

	def __init__(self, xmin, xmax, ymin, ymax, instances):
		self.xmin = xmin
		self.xmax = xmax
		self.ymin = ymin
		self.ymax = ymax
		self.instances = instances
		self.children = []

	def center(self):
                return [ ((self.xmax - self.xmin) / 2) + self.xmin,
			 ((self.ymax - self.ymin) / 2) + self.ymin,
			 "None" ]

        def density(self):
                n = len(self.instances)
                volume = (self.xmax - self.xmin) * (self.ymax - self.ymin)
		if volume == 0:
			return 0
		else:
			return n/volume
	
	def coords(self):
		return [ inst.coord for inst in self.instances ]

	def ClassCoords(self):
                returnset = []
                for instance in self.instances:
                        returnset.append([instance.coord.x, instance.coord.y,instance.klass()])
                return returnset

	def datums(self):
		return [ inst.datum for inst in self.instances ]
	
	def split(self):
		x_split = equal_frequency_ticks_x(self.coords(), 1)[0]
		y_split = equal_frequency_ticks_y(self.coords(), 1)[0]
		return [ Quadrant(self.xmin, x_split, self.ymin, y_split, self.instances_in_bounds(self.xmin, x_split, self.ymin, y_split)),
			 Quadrant(x_split, self.xmax, self.ymin, y_split, self.instances_in_bounds(x_split, self.xmax, self.ymin, y_split)),
			 Quadrant(self.xmin, x_split, y_split, self.ymax, self.instances_in_bounds(self.xmin, x_split, y_split, self.ymax)),
			 Quadrant(x_split, self.xmax, y_split, self.ymax, self.instances_in_bounds(x_split, self.xmax, y_split, self.ymax)) ]
		
	def instances_in_bounds(self, xmin, xmax, ymin, ymax):
		instances = []
		for instance in self.instances:
			x = instance.coord.x
			y = instance.coord.y
			if ( x >= xmin and x <= xmax) and ( y > ymin and y < ymax ):
				instances.append(instance)
		return instances

	def describe(self):
		print "Quadrant:"
		print "\tSize: %d" % (len(self.instances))

	def qvariance(self):
		return variance([inst.datum for inst in self.instances])
	
	def weighted_variance(self):
		if self.children == []:
			return self.qvariance()
		else:
			num = 0
			denom = 0
			for child in self.children:
				num += (child.qvariance() * len(child.instances))
				denom += (len(child.instances))
			return (num / denom)
			
	def qmedian(self):
		return median(transpose([inst.datum for inst in self.instances])[-1])

	def is_adjacent(self, other_quadrant):
		if ((self.xmin == other_quadrant.xmax) or (self.xmax == other_quadrant.xmin)) or ((self.ymin == other_quadrant.ymax) or (self.ymax == other_quadrant.ymin)):
			return True
		else:
			return False
