import genome
from xml.dom.minidom import getDOMImplementation
from enum import Enum
import numpy as np

class Creature():
    def __init__(self,gene_count):
        self.spec = genome.Genome.get_gene_spec()
        self.dna = genome.Genome.get_random_genome(len(self.spec), gene_count)
        self.flat_links = None
        self.motors = None
        self.get_flat_links()
        self.get_expanded_links()
        self.start_position = None
        self.last_position = None
        self.dist = 0


    def get_flat_links(self):
        if self.flat_links != None:
            return self.flat_links
        else:
            gdicts = genome.Genome.get_genome_dict(self.dna,self.spec)
            links = genome.Genome.genome_to_links(gdicts)
            self.flat_links = links
            return self.flat_links    
        
    def get_expanded_links(self):
        if self.flat_links == None:
            print("hello there is no flat links")
            self.get_flat_links()
        exp_links = [self.flat_links[0]]
        expanded_links = genome.Genome.expandLinks(self.flat_links[0],
                                  self.flat_links[0].name,
                                  self.flat_links,
                                  exp_links)
        if expanded_links is None:
            pass
        elif isinstance(expanded_links, list):

            exp_links.extend(expanded_links)
        else:
            raise TypeError("expandlinks returned unexpected type")
        self.exp_links = exp_links
        return self.exp_links
    
    def to_xml(self):
        self.get_flat_links()
        self.get_expanded_links()
        
        domimpl = getDOMImplementation()
        adom = domimpl.createDocument(None,"start",None)
        robot_tag = adom.createElement("robot")
        for link in self.exp_links:
            robot_tag.appendChild(link.to_link_element(adom))
        first = True
        for link in self.exp_links:
            if first: #skip root node
                first = False
                continue
            robot_tag.appendChild(link.to_joint_element(adom))
        robot_tag.setAttribute("name", "woohoo")
        return robot_tag.toprettyxml()
    
    def get_motors(self):
        assert(self.exp_links != None),"creature: call get_exp_links before get_motors "
        if self.motors == None:
            motors = []
            for i in range (1, len(self.exp_links)):
                l = self.exp_links[i]
                m = Motor(l.control_waveform, l.control_amp, l.control_freq)
                motors.append(m)
            self.motors = motors
        return self.motors
    
    def update_position(self,pos):
        if self.last_position != None:
            p1 = np.array(self.last_position)
            p2 = np.array(pos)
            dist = np.linalg.norm(p1-p2)
            self.dist = self.dist + dist

        if self.start_position == None:
            self.start_position = pos
        else: 
            self.last_position = pos

    #fitness function, calculating how far the creature moved
    def get_distance_travelled(self):
        return self.dist       
    
    def update_dna(self,dna):
        self.dna = dna
        self.flat_links = None
        self.exp_links = None
        self.motors = None
        self.start_position = None
        self.last_position = None
        self.dist = 0
    
class MotorType(Enum):
    PULSE = 1
    SINE = 2

class Motor:
    def __init__(self,control_waveform,control_amp,control_freq):
        if control_waveform <=0.5:
            self.motor_type = MotorType.PULSE
        else:
            self.motor_type = MotorType.SINE
        self.amp = control_amp
        self.freq = control_freq
        self.phase = 0

    def get_output(self):
        self.phase = (self.phase + self.freq) % (np.pi * 2)
        if self.motor_type == MotorType.PULSE:
            if self.phase < np.pi:
                output = 1
            else:
                output = -1
            
        if self.motor_type == MotorType.SINE:
            output = np.sin(self.phase)

        return output