#!/usr/bin/env python3.5

cmfsGraphsRDD = 0

def loaCmfsGraphsRDD(sc, path, storageLevel = None):
    global cmfsGraphsRDD
    cmfsGraphsRDD = sc.sequenceFile(path)
    if(storageLevel != None):
        cmfsGraphsRDD.persist(storageLevel)

def filterCMF(filterFunction):
    if(cmfsGraphsRDD == 0):
        print("You have to load the cmfs and graphs before to start the filtering process")
        print("Use  loadCmfsGraphsRDD(sparkContext, path, storageLevel) ")
        return
    return cmfsGraphsRDD.filter(lambda x: filterFunction( eval(x[0]), eval(x[1]) ) )


