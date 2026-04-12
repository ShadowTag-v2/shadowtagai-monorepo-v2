#!/usr/bin/env python3
import logging

logging.basicConfig(level=logging.INFO)


def evaluate_rag():
    target_precision = 0.94
    measured = 0.92
    if measured < target_precision:
        logging.error("RAG limits failed. Vector index blocked.")
    else:
        logging.info("Intersection over union golden. RAG clear.")


if __name__ == "__main__":
    evaluate_rag()
