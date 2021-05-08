# see surf_foil.py for an improved version of this

#from __future__ import unicode_literals
from FreeCAD import Base
#import Draft, Part
import Part, math

class foil():
    
    class profile():
       def __init__(self, profileDAT, doc = None, source = None):
          self.profileDAT = profileDAT 
          self.doc        = doc
          self.source     = source
    
    class LeadTrail():
       def __init__(self, leadingEdge, trailingEdge, doc = None, source = None):
          self.leadingEdge  = leadingEdge
          self.trailingEdge = trailingEdge
          self.doc          = doc
          self.source       = source
    
    class construction():
       def __init__(self, leadingEdgeBspline, profileList, rotation):
          self.leadingEdgeBspline = leadingEdgeBspline 
          self.profileList        = profileList
          self.rotation           = rotation
    
    def __init__(self, file_profile = None, file_LeadTrail = None,
                  profile = None, LeadTrail = None, foil = None):
        """
        Define a foil object with source file and construction information.
        The init method can specify source files file_profile, file_LeadTrail
        in which case they are loaded then constuction and foil are calculated.
        Otherwise ...
        """
        #   if not (-90 <= lat <= 90):
        #      raise ValueError("must have  -90 <=  latitude <= 90")
        
        if file_profile is not None:
            self.loadProfileDAT(file_profile)
        else:
            self.profile  =  profile #CLASS IS NOT EXTERNAL
            #self.profile(profileDAT, doc = profile_doc, source = file_profile)
        
        if file_LeadTrail is not None:
            self.loadLeadTrail(file_LeadTrail)
        else:
            self.profile  =  profile #CLASS IS NOT EXTERNAL
            #self.LeadTrail= self.LeadTrail(leadingEdge, trailingEdge,
            #                doc = LeadTrail_doc, source = file_LeadTrail)
        
        # Draft.makeBSpline works here, but using Part.BSplineCurve to be consistent profiles
        # traj=Part.Wire([Draft.makeBSpline(leadingEdge).Shape])
        # however, I as getting a hollow pipe using Draft.makeBSpline
        
        print("making traj wire.")
        traj = Part.BSplineCurve()
        traj.interpolate(self.LeadTrail.leadingEdge)       
        leadingEdgeBspline = Part.Wire(traj.toShape())
        
        def scaledBspline(dat, sc):
           z = [FreeCAD.Vector(v[0]*sc, v[1]*sc, v[2]*sc) for v in dat]
           prof=Part.BSplineCurve()
           prof.interpolate(z)       
           prof=Part.Wire(prof.toShape())
           return prof
        
        print("calculating aprox. tangent to Bspline.")
        #angle adjustmentPosition is at leadingEndge, 
        #rotate around cord. The
        #angle from X-Y plane determined by angle between tangent to 
        # leadingEdgeBspline and Z axis
        # this should really be the projection of the tangent onto the
        # plane defined by the cord being its normal. but for foils with the
        # cord aproximately in the direction of the X axis this will be aprox Dy/Dz.
        # Ends are one-sided tangent aprox, interior points use two adjacent
        Z = FreeCAD.Vector(0, 0, 1)
        e = self.LeadTrail.leadingEdge
        ln = len(e)
        rotation = [ Z.getAngle(e[1] - e[0])*180/math.pi ]
        for i  in range(ln - 2):
           rotation.append(Z.getAngle(e[i+2] - e[i])*180/math.pi)
        rotation.append(Z.getAngle(e[ln-1] - e[ln-2])*180/math.pi)
        
        print("building profileList.")
        profileList = []
        for ld, tr, r  in zip(self.LeadTrail.leadingEdge, 
                   self.LeadTrail.trailingEdge, rotation):
           # max here is just for zero case at tip
           sc = max (1e-2, ld.distanceToPoint(tr))
           print("scaling profile " + str(sc))
           p  = scaledBspline(self.profile.profileDAT, sc)
           p.translate(FreeCAD.Vector(ld))
           #angle adjustment
           # ld - tr or tr - ld reverse rotationBase.
           #FreeCADError: Unknown C++ exception
           p.rotate(ld, tr - ld, -r)
           profileList.append(p)
                
        self.construction = self.construction(leadingEdgeBspline, profileList, rotation)
       
        print("making pipe.")
        #need isFrenet=False or there can be very strange twisting?
        self.foil = Part.Wire(
            self.construction.leadingEdgeBspline).makePipeShell(
               self.construction.profileList, True, False) #makeSolid, isFrenet)
    
    def foil(self) :
       """Extract the foil FreeCAD object."""
       return(self.foil)

    def profileDAT(self) :
       """Extract profileDAT."""
       return(self.profile.profileDAT)
    
    def profileList(self) :
       """Extract profileList."""
       return(self.construction.profileList)
    
    def rotation(self) :
       """Extract rotation."""
       return(self.construction.rotation)
    
    def leadingEdgeBspline(self) :
       """Extract leadingEdgeBspline."""
       return(self.construction.leadingEdgeBspline)
    
    def showProfiles(self) :
       """FreeCAD plot of profileList."""
       for p in self.construction.profileList: Part.show(p)
       return None
    
    def showBspline(self) :
       """FreeCAD plot of leadingEdgeBspline."""
       Part.show(self.construction.leadingEdgeBspline)
       return None
    
    def showfoil(self) :
       """FreeCAD plot of foil."""
       Part.show(self.foil)
       return None
    
    def showfoil2(self) :
       """FreeCAD plot of foil."""
       Part.show(self.foil2)
       return None
         
    def show(self) :
       """FreeCAD plot of foil, spline, and profiles."""
       self.showBspline()
       self.showProfiles()
       self.showfoil()
       return None
        
    def loadProfileDAT(self, source):
        """read profile from a dat file and return it."""
        doc = []
        profileDAT =  []
        Z = 0.0
        print("loading profile.")
        with open(source) as f:  
           for i in f.readlines():
              ln =  i.split()
              ln = [b.strip()  for b in  ln]
              #print(ln)
              try : 
                 X = float(ln[0])
                 Y = float(ln[1])
                 #print(X, Y)
                 profileDAT.append(FreeCAD.Vector(X, Y, Z))
              except :
                 doc.append(ln)
        
        self.profile = self.profile(profileDAT, doc=doc, source=source)

    def loadLeadTrail(self, source="/home/paul/CAD/foil/test.sweepPath"):
        """read Lead and Trailing edge data from file and return it."""
        doc =  []
        leadingEdge =  []
        trailingEdge = []
        print("loading leading and trailing edges.")
        with open(source) as f:  
           for i in f.readlines():
              ln =  i.split()
              ln = [b.strip()  for b in  ln]
              #print(ln)
              try : 
                 X = float(ln[0])
                 Y = float(ln[1])
                 Z = float(ln[2])
                 leadingEdge.append(FreeCAD.Vector(X, Y, Z))
                 X = float(ln[3])
                 Y = float(ln[4])
                 Z = float(ln[5])
                 trailingEdge.append(FreeCAD.Vector(X, Y, Z))
              except :
                 doc.append(ln)
             
        self.LeadTrail = self.LeadTrail(leadingEdge,trailingEdge, doc=doc, source=source)


