import random
import re
import jsonpickle
import sys
import numpy as np


class NetworkSampler(object):
    def __init__(self,peakset):
        self.peakset = peakset
        self.transformations = []
        self.delta = 1.00
        self.transformation_file = 'all_transformations_masses.txt'
        self.n_samples = 1000
        self.n_burn = 100

    def set_parameters(self,params):
        if 'n_samples' in params:
            self.n_samples = params['n_samples']
        if 'n_burn' in params:
            self.n_burn = params['n_burn']
        if 'delta' in params:
            self.delta = params['delta']
        if 'transformation_file' in params:
            self.transformation_file = params['transformation_file']

    def sample(self):
        self.initialise_sampler()
        self.multiple_network_sample(self.n_burn,record=False)
        self.multiple_network_sample(self.n_samples,record=True)
        self.compute_posteriors()


    def load_transformations(self):
        self.transformations = []
        with open(self.transformation_file) as infile:
            for line in infile:
                line = line.rstrip('\r\n')
                splitline = line.split('\t')
                name = splitline[0]
                formula = splitline[1]
                self.transformations.append(Transformation(formula,name))


    def summarise_posterior(self):
        print
        print "POSTERIOR"
        print
        for m in self.peakset.measurements:
            print "Measurement: " + str(m.id)
            for k in m.annotations:
                print "  " + str(k.formula) + "(" + str(m.annotations[k]) + "): " + str(1.0*self.peakset.posterior_probability[m][k])


    def prob_only_sample(self,record = True,verbose = False):
        self.n_samples += 1
        for m in self.peakset.measurements:
            if m.annotations != {}:
                tempprobs = {}
                totalprob = 0.0

                for a in self.adjacency[self.assignment[m].compound]:
                    self.in_degree[a] -= 1

                for k in m.annotations:
                    tempprobs[k] = m.annotations[k]
                    totalprob+=tempprobs[k]
                u = random.random()*totalprob
                cumprob = 0
                choosepos = -1
                for k in m.annotations:
                    cumprob += m.annotations[k]
                    choose = k
                    if u <= cumprob:
                        break

                self.assignment[m] = choose
                for a in self.adjacency[choose.compound]:
                    self.in_degree[a] += 1

                if record:
                    self.peakset.posterior_counts[m][choose] += 1
                    self.peakset.edge_counts[m][choose] += self.in_degree[choose]

                if verbose:
                    print "Measurement: " + str(m.id) + " assigned to " + str(choose.formula) + "(" + str(self.peakset.posterior_counts[m][choose]) + ")"

    def multiple_network_sample(self,n_its,record=True,verbose=False):
        for i in range(n_its):
            self.network_sample(record,verbose)

    def network_sample(self,record = True,verbose = False):
        self.n_samples += 1
        for m in self.peakset.measurements:
            if m.annotations != {}:
                tempprobs = {}
                totalprob = 0.0

                for a in self.adjacency[self.assignment[m].compound]:
                    self.in_degree[a] -= 1


                for k in m.annotations:
                    tempprobs[k] = m.annotations[k] * (self.delta + self.in_degree[k.compound])
                    totalprob+=tempprobs[k]

                u = random.random()*totalprob
                cumprob = 0.0
                for k in m.annotations:
                    cumprob += tempprobs[k]
                    choose = k
                    if u <= cumprob:
                        break

                self.assignment[m] = choose

                for a in self.adjacency[choose.compound]:
                    self.in_degree[a] += 1

                if record:
                    self.peakset.posterior_counts[m][choose] += 1
                    self.peakset.edge_counts[m][choose] += self.in_degree[choose.compound]

                if verbose:
                    print "Measurement: " + str(m.id) + " assigned to " + str(choose.compound.formula) + "(" + str(self.peakset.posterior_counts[m][choose]) + ")"


    def initialise_sampler(self,verbose = False):
        self.create_adjacency()
        self.n_samples = 0
        self.assignment = {}
        self.peakset.posterior_counts = {}
        self.peakset.edge_counts = {}
        self.in_degree = {}
        for a in self.peakset.compounds:
            self.in_degree[a] = 0
        for m in self.peakset.measurements:
            if m.annotations != {}:
                self.peakset.posterior_counts[m] = {}
                self.peakset.edge_counts[m] = {}
                tempprobs = {}
                totalprob = 0.0
                for k in m.annotations:
                    self.peakset.posterior_counts[m][k] = 0
                    self.peakset.edge_counts[m][k] = 0
                    tempprobs[k] = m.annotations[k]
                    totalprob+=tempprobs[k]
                u = random.random()*totalprob
                cumprob = 0.0
                for k in m.annotations:
                    cumprob += m.annotations[k]
                    choose = k
                    if u <= cumprob:
                        break

                self.assignment[m] = choose

                for a in self.adjacency[choose.compound]:
                    self.in_degree[a] += 1

                if verbose:
                    print "Measurement: " + str(m.id) + " assigned to " + str(choose.formula)

    def global_edge_count(self):
        import itertools
        edge_dict = {}
        for t in self.transformations:
            edge_dict[t] = 0
        for m1,m2 in itertools.combinations(self.peakset.measurements,2):
            if m1.annotations != {} and m2.annotations!= {}:
                if self.assignment[m2] in self.adjacency[self.assignment[m1].compound]:
                    this_edge = self.adjacency[self.assignment[m1].compound][self.assignment[m2].compound]
                    edge_dict[this_edge] += 1
        return edge_dict


    def compute_posteriors(self):
        self.peakset.posterior_probability = {}
        self.peakset.prior_probability = {}
        self.peakset.posterior_edges = {}
        for m in self.peakset.measurements:
            total_count = 0
            total_prob = 0.0
            self.peakset.posterior_probability[m] = {}
            self.peakset.prior_probability[m] = {}
            self.peakset.posterior_edges[m] = {}
            for a in m.annotations:
                total_count += self.peakset.posterior_counts[m][a]
                total_prob += m.annotations[a]
            for a in m.annotations:
                self.peakset.posterior_probability[m][a] = 1.0*self.peakset.posterior_counts[m][a]/(1.0*total_count)
                self.peakset.prior_probability[m][a] = m.annotations[a]/(total_prob)
                if self.peakset.posterior_counts[m][a] > 0:
                    self.peakset.posterior_edges[m][a] = 1.0*self.peakset.edge_counts[m][a]/(1.0*self.peakset.posterior_counts[m][a])
                else:
                    self.peakset.posterior_edges[m][a] = 0.0


    def create_adjacency(self,verbose=False):
        print "Loading transformations"
        self.load_transformations()
        print "Creating adjacency structure. This might take some time..."
        self.adjacency = {}
        import itertools
        total_found = 0
        for a in self.peakset.compounds:
            self.adjacency[a] = {}
        # Loop over annotations
        for a1,a2 in itertools.combinations(self.peakset.compounds,2):
            match_t = self.can_transform(a1,a2)
            if match_t!=None:
                if verbose:
                    print "Found match: " + str(a1.compound.formula) + " -> " + str(match_t.formula) + " -> " + str(a2.compound.formula)
                self.adjacency[a1][a2] = match_t
                self.adjacency[a2][a1] = match_t
                # self.adjacency[a1].append(a2)
                # self.adjacency[a2].append(a1)
                total_found += 2

        print "Found " + str(total_found) + " (sparsity ratio = " + str(1.0*total_found/(1.0*len(self.peakset.compounds)**2)) + ")"

    def get_all_transforms(self,a1,a2):
        tlist = []
        for t in self.transformations:
            tf = t.formula
            poshit = 1
            neghit = 1
            for a in tf.atoms:
                if a1.formula.atoms[a] - a2.formula.atoms[a] != tf.atoms[a]:
                    poshit = 0
                if a2.formula.atoms[a] - a1.formula.atoms[a] != tf.atoms[a]:
                    neghit = 0
                if poshit == 0 and neghit == 0:
                    break
            if poshit == 1 or neghit == 1:
                tlist.append(t)
        return tlist


    def can_transform(self,a1,a2):
        for t in self.transformations:
            tf = t.formula
            poshit = 1
            neghit = 1
            for a in tf.atoms:
                if a1.formula.atoms[a] - a2.formula.atoms[a] != tf.atoms[a]:
                    poshit = 0
                if a2.formula.atoms[a] - a1.formula.atoms[a] != tf.atoms[a]:
                    neghit = 0
                if poshit == 0 and neghit == 0:
                    break
            if poshit == 1 or neghit == 1:
                return t

        if poshit == 0 and neghit == 0:
            return None

    def dump_output(self,outstream = sys.stdout):
        for m in self.peakset.measurements:
            total_prob = 0.0
            total_count = 0
            if m.annotations == {}:
                continue
            for an in m.annotations:
                total_prob += m.annotations[an]
                total_count += self.peakset.posterior_counts[m][an]
            print >> outstream, "Measurement: {}".format(m.id)
            for an in m.annotations:
                print >> outstream, "\t<<{}>>,<<{}>>,Prior: {:.4f}, Posterior {:.4f}, Degree {}".format(
                                    an.formula,an.name,m.annotations[an]/total_prob,
                                    1.0*self.peakset.posterior_counts[m][an]/total_count,self.in_degree[an])

