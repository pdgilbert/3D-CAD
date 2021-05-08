# Plug for mold to make (probably epoxy) box on which solar panel fits (glues) directly.
# (Compare  solar_box_plug.py and solar_lid_plug.py which fit together with
#  the lid holding the solar panel.

import Part, PartDesignGui
import Mesh, MeshPart, MeshPartGui
import math


########################################################
############### construction parameters ################
########################################################

ORIGIN   = FreeCAD.Vector(0.0,   0.0, 0.0)    

DR = FreeCAD.Vector(0,0,1)  # default direction specifying parts


#####  parameters

theta = -12.0  # angle in degrees of top edge   ADJUST

solarPocketLength     = 111.5  # 110.0 + 1.5mm tolerance gap
solarPocketWidth      =  70.5  #  69.0 + 1.5mm
solarPocketInset      =   2.0  # depth of inset to hold solar panel
solarPerimeterWrap    =   2.0  # extension of wall beyond solar panel edge

batteryDia    = 14.0 

boxLength  = solarPocketLength + 2.0 * solarPerimeterWrap

# lid fits sloped edge not width
boxWidth   = math.cos(math.radians(theta)) * solarPocketWidth  + 2.0 * solarPerimeterWrap

bottomThickness  = 2.0
InsideBoxHeight  = 5.0  + batteryDia  # high edge. Extra so cutoff rotation leaves battery space
boxHeight        = InsideBoxHeight  + bottomThickness

# this is not used, height determinde by angle theta
#InsideBoxHeight2 = 4.0                # low edge. Raise so whole box can be used for PCB
#boxHeight2       = InsideBoxHeight2 + bottomThickness

wallThickness   = 2.0
lipThickness    = 4.0  # lip to hold (glue) solar panel. This is used aproximately by chamfer

XYcenter = FreeCAD.Vector(boxLength/ 2.0, boxWidth/ 2.0, 0)



#####  battery box parameter

batteryLength = 50.0 
batteryWallThickness = 1.0

clipSpace      = 8.0       # 8.0 for simple clips with a spring, both ends =6+2
clipThickness  = 1.0       # frame space to hold clip (2.0 too big, too small closes when printing)
clipProp       = 2.5 - 0.5 # lift clip so it centers on battery, less tolerance
clipShim       = 2.5 - 0.5 # center clip sides on battery, less tolerance

frameWidth     = clipShim + 2.5   # frame to hold clip, beyond shim
frameThickness = 1.0

insideBatteryBoxLength =  batteryLength + clipSpace  
insideBatteryBoxWidth  =  1.0  + batteryDia    
insideBatteryBoxHeight =  1.0  + batteryDia

# 6.0 is gap for clip spring/knob (5.0 + tolerance)
if (insideBatteryBoxWidth != 2.0 * frameWidth + 6.0) : complain1

# 11.0 is width of space for clip (10.0 + tolerance)
if (insideBatteryBoxWidth != 2.0 * clipShim + 11.0) : complain2

outsideBatteryBoxLength =   insideBatteryBoxLength + 2.0 * batteryWallThickness
outsideBatteryBoxWidth  =   insideBatteryBoxWidth  + 2.0 * batteryWallThickness
outsideBatteryBoxHeight =   insideBatteryBoxHeight + bottomThickness

BatteryBoxORIGIN = ORIGIN + FreeCAD.Vector(
                                boxLength - wallThickness - outsideBatteryBoxLength,   
				wallThickness, bottomThickness)

#######################################
#####    main box construction    #####
#######################################

boxPlate = Part.makeBox(          # slab only
   boxLength,
   boxWidth,
   boxHeight,     
   ORIGIN, 
   DR   
) 

# Cut off top on angle.
# The reason for the angle is to reduce the profile on one edge and
#  so that a second solar panel can be added flat on the deck.

topCut = Part.makeBox(          
   boxLength,
   boxWidth + 10.0,                    # enough bigger to cover top on angle
   30.0,                               # just needs to be big enough
   ORIGIN + FreeCAD.Vector(0, -5.0,    # displace -5.0 so rotation does not leave edge uncut.
             boxHeight),               #raised. high side is at origin
   DR        
   )

topCut.rotate(FreeCAD.Vector(0, 
                       0, 
                       boxHeight),                # center of rotation
                   FreeCAD.Vector(1, 0, 0),       # axis   of rotation
		   theta)                         # angle  of rotation


