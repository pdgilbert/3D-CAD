import Part, Mesh, MeshPart
#import math
from FreeCAD import Vector

#https://www.freecadweb.org/wiki/Part_API
#https://www.freecadweb.org/wiki/TopoShape_API
#https://www.freecadweb.org/wiki/Topological_data_scripting#Rotating_a_shape
# for transformation matrix need
# from FreeCAD import Base
# import math

def makeSTL(shp,  f) :
   ''' 
   Generate an STL mesh file. shp is a shape object and 
   f is a string that will be appended with .stl for a file name.
   ''' 
   
   FreeCAD.Console.PrintMessage('generating stl file.\n')

   m = MeshPart.meshFromShape(Shape=shp, 
          LinearDeflection=0.1, AngularDeflection=0.523599, Relative=False)
   
   #mesh.ViewObject.CreaseAngle=25.0

   #Mesh.export([m], "./BT-" + f + ".stl")
   Mesh.export([m],  f + ".stl")
   m.write(Filename = f + ".stl")
   return None


def roundedEdge(r, w, lip, h, place=None, rot=None ):
   ''' 
   Generate edge 1/4 round outside, ellipse inside
   r  outside radius
   w  wall thickness (flat wall of case)
   lip  width of lip (where glands join)
   h  length (height)
   place  placement
   rot    [rotation axis, degrees]
   The default (no placement or rot) will be at (0,0,0) and along x axis 
   with curve as for bottom, that is,  rounded in the negative y direction.
   Place and rot are applied to the default, rot first.
   e.g.
   b = roundedEdge(6, 2, length, Vector(-10,-4,-8), [Vector(0,1,0), 90])
   ''' 
   # Part.Ellipse(S1,S2,Center)  Creates an ellipse centered on the point Center,
   #  where the plane of the ellipse is defined by Center, S1 and S2, its major 
   #  axis is defined by Center and S1, its major radius is the distance 
   #  between Center and S1, and its minor radius is the distance between S2 and 
   #  the major axis. 

   # this would not need to be rotated, but s2 does not work the way I think
   #c  = Vector(0.0, 0.0, r)
   #s1 = Vector(0.0, 0.0, r-w)
   #s2 = Vector(0.0, r-lip, r)
   #e = Part.Ellipse(s1, s2, c).toShape()

   e = Part.Ellipse(Vector(0,0,0), r-w, r-lip).toShape()
   e.rotate(Vector(0,0,0),  Vector(1,0,0), 90)
   e.rotate(Vector(0,0,0),  Vector(0,0,1), -90)
   wi = Part.Wire(e)
   # wi.isClosed()
   d = Part.Face(wi)
   dd = d.extrude(Vector(h,0,0)) #in X direction then rotate below after cut
   #Part.show(dd) 
   b = Part.makeCylinder(r, h, Vector(0,0,0), Vector(1,0,0), 90)
   #b = b.cut(Part.makeCylinder(r-w, h, Vector(0,0,0), Vector(1,0,0), 90))
   b = b.cut(dd)

   b.rotate(Vector(0,0,0),  Vector(1,0,0), 90)
   b.translate(Vector(0,0,r)) #otherwise it is below 0 from rotation
 
   if  rot  is not None: b.rotate(Vector(0,0,0), rot[0], rot[1])
   if place is not None: b.translate(place)
   
   if b is None: print('warning, b is None before return.')
   return(b)

#z = roundedEdge(edgeRadius, wall, lip, length)
#Part.show(z)

def roundedCorner(r, w, lip, place=None, rot=None ):
   ''' 
   Generate  corner 1/4 round outside, ellipse inside
   r  outside radius
   w  wall thickness
   place  placement
   rot    [rotation axis, degrees]
   The default (no placement or rot) will be at (0,0,0) and along x axis 
   with curve as for bottom, that is,  rounded in the negative x and y direction.
   Place and rot are applied to the default, rot first.
   e.g.
   b = roundedCorner(6, 2, 8, Vector(-10,-4,-8), [Vector(0,1,0), 90])
   ''' 
   Z = Vector(0.0, 0.0, 1.0)
   
   c  = Vector(0.0,   0.0,   0.0 )
   s1 = Vector(0.0,   0.0,   w-r )
   s2 = Vector(0.0,  r-lip,  0.0 )

   # without Part.Face() next gives shell
   cut = Part.Face(Part.makePolygon( [c, s1, s2, c] )).revolve(c, Z, 360)
 
   #Part.show(cut)
  
   #e = Part.Ellipse(Vector(0,0,0), r-w, r-lip).toShape()
   #Part.show(e)
   #wi = Part.Wire(e)
   # wi.isClosed()
   #dw = wi.revolve(Vector(0.0, 0.0, 0.0), Vector(1.0, 0.0, 0.0), 180) 
   #Part.show(dw) 
   #d = Part.Face(wi)
   #dd = d.revolve(Vector(0.0, 0.0, 0.0), Vector(1.0, 0.0, 0.0), 180) 
   #Part.show(dd) 
   #e.rotate(Vector(0,0,0),  Vector(0,0,1), 90)
   #e.rotate(Vector(0,0,0),  Vector(1,0,0), 90)

   b = Part.makeSphere(r, Vector(0,0,0), Vector(-1,0,0), 0, 90, 90).cut(cut)
   #Part.show(b) 

   b.translate(Vector(0,0,r)) #otherwise it is below 0 from rotation
   
   if  rot  is not None: b.rotate(Vector(0,0,0), rot[0], rot[1])   
   if place is not None: b.translate(place)
   
   if b is None: print('warning, b is None before return.')
   return(b)