class Transformation(object):
    def __init__(self,formula,name):
        self.formula = Formula(formula)
        self.name = name


class FragSet(object):
    def __init__(self):
        self.measurements = []

class Peak(object):
    def __init__(self,mass,rt,intensity):
        self.mass = mass
        self.rt = rt
        self.intensity = intensity
        self.norm_intensity = intensity

    def __repr__(self):
        return "Mass: {}, RT: {}, Intensity: {}".format(self.mass,self.rt,self.intensity)

class PeakSet(object):
    def __init__(self,peaks):
        self.peaks = peaks
        masses = [p.mass for p in peaks]
        rts = [p.rt for p in peaks]
        intensities = [p.intensity for p in peaks]
        basepos = np.argmax(np.array(intensities))
        self.basepeak = peaks[basepos]

        self.normalise_intensities()
        self.n_peaks = len(peaks)


    def normalise_intensities(self):
        for p in self.peaks:
            p.norm_intensity = 100.0*p.intensity/self.basepeak.intensity


class Measurement(object):
    def __init__(self,thisid):
        self.id = thisid
        self.annotations = {}

    def add_peak_set(self,peakset):
        self.peakset = peakset

class Compound(object):
    def __init__(self,cid,formula,name):
        self.formula = Formula(formula)
        self.name = name
        self.id = cid


