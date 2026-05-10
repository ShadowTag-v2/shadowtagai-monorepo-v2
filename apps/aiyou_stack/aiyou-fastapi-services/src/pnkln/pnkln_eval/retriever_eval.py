import json
import statistics as stats
import sys


def recall_at_k(g, p, k):
    G = set(g)
    P = set(p[:k])
    return len(G & P) / len(G) if G else 0


def mrr_at_k(g1, p, k):
    for i, x in enumerate(p[:k], 1):
        if x == g1:
            return 1 / i
    return 0


def evaluate(path):
    R5, R10, MRR = [], [], []
    for l in open(path):  # noqa: E741, SIM115
        ex = json.loads(l)
        R5.append(recall_at_k(ex["gold"], ex["preds"], 5))
        R10.append(recall_at_k(ex["gold"], ex["preds"], 10))
        MRR.append(mrr_at_k(ex["gold"][0], ex["preds"], 10))
    return {"recall@5": stats.mean(R5), "recall@10": stats.mean(R10), "mrr@10": stats.mean(MRR)}


if __name__ == "__main__":
    print(json.dumps(evaluate(sys.argv[1]), indent=2))
