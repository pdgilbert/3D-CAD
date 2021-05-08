##  test size and clips for 14500 (AA) battery

import Part, PartDesignGui
import Mesh, MeshPart, MeshPartGui
import math

####### define utilities ###################

def makeSTL(part, body) :
   ''' 
   Generate an STL mesh file. part is string used to generate stl file name.
   body is a string indicating an object in doc that has a .Shape attribute
   ''' 
   
   FreeCAD.Console.PrintMessage('generating stl file.\n')

   Gui.activateWorkbench("MeshWorkbench")
   App.setActiveDocument(docName)

   mesh = doc.addObject("Mesh::Feature","Mesh")
   mesh.Mesh = MeshPart.meshFromShape(Shape=doc.getObject(body).Shape, 
              LinearDeflection=0.1, AngularDeflection=0.523599, Relative=False)
   mesh.Label= body + " (Meshed)"
   mesh.ViewObject.CreaseAngle=25.0

   Mesh.export([mesh], "./" + part + ".stl")
   return None

################ common variables ################

ORIGIN   = FreeCAD.Vector(0.0,   0.0, 0.0)    

DR = FreeCAD.Vector(0,0,1)  # default direction specifying parts

bottomThickness = 0.5

batteryLength = 50.0 
batteryDia    = 14.0 
wallThickness = 1.0

clipSpace      = 8.0       # 8.0 for simple clips with a spring, both ends =6+2
clipThickness  = 1.0       # frame space to hold clip (2.0 too big, too small closes when printing)
clipProp       = 4.0 - 0.5 # lift clip to battery center less tolerance
clipShim       = 2.5 - 0.5 # center clip on battery less tolerance

frameWidth     = clipShim + 2.5   # frame to hold clip, 2.0 beyond shim
frameThickness = 1.0

insideBatteryBoxLength =  batteryLength + clipSpace  
insideBatteryBoxWidth  =  1.0  + batteryDia    
insideBatteryBoxHeight =  1.0  + batteryDia

# 6.0 is gap for clip spring/knob (5.0 + tolerance)
if (insideBatteryBoxWidth != 2.0 * frameWidth + 6.0) : complain1

# 11.0 is width of space for clip (10.0 + tolerance)
if (insideBatteryBoxWidth != 2.0 * clipShim + 11.0) : complain2

#######################################
#######################################

inside = Part.makeBox(          
   insideBatteryBoxLength,
   insideBatteryBoxWidth,
   insideBatteryBoxHeight, 
   FreeCAD.Vector(wallThickness, wallThickness, bottomThickness), 
   DR   
) 

#Part.show(inside)

outside = Part.makeBox ( 
   insideBatteryBoxLength + 2.0 * wallThickness,
   insideBatteryBoxWidth  + 2.0 * wallThickness,
   insideBatteryBoxHeight + bottomThickness, ORIGIN, DR)

#Part.show(outside)
 
# holes = []  # fused to inside and removed
# holes.append(inside)

FreeCAD.Console.PrintMessage('finished box definition.\n')

box = outside.cut(inside)

#or something like remove = Part.makeCompound(holes)


# see https://www.freecadweb.org/wiki/Topological_data_scripting


#####  sides and bottom of clips to center clip on battery 

# one end  
shim1A = Part.makeBox(        # one side  
   clipThickness, clipShim, insideBatteryBoxHeight - clipProp, 
   FreeCAD.Vector(wallThickness, 
                  wallThickness, 
		  bottomThickness + clipProp), DR ) 
   
shim1B = Part.makeBox(        # bottom  
   clipThickness, insideBatteryBoxWidth, clipProp, 
   FreeCAD.Vector(wallThickness, 
                  wallThickness, 
		  bottomThickness), DR ) 
   
shim1C = Part.makeBox(        # other side  
   clipThickness, clipShim, insideBatteryBoxHeight - clipProp, 
   FreeCAD.Vector(wallThickness, 
                  wallThickness + insideBatteryBoxWidth - clipShim, 
		  bottomThickness + clipProp), DR ) 

# other end
shim2A = Part.makeBox(        # one side          
   clipThickness, clipShim, insideBatteryBoxHeight - clipProp, 
   FreeCAD.Vector(wallThickness + insideBatteryBoxLength - clipThickness, 
                  wallThickness, 
		  bottomThickness + clipProp), DR ) 

shim2B = Part.makeBox(        # bottom          
   clipThickness, insideBatteryBoxHeight, clipProp, 
   FreeCAD.Vector(wallThickness + insideBatteryBoxLength - clipThickness, 
                  wallThickness, 
		  bottomThickness), DR ) 