# class Annotation(object):
# 	def __init__(self,formula,name,cid,parentid):
# 		self.formula = Formula(formula)
# 		self.name = name
# 		self.id = cid
# 		self.parentid = parentid

class Annotation(object):
    def __init__(self,compound,parentid):
        self.compound = compound
        self.parentid = parentid


class Formula(object):
    def __init__(self,formula):
        self.atom_names = ['C','H','N','O','P','S','Cl','I','Br','Si','F','D']
        self.formula = formula
        self.atoms = {}
        for atom in self.atom_names:
            self.atoms[atom] = self.get_atoms(atom)


    def correct_gcms_derivatives(self):
        n_silicons = self.atoms['Si']
        self.atoms['Si'] = 0
        self.atoms['C'] -= n_silicons
        self.atoms['H'] -= 3*n_silicons
        self.atoms['H'] += n_silicons
        self.make_string()

    def make_string(self):
        self.formula = ""
        for atom in self.atom_names:
            atom_no = self.atoms[atom]
            if atom_no == 1:
                self.formula += atom
            elif atom_no > 1:
                self.formula += atom + str(atom_no)


    def get_atoms(self,atom_name):
        # Do some regex matching to find the numbers of the important atoms
        ex = atom_name + '(?![a-z])' + '\d*'
        m = re.search(ex,self.formula)
        if m == None:
            return 0
        else:
            ex = atom_name + '(?![a-z])' + '(\d*)'
            m2 = re.findall(ex,self.formula)
            total = 0
            for a in m2:
                if len(a) == 0:
                    total += 1
                else:
                    total += int(a)
            return total

    def compute_exact_mass(self):
        masses = {'C':12.00000000000,'H':1.00782503214,'O':15.99491462210,'N':14.00307400524,'P':30.97376151200,'S':31.97207069000,'Cl':34.96885271000,'I':126.904468,'Br':78.9183376,'Si':27.9769265327,'F':18.99840320500,'D':2.01410177800}
        exact_mass = 0.0
        for a in self.atoms:
            exact_mass += masses[a]*self.atoms[a]
        return exact_mass

    def __repr__(self):
        return self.formula

    def __str__(self):
        return self.formula


if __name__ == '__main__':
    a = NistOutput('nist_out.txt')
    a.initialise_sampler()
    a.network_sample(100)
    test = jsonpickle.encode(a)
    f = open('picklemodel.txt','w')
    f.write(test)
    # f = open('picklemodel.txt','r')
    # a = jsonpickle.decode(f.read())
