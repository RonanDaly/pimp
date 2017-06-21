#!/usr/bin/python2.7
# -*-coding:Utf-8 -*

class PeriodicTable:

    def __init__(self):
        self.elements = {}
        self.elements["C"] = Element("carbon","C",4,12.01070000000,[[12,12.00000000000],[13,13.00335483780],[14,14.00324198800]])
        self.elements["H"] = Element("hydrogen", "H",1,1.00794000000,[[1,1.00782503214],[2,  2.01410177800],[3,  3.0160492675]])
        self.elements["F"] = Element("fluorine", "F",1,18.99840325000,[[19, 18.99840320500]])
        self.elements["N"] = Element("nitrogen", "N",3,14.00670000000,[[14, 14.00307400524],[15, 15.00010889840]])
        self.elements["O"] = Element("oxygen", "O",2,15.99940000000,[[16, 15.99491462210],[18, 17.99916040000],[17, 16.99913150000]])
        self.elements["P"] = Element("phosphor", "P",3,30.97376149000,[[31, 30.97376151200]])
        self.elements["Cl"] = Element("chlorine", "Cl",1,35.45273000000,[[35, 34.96885271000],[37, 36.96590260000],[36, 35.96830695000]])
        self.elements["S"] = Element("sulfur", "S",2,32.06533000000,[[32, 31.97207069000],[33, 32.97145850000],[34, 33.96786683000],[35, 34.96903214000],[36, 35.96708088000]])
        self.elements["Na"] = Element("natrium", "Na",1,22.989770,[[23, 22.98976967]])
        self.elements["K"] = Element("potassium", "K",1,39.0983,[[39, 38.96370668000],[40, 39.96399848000],[41, 40.96182576000]])
        self.elements["Cu"] = Element("copper", "Cu",0,63.5463,[[63, 62.929601115],[65, 64.927793719]])

    def getElementMass(self,symbol):
        try:
            response = self.elements[symbol].mass
        except KeyError, e:
            response = None
        return response

    def getIsotopeMass(self, symbol, id):
        response = None
        try:
            element = self.elements[symbol]
            if element.standard_form.id == id:
                response = element.standard_form.mass
            else:
                for isotope in element.isotopes:
                    if isotope.id == id:
                        response = isotope.mass
                        break
        except KeyError, e:
            return response
        return response

    def getElementName(self, symbol):
        try:
            response = self.elements[symbol].name
        except KeyError, e:
            response = None
        return response

class Element:

    def __init__(self,name,symbol,valence,mass,data):
        self.name = name
        self.symbol = symbol
        self.valence = valence
        self.mass = mass
        self.standard_form = None
        self.isotopes = []

        for ele in data:
            form = Form(ele)
            if ele == data[0]:
                self.standard_form = form
            else:
                self.isotopes.append(form)


class Form:

    def __init__(self,info):
        self.id = info[0]
        self.mass = info[1]