z = foil(file_profile="/home/paul/CAD/foil/H105Coord.dat",
          file_LeadTrail="/home/paul/CAD/foil/test.sweepPath")
z.show()

#z.showfoil()  
#z.showProfiles()
#z.showBspline()

z2 = foil(file_profile="/home/paul/CAD/foil/H105Coord.dat",
          file_LeadTrail="/home/paul/CAD/foil/test2.sweepPath")
z2.show()

z3 = foil(file_profile="/home/paul/CAD/foil/H105Coord.dat",
          file_LeadTrail="/home/paul/CAD/foil/test3.sweepPath")
z3.show()

zzz = z3.leadingEdgeBspline()
zz  = z3.profileList()[2]
zx = Part.wire(zz)


zzz = z3.profileList()
zz = zzz.pop(0)
z = zz.makePipeShell([zzz[2]]) # this is screwy

zzz = z3.profileList()
#   Part.makeLoft(zzz, solid=True, ruled=False, closed=False, maxDegree=5) 
z = Part.makeLoft(zzz, True, False, False, 5) 

Part.show(z)


BELOW IS OLD

def loadFoil(file_profile="/home/paul/CAD/foil/H105Coord.dat",
             file_LeadTrail="/home/paul/CAD/foil/test.sweepPath"):
   """
   Load a foil profile (section) from file_profile and leading and trailing edges
   from file_LeadTrail. The leading edge defines the sweep path (trajectory).
   The leading and traing edges define the direction of ech section, and the cord
   length from the leading to trailing edge defines the scale applied to each 
   section.
   The path is a sequence of pairs of 
   vectors defining the leading and training edges, each pair defining a cord.
   The profile is scaled to the length of each cord.
   
   The profile is defined in the XxY plane, so Z=0, but position of the
   result is determined by the sweep path.
   """
   nmp = []
   profileDAT =  []
   Z = 0.0
   print("loading profile.")
   with open(file_profile) as f:  
      for i in f.readlines():
         ln =  i.split()
         ln = [b.strip()  for b in  ln]
         #print(ln)
         try : 
            X = float(ln[0])
            Y = float(ln[1])
            #print(X, Y)
            profileDAT.append(FreeCAD.Vector(X, Y, Z))
         except :
            nmp.append(ln)
   
   nms =  []
   leadingEdge =  []
   trailingEdge = []
   print("loading leading and trailing edges.")
   with open(file_LeadTrail) as f:  
      for i in f.readlines():
         ln =  i.split()
         ln = [b.strip()  for b in  ln]
         #print(ln)
         try : 
            X = float(ln[0])
            Y = float(ln[1])
            Z = float(ln[2])
            leadingEdge.append(FreeCAD.Vector(X, Y, Z))
            X = float(ln[3])
            Y = float(ln[4])
            Z = float(ln[5])
            trailingEdge.append(FreeCAD.Vector(X, Y, Z))
         except :
            nms.append(ln)
   
   
   # Draft.makeBSpline works here, but using Part.BSplineCurve to be consistent profiles
   # traj=Part.Wire([Draft.makeBSpline(leadingEdge).Shape])
   # however, I as getting a hollow pipe using Draft.makeBSpline

   print("making traj wire.")
   traj = Part.BSplineCurve()
   traj.interpolate(leadingEdge)       
   traj = Part.Wire(traj.toShape())

   #  this does not seem to make a wire?
   #prof = Draft.makeWire(profileDAT, closed=True, face=False, support=None) 
   # or Bspline
   # there seems to be a bug in Draft.makeBSpline, see notes below

   def scaledBspline(dat, sc):
      z = [FreeCAD.Vector(v[0]*sc, v[1]*sc, v[2]*sc) for v in dat]
      prof=Part.BSplineCurve()
      prof.interpolate(z)       
      prof=Part.Wire(prof.toShape())
      return prof
   
   #p1 = scaledBspline(profileDAT, 1.0)
   #p2 = scaledBspline(profileDAT, 2.0)
   #p2.translate(FreeCAD.Vector(0, 0, 2))
   #profileList = [p1, p2]

   print("building profileList.")
   profileList = []
   for l, t  in zip(leadingEdge, trailingEdge):
     # max here is just for zero case at tip
     sc = max (1e-2, l.distanceToPoint(t))
     print("scaling profile " + str(sc))
     p  = scaledBspline(profileDAT, sc)
     p.translate(FreeCAD.Vector(l))
     #needs angle adjustment too
     profileList.append(p)
   
   print("making pipe.")
   #THIS WORKS WITH profileList as [p1,p1] BUT NOT WITH [p1,p2] even when p1 and p2 are made the same
   pipe = Part.Wire(traj).makePipeShell(profileList, True, True) #makeSolid, isFrenet)
  
   #return([nmp, profileDAT, profileList, nms, leadingEdge, trailingEdge, traj, pipe])
