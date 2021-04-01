import random
import sys
import math
import numpy as np

# Boundaries for track generation
track_boundary_x_lower = 6.06
track_boundary_x_upper = 90.9
track_boundary_y_lower = 0.0
track_boundary_y_upper = 262.7

# Hit distance resolution, in mm
hit_resolution = 0.100

# Radius of straws, in mm. Hits further from this distance from the wire should be excluded.
straw_rad = 2.5

class Wire:
    
    # Class representing a single wire in the detector

    def __init__(self, x_rel_to_layer, x_layer_absolute, y_layer_absolute):
        
        # Finds up absolute x-position of wire, and sets other variables         
        self.x_rel_to_layer = x_rel_to_layer
        self.y_layer_absolute = y_layer_absolute
        self.absolute_x = self.x_rel_to_layer + x_layer_absolute

    def get_x_rel_to_layer(self):
        # Returns position relative to layer
        return self.x_rel_to_layer

    def get_absolute_x(self):
        # Returns absolute x-pos
        return self.absolute_x

    def get_absolute_y(self):
        # Returns absolute y-pos (same as parent layer)
        return self.y_layer_absolute

    def set_absolute_layer_x(self, x_layer_absolute):
        # Sets new position of wire, from new position of layer
        self.absolute_x = self.x_rel_to_layer + x_layer_absolute


class Layer:

    # Class representing a layer of wires

    def __init__(self, x_rel_to_plane, y_rel_to_plane, x_plane_absolute, y_plane_absolute):

        # Gets absolute position of layer
        self.x_rel_to_plane = x_rel_to_plane
        self.y_rel_to_plane = y_rel_to_plane
        self.absolute_x = self.x_rel_to_plane + x_plane_absolute
        self.absolute_y = self.y_rel_to_plane + y_plane_absolute
        
        # Creates set of wires within layer
        self.wires = [Wire(6.06 * i, self.absolute_x, self.absolute_y) for i in range(16)]

    def get_x_rel_to_plane(self):
        # Returns x-pos of layer relative to parent plane
        return self.x_rel_to_plane;

    def get_y_rel_to_plane(self):
        # Returns y-pos of layer relative to parent plane        
        return self.y_rel_to_plane;

    def get_wires_x(self):
        # Returns x-pos of all wires in layer
        return [wire.get_absolute_x() for wire in self.wires]
    
    def get_wires_y(self):
        # Returns y-pos of all wires in layer
        return [wire.get_absolute_y() for wire in self.wires]
    
    def get_wires(self):
        # Returns all wires in layer
        return self.wires

    def set_absolute_plane_x(self, x_plane_absolute):
        # Sets new position for layer, from new position of plane
        self.absolute_x = self.x_rel_to_plane + x_plane_absolute
        for wire in self.wires:
            wire.set_absolute_layer_x(self.absolute_x)
        

class Plane:

    # Class representing a plane of two layers of wires

    def __init__(self, x_rel_to_module, y_rel_to_module, x_module_absolute, y_module_absolute):

        # Get absolute pos of plane
        self.x_rel_to_module = x_rel_to_module
        self.y_rel_to_module = y_rel_to_module
        self.absolute_x = self.x_rel_to_module + x_module_absolute
        self.absolute_y = self.y_rel_to_module + y_module_absolute

        # Set up two layers of straws in plane
        self.layer_1 = Layer(0, 0, self.absolute_x, self.absolute_y)
        self.layer_2 = Layer(3.03, 5.15, self.absolute_x, self.absolute_y)

    def get_x_rel_to_module(self):
        # Return x-pos relative to parent module
        return self.x_rel_to_module

    def get_y_rel_to_module(self):
        # Return y-pos relative to parent module
        return self.y_rel_to_module

    def get_wires_x(self):
        # Return x-pos of all wires in plane
        return self.layer_1.get_wires_x() + self.layer_2.get_wires_x()        

    def get_wires_y(self):
        # Return y-pos of all wires in plane
        return self.layer_1.get_wires_y() + self.layer_2.get_wires_y()        

    def get_layer(self, layer_num):
        # Return layer denoted by specified number
        if layer_num == 1:
            return self.layer_1
        elif layer_num == 2:
            return self.layer_2
        
    def set_absolute_module_x(self, x_module_absolute):
        # Sets new absolute position for planes, from specified position of module
        self.absolute_x = self.x_rel_to_module + x_module_absolute
        self.layer_1.set_absolute_plane_x(self.absolute_x)
        self.layer_2.set_absolute_plane_x(self.absolute_x)


