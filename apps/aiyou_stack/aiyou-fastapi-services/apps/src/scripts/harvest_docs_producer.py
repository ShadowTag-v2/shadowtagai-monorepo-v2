import argparse
import json
import logging
import sys
import time

from kafka import KafkaProducer
from kafka.errors import KafkaError, RequestTimedOutError


# Configure JSON Logging
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)


logger = logging.getLogger("HarvestDocsProducer")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def create_producer(bootstrap_servers: str) -> KafkaProducer | None:
    try:
        producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            retries=5,
            request_timeout_ms=5000,
        )
        logger.info(f"Connected to Kafka at {bootstrap_servers}")
        return producer
    except Exception as e:
        logger.error(f"Failed to create Kafka producer: {e}")
        return None


def produce_documents(producer: KafkaProducer, topic: str, batch_size: int, limit: int):
    count = 0
    while limit == -1 or count < limit:
        # Mock document generation
        doc = {
            "id": f"doc-{count}",
            "content": f"Harvested content {count}",
            "timestamp": time.time(),
        }

        try:
            future = producer.send(topic, doc)
            # Block for result to catch immediate errors (optional, reduces throughput but safer for critical data)
            # future.get(timeout=10)

            logger.info(f"Sent document {doc['id']} to {topic}")
            count += 1

            if count % batch_size == 0:
                logger.info(f"Batch {count // batch_size} complete. Flushing...")
                producer.flush()

        except RequestTimedOutError:
            logger.error(f"Timeout sending document {doc['id']}")
        except KafkaError as e:
            logger.error(f"Kafka error sending document {doc['id']}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

        time.sleep(0.1)  # Simulate work


def main():
    parser = argparse.ArgumentParser(description="Harvest Docs Producer")
    parser.add_argument(
        "--bootstrap_servers",
        default="localhost:9092",
        help="Kafka bootstrap servers",
    )
    parser.add_argument("--topic", default="harvested-docs", help="Kafka topic")
    parser.add_argument("--batch_size", type=int, default=100, help="Batch size for flushing")
    parser.add_argument(
        "--limit",
        type=int,
        default=-1,
        help="Number of docs to produce (-1 for infinite)",
    )

    args = parser.parse_args()

    producer = create_producer(args.bootstrap_servers)
    if producer:
        try:
            produce_documents(producer, args.topic, args.batch_size, args.limit)
        except KeyboardInterrupt:
            logger.info("Stopping producer...")
        finally:
            producer.close()
            logger.info("Producer closed")


if __name__ == "__main__":
    main()