shim2C = Part.makeBox(        # other side          
   clipThickness, clipShim, insideBatteryBoxHeight - clipProp,
   FreeCAD.Vector(wallThickness + insideBatteryBoxLength - clipThickness, 
                  wallThickness + insideBatteryBoxWidth  - clipShim, 
		  bottomThickness + clipProp), DR ) 


##### frames to hold clips in place

frame1A = Part.makeBox(          
   frameThickness, frameWidth, insideBatteryBoxHeight, 
   FreeCAD.Vector(wallThickness + clipThickness, 
                  wallThickness, 
		  bottomThickness), DR ) 

frame1B = Part.makeBox(          
   frameThickness, insideBatteryBoxWidth, frameWidth, 
   FreeCAD.Vector(wallThickness + clipThickness, 
                  wallThickness, 
		  bottomThickness), DR ) 

frame1C = Part.makeBox(          
   frameThickness, frameWidth, insideBatteryBoxHeight, 
   FreeCAD.Vector(wallThickness + clipThickness, 
                  wallThickness + insideBatteryBoxWidth - frameWidth, 
                  bottomThickness), DR ) 

frame2A = Part.makeBox(          
   frameThickness, frameWidth, insideBatteryBoxHeight, 
  FreeCAD.Vector(wallThickness + insideBatteryBoxLength - (clipThickness + frameThickness),
                  wallThickness, 
		  bottomThickness), DR ) 

frame2B = Part.makeBox(          
   frameThickness, insideBatteryBoxWidth, frameWidth, 
   FreeCAD.Vector(wallThickness + insideBatteryBoxLength - (clipThickness + frameThickness), 
                  wallThickness, 
		  bottomThickness), DR ) 

frame2C = Part.makeBox(          
   frameThickness, frameWidth, insideBatteryBoxHeight, 
   FreeCAD.Vector(wallThickness + insideBatteryBoxLength - (clipThickness + frameThickness), 
                  wallThickness + insideBatteryBoxWidth - frameWidth, 
                  bottomThickness), DR ) 

box = box.fuse([frame1A, frame1B, frame1C, frame2A, frame2B, frame2C,
                 shim1A, shim1B, shim1C, shim2A, shim2B, shim2C])

# Part.show(box)

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

#######################################
#####  Mesh
#######################################

docName = 'AAbatteryBox'
doc = FreeCAD.newDocument(docName) 
App.setActiveDocument(docName)

mesh = doc.addObject("Mesh::Feature","Mesh")
mesh.Mesh = MeshPart.meshFromShape(Shape=box, 
	   LinearDeflection=0.1, AngularDeflection=0.523599, Relative=False)

mesh.Label= "box  (Meshed)"
mesh.ViewObject.CreaseAngle=25.0
Mesh.export([mesh], "./" + "battery_holder_test_box.stl")


#######################################

##### Show

#######################################

doc.Tip = doc.addObject('App::Part','batteryBox')

Gui.ActiveDocument=Gui.getDocument(docName)  
Gui.activateWorkbench("PartDesignWorkbench")
Gui.activeView().setActiveObject('pdbody', App.activeDocument().batteryBox)# this adds origin to batteryBox
Gui.activeView().setActiveObject('part',   App.activeDocument().batteryBox)
Gui.Selection.clearSelection()
Gui.Selection.addSelection(App.ActiveDocument.batteryBox)


# remove = doc.addObject("Part::Feature","Remove")
# remove.Shape = inside.fuse(holes)
#or something like remove = Part.makeCompound(holes)


Outside = doc.addObject("Part::Feature","Outside")
Outside.Placement.Base = ORIGIN 
Outside.Shape = outside

Inside = doc.addObject("Part::Feature","Inside")
Inside.Placement.Base = ORIGIN 
Inside.Shape = inside

Box=doc.addObject("Part::Cut","Box")
Box.Base = Outside
Box.Tool = Inside

# Part.show(Box)   argument 1 must be Part.Shape, not Part.Feature

doc.Outside.addObject(doc.Box) #mv Box (body) into part Outside

   # slots for end clips

doc.recompute() 
Gui.activeDocument().resetEdit()
Gui.SendMsgToActiveView("ViewFit")
Gui.activeDocument().activeView().viewAxonometric()

FreeCAD.Console.PrintMessage('Outside object construction complete.\n')

##### STL


###makeSTL("Outside", "Box")