ORDER OF THESE IS REARRANGED
   r = foil(pipe, profileDAT, profileList, leadingEdge, trailingEdge,
            traj,  nmp, nms, file_profile = file_profile, 
            file_LeadTrail = file_LeadTrail)
   
   return(r)

z = loadFoil()

z.show()

#z.showfoil()       #Part.show(z.foil)
#z.showBspline()    #Part.show(z.leadingEdgeBspline)
#z.showProfiles()   #Part.show(z.profileList[3])


zz = loadFoil(file_LeadTrail="/home/paul/CAD/foil/test2.sweepPath")
zz.show()
zz.showProfiles() 
zz.showBspline() 


# bug in Draft.makeBSpline so this fails first time but not second.
# first also was warning message (temporarilly in boarder below command window)
# that equal end points forces closed.
prof = Part.Wire([Draft.makeBSpline(z[1]).Shape])
prof = Part.Wire([Draft.makeBSpline(z[1]).Shape])
#         closed=True causes  TypeError: shape is neither edge nor wire
# The problem seems to be that the Shape from first call to Draft.makeBSpline
# is a Face, whereas an Edge is returned the second and further times.
Note loadFoil() has to be called as it is only the first call after z is created.
# z = loadFoil()
# >>> zzz = Draft.makeBSpline(z[1])
# >>> zzz.Shape
# <Face object at 0x5abebd0>
# >>> zzz = Draft.makeBSpline(z[1])
# >>> zzz.Shape
# <Edge object at 0x59aa8e0>
# >>> 