def copyAt(b, place, rot=None):
   ''' 
   make a copy of b at 
   place  placement
   rot  [axis, angle]  rotation
   e.g.
   b1 = copyAt(b, Vector(-10,-4,-8), [Vector(0,1,0), 90])   
   b2 = copyAt(b, Vector(20,20,20) )
   ''' 
   b2 = b.copy()
   b2.Placement.Base = place
   if rot is not None: b2.rotate(Vector(0,0,0), rot[0], rot[1])
   return(b2)


def glandGroove(a, c, tongueDepth = 2.0, sealDia = 3.0, clr = 0.4  ):
   ''' 
   Generate gland groove. Corners a and d define the outer size, 
   and a gives placement. The z coordinate of a and d should be surface
   height, from which the gland will be cut into lip.
   Clearance clr is added to both sides of groove so the same a and d 
   can be used to define both the tongue and the groove, that is, the 
   groove is wider than given by a and d by 2 * clr and placement a is
   adjusted closer to origin by clr.
   
   gland width  (3.6 is 20% larger than 3.0 seal dia.)
   ''' 
   Z = Vector(0, 0, 1) # dr for boxes
   glandWidth  = 1.2 * sealDia
   glandDepth  = tongueDepth + 0.75 * sealDia
   glandCornerRadius_inside  = 4.1  #5.0   
   glandCornerRadius_outside = 8.5 
   
   # Length in  X direction, width in Y direction
   l = c[0] - a[0]
   w = c[1] - a[1]
   
   # fillet all gland corners (verticle edges so x and y coordinates of 
   #    end points are equal)
   
   g_out = Part.makeBox( l + 2*clr, w + 2*clr, glandDepth, 
               a - Vector(clr, clr, glandDepth), Z )
   edgesCo=[]
   for e in g_out.Edges :
      if e.Vertexes[0].Point[0] ==  e.Vertexes[1].Point[0] and \
         e.Vertexes[0].Point[1] ==  e.Vertexes[1].Point[1] : edgesCo.append(e)
   
   g_out  =  g_out.makeFillet(glandCornerRadius_outside,  list(set(edgesCo)))
   
   
   g_in = Part.makeBox( l - 2 * (clr + glandWidth),
                        w - 2 * (clr + glandWidth), glandDepth, 
                 a + Vector(clr + glandWidth, clr + glandWidth, -glandDepth), Z )
   
   edgesCi=[]
   for e in g_in.Edges :
      if e.Vertexes[0].Point[0] ==  e.Vertexes[1].Point[0] and \
         e.Vertexes[0].Point[1] ==  e.Vertexes[1].Point[1] : edgesCi.append(e)

   g_in =  g_in.makeFillet(glandCornerRadius_inside,  list(set(edgesCi)))
   
   g = g_out.cut(g_in)
   #Part.show(g)
   
   # fillet gland bottom edges (both edge ends at height a[2] - glandDepth)
   h = a[2] - glandDepth
   edgesB=[]
   for e in g.Edges :
      if (e.Vertexes[0].Point[2] == h ) and \
         (e.Vertexes[1].Point[2] == h ) : edgesB.append(e)

   edgesB = list(set(edgesB)) # unique elements
   
   g = g.makeFillet(sealDia/2, edgesB) # radius = seal  dia/2 =3/2 
   
   return(g)


######## parameters ########

Z = Vector(0,0,1)

place = Vector(0,0,0)

# length and width are flat part. Curved edge is added on all sides
# so for overall dimensions add 2*edgeRadius
length =  180  # 220  
width  = 150

