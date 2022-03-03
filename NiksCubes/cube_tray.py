# Mold for large cube tray

import Part, PartDesignGui
import Mesh, MeshPart, MeshPartGui
import math


########################################################
############### construction parameters ################
########################################################

ORIGIN   = FreeCAD.Vector(0.0,   0.0, 0.0)    

DR = FreeCAD.Vector(0,0,1)  # default direction specifying parts


#####  parameters

cubeLength = 198.0
cubeWidth  =  97.0
cubeHeight =  38.0
cubeFillet =   3.0  # rounding inside edges

cubeNumberWide = 2
cubeNumberLong = 3

dividerThickness   = 2.5

lipHeigth = 3.0

# mold is PLA mold for making silicone mold
# tray is silicone mold

moldWall  = 2.0
moldBottomThickness = 2.0

trayHeight = cubeHeight + moldBottomThickness 

moldLength  = cubeNumberLong * cubeLength  +  (cubeNumberLong + 1) * dividerThickness  +  2.0 * moldWall
moldWidth   = cubeNumberWide   * cubeWidth   +   (cubeNumberWide + 1) * dividerThickness  +  2.0 * moldWall
moldHeight  = trayHeight + moldBottomThickness + lipHeigth

#XYcenter = FreeCAD.Vector(trayLength/ 2.0, trayWidth/ 2.0, 0)


#####  dimension check  - could need a tolerance here on max size  #####

print("tray length (inches)", (moldLength - 2* moldWall)/ 25.4)

print("tray width (inches)", (moldWidth - 2* moldWall)/ 25.4)

if not ((moldLength - 2* moldWall) <  (25.4 * 24.0 ))  : complain0A    # tray max length 24"

if not ((moldLength - 2* moldWall) >  (25.4 * 23.75))  : complain0B    # tray min length 23.75"

if not ((moldWidth  - 2* moldWall) <  (25.4 *  8.0 ))  : complain0C    # tray max width  8"

if not ((moldWidth  - 2* moldWall) >  (25.4 *  7.75))  : complain0D    # tray min width  7.75"


#######################################
#####    outer construction    #####
#######################################

boxOutside = Part.makeBox(          # outer box
   moldLength,
   moldWidth,
   moldHeight,     
   ORIGIN, 
   DR   
) 

#Part.show(boxOutside)

cutout1 = Part.makeBox(  # cut out interior
   moldLength - 2.0 * moldWall,
   moldWidth  - 2.0 * moldWall, 
   moldHeight - moldBottomThickness + lipHeigth ,     
   ORIGIN + FreeCAD.Vector(moldWall, moldWall, moldBottomThickness),
   DR   
) 

box = boxOutside.cut([cutout1])

#Part.show(box)


cube = Part.makeBox(     
   cubeLength,
   cubeWidth, 
   cubeHeight,  
   ORIGIN,
   DR        
   ) 


#Part.show(cube )


# Chamfer top high side and top ends to leave lip.
# It is a bit trick to select these. The cutout1 is below boxHeight.
# One end of edge is above 1/2  boxHeight and the other is a bit above bottomThickness.

edges=[]   

for e in cube.Edges :
   if ((e.Vertexes[0].Point[2] > moldBottomThickness)  or \
       (e.Vertexes[1].Point[2] > moldBottomThickness) )   : edges.append(e)

edges = list(set(edges)) # unique elements

if (len(edges) != 8 ) : complain3


#Part.show(box)


# FILLET EDGES
cube = cube.makeFillet(cubeFillet, edges)

#Part.show(cube )

############# [rotate and] translate to position
  
#cube.rotate(ORIGIN,                  # center of rotation
#               FreeCAD.Vector(0, 1, 0), # axis   of rotation
#	       -90.0)                    # angle  of rotation

# note rotation does not change corner which determines Placement.Base

cubes = []
for L in range(0, cubeNumberLong):
   for W in range(0, cubeNumberWide):
      z = cube.copy()
      z.translate(ORIGIN + FreeCAD.Vector(
                      moldWall + (L+1) * dividerThickness + L * cubeLength, 
                      moldWall + (W+1) * dividerThickness + W * cubeWidth, 
                      moldBottomThickness))
      cubes.append(z)


if (len(cubes) != cubeNumberLong * cubeNumberWide ) : complain4

#######################################
######## final
#######################################

#box = box.fuse([cube])
box = box.fuse(cubes)

# Part.show(box)


#######################################
#####  Mesh
#######################################

# export stl for slicing.

docName = 'moldForSilicone'
doc = FreeCAD.newDocument(docName) 
App.setActiveDocument(docName)


meshBox = doc.addObject("Mesh::Feature","MeshBox")
meshBox.Mesh = MeshPart.meshFromShape(Shape=box, 
	   LinearDeflection=0.1, AngularDeflection=0.523599, Relative=False)
meshBox.Label= "moldForSilicone  (Meshed)"
meshBox.ViewObject.CreaseAngle=25.0
Mesh.export([meshBox], "./" + "moldForSilicone.stl")


#######################################
#####  tray dimensions
#######################################

print("tray length (inches)", (moldLength - 2* moldWall)/ 25.4)

print("tray width (inches)", (moldWidth - 2* moldWall)/ 25.4)