###### when all is working, clean out below
#https://forum.freecadweb.org/viewtopic.php?t=11966
from FreeCAD import Vector
Arc=Part.Arc(Vector(0, 0, 0.0), Vector(2, 2, 1.0), Vector(3, 3, 3.0))
traj=Part.Wire([Arc.toShape()])    # trajectory Wire must be made from object type shape 
makeSolid= True  
isFrenet= True
#  important to locate profile correctly on the trajectory
prof1=Part.Wire([Part.makeCircle(1.5, Vector(1, 1, 1), Vector(1, 0, 0))])  # radius, point, direction
prof2=Part.Wire([Part.makeCircle(2.5, Vector(5, 5, 5), Vector(1, 0, 0))]) 

# here traj, prof1 are  <type 'Part.Wire'> and pipe.ShapeType is solid
pipe = Part.Wire(traj).makePipeShell([prof1], makeSolid, isFrenet)

# here traj, prof1, prof2are  <type 'Part.Wire'> and pipe.ShapeType is shell
pipe = Part.Wire(traj).makePipeShell([prof1, prof2], makeSolid, isFrenet)
Part.show (pipe)  


import importAirfoilDAT
importAirfoilDAT.insert("/home/paul/CAD/foil/H105Coord.dat","H105")
w = FreeCAD.getDocument("H105").getObject("DWire")
Part.show(w.Shape)

App.getDocument('Unnamed1').addObject('Part::Loft','Loft')
>>> App.getDocument('Unnamed1').ActiveObject.Sections=[App.getDocument('Unnamed1').DWire, App.getDocument('Unnamed1').DWire001, ]
>>> App.getDocument('Unnamed1').ActiveObject.Solid=True
>>> App.getDocument('Unnamed1').ActiveObject.Ruled=False
>>> App.getDocument('Unnamed1').ActiveObject.Closed=False
>>> 

import Part, FreeCAD, math, PartGui, FreeCADGui
from FreeCAD import Base

# pick selected objects, where 1st selection is the trajectory and the 2nd and next are the sections to sweep
s = FreeCADGui.Selection.getSelection()
try:
    num=len(FreeCADGui.Selection.getSelection())#number of selected objects
    traj = Part.Wire([s[0].Shape])#first wire is a trajectory
    for i in range(1, num):
        if i == 1:
            sectionlist = [Part.Wire([s[1].Shape])]#at least one section is necessary
        elif i > 1:
            sectionlist = sectionlist + [Part.Wire([s[i].Shape])]
            #print i

except:
    print "Wrong selection"

# create a Part object into the active document
myObject=App.ActiveDocument.addObject("Part::Feature","VariableSectionSweep")

makeSolid = 1
isFrenet = 1

# Create the 3D shape and set it to the Part object
VariableSectionSweep = Part.Wire(traj).makePipeShell(sectionlist,makeSolid,isFrenet)
myObject.Shape = VariableSectionSweep
