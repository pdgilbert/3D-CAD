# Box on which solar panel fits (glues?) directly. This has higher profile and no slope,
# intended to fit breadboard, so battery is moved to the end.
# Possibly could be used as mold plug, but probably just 3D print and use.
# (Compare  solar_epoxy_box_plug.py which has sloped top and lower profile.)

import Part, PartDesignGui
import Mesh, MeshPart, MeshPartGui
import math


########################################################
############### construction parameters ################
########################################################

ORIGIN   = FreeCAD.Vector(0.0,   0.0, 0.0)    

DR = FreeCAD.Vector(0,0,1)  # default direction specifying parts


#####  parameters

solarPocketLength     = 111.0  # 110.0 + 1mm tolerance gap (0.5 was a bit tight)
solarPocketWidth      =  70.0  #  69.0 + 1mm
solarPocketInset      =   2.0  # depth of inset to hold solar panel
solarPerimeterWrap    =   3.5  # Extension of wall beyond solar panel edge.
                               # This affects boxWidth and boxLength and then with
                               # wallThickness determines inside width and length.
                               # 2.0 for solarPerimeterWrap and also wallThickness seems
                               # good but setting bigger solarPerimeterWrap and smaller
                               # wallThickness increases inside width.

batteryDia    = 14.0 

boxLength  = solarPocketLength + 2.0 * solarPerimeterWrap

# lid fits sloped edge not width
boxWidth   = solarPocketWidth  + 2.0 * solarPerimeterWrap

bottomThickness  = 2.0
boxInsideHeight  = 30.0  # high enough for breadboard and components
boxHeight        = boxInsideHeight  + bottomThickness

wallThickness   = 1.0  # previously 2.0
# lipThickness is used very approximately by determine chamfer. 4.0 is too small.
lipThickness    = 6.0  # lip to hold (glue) solar panel. 

XYcenter = FreeCAD.Vector(boxLength/ 2.0, boxWidth/ 2.0, 0)

# for box to hold two breadboards (with no power strips)
if not (boxWidth  - 2.0 * wallThickness) > 72.0 : complain0 


#####  battery box parameter

batteryLength = 50.0 
batteryWallThickness = 1.0
batteryBoxWallCut = 3.0

clipSpace      = 2.5       # with battery protection circuit, so end clips with spring are not used.
#clipSpace     = 8.0       # 8.0 for simple clips with a spring, both ends =6+2
#clipThickness  = 1.0       # frame space to hold clip (2.0 too big, too small closes when printing)
#clipProp       = 2.5 - 0.5 # lift clip so it centers on battery, less tolerance
#clipShim       = 3.5 - 0.5 # center clip sides on battery, less tolerance
#                           # 2.5 - 0.5 if tang come out top. 
#
#frameWidth     = 4.5       # frame to hold clip, with opening for contacts. 
#frameThickness = 1.0

batteryBoxInsideLength =  batteryLength + clipSpace  
batteryBoxInsideWidth  =  3.75  + batteryDia  #1.0 telerance +added 2.75 for battery protection circuit 
batteryBoxInsideHeight =  1.0  + batteryDia   # could add to bring up to lip, cut by insert

# 6.0 is gap for clip spring/knob (5.0 + tolerance)
# if (batteryBoxInsideWidth != 2.0 * frameWidth + 6.0) : complain1

# 11.0 is width of space for clip (10.0 + tolerance)
# if (batteryBoxInsideWidth != 2.0 * clipShim + 11.0) : complain2

batteryBoxOutsideLength =   batteryBoxInsideLength + 2.0 * batteryWallThickness
batteryBoxOutsideWidth  =   batteryBoxInsideWidth  + 2.0 * batteryWallThickness
batteryBoxOutsideHeight =   batteryBoxInsideHeight # using box for bottom, otherwise +bottomThickness )

