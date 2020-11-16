import json
import sys

# pyspark
from pyspark.context import SparkContext
from pyspark.sql import functions as func
from pyspark.sql.window import Window
# glue
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext

# generate spark-context
sc = SparkContext()
glue_context = GlueContext(sc)
spark = glue_context.spark_session

# set custom logging on
logger = glue_context.get_logger()


def main():
    # arguments
    args = getResolvedOptions(sys.argv, ['JOB_NAME', 'target_date', 'input_path', 'output_path'])
    target_date = json.loads(args['target_date'])
    input_path = json.loads(args['input_path'])
    output_path = json.loads(args['output_path'])

    # define `lag window`
    window = Window.partitionBy("id").orderBy("timestamp")

    # load data and add new_columns
    df = spark.read.csv(input_path, header=True) \
        .filter(func.col("dt") == target_date) \
        .withColumn("input_path", func.input_file_name()) \
        .withColumn("file_name", func.split(func.col("input_path"), "/").get_iten()) \
        .withColumn("prev_timestamp", func.lag(func.col("timestamp")).over(window))
    # export
    df.write.coalesce(1).mode("overwrite").csv(output_path, header=True)


if __name__ == "__main__":
    # ETL処理の実行
    main()