class Module:

    # Class representing a module of two planes in the detector

    def __init__(self, x_rel_to_tracker, y_rel_to_tracker, x_tracker_absolute, y_tracker_absolute):
        
        # Get absolute position of module
        self.x_rel_to_tracker = x_rel_to_tracker
        self.y_rel_to_tracker = y_rel_to_tracker
        self.absolute_x = self.x_rel_to_tracker + x_tracker_absolute 
        self.absolute_y = self.y_rel_to_tracker + y_tracker_absolute 

        # Set up two planes in module
        self.plane_1 = Plane(0, 0, self.absolute_x, self.absolute_y)
        self.plane_2 = Plane(0, 20.20, self.absolute_x, self.absolute_y)

    def get_x_rel_to_tracker(self):
        # Returns x-pos relative to parent tracker
        return self.x_rel_to_tracker;

    def get_y_rel_to_tracker(self):
        # Returns y-pos relative to parent tracker
        return self.y_rel_to_tracker;

    def get_wires_x(self):
        # Returns x-pos of all wires in module
        return self.plane_1.get_wires_x() + self.plane_2.get_wires_x()        

    def get_wires_y(self):
        # Returns y-pos of all wires in module
        return self.plane_1.get_wires_y() + self.plane_2.get_wires_y()        

    def get_plane(self, plane_num):
        # Returns plane denoted by specified number
        if plane_num == 1:
            return self.plane_1
        elif plane_num == 2:
            return self.plane_2

    def set_x_align(self, align_dist):
        # Sets x-alignment for module - gives new position to planes
        self.absolute_x = self.x_rel_to_tracker + align_dist
        self.plane_1.set_absolute_module_x(self.absolute_x)
        self.plane_2.set_absolute_module_x(self.absolute_x)
        

class Detector:    

    # Class representing the whole traceback detector

    def __init__(self, smearing=True, verbose=False, finite_straws=True):
        # Sets up two modules in the detector
        self.module_1 = Module(0, 50, 0, 0)
        self.module_2 = Module(0, 187.35, 0, 0)

        # List containing events in detector, each representing a track and wire hits generated by track travelling through detector
        self.events = []

        # Whether to print additional info for debugging, whether to smear residuals, whether to use finite straw sizes
        self.verbose = verbose
        self.smearing = smearing
        self.finite_straws = finite_straws
        
    def is_smearing(self):
        return self.smearing

    def get_wires_x(self):
        # Returns x-pos of all wires in detector
        return self.module_1.get_wires_x() + self.module_2.get_wires_x()
    
    def get_wires_y(self):
        # Returns y-pos of all wires in detector
        return self.module_1.get_wires_y() + self.module_2.get_wires_y()
        
    def get_module(self, module_num):
        # Returns module denoted by specified number
        if module_num == 1:
            return self.module_1
        elif module_num == 2:
            return self.module_2

    def refresh_wires(self):
        # Updates wires used in list of events, as their position may have changed by a shift in alignment of some object.
        for event in self.events:
            for wire_hit in event.wire_hits:
                new_wire = self.get_module(wire_hit.get_module_num()).get_plane(wire_hit.get_plane_num()).get_layer(wire_hit.get_layer_num()).get_wires()[wire_hit.get_wire_num()]
                wire_hit.set_wire(new_wire)


    def set_module_x_align(self, module_num, align_dist):
        # Changes alignment of specified module.
        if module_num == 1:
            self.module_1.set_x_align(align_dist)
        elif module_num == 2:
            self.module_2.set_x_align(align_dist)
            
        self.refresh_wires() # Refresh wire positions in recorded wire hits


    def set_events(self, events):
        # Assigns a list of wire hits to the detector, produced by a track
        self.events = events

    def get_events(self):
        return self.events

    def get_hit_keys(self):
        # Returns a list of keys - strings representing wires hit by each track, contained in each event 
        hit_keys = []

        for event in self.events:
            for wire_hit in event.wire_hits:
                hit_keys.append(str(event.index) + "-" + str(wire_hit.get_module_num()) + "." + str(wire_hit.get_plane_num()) + "." + str(wire_hit.get_layer_num()))

        return hit_keys


    def get_hit_radius(self, wire_keys, *params):
        
        # Calculates smallest distance between position of wire in detector hit by track, and track with specified gradient and intercept
        # First argument a list of strings taking the form of a number indexing the track to be examined, followed by a number indexing the wire hit to be examined.
        # Second argument a list of parameters for all tracks being examined, with alternating gradients and intercepts.

        # Handles weirdness when using this function with the list of optimised parameters from curve_fit 
        if len(params) == 1:
            params = params[0]

        if self.verbose:
            print (params)

        self.set_module_x_align(1, params[-1]) # Set alignment of detector module

        # Returns list of x-displacements if list of layer numbers is given, or single x-displacement if not.

        hit_rads = [] # Contains all calculated hit radii

        for key in wire_keys:
            
            # Split key to get number for track secondary key for wire
            split_key = key.split("-")
            track_num = int(split_key[0])
            wire_key = split_key[1]

            # Get gradient and intercept of track from list of parameters, then create track

            track_grad = params[2 * track_num]
            track_int = params[(2 * track_num) + 1]
            track = Track(track_grad, track_int)

            # Calculate hit radius for wire and track, and append to list
            selected_event = 0
            for event in self.events:
                
                if event.index == track_num:
                    selected_event = event

            hit_rads.append(calc_approach_distance(selected_event.get_wire_by_key(wire_key), track))

        return hit_rads


