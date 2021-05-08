# Frame to hold 14500 battery, LEDs, USB connector, and PCB platform.
# This is not structural and may not be used, but is size for interior 
# of a silicon? box which would be closed by solar panel.

import Part, PartDesignGui
import Mesh, MeshPart, MeshPartGui
import math


########################################################
############### construction parameters ################
########################################################

ORIGIN   = FreeCAD.Vector(0.0,   0.0, 0.0)    

DR = FreeCAD.Vector(0,0,1)  # default direction specifying parts


bottomThickness = 0.5
wallThickness   = 1.0

#####  platform parameter

solarPanelLength     = 110.0
solarPanelWidth      =  69.0
panelPerimeterWrap   =   3.0  # extension of silicon beyond panel edge
siliconbatteryWallThickness =   8.0

platformLength  = solarPanelLength + panelPerimeterWrap - siliconbatteryWallThickness

# width might need to be less if panel slope cuts into bottom !!!

platformWidth   = solarPanelWidth  + panelPerimeterWrap - siliconbatteryWallThickness

#####  battery box parameter

batteryLength = 50.0 
batteryDia    = 14.0 
batteryWallThickness = 1.0

clipSpace      = 8.0       # 8.0 for simple clips with a spring, both ends =6+2
clipThickness  = 1.0       # frame space to hold clip (2.0 too big, too small closes when printing)
clipProp       = 2.5 - 0.5 # lift clip so it centers on battery, less tolerance
clipShim       = 2.5 - 0.5 # center clip sides on battery, less tolerance

frameWidth     = clipShim + 2.5   # frame to hold clip, 2.0 beyond shim
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
                                platformLength - outsideBatteryBoxLength,   
				0.0, 0.0)

#######################################
#######################################

#  simple slab and wall to define component space

#platform = Part.makeBox(          # slab only
#   platformLength,
#   platformWidth,
#   bottomThickness, 
#   ORIGIN, 
#   DR   
#) 

platform =Part.makeBox ( 
   platformLength, platformWidth, 20.0, # high enough, it gets cut by lid below.
    ORIGIN, DR ).cut( Part.makeBox(          
       platformLength - 2.0 * wallThickness,
       platformWidth  - 2.0 * wallThickness,
       20.0, 
       ORIGIN + FreeCAD.Vector(
                             wallThickness, wallThickness, bottomThickness), 
       DR) 
      ) 
 

# Cut off top (wall and battery box) on angle of solar panel.
# The reason for the angle is to reduce the profile on one edge and
#  so that a second panel can be added flat on the deck.

solarLidCut = Part.makeBox(          
   platformLength,
   platformWidth + 10.0,               # enough bigger to cover top on angle
   30.0,                               # just needs to be big enough
   ORIGIN + FreeCAD.Vector(0, -5.0,    # displace -5.0 so rotation does not leave edge uncut.
             outsideBatteryBoxHeight), #raised. high side is at origin
   DR        
   ) 

# rotate lid around top center of battery
solarLidCut.rotate(FreeCAD.Vector(0, 
                       outsideBatteryBoxWidth/2.0, 
                       outsideBatteryBoxHeight),  # center of rotation
                   FreeCAD.Vector(1, 0, 0),       # axis of rotation
		   -15)                           # angle possibly ADJUST

#Part.show(platform)
#Part.show(solarLidCut)

platform = platform.cut([solarLidCut])

#######################################
######## battery box
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

THIS IS TOO HIGH, IMPEDES CONTACT
frame1B = Part.makeBox(         # bottom 
   frameThickness, insideBatteryBoxWidth, clipProp + frameWidth, 
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

THIS IS TOO HIGH, IMPEDES CONTACT
frame2B = Part.makeBox(          # bottom
   frameThickness, insideBatteryBoxWidth, clipProp + frameWidth, 
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

batteryBox =batteryBox.cut([solarLidCut, cut1C, cut2C])

# Part.show(batteryBox)

#######################################
######## LEDS
#######################################

#######################################
######## USB
#######################################


#######################################
######## final componentFrame
#######################################

componentFrame = batteryBox.fuse([platform])

# Part.show(componentFrame)

# Part.show(platform )
# Part.show(frame1A )
# Part.show(frame1B )
# Part.show(frame1C )
# Part.show(frame2A )
# Part.show(frame2B )
# Part.show(frame2C )

# Part.show(shim1A )
# Part.show(shim1B )
# Part.show(shim1C )
# Part.show(shim2A )
# Part.show(shim2B )
# Part.show(shim2C )

FreeCAD.Console.PrintMessage('Design Construction complete.\n')

#######################################
#####  Mesh
#######################################

docName = 'componentFrame'
doc = FreeCAD.newDocument(docName) 
App.setActiveDocument(docName)

mesh = doc.addObject("Mesh::Feature","Mesh")
mesh.Mesh = MeshPart.meshFromShape(Shape=componentFrame, 
	   LinearDeflection=0.1, AngularDeflection=0.523599, Relative=False)

mesh.Label= "componentFrame  (Meshed)"
mesh.ViewObject.CreaseAngle=25.0
Mesh.export([mesh], "./" + "componentFrame.stl")


#######################################

##### Show

#######################################

##doc.Tip = doc.addObject('App::Part','componentFrame')
##
##Gui.ActiveDocument=Gui.getDocument(docName)  
##Gui.activateWorkbench("PartDesignWorkbench")
##Gui.activeView().setActiveObject('pdbody', App.activeDocument().batteryBox)# this adds origin to batteryBox
##Gui.activeView().setActiveObject('part',   App.activeDocument().batteryBox)
##Gui.Selection.clearSelection()
##Gui.Selection.addSelection(App.ActiveDocument.batteryBox)
##
##
### remove = doc.addObject("Part::Feature","Remove")
### remove.Shape = inside.fuse(holes)
###or something like remove = Part.makeCompound(holes)
##
##
##Outside = doc.addObject("Part::Feature","Outside")
##Outside.Placement.Base = ORIGIN 
##Outside.Shape = outside
##
##Inside = doc.addObject("Part::Feature","Inside")
##Inside.Placement.Base = ORIGIN 
##Inside.Shape = inside
##
##Box=doc.addObject("Part::Cut","Box")
##Box.Base = Outside
##Box.Tool = Inside
##
# Part.show(Box)   argument 1 must be Part.Shape, not Part.Feature
##
##doc.Outside.addObject(doc.Box) #mv Box (body) into part Outside
##
##doc.recompute() 
##Gui.activeDocument().resetEdit()
##Gui.SendMsgToActiveView("ViewFit")
##Gui.activeDocument().activeView().viewAxonometric()

