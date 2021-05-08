# Plug for mold to make (flexible) box which goes under solar panel.
#  (solar_lid fits on top to hold panel- compare Length and Width parameters!! )
# This is superceded by solar_epoxy_box on which solar panel fits directly (no lid).

import Part, PartDesignGui
import Mesh, MeshPart, MeshPartGui
import math


########################################################
############### construction parameters ################
########################################################

ORIGIN   = FreeCAD.Vector(0.0,   0.0, 0.0)    

DR = FreeCAD.Vector(0,0,1)  # default direction specifying parts


#####  parameters

solarPocketLength     = 111.5  # 110.0 + 1.5mm tolerance gap
solarPocketWidth      =  70.5  #  69.0 + 1.5mm
solarPerimeterWrap    =   2.0  # extension of silicon beyond solar panel edge

batteryDia    = 14.0 

boxLength  = solarPocketLength + 2.0 * solarPerimeterWrap
boxWidth   = solarPocketWidth  + 2.0 * solarPerimeterWrap - 2.0 # -2 so lid fits sloped edge not width
InsideBoxHeight  = 5.0  + batteryDia  # high edge. Extra so cutoff rotation leaves battery space
bottomThickness  = 3.0
boxHeight        = InsideBoxHeight + bottomThickness

bottomThickness  = 3.0
wallThickness    = 4.0

XYcenter = FreeCAD.Vector(boxLength/ 2.0, boxWidth/ 2.0, 0)

## 6.0 is gap for clip spring/knob (5.0 + tolerance)
#if (insideBatteryBoxWidth != 2.0 * frameWidth + 6.0) : complain1

#######################################
#######################################

boxPlate = Part.makeBox(          # slab only
   boxLength,
   boxWidth,
   boxHeight,     
   ORIGIN, 
   DR   
) 

#Part.show(boxPlate)

cutout1 = Part.makeBox(  # cut out interior
   boxLength - 2.0 * wallThickness,
   boxWidth  - 2.0 * wallThickness,
   boxHeight - bottomThickness,     
   ORIGIN + FreeCAD.Vector(wallThickness, wallThickness, bottomThickness),
   DR   
) 

#edges=[]   # Fillet some outside edges ??
#Ht = ??
#
#for e in cutout1.Edges :
#   if (e.Vertexes[0].Point[2] == Ht) and \
#      (e.Vertexes[1].Point[2] == Ht)  : edges.append(e)
#
#edges = list(set(edges)) # unique elements
#cutout1 = cutout1.makeFillet(solarPerimeterOverlap - 0.1, edges)


#Part.show(cutout1 )


# Cut off top on angle.
# The reason for the angle is to reduce the profile on one edge and
#  so that a second solar panel can be added flat on the deck.

solarLidCut = Part.makeBox(          
   boxLength,
   boxWidth + 10.0,                    # enough bigger to cover top on angle
   30.0,                               # just needs to be big enough
   ORIGIN + FreeCAD.Vector(0, -5.0,    # displace -5.0 so rotation does not leave edge uncut.
             boxHeight),               #raised. high side is at origin
   DR        
   ) 

#Part.show(solarLidCut )

# rotate lid around top center of battery
solarLidCut.rotate(FreeCAD.Vector(0, 
                       0, 
                       boxHeight),                # center of rotation
                   FreeCAD.Vector(1, 0, 0),       # axis of rotation
		   -16)                           # angle possibly ADJUST


box =boxPlate.cut([cutout1, solarLidCut])

#Part.show(box)

# small piece for testing. Cut away most of part.
boxSlice = box.cut(Part.makeBox( 
   boxLength,
   boxWidth,
   boxHeight,     
   ORIGIN + FreeCAD.Vector( 15 , 0, 0),
   DR )  
) 

#Part.show(boxSlice)

#######################################
#####  Mesh
#######################################

docName = 'box'
doc = FreeCAD.newDocument(docName) 
App.setActiveDocument(docName)

mesh = doc.addObject("Mesh::Feature","Mesh")
mesh.Mesh = MeshPart.meshFromShape(Shape=boxSlice, 
	   LinearDeflection=0.1, AngularDeflection=0.523599, Relative=False)

mesh.Label= "box  (Meshed)"
mesh.ViewObject.CreaseAngle=25.0
Mesh.export([mesh], "./" + "solar_box_plug.stl")