class Track:

    # Class representing a track through the detector

    def __init__(self, gradient, intercept):
 
        # Takes arguments of gradient and integer for track. Note: gradient is taken as dx/dy, as direction of x is parallel to wire planes.
        # Calculates points track travels through, at upper and lower y-boundaries
        self.y_bottom = track_boundary_y_lower
        self.y_top = track_boundary_y_upper
        self.x_bottom = (gradient * track_boundary_y_lower) + intercept
        self.x_top = (gradient * track_boundary_y_upper) + intercept 

        self.gradient = gradient
        self.intercept = intercept
 
    def get_bottom_point(self):
        # Returns bottom point of track
        return [self.x_bottom, self.y_bottom]

    def get_top_point(self):
        # Returns top point of track
        return [self.x_top, self.y_top]

    def get_gradient(self):
        # Returns gradient of track
        return self.gradient 
    
    def get_intercept(self):
        # Returns x-intercept of track
        return self.intercept

    def set_intercept(self, intercept):
        # Sets x-intercept of track, changing bottom and top coordinates accordingly
        self.intercept = intercept
        self.x_bottom = (self.gradient * self.y_bottom) + self.intercept 
        self.x_top = (self.gradient * self.y_top) + self.intercept 

    def set_gradient(self, gradient):
        # Sets gradient of track, changing bottom and top coordinates accordingly   
        self.gradient = gradient
        self.x_bottom = (self.gradient * self.y_bottom) + self.intercept 
        self.x_top = (self.gradient * self.y_top) + self.intercept 

    def get_x_points(self):
        # Returns x-pos of beginning, end of track
        return [self.x_bottom, self.x_top]

    def get_y_points(self):
        # Returns y-pos of beginning, end of track
        return [self.y_bottom, self.y_top]


class WireHit:

    # Class to represent a single hit of a wire. Takes arguments of wire which was hit, x-displacement of hit from wire, y-displacement of hit from wire, and numbers indexing the module, plane, layer, and wire of hit. 

    def __init__(self, wire, hit_x_disp, hit_y_disp, module_num, plane_num, layer_num, wire_num, smearing, finite_straws):
        # Set variables for wires hit. Calculate distance of hit from wire, and displacement in x and y for hit point from wire.
        self.wire = wire
        self.hit_x_disp = hit_x_disp 
        self.hit_y_disp = hit_y_disp 
        self.hit_dist = math.sqrt(hit_x_disp**2 + hit_y_disp**2)

        # Index  position of wire in detector.
        self.module_num = module_num
        self.plane_num = plane_num
        self.layer_num = layer_num
        self.wire_num = wire_num

        # Smear hit residual, according to Gaussian distribution with standard deviation equal to hit resolution
        if (smearing):
            smear_dist = np.random.normal(scale=hit_resolution)

            # If smearing gives distance below zero, set distance to zero. Likewise if above hit radius, set distance to hit radius
            if self.hit_dist + smear_dist < 0:
                self.hit_dist = 0
            elif finite_straws & (self.hit_dist + smear_dist > straw_rad):
                self.hit_dist = straw_rad
            else:
                self.hit_dist = self.hit_dist + smear_dist

    def set_wire(self, wire):
        # Sets wire hit
        self.wire = wire

    def get_wire(self):
        # Gets wire hit
        return self.wire

    def get_module_num(self):
        # Gets number of module for hit
        return self.module_num

    def get_plane_num(self):
        # Gets number of plane for hit
        return self.plane_num

    def get_layer_num(self):
        # Gets number of layer for hit
        return self.layer_num
    
    def get_wire_num(self):
        # Gets number of wire for hit
        return self.wire_num

    def get_hit_dist(self):
        # Gets distance of hit from wire
        return self.hit_dist
    
    def get_hit_x_disp(self):
        # Gets x-displacement from wire to hit point 
        return self.hit_x_disp

    def get_hit_y_disp(self):
        # Gets y-displacement from wire to hit point 
        return self.hit_y_disp


