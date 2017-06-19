# CMFGenerator

Generator of combinatorial multivector fields on 2d cubical complexes on a cubical complex


# Usage

The project is thought to be used with the pyspark interactive console.
Once imported the project files, it is possible to start the generator with

    generateCMF( sc, n, m, monoProcLimit, confPerProc, monop )
    
    - sc is the spark context. In pyspark, the variable is exactly   'sc'
    - n,m represent the size of the cubical complex
    - monoProcLimit, how many cells a single core has to analyse before start the parallel computation? [default = 1]
    - confPerProc, useful for debugging, it sets a limit on the structures generated per process [default = -1, no limit]
    - monop, useful for debugging, if it is True just one core will be used for the computation [dafault = True]
    
 In the case we want to save the configurations on file, the format returned by the generation function can be saved as sequence file:
 
     configurationsRDD = generateCMF(sc, n, m)
     configurationsRDD.saveAsSequenceFile(path [, "org.apache.hadoop.io.compress.BZip2Codec"])
 
 The format of the cmfs will be (None, str(cmf)). We have to convert the array in string otherwise we can not save it as sequence file, without modify spark source. 
 
 To load them again:
 
     configurationsRDD = sc.sequenceFile(path)
     
# Configuration

  ## Import the files
  To use the instruction 'import genCMF' on the interactive console we need to move all the project files in the directory of   python lib used by spark  (es. /usr/lib/pythonX.X/).
  Alternatively we can add file directly from the console:
  
      sc.addFile("/[AbsolutePathTo]/xxx.py")  # sc, spark context
      import xxx.py
      
  ## Set spark variable
  So far, two variable could cause problems during the generation process. They have to be set in a proper way to prevent exception.
  To set these variables in a 'permanent' way, we need to edit the spark conf file spark-defaults.conf ( $SPARK_HOME/conf/ ) adding these two lines:
  
      spark.driver.memory 1g      # The process can require lot of memory
      spark.network.timeout 600s  # The computation require time on every single worker
      
  To set these variables directly from the console we can use:
    
      sc.getConf().set("spark.driver.memory", "1g")
      
  The values of these variables need to be set with respect of the computation size