# 2* edgeRadius - 2* wall is thickness available inside
edgeRadius = 9  #10.0
wall = 1.5  #2.0
lip  = 8.0

LCDlip    = wall - 0.05  # needs to be less than wall for chamfer
LCDlength = 170 
LCDwidth  = 110 
LCDplace  = Vector(length - 5 - LCDlength , width - 5 - LCDwidth, 0)

######## quarter round edges ########

top=Part.makeBox(length, width, wall, place )

# remove LCD opening

# It should be possible to taper the LCD opening (to be smaller on the outside)
# either by generating a wedge or by creating a shape with polygon from vertexes
# (to edges to shell to shape) but I have not figured out those ways,
# so am using chamfer.

# lcdi = Part.makePlane(LCDlength, LCDwidth)
# lcdi.translate(Vector(0,0,wall))
# lcdo = Part.makePlane(LCDlength - 2 * LCDlip, LCDwidth - 2 * LCDlip)
# # Part.show(lcdcut)
# lcdcut = Part.Compound([lcdi, lcdo])
# lcdcut = Part.Shape([lcdi.Edges, lcdo.Edges])
# lcdcut = Part.Shell(lcdcut)
# lcdcut = Part.Solid(lcdcut)
# # Part.show(lcdcut)

# wire = Part.makePolygon([Vector(0,5,0), Vector(0,0,0), Vector(5,0,0),Vector(0,5,0)])

# wire = Part.makePolygon([Vector(0,5,0), Vector(0,0,0), Vector(5,0,0),Vector(0,5,0),
#   Vector(0,5,2), Vector(0,0,2), Vector(5,0,2),Vector(0,5,2)])
# Part.show(wire)
# print( wire.isClosed() )

# makeWedge(xmin, ymin, zmin, z2min, x2min, xmax, ymax, zmax, z2max, x2max,[pnt,dir])
# lcdcut = Part.makeWedge(0,0,0, 10,10, 5,5,5, 20,20)
# lcdcut = Part.makeWedge(0,0,0, 0,0, 5,5,5, 5,5) # cube
# lcdcut.rotate(Vector(2.5,2.5,0), Vector(1,0,0), -90)
# lcdcut.Base.Placement(Base.Vector(0.0,0.0,0.0),Base.Rotation(0.0,0.0,0.0,1.0))

# Chamfer edges of *part being removed* to hold  panel.
# These are the edge with ends all at zero height. The result will be that
# the outside (bottom in layout) is smaller since the fillet
# makes the part removed smaller at the bottom.

lcdcut = Part.makeBox(LCDlength, LCDwidth, wall, place + LCDplace)
edges=[]
for e in lcdcut.Edges :
   if (e.Vertexes[0].Point[2] == 0.0 ) and \
      (e.Vertexes[1].Point[2] == 0.0 ) : edges.append(e)

lcdcut = lcdcut.makeChamfer(LCDlip, edges)

top=top.cut(lcdcut)

# Part.show(top)

######## add round corners and edges ########
# corners a-b-c-d clockwise from origin

a = roundedCorner(edgeRadius, wall, lip)
b = roundedCorner(edgeRadius, wall, lip, Vector(  0,   width,0), [Z, -90])
c = roundedCorner(edgeRadius, wall, lip, Vector(length,width,0), [Z, 180])
d = roundedCorner(edgeRadius, wall, lip, Vector(length,  0,  0), [Z,  90])
# Part.show(d)

# edges join corners

ab = roundedEdge(edgeRadius, wall, lip, width,  Vector(  0,   width,0), [Z, -90])
bc = roundedEdge(edgeRadius, wall, lip, length, Vector(length,width,0), [Z, 180])
cd = roundedEdge(edgeRadius, wall, lip, width,  Vector(length,  0,  0), [Z,  90])
da = roundedEdge(edgeRadius, wall, lip, length)
#Part.show(da)

top = top.fuse([a, b, c, d, ab, bc, cd, da])

# Part.show(top)

# The overall length of the top is length + 2*edgeRadius
# Put the outside edge of groove in 2, so its length is length + 2*edgeRadius -4

g_inset = Vector(2 - edgeRadius, 2 - edgeRadius, edgeRadius)
gland = glandGroove(g_inset,  g_inset + 
                  Vector(length + 2*edgeRadius - 4, width + 2*edgeRadius - 4, 0), 
                  tongueDepth = 2.0, sealDia = 3.0, clr = 0.4  )
# Part.show(gland)

top = top.cut(gland)

Part.show(top)

makeSTL(top,  "RCpad")