boxPlate = boxPlate.cut([topCut])

boxPlate = boxPlate.makeFillet(2.0, boxPlate.Edges)

#Part.show(boxPlate)
#Part.show(topCut)

cutout1 = Part.makeBox(  # cut out interior
   boxLength - 2.0 * wallThickness,
   boxWidth  - 2.0 * wallThickness - lipThickness,    # cut out under lip on high side only
   boxHeight - bottomThickness,     
   ORIGIN + FreeCAD.Vector(wallThickness, wallThickness, bottomThickness),
   DR   
) 

cutout1 =cutout1.cut([topCut])

# Chamfer top high side and top ends to leave lip.
# It is a bit trick to select these. The cutout1 is below boxHeight.
# One end of edge is above 1/2  boxHeight and the other is a bit above bottomThickness.

edges=[]   
Ht1 = boxHeight / 2.0
Ht2 = bottomThickness + 1.0

for e in cutout1.Edges :
   if ((e.Vertexes[0].Point[2] >= Ht1)  and \
       (e.Vertexes[1].Point[2] >= Ht2) ) or \
      ((e.Vertexes[1].Point[2] >= Ht1) and \
       (e.Vertexes[0].Point[2] >= Ht2))  : edges.append(e)

edges = list(set(edges)) # unique elements

if (len(edges) != 3 ) : complain3

cutout1 = cutout1.makeChamfer( 1.5 * lipThickness, edges) # 1.5 is aprox.


#Part.show(cutout1 )


Inset = Part.makeBox(     
   solarPocketLength,
   solarPocketWidth, 
   solarPocketInset,  
   ORIGIN + FreeCAD.Vector(solarPerimeterWrap, solarPerimeterWrap,  
             boxHeight - solarPocketInset), 
   DR        
   ) 

Inset.rotate(FreeCAD.Vector(0,
                       0, 
                       boxHeight),          
                   FreeCAD.Vector(1, 0, 0), 
		   theta)           # NB same rotation at topCut     


box = boxPlate.cut([cutout1, Inset])

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
########    battery box        ########
#######################################

batteryBox =Part.makeBox ( 
   outsideBatteryBoxLength, outsideBatteryBoxWidth, outsideBatteryBoxHeight, 
    BatteryBoxORIGIN, DR ).cut( Part.makeBox(          
       insideBatteryBoxLength,
       insideBatteryBoxWidth,
       insideBatteryBoxHeight, 
       BatteryBoxORIGIN + FreeCAD.Vector(
                             batteryWallThickness, batteryWallThickness, bottomThickness), 
       DR) 
      ) 
 
   

#Part.show(batteryBox)
 
# holes = []  # fused to something and removed
# holes.append(something)
#or something like remove = Part.makeCompound(holes)
# see https://www.freecadweb.org/wiki/Topological_data_scripting


#####  shim sides and bottom of clips to center clip on battery 

# one end  
shim1A = Part.makeBox(        # one side  
   clipThickness, clipShim, insideBatteryBoxHeight - clipProp, 
   BatteryBoxORIGIN + FreeCAD.Vector(batteryWallThickness, 
                  batteryWallThickness, 
		  bottomThickness + clipProp), DR ) 
   
shim1B = Part.makeBox(        # bottom  
   clipThickness, insideBatteryBoxWidth, clipProp, 
   BatteryBoxORIGIN + FreeCAD.Vector(batteryWallThickness, 
                  batteryWallThickness, 
		  bottomThickness), DR ) 
   
shim1C = Part.makeBox(        # other side  
   clipThickness, clipShim, insideBatteryBoxHeight - clipProp, 
   BatteryBoxORIGIN + FreeCAD.Vector(batteryWallThickness, 
		  batteryWallThickness + insideBatteryBoxWidth - clipShim, 
		  bottomThickness + clipProp), DR ) 
   
cut1C = Part.makeBox(        # to insert battery clip with tang horizontal 
   clipThickness, outsideBatteryBoxWidth/2.0, insideBatteryBoxHeight, 
   BatteryBoxORIGIN + FreeCAD.Vector(batteryWallThickness, 
		  outsideBatteryBoxWidth/2.0, 
		  bottomThickness + (batteryDia/2.0) - 2.0), DR ) 

