"""Optional distributed-scale analogue; pip install pyspark and configure Java first."""
import argparse

def run(source,destination):
    from pyspark.sql import SparkSession,functions as F,types as T
    spark=SparkSession.builder.appName('EpiScopeSentinel-SimulatedSentinelETL').getOrCreate()
    schema=T.StructType([T.StructField('week_start',T.StringType()),T.StructField('district',T.StringType()),
                         T.StructField('syndrome',T.StringType()),T.StructField('cases',T.IntegerType()),
                         T.StructField('visits',T.IntegerType()),T.StructField('source',T.StringType())])
    data=spark.read.option('header',True).schema(schema).csv(source)
    filtered=data.filter((F.col('cases')>=0)&(F.col('visits')>=F.col('cases')) &
                         (F.col('source')=='SIMULATED_SENTINEL'))
    grouped=filtered.groupBy('week_start','syndrome').agg(F.sum('cases').alias('cases'),F.sum('visits').alias('visits'))
    grouped.write.mode('overwrite').partitionBy('syndrome').parquet(destination)
    spark.stop()
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',default='data/weekly_synthetic.csv')
    p.add_argument('--output',default='data/spark_output');a=p.parse_args();run(a.input,a.output)