# This is used to place battery box so end is not under lip, and also to fill space under lip.
# Calculation is tricky because lipThickness is used only in approximation for chamfer.
# By visual check lipThickness is adjusted - 2.5
batteryBoxHead = boxWidth  - solarPerimeterWrap - (lipThickness - 2.5) #+ frameThickness

batteryBoxORIGIN = ORIGIN + FreeCAD.Vector(
                                boxLength,   
				batteryBoxHead - batteryBoxOutsideLength, 
                                bottomThickness) 

# batteryBox placement assumes batteryWallThickness >= wallThickness
if (batteryWallThickness <  wallThickness) : complain3


#### extra fill
# fill small space between box wall and end of the battery box.
# USB hole can go in this

extraFillORIGIN = FreeCAD.Vector(batteryBoxInsideLength + wallThickness, 
                                 wallThickness, 
                                 0)
extraFillLength = 7.0
extraFillWidth  = batteryBoxOutsideWidth  - wallThickness
extraFillHeight = batteryBoxOutsideHeight


#####  USB hole parameters

# This is sized for a micro usb socket which has a rectangular plastic sheath it fits into.
# The socket allows 5 wires, 5v, d-, d+, id, grd . Only using 5v and grd so far.

# A horizontal USBhole is rotated 180 so placement base will be furthest corner from origin
# A vertical USBhole is rotated 90 about a different axis.

# The plastic sheath outside is 9.0 x 4.4. Swelling or calibration is 
# different in Z vs XxY on my printer. 
# 4.75x9.25 works well with a horizontal hole (4.5x9.0 is too small and 5.0x9.5 is loose)
# but is too small (prints 4.1x8.5) with a vertical hole.
# With the vertical hole there is some swelling on the first layer that can make the hole
# too small. There should be a camfer, but scapin away the small lip also works.
# Making the hole bigger means the insert is loose once inserted.

# Length, Width, Height were directions with vertical hole.
USBholeLength     = 18.0   # 14.0 if using wire hole
USBholeWidth      =  5.1  
USBholeHeight     = 10.0   # 9.75  very slightly too small
USBholeFillet     =  1.0
#USBwireHoleLength =  batteryBoxOutsideWidth  + 5.0 # can be longer than needed
#USBwireHoleWidth  =  2.0
#USBwireHoleHeight =  4.0

USBholeORIGIN     = FreeCAD.Vector( boxLength - 5.0, 
                                    boxWidth - wallThickness - USBholeWidth - 0.75, 
                                    - USBholeFillet)


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

boxPlate = boxPlate.makeFillet(2.0, boxPlate.Edges)

#Part.show(boxPlate)
#
cutout1 = Part.makeBox(  # cut out interior
   boxLength - 2.0 * wallThickness,
   boxWidth  - 2.0 * wallThickness, 
   boxHeight - bottomThickness,     
   ORIGIN + FreeCAD.Vector(wallThickness, wallThickness, bottomThickness),
   DR   
) 

# Chamfer top high side and top ends to leave lip.
# It is a bit trick to select these. The cutout1 is below boxHeight.
# One end of edge is above 1/2  boxHeight and the other is a bit above bottomThickness.

edges=[]   
Ht = boxHeight / 2.0

for e in cutout1.Edges :
   if ((e.Vertexes[0].Point[2] >= Ht)  and \
       (e.Vertexes[1].Point[2] >= Ht) )   : edges.append(e)

edges = list(set(edges)) # unique elements

if (len(edges) != 4 ) : complain3

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

box = boxPlate.cut([cutout1, Inset])

#Part.show(box)


#######################################
########    battery box        ########
#######################################

# build this at ORIGIN then rotate and translate to batteryBoxORIGIN

batteryBox =Part.makeBox ( 
   batteryBoxOutsideLength, batteryBoxOutsideWidth, batteryBoxOutsideHeight, 
    ORIGIN, DR ).cut( Part.makeBox(          
       batteryBoxInsideLength,
       batteryBoxInsideWidth,
       batteryBoxInsideHeight, 
       ORIGIN + FreeCAD.Vector(
                             batteryWallThickness, batteryWallThickness, 0),
       DR) 
      ) 