class DetectorHitEvent:

    # Class to represent hits by a single track. Contains the track, and list of wire hits caused by the track

    def __init__(self, track, wire_hits, index):
        # Takes inputs of track, list of wire hits by track, and integer to index track
        self.track = track
        self.wire_hits = wire_hits
        self.index = index
                                
    def get_wire_by_key(self, key):
        # Splits keys to get index for selected module, plane, and layer.
        split_key = key.split(".")
        module_num = int(split_key[0])
        plane_num = int(split_key[1])
        layer_num = int(split_key[2])

        for wire_hit in self.wire_hits:
            
            # Returns wire_hit in list corresponding to supplied key.
            if (wire_hit.get_module_num() == module_num) & (wire_hit.get_plane_num() == plane_num) & (wire_hit.get_layer_num() == layer_num):
                
                return wire_hit.wire
            
                    

def calc_approach_distance(wire, track):
    
    # Function to calculate perpendicular distance from track to wire
    
    # Get pos of wire
    x_0 = wire.get_absolute_x()
    y_0 = wire.get_absolute_y()
    
    # Get pos of beginning, end of track
    x_1 = track.get_bottom_point()[0]
    y_1 = track.get_bottom_point()[1]
    x_2 = track.get_top_point()[0]
    y_2 = track.get_top_point()[1]
    
    # Return perpendicular distance
    return abs((y_2 - y_1) * x_0 - (x_2 - x_1) * y_0 + x_2 * y_1 - y_2 * x_1) / math.sqrt((y_2 - y_1)**2 + (x_2 - x_1)**2)
    

def closest_hit_wires(detector, track):
    
    # Function to find closest approached wires in each layer in detector

    wire_hits = [] # Contains closest approached wires
    smearing = detector.is_smearing()

    # Iterating across all layers
    for module_num in [1,2]:
        for plane_num in [1,2]:
            for layer_num in [1,2]:
                
                # Set up initial values for closest approach distance, wire in layer
                closest_approach = sys.float_info.max 
                closest_wire = None

                # Indexes wire position in layer
                closest_wire_num = 0
                wire_num = 0
                
                # Iterate across wires in layer
                for wire in detector.get_module(module_num).get_plane(plane_num).get_layer(layer_num).get_wires():
                    
                    # Calculate approach distance
                    approach = calc_approach_distance(wire, track)
                    
                    # Check if wire closer to track than previously checked ones
                    if approach < closest_approach:
                        closest_approach = approach
                        closest_wire = wire
                        closest_wire_num = wire_num

                    wire_num = wire_num + 1


                # Calculate positions of hits
                track_grad = track.get_gradient()
                track_int = track.get_intercept()

                wire_y = closest_wire.get_absolute_y()
                wire_x = closest_wire.get_absolute_x()

                delta_x = track.get_top_point()[0] - track.get_bottom_point()[0]
                delta_y = track.get_top_point()[1] - track.get_bottom_point()[1]

                y_hit_pos = ((wire_x * delta_x) - (track_int * delta_x) + (wire_y * delta_y)) / (delta_y + (track_grad * delta_x))
                x_hit_pos = (track_grad * y_hit_pos) + track_int 

                # Add wire hit to list of wire hits
                wire_hit = WireHit(closest_wire, x_hit_pos - wire_x, y_hit_pos - wire_y, module_num, plane_num, layer_num, closest_wire_num, smearing, detector.finite_straws)

                # If detector is using finite straw sizes, only appends wire_hit to list if hit distance is less than straw radius.
                if (detector.finite_straws):
                    if (math.sqrt((x_hit_pos - wire_x)**2 + (y_hit_pos - wire_y)**2) < straw_rad):
                        wire_hits.append(wire_hit)
                elif (not detector.finite_straws):
                    wire_hits.append(wire_hit)

    # Return list of wire hits in each layer
    return wire_hits


def calc_x_approach_dist(wire, track):
    
    # Calculates x-displacement between wire position closest approach position

    # Get gradient, intercept of track, and position of wire
    track_grad = track.get_gradient()
    track_int = track.get_intercept()
    wire_y = wire.get_absolute_y()
    wire_x = wire.get_absolute_x()
    
    # Changes in x and y across track length
    delta_x = track.get_top_point()[0] - track.get_bottom_point()[0]
    delta_y = track.get_top_point()[1] - track.get_bottom_point()[1]

    # Calculates position of closest approach by track
    y_hit_pos = ((wire_x * delta_x) - (track_int * delta_x) + (wire_y * delta_y)) / (delta_y + (track_grad * delta_x))
    x_hit_pos = (track_grad * y_hit_pos) + track_int 
    
    # Return x-displacement
    return x_hit_pos - wire_x
    
