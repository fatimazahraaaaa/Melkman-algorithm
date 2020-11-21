from arcpy import *


def inserepolygon(path,L): #This function create the convex polygon on new llayer from a list L of points that form this polygon.
	CreateFeatureclass_management(env.workspace,Describe(path).name,"Polygon")
	with da.InsertCursor(Describe(path).name,["shape@"]) as cursor:
		cursor.insertRow([Polygon(L)])


def isleft(A,B,C):  #This function returns 1 if C is in the left of the line AB, 0 if it is in the right, and 0 if they are colinear.
	det=(B.X-A.X)*(C.Y-A.Y)-(B.Y-A.Y)*(C.X-A.X)
	if det>0:
		return 1
	elif det<0 :
		return 0
	else:
		return -1


from operator import attrgetter
#This operator allows to sort the list of points as objects.

def ConvexHullMelkman(path):
	R=Array()
	C=Array()
	if (Describe(path).shapeType=="Polyline") or (Describe(path).shapeType=="Polygon"): # if feature class is a polyline or polygon, the processus is a little different than if we have points
		with da.SearchCursor(path,["Shape@"]) as cursor :
			for row in cursor:
				for part in row[0]:
					for pt in part:
						R.append(pt)
	        C=sorted(R,key=attrgetter("Y"),reverse=True)
	if Describe(path).featureType=="Point":
		with da.SearchCursor(path,["Shape@XY"]) as cursor :
			for row in cursor:
				R.append(Point(row[0][0],row[0][1])) #Get points from the layer
	        C=sorted(R,key=attrgetter("Y"),reverse=True) #Sort the points based on Y (from the top to the bottom)
	#initialization of the list that will contain points forming the convex polygon
	if isleft(C[0],C[1],C[2]):
		D=Array([C[2],C[0],C[1],C[2]])
	else :
		D=Array([C[2],C[1],C[0],C[2]])
	for i in range(3,len(C)):
		if isleft(D[-2],D[-1],C[i])==1 and isleft(D[0],D[1],C[i])==1: #This means that we neglect points which are already inside the polygon
			continue
		while  isleft(D[0],D[1],C[i])<=0: #add points which are outside the polygon
			D.remove(0)
		D.insert(0,C[i])
		while isleft(D[-2],D[-1],C[i])<=0: #add points which are outside the polygon
			D.remove(len(D)-1)
		D.append(C[i])
	inserepolygon(path,D)
