
#import the required pacakages:
from pyspark.sql import SparkSession
from pyspark.sql import Row
from pyspark.sql import functions

#function creation for applying scheema
def parseInput(line):
    fields = line.split('|')
    return Row(user_id = int(fields[0]), age = int(fields[1]), gender = fields[2], occupation = fields[3], zip = fields[4])

if __name__ == "__main__":
    # Create a SparkSession
    spark = SparkSession.\
    builder.appName("MongoDBIntegration").\
    getOrCreate()

    # Build RDD on top of emp data file
    lines = spark.sparkContext.textFile("hdfs:///user/maria_dev/employee.txt")
    
    # Creating new RDD by passing the parser fuction
    users = lines.map(parseInput)
    
    # Convert RDD into a DataFrame
    usersDataset = spark.createDataFrame(users)

    # Write the data into MongoDB(emp is the database name and data is the table/collection)
    usersDataset.write\
        .format("com.mongodb.spark.sql.DefaultSource")\
        .option("uri","mongodb://127.0.0.1/emp.data")\
        .mode('append')\
        .save()

    # Read it back from MongoDB into a new Dataframe(temp view)(emp is the database name and data is the table/collection
    readUsers = spark.read\
    .format("com.mongodb.spark.sql.DefaultSource")\
    .option("uri","mongodb://127.0.0.1/emp.data")\
    .load()

    #create SQL view 
    readUsers.createOrReplaceTempView("data")
    sqlDF = spark.sql("SELECT * FROM data LIMIT 10")
    sqlDF.show()
  

    # Stop the SparkSession
    spark.stop()
