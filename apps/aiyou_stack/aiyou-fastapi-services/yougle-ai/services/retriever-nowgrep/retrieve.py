# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

async def retrieve(query: str, k=12, mode="default"):
    # 1) dense embed
    # qv = await _embed(query)
    # 2) locality cluster + topK
    # docs = await _hnsw_topk(qv, k=k)
    # return docs
    return ["Doc 1", "Doc 2"]