#Part.show(batteryBox)

########### one end  

##### frames to hold battery clips in place
#
#frame1A = Part.makeBox(         # one side 
#   frameThickness, frameWidth, batteryBoxInsideHeight, 
#   ORIGIN + FreeCAD.Vector(batteryWallThickness + clipThickness, 
#                  batteryWallThickness, 
#		  0), DR ) 
#
#frame1B = Part.makeBox(         # bottom 
#   frameThickness, batteryBoxInsideWidth, clipProp + frameWidth - 1.0, # impedes contact if too high
#   ORIGIN + FreeCAD.Vector(batteryWallThickness + clipThickness, 
#                  batteryWallThickness, 
#                  0), DR ) 
#
#frame1C = Part.makeBox(         # other side 
#   frameThickness, frameWidth, batteryBoxInsideHeight, 
#   ORIGIN + FreeCAD.Vector(batteryWallThickness + clipThickness, 
#                  batteryWallThickness + batteryBoxInsideWidth - frameWidth, 
#                  0), DR ) 
#
######  shim sides and bottom of clips to center clip on battery 
#
#shim1A = Part.makeBox(        # one side  
#   clipThickness, clipShim, batteryBoxInsideHeight - clipProp, 
#   ORIGIN + FreeCAD.Vector(batteryWallThickness, 
#                  batteryWallThickness, 
#                  clipProp), DR ) 
#   
#shim1B = Part.makeBox(        # bottom  
#   clipThickness, batteryBoxInsideWidth, clipProp, 
#   ORIGIN + FreeCAD.Vector(batteryWallThickness, 
#                  batteryWallThickness, 
#                  0), DR ) 
#   
#shim1C = Part.makeBox(        # other side  
#   clipThickness, clipShim, batteryBoxInsideHeight - clipProp, 
#   ORIGIN + FreeCAD.Vector(batteryWallThickness, 
#                  batteryWallThickness + batteryBoxInsideWidth - clipShim, 
#                  clipProp), DR ) 
#
#cut1C = Part.makeBox(        # to insert battery clip with tang horizontal 
#   clipThickness, batteryBoxOutsideWidth/2.0, batteryBoxInsideHeight, 
#   ORIGIN + FreeCAD.Vector(batteryWallThickness, 
#                  batteryBoxOutsideWidth/2.0, 
#                  (batteryDia/2.0) - 4.0), DR )  # previously -2.0
#
## with battery protection circuit there are not frames and shims to hold clips
##frames and shims to hold clips
#oneEnd = frame1A.fuse([frame1B, frame1C, shim1A, shim1B, shim1C]).cut([cut1C])
#
## Part.show(oneEnd)
## Part.show(shim1B)
#
############# other end  
#
#batteryXYcenter = FreeCAD.Vector(batteryBoxOutsideLength/ 2.0, batteryBoxOutsideWidth/ 2.0, 0)
#otherEnd = oneEnd.mirror(batteryXYcenter, FreeCAD.Vector(1,0,0))


########### cut away wall for bigger opening (constricted by lip)

cutWall = Part.makeBox(
       batteryBoxInsideLength,
       batteryWallThickness,
       batteryBoxInsideHeight - batteryBoxWallCut, 
       ORIGIN + FreeCAD.Vector(
                             batteryWallThickness, 
                             batteryWallThickness + batteryBoxInsideWidth, 
                             batteryBoxInsideHeight - batteryBoxWallCut), 
       DR) 


########### cut slit half way along wall for wires from battery protection circuit

cutWireSlit = Part.makeBox(
       4.0,
       batteryWallThickness,
       batteryBoxInsideHeight, 
       ORIGIN + FreeCAD.Vector(
                             batteryBoxInsideLength / 2.0, 
                             batteryWallThickness + batteryBoxInsideWidth, 
                             batteryBoxInsideHeight / 4.0), 
       DR) 

