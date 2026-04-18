# Source: https://openreview.net/forum?id=tO3ASKZlok

TurboQuant: Online Vector Quantization with Near-optimal Distortion Rate | OpenReview

[![back arrow](/images/arrow_left.svg)Go to **ICLR 2026 Conference** homepage](/group?id=ICLR.cc/2026/Conference "Venue Homepage")

## TurboQuant: Online Vector Quantization with Near-optimal Distortion Rate

[![Download PDF](/images/pdf_icon_blue.svg)](/pdf?id=tO3ASKZlok "Download PDF")

### [Amir Zandieh](/profile?id=~Amir_Zandieh2 "~Amir_Zandieh2"), [Majid Daliri](/profile?id=~Majid_Daliri1 "~Majid_Daliri1"), [Majid Hadian](/profile?id=~Majid_Hadian1 "~Majid_Hadian1"), [Vahab Mirrokni](/profile?id=~Vahab_Mirrokni2 "~Vahab_Mirrokni2")

Published: 26 Jan 2026, Last Modified: 02 Mar 2026ICLR 2026 PosterEveryone[Revisions](/revisions?id=tO3ASKZlok)[BibTeX](#)[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/ "Licensed under Creative Commons Attribution 4.0 International")

**Keywords:** Vector Quantization, KV Cache Compression, Nearest Neighbor Search, Similarity Search Acceleration, Online Compression Algorithms

**Abstract:** Vector quantization, a problem rooted in Shannon's source coding theory, aims to quantize high-dimensional Euclidean vectors while minimizing distortion in their geometric structure. We propose TurboQuant to address both mean-squared error (MSE) and inner product distortion, overcoming limitations of existing methods that fail to achieve optimal distortion rates. Our data-oblivious algorithms, suitable for online applications, achieve near-optimal distortion rates (within a small constant factor) across all bit-widths and dimensions. TurboQuant achieves this by randomly rotating input vectors, inducing a concentrated Beta distribution on coordinates, and leveraging the near-independence property of distinct coordinates in high dimensions to simply apply optimal scalar quantizers per each coordinate. Recognizing that MSE-optimal quantizers introduce bias in inner product estimation, we propose a two-stage approach: applying an MSE quantizer followed by a 1-bit Quantized JL (QJL) transform on the residual, resulting in an unbiased inner product quantizer. We also provide a formal proof of the information-theoretic lower bounds on best achievable distortion rate by any vector quantizer, demonstrating that TurboQuant closely matches these bounds, differing only by a small constant ($\approx 2.7$) factor. Experimental results validate our theoretical findings, showing that for KV cache quantization, we achieve absolute quality neutrality with 3.5 bits per channel and marginal quality degradation with 2.5 bits per channel. Furthermore, in nearest neighbor search tasks, our method outperforms existing product quantization techniques in recall while reducing indexing time to virtually zero.

**Supplementary Material:**  [zip](/attachment?id=tO3ASKZlok&name=supplementary_material "Download Supplementary Material")

**Primary Area:** optimization

**Submission Number:** 16479

Loading

[OpenReview](/about) is a long-term project to advance science through improved peer review with legal nonprofit status. We gratefully acknowledge the support of the [OpenReview Sponsors](/sponsors). © 2026 OpenReview