# other end
shim2A = Part.makeBox(        # one side          
   clipThickness, clipShim, insideBatteryBoxHeight - clipProp, 
   BatteryBoxORIGIN + FreeCAD.Vector(
                  batteryWallThickness + insideBatteryBoxLength - clipThickness, 
                  batteryWallThickness, 
		  bottomThickness + clipProp), DR ) 

shim2B = Part.makeBox(        # bottom          
   clipThickness, insideBatteryBoxHeight, clipProp, 
   BatteryBoxORIGIN + FreeCAD.Vector(
                  batteryWallThickness + insideBatteryBoxLength - clipThickness, 
                  batteryWallThickness, 
		  bottomThickness), DR ) 

shim2C = Part.makeBox(        # other side	    
   clipThickness, clipShim, insideBatteryBoxHeight - clipProp,
   BatteryBoxORIGIN + FreeCAD.Vector(
		  batteryWallThickness + insideBatteryBoxLength - clipThickness, 
		  batteryWallThickness + insideBatteryBoxWidth  - clipShim, 
		  bottomThickness + clipProp), DR ) 


cut2C = Part.makeBox(         # to insert battery clip with tang horizontal
   clipThickness, outsideBatteryBoxWidth/2.0, insideBatteryBoxHeight, 
   BatteryBoxORIGIN + FreeCAD.Vector(
                  batteryWallThickness + insideBatteryBoxLength - clipThickness, 
		  outsideBatteryBoxWidth/2.0, 
		  bottomThickness + (batteryDia/2.0) - 2.0), DR ) 


##### frames to hold battery clips in place

# one end  
frame1A = Part.makeBox(         # one side 
   frameThickness, frameWidth, insideBatteryBoxHeight, 
   BatteryBoxORIGIN + FreeCAD.Vector(batteryWallThickness + clipThickness, 
                  batteryWallThickness, 
		  bottomThickness), DR ) 

frame1B = Part.makeBox(         # bottom 
   frameThickness, insideBatteryBoxWidth, clipProp + frameWidth - 1.0, # impedes contact if too high
   BatteryBoxORIGIN + FreeCAD.Vector(batteryWallThickness + clipThickness, 
                  batteryWallThickness, 
		  bottomThickness), DR ) 

frame1C = Part.makeBox( 	# other side 
   frameThickness, frameWidth, insideBatteryBoxHeight, 
   BatteryBoxORIGIN + FreeCAD.Vector(batteryWallThickness + clipThickness, 
		  batteryWallThickness + insideBatteryBoxWidth - frameWidth, 
		  bottomThickness), DR ) 

# other end
frame2A = Part.makeBox(          # one side
   frameThickness, frameWidth, insideBatteryBoxHeight, 
   BatteryBoxORIGIN + FreeCAD.Vector(batteryWallThickness + insideBatteryBoxLength - (clipThickness + frameThickness),
                  batteryWallThickness, 
		  bottomThickness), DR ) 

frame2B = Part.makeBox(          # bottom
   frameThickness, insideBatteryBoxWidth, clipProp + frameWidth - 1.0,  # impedes contact if too high
   BatteryBoxORIGIN + FreeCAD.Vector(batteryWallThickness + insideBatteryBoxLength - (clipThickness + frameThickness), 
                  batteryWallThickness, 
		  bottomThickness), DR ) 

frame2C = Part.makeBox( 	 # other side
   frameThickness, frameWidth, insideBatteryBoxHeight, 
   BatteryBoxORIGIN + FreeCAD.Vector(batteryWallThickness + insideBatteryBoxLength - (clipThickness + frameThickness), 
		  batteryWallThickness + insideBatteryBoxWidth - frameWidth, 
		  bottomThickness), DR ) 

batteryBox = batteryBox.fuse([frame1A, frame1B, frame1C, frame2A, frame2B, frame2C,
                 shim1A, shim1B, shim2A, shim2B])

batteryBox =batteryBox.cut([topCut, Inset, cut1C, cut2C])

BATTERY AND CLIPS WON'T GO IN LIKE THIS
# Part.show(batteryBox)

#######################################
######## LEDS
#######################################

#######################################
######## USB
#######################################


#######################################
######## final
#######################################

box = box.fuse([batteryBox])

# Part.show(box)

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
Mesh.export([mesh], "./" + "solar_epoxy_box_plug.stl")