########### extra fill (under lip) at head of batteryBox

# if the lip is low extend this up to it

extraFill = Part.makeBox(extraFillLength, extraFillWidth, extraFillHeight,
       ORIGIN + extraFillORIGIN,
       DR) 

#batteryBox = batteryBox.fuse([oneEnd, otherEnd, extraFill]).cut([cutWall, cutWireSlit])
# with battery protection circuit there are not frames and shims to hold clips

batteryBox = batteryBox.fuse([extraFill]).cut([cutWall, cutWireSlit])


############ rotate and translate to position
  
batteryBox.rotate(ORIGIN,                   # center of rotation
                   FreeCAD.Vector(0, 0, 1), # axis   of rotation
		   90.0)                    # angle  of rotation

# rotate does not change reference corner, so it is no longer closest corner to origin.
# translate moves by given amount, so next is moveTo. (There is probably a better way.)

batteryBox.translate(batteryBoxORIGIN -  batteryBox.Placement.Base)

# cut inset is just cleanup but important if top is sloped.
batteryBox = batteryBox.cut([Inset])

# Part.show(batteryBox)

#######################################
######## LEDS
#######################################

#######################################
######## USB
#######################################

# build this at ORIGIN then rotate and translate to USBholeORIGIN

# extend outward by fillet so it does not apply to outside edge

USBhole = Part.makeBox(USBholeLength + USBholeFillet, USBholeWidth, USBholeHeight, 
    ORIGIN, DR )

# FILLET EDGES
USBhole = USBhole.makeFillet(USBholeFillet, USBhole.Edges)

## add wire hole
#USBhole = USBhole.fuse([
#             Part.makeBox(USBwireHoleLength, USBwireHoleWidth, USBwireHoleHeight, 
#               ORIGIN + FreeCAD.Vector(0, USBholeWidth / 3.0, USBholeHeight / 4.0), 
#               DR)])
 

# Part.show(USBhole)

############ rotate and translate to position
  
USBhole.rotate(ORIGIN,                  # center of rotation
               FreeCAD.Vector(0, 1, 0), # axis   of rotation
	       -90.0)                    # angle  of rotation

# note rotation does not change corner which determines Placement.Base
USBhole.translate(USBholeORIGIN -  USBhole.Placement.Base)

# Part.show(USBhole)

#######################################
######## final
#######################################

box = box.fuse([batteryBox]).cut(USBhole)

# Part.show(box)
 
#######################################
#####  test slice
#######################################

# small piece for testing. Cut away most of part.
boxSlice = box.cut(Part.makeBox( 
   boxLength - 25,
   boxWidth,
   boxHeight,     
   ORIGIN,
   DR )  
) 

#Part.show(boxSlice)


#######################################
#####  Mesh
#######################################

# export stl for boxSlice and box.

docName = 'box'
doc = FreeCAD.newDocument(docName) 
App.setActiveDocument(docName)


meshSlice = doc.addObject("Mesh::Feature","Mesh")
meshSlice.Mesh = MeshPart.meshFromShape(Shape=boxSlice, 
	   LinearDeflection=0.1, AngularDeflection=0.523599, Relative=False)

meshSlice.Label= "boxSlice  (Meshed)"
meshSlice.ViewObject.CreaseAngle=25.0
Mesh.export([meshSlice], "./" + "slice_solar_breadboard_box.stl")


meshBox = doc.addObject("Mesh::Feature","MeshBox")
meshBox.Mesh = MeshPart.meshFromShape(Shape=box, 
	   LinearDeflection=0.1, AngularDeflection=0.523599, Relative=False)
meshBox.Label= "box  (Meshed)"
meshBox.ViewObject.CreaseAngle=25.0
Mesh.export([meshBox], "./" + "solar_breadboard_box.stl")

