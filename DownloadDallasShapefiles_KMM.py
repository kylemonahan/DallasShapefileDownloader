## Getting started with scraping shapefiles adapted from Bryan McIntosh. Kyle Monahan

## Adapted from: https://www.spatialtimes.com/2016/09/map-service-to-shapefile-with-python-part-2-iteration/
## Map server to download, from Kai: http://www.arcgis.com/home/webmap/viewer.html?url=https://gis.dallascityhall.com/wwwgis/rest/services/Basemap/DallasTaxParcels/MapServer/0

#Name: Export ArcGIS Server Map Service Layer to Shapefile with Iterate
#Author: Bryan McIntosh
#Description: Python script that connects to an ArcGIS Server Map Service and downloads a single vector layer
#             to shapefiles. If there are more features than AGS max allowed, it will iterate to extract all features.

import urllib2,json,os,arcpy,itertools
ws = os.getcwd() + os.sep

#Set connection to ArcGIS Server, map service, layer ID, and server max requests (1000 is AGS default if not known).
serviceURL = "https://gis.dallascityhall.com/wwwgis/rest/services/" # Note how we have to pass the services component
serviceMap = "/Basemap/DallasTaxParcels/MapServer" # Note how I remove the slash
serviceLayerID = 0 # This is the slash zero at the end
serviceMaxRequest = 1000 # Most common default, we may need to request for this from the base server as TTL
dataOutputName = "MyShapefile"

def defServiceGetIDs():
    IDsRequest = serviceURL + serviceMap + "/" + str(serviceLayerID) + "/query?where=1%3D1&text=&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=&returnGeometry=true&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&outSR=&returnIdsOnly=true&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&returnDistinctValues=false&resultOffset=&resultRecordCount=&f=pjson"
    IDsResponse = urllib2.urlopen(IDsRequest)
    IDsJSON = json.loads(IDsResponse.read())
    IDsSorted = sorted(IDsJSON['objectIds'])
    return IDsSorted

def defGroupList(n, iterable):
    args = [iter(iterable)] * n
    return ([e for e in t if e != None] for t in itertools.izip_longest(*args))
    
def defQueryExtractRequests(idMin, idMax):
    myQuery = "&where=objectid+>%3D+" + idMin + "+and+objectid+<%3D+" + idMax
    myParams = "query?geometryType=esriGeometryEnvelope&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=*&returnGeometry=true&geometryPrecision=&outSR=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&returnZ=false&returnM=false&returnDistinctValues=false&returnTrueCurves=false&f=pjson"
    myRequest = serviceURL + serviceMap + "/" + str(serviceLayerID) + "/" + myParams + myQuery
    response = urllib2.urlopen(myRequest)
    myJSON = response.read()
    # Write response to json text file
    foo = open(dataOutputName + idMin + ".json", "w+")
    foo.write(myJSON);
    foo.close()
    # Create Feature Class
    arcpy.JSONToFeatures_conversion(dataOutputName + idMin + ".json", ws + dataOutputName + idMin + ".shp")
    
#**MAIN**#
#Get all objectIDs (OIDs) for the layer (there is no server limit for this request)
AllObjectIDs = defServiceGetIDs()
#Divide the OIDs into chunks since there is a limit to map queries (assumed limit stored in serviceMaxRequest variable)
ObjectID_Groups = list(defGroupList(serviceMaxRequest, AllObjectIDs))
#Create a shapefile for each chunk
for ObjectID_Group in ObjectID_Groups:
    idMin = str(ObjectID_Group[0])
    idMax = str(ObjectID_Group[-1])
    defQueryExtractRequests(idMin, idMax)
#Append all shapefiles if desired