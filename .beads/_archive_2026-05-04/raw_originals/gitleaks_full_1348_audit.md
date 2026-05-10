# 🛡️ Gitleaks Guardian — Audit Report

**Generated**: 2026-04-19T02:10:06Z
**Total Findings**: 1348
**BLOCK**: 731 | **WARN**: 287 | **IGNORE**: 330

---

## 🚨 BLOCK — Immediate Action Required

> [!CAUTION]
> 731 credential(s) detected in production code. Pipeline HALTED.

| # | Rule | File | Line | Secret (redacted) | Remediation |
|---|------|------|------|-------------------|-------------|
| 1 | `google-api-key` | `apps/shadowtagai/src/governance/Cor.Claude_Code_6.py` | 634 | `AIza...Y2Iw` | Review and remediate per Cor.30 R3 |
| 2 | `google-api-key` | `tools/chrome-devtools-mcp/src/tools/performance.ts` | 229 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 3 | `google-api-key` | `tools/timeline-viewer/docs/auth.js` | 18 | `AIza...j308` | Review and remediate per Cor.30 R3 |
| 4 | `google-api-key` | `.tmp.driveupload/10809195` | 76 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 5 | `google-api-key` | `.tmp.driveupload/10809210` | 76 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 6 | `google-api-key` | `.tmp.driveupload/10809832` | 426 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 7 | `google-api-key` | `.tmp.driveupload/10809832` | 427 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 8 | `google-api-key` | `.tmp.driveupload/10809832` | 428 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 9 | `google-api-key` | `.tmp.driveupload/10809832` | 478 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 10 | `google-api-key` | `.tmp.driveupload/10809832` | 479 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 11 | `google-api-key` | `.tmp.driveupload/10809832` | 480 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 12 | `google-api-key` | `.tmp.driveupload/10809832` | 481 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 13 | `google-api-key` | `.tmp.driveupload/10809832` | 531 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 14 | `google-api-key` | `.tmp.driveupload/10809832` | 532 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 15 | `google-api-key` | `.tmp.driveupload/10809832` | 533 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 16 | `google-api-key` | `.tmp.driveupload/10809832` | 534 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 17 | `google-api-key` | `.tmp.driveupload/10809832` | 584 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 18 | `google-api-key` | `.tmp.driveupload/10809832` | 585 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 19 | `google-api-key` | `.tmp.driveupload/10809832` | 586 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 20 | `google-api-key` | `.tmp.driveupload/10809832` | 587 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 21 | `google-api-key` | `.tmp.driveupload/10809828` | 1132 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 22 | `google-api-key` | `.tmp.driveupload/10809828` | 1135 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 23 | `google-api-key` | `.tmp.driveupload/10809828` | 1136 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 24 | `google-api-key` | `.tmp.driveupload/10809828` | 1137 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 25 | `google-api-key` | `.tmp.driveupload/10809828` | 1187 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 26 | `google-api-key` | `.tmp.driveupload/10809828` | 1188 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 27 | `google-api-key` | `.tmp.driveupload/10809828` | 1189 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 28 | `google-api-key` | `.tmp.driveupload/10809828` | 1190 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 29 | `google-api-key` | `.tmp.driveupload/10809828` | 1240 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 30 | `google-api-key` | `.tmp.driveupload/10809828` | 1241 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 31 | `google-api-key` | `.tmp.driveupload/10809828` | 1242 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 32 | `google-api-key` | `.tmp.driveupload/10809828` | 1243 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 33 | `google-api-key` | `.tmp.driveupload/10809828` | 1293 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 34 | `google-api-key` | `.tmp.driveupload/10809828` | 1294 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 35 | `google-api-key` | `.tmp.driveupload/10809828` | 1295 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 36 | `google-api-key` | `.tmp.driveupload/10809828` | 1296 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 37 | `google-api-key` | `.tmp.driveupload/10809828` | 1384 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 38 | `google-api-key` | `.tmp.driveupload/10809828` | 1436 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 39 | `google-api-key` | `.tmp.driveupload/10809828` | 1438 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 40 | `google-api-key` | `.tmp.driveupload/10809828` | 1439 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 41 | `google-api-key` | `.tmp.driveupload/10809828` | 1440 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 42 | `google-api-key` | `.tmp.driveupload/10809828` | 1491 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 43 | `google-api-key` | `.tmp.driveupload/10809828` | 1492 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 44 | `google-api-key` | `.tmp.driveupload/10809828` | 1493 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 45 | `google-api-key` | `.tmp.driveupload/10809828` | 1494 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 46 | `google-api-key` | `.tmp.driveupload/10809828` | 1544 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 47 | `google-api-key` | `.tmp.driveupload/10809828` | 1545 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 48 | `google-api-key` | `.tmp.driveupload/10809828` | 1546 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 49 | `google-api-key` | `.tmp.driveupload/10809828` | 1547 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 50 | `google-api-key` | `.tmp.driveupload/10809828` | 1597 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 51 | `google-api-key` | `.tmp.driveupload/10809828` | 1598 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 52 | `google-api-key` | `.tmp.driveupload/10809828` | 1599 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 53 | `google-api-key` | `.tmp.driveupload/10809828` | 1600 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 54 | `google-api-key` | `.tmp.driveupload/10809828` | 1650 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 55 | `google-api-key` | `.tmp.driveupload/10809828` | 1651 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 56 | `google-api-key` | `.tmp.driveupload/10809828` | 1652 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 57 | `google-api-key` | `.tmp.driveupload/10809828` | 1653 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 58 | `google-api-key` | `.tmp.driveupload/10809828` | 1751 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 59 | `google-api-key` | `.tmp.driveupload/10809828` | 1752 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 60 | `google-api-key` | `.tmp.driveupload/10809828` | 1753 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 61 | `google-api-key` | `.tmp.driveupload/10809828` | 1754 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 62 | `google-api-key` | `.tmp.driveupload/10809828` | 1804 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 63 | `google-api-key` | `.tmp.driveupload/10809828` | 1805 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 64 | `google-api-key` | `.tmp.driveupload/10809828` | 1806 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 65 | `google-api-key` | `.tmp.driveupload/10809828` | 1807 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 66 | `google-api-key` | `.tmp.driveupload/10809828` | 1857 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 67 | `google-api-key` | `.tmp.driveupload/10809828` | 1858 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 68 | `google-api-key` | `.tmp.driveupload/10809828` | 1859 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 69 | `google-api-key` | `.tmp.driveupload/10809828` | 1860 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 70 | `google-api-key` | `.tmp.driveupload/10809828` | 1910 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 71 | `google-api-key` | `.tmp.driveupload/10809828` | 1911 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 72 | `google-api-key` | `.tmp.driveupload/10809828` | 1912 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 73 | `google-api-key` | `.tmp.driveupload/10809828` | 1913 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 74 | `google-api-key` | `.tmp.driveupload/10809828` | 1986 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 75 | `google-api-key` | `.tmp.driveupload/10809828` | 1988 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 76 | `google-api-key` | `.tmp.driveupload/10809828` | 2004 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 77 | `google-api-key` | `.tmp.driveupload/10809828` | 2005 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 78 | `github-token` | `.tmp.driveupload/10809828` | 1706 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 79 | `github-token` | `.tmp.driveupload/10809828` | 1707 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 80 | `github-token` | `.tmp.driveupload/10809828` | 1742 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 81 | `github-token` | `.tmp.driveupload/10809828` | 1745 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 82 | `github-token` | `.tmp.driveupload/10809828` | 1745 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 83 | `github-token` | `.tmp.driveupload/10809828` | 1748 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 84 | `github-token` | `.tmp.driveupload/10809828` | 1952 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 85 | `github-token` | `.tmp.driveupload/10809828` | 1953 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 86 | `github-token` | `.tmp.driveupload/10809828` | 1994 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 87 | `github-token` | `.tmp.driveupload/10809828` | 1994 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 88 | `github-token` | `.tmp.driveupload/10809828` | 2002 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 89 | `github-token` | `.tmp.driveupload/10809828` | 2007 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 90 | `github-token` | `.tmp.driveupload/10809828` | 2008 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 91 | `github-token` | `.tmp.driveupload/10809828` | 2047 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 92 | `github-token` | `.tmp.driveupload/10809828` | 2047 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 93 | `github-token` | `.tmp.driveupload/10809828` | 2053 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 94 | `github-token` | `.tmp.driveupload/10809828` | 1994 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 95 | `github-token` | `.tmp.driveupload/10809828` | 2047 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 96 | `google-api-key` | `.tmp.driveupload/10814942` | 660 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 97 | `google-api-key` | `.tmp.driveupload/10814942` | 662 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 98 | `google-api-key` | `.tmp.driveupload/10814942` | 663 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 99 | `google-api-key` | `.tmp.driveupload/10814942` | 664 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 100 | `google-api-key` | `.tmp.driveupload/10814942` | 715 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 101 | `google-api-key` | `.tmp.driveupload/10814942` | 716 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 102 | `google-api-key` | `.tmp.driveupload/10814942` | 717 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 103 | `google-api-key` | `.tmp.driveupload/10814942` | 718 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 104 | `google-api-key` | `.tmp.driveupload/10814942` | 768 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 105 | `google-api-key` | `.tmp.driveupload/10814942` | 769 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 106 | `google-api-key` | `.tmp.driveupload/10814942` | 770 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 107 | `google-api-key` | `.tmp.driveupload/10814942` | 771 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 108 | `google-api-key` | `.tmp.driveupload/10814942` | 821 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 109 | `google-api-key` | `.tmp.driveupload/10814942` | 822 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 110 | `google-api-key` | `.tmp.driveupload/10814942` | 823 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 111 | `google-api-key` | `.tmp.driveupload/10814942` | 824 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 112 | `google-api-key` | `.tmp.driveupload/10814942` | 874 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 113 | `google-api-key` | `.tmp.driveupload/10814942` | 875 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 114 | `google-api-key` | `.tmp.driveupload/10814942` | 876 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 115 | `google-api-key` | `.tmp.driveupload/10814942` | 877 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 116 | `google-api-key` | `.tmp.driveupload/10814942` | 975 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 117 | `google-api-key` | `.tmp.driveupload/10814942` | 976 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 118 | `google-api-key` | `.tmp.driveupload/10814942` | 977 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 119 | `google-api-key` | `.tmp.driveupload/10814942` | 978 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 120 | `google-api-key` | `.tmp.driveupload/10814942` | 1028 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 121 | `google-api-key` | `.tmp.driveupload/10814942` | 1029 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 122 | `google-api-key` | `.tmp.driveupload/10814942` | 1030 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 123 | `google-api-key` | `.tmp.driveupload/10814942` | 1031 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 124 | `google-api-key` | `.tmp.driveupload/10814942` | 1081 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 125 | `google-api-key` | `.tmp.driveupload/10814942` | 1082 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 126 | `google-api-key` | `.tmp.driveupload/10814942` | 1083 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 127 | `google-api-key` | `.tmp.driveupload/10814942` | 1084 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 128 | `google-api-key` | `.tmp.driveupload/10814942` | 1134 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 129 | `google-api-key` | `.tmp.driveupload/10814942` | 1135 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 130 | `google-api-key` | `.tmp.driveupload/10814942` | 1136 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 131 | `google-api-key` | `.tmp.driveupload/10814942` | 1137 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 132 | `google-api-key` | `.tmp.driveupload/10814942` | 1210 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 133 | `google-api-key` | `.tmp.driveupload/10814942` | 1212 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 134 | `github-token` | `.tmp.driveupload/10814942` | 930 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 135 | `github-token` | `.tmp.driveupload/10814942` | 931 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 136 | `github-token` | `.tmp.driveupload/10814942` | 966 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 137 | `github-token` | `.tmp.driveupload/10814942` | 969 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 138 | `github-token` | `.tmp.driveupload/10814942` | 969 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 139 | `github-token` | `.tmp.driveupload/10814942` | 972 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 140 | `github-token` | `.tmp.driveupload/10814942` | 1176 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 141 | `github-token` | `.tmp.driveupload/10814942` | 1177 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 142 | `github-token` | `.tmp.driveupload/10814942` | 1219 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 143 | `github-token` | `.tmp.driveupload/10814942` | 1219 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 144 | `github-token` | `.tmp.driveupload/10814942` | 1227 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 145 | `github-token` | `.tmp.driveupload/10814942` | 1219 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 146 | `google-api-key` | `.tmp.driveupload/10841328` | 6 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 147 | `google-api-key` | `.tmp.driveupload/10841444` | 240 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 148 | `github-token` | `.tmp.driveupload/10896361` | 27 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 149 | `github-token` | `.tmp.driveupload/10896361` | 27 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 150 | `github-token` | `.tmp.driveupload/10896361` | 27 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 151 | `github-token` | `.tmp.driveupload/13386362` | 11 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 152 | `github-token` | `.tmp.driveupload/13386362` | 69 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 153 | `github-token` | `.tmp.driveupload/13386362` | 71 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 154 | `google-api-key` | `apps/devrel-demos/data-analytics/data-dash/test.ipynb` | 1 | `AIza...fB5U` | Review and remediate per Cor.30 R3 |
| 155 | `google-api-key` | `apps/devrel-demos/data-analytics/next25-turbocharge-ecomm/demo6_publish_and_retrieve.ipynb` | 390 | `AIza...zyy7` | Review and remediate per Cor.30 R3 |
| 156 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1887492 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 157 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1887498 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 158 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1887504 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 159 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1887510 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 160 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1887516 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 161 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1887804 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 162 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1887810 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 163 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1887816 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 164 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1887822 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 165 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1887828 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 166 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1887834 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 167 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1888122 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 168 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1888128 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 169 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1888134 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 170 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1888140 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 171 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1888146 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 172 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1888152 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 173 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1888440 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 174 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1888446 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 175 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1888452 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 176 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1888458 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 177 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1888464 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 178 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1888470 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 179 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1888758 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 180 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1888764 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 181 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1888770 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 182 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1888776 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 183 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1888782 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 184 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1888788 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 185 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1889076 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 186 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1889082 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 187 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1889088 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 188 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1889094 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 189 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1889100 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 190 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1889106 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 191 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1889394 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 192 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1889400 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 193 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1889406 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 194 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1889412 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 195 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1889418 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 196 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1889424 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 197 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1889712 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 198 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1889718 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 199 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1889724 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 200 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1889730 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 201 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1889736 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 202 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1889742 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 203 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1890030 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 204 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1890036 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 205 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1890042 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 206 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1890048 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 207 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1890054 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 208 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1890060 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 209 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1890348 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 210 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1890354 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 211 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1890360 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 212 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1890366 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 213 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1890372 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 214 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1890378 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 215 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1890666 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 216 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1890672 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 217 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1890678 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 218 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1890684 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 219 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1890690 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 220 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1890696 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 221 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1890984 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 222 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1890990 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 223 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1890996 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 224 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1891002 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 225 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1891008 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 226 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1891014 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 227 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1891302 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 228 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1891308 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 229 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1891554 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 230 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1891560 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 231 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1891566 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 232 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1891572 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 233 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1891596 | `AIza...TJrQ` | Review and remediate per Cor.30 R3 |
| 234 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1891602 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 235 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1891608 | `AIza...J8zw` | Review and remediate per Cor.30 R3 |
| 236 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1891614 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 237 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1891620 | `AIza...xxxx` | Review and remediate per Cor.30 R3 |
| 238 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1891626 | `AIza...ewQe` | Review and remediate per Cor.30 R3 |
| 239 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1891632 | `AIza...UIjA` | Review and remediate per Cor.30 R3 |
| 240 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1891638 | `AIza...UIjA` | Review and remediate per Cor.30 R3 |
| 241 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1891644 | `AIza...UIjA` | Review and remediate per Cor.30 R3 |
| 242 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1891650 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 243 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1891656 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 244 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1891662 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 245 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1891674 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 246 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1891680 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 247 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1891686 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 248 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1891692 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 249 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1891698 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 250 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1891986 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 251 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1891992 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 252 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1891998 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 253 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1892004 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 254 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1892010 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 255 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1892016 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 256 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1892304 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 257 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1892310 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 258 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1892316 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 259 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1892322 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 260 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1892328 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 261 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1892334 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 262 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1892622 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 263 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1892628 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 264 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1892874 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 265 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1892880 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 266 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1892886 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 267 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1892892 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 268 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1892916 | `AIza...TJrQ` | Review and remediate per Cor.30 R3 |
| 269 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1892922 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 270 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1892928 | `AIza...J8zw` | Review and remediate per Cor.30 R3 |
| 271 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1892934 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 272 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1892940 | `AIza...xxxx` | Review and remediate per Cor.30 R3 |
| 273 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1892946 | `AIza...ewQe` | Review and remediate per Cor.30 R3 |
| 274 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1892952 | `AIza...UIjA` | Review and remediate per Cor.30 R3 |
| 275 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1892958 | `AIza...UIjA` | Review and remediate per Cor.30 R3 |
| 276 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1892964 | `AIza...UIjA` | Review and remediate per Cor.30 R3 |
| 277 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1892970 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 278 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1892976 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 279 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1892982 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 280 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1892994 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 281 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1893000 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 282 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1893006 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 283 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1893012 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 284 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1893018 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 285 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1893306 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 286 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1893312 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 287 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1893318 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 288 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1893324 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 289 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1893330 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 290 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1893336 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 291 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1893624 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 292 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1893630 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 293 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1893636 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 294 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1893642 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 295 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1893648 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 296 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1893654 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 297 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1893942 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 298 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1893948 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 299 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1893954 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 300 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1893960 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 301 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1893966 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 302 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1893972 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 303 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894194 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 304 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894200 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 305 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894206 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 306 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894212 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 307 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894236 | `AIza...TJrQ` | Review and remediate per Cor.30 R3 |
| 308 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894242 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 309 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894248 | `AIza...J8zw` | Review and remediate per Cor.30 R3 |
| 310 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894254 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 311 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894260 | `AIza...xxxx` | Review and remediate per Cor.30 R3 |
| 312 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894266 | `AIza...ewQe` | Review and remediate per Cor.30 R3 |
| 313 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894272 | `AIza...UIjA` | Review and remediate per Cor.30 R3 |
| 314 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894278 | `AIza...UIjA` | Review and remediate per Cor.30 R3 |
| 315 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894284 | `AIza...UIjA` | Review and remediate per Cor.30 R3 |
| 316 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894290 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 317 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894296 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 318 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894302 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 319 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894314 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 320 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894320 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 321 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894326 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 322 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894332 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 323 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894338 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 324 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894626 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 325 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894632 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 326 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894638 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 327 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894644 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 328 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894650 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 329 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894656 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 330 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894944 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 331 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894950 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 332 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894956 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 333 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894962 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 334 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894968 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 335 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1894974 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 336 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895262 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 337 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895268 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 338 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895274 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 339 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895280 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 340 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895286 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 341 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895292 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 342 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895514 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 343 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895520 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 344 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895526 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 345 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895532 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 346 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895556 | `AIza...TJrQ` | Review and remediate per Cor.30 R3 |
| 347 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895562 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 348 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895568 | `AIza...J8zw` | Review and remediate per Cor.30 R3 |
| 349 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895574 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 350 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895580 | `AIza...xxxx` | Review and remediate per Cor.30 R3 |
| 351 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895586 | `AIza...ewQe` | Review and remediate per Cor.30 R3 |
| 352 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895592 | `AIza...UIjA` | Review and remediate per Cor.30 R3 |
| 353 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895598 | `AIza...UIjA` | Review and remediate per Cor.30 R3 |
| 354 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895604 | `AIza...UIjA` | Review and remediate per Cor.30 R3 |
| 355 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895610 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 356 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895616 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 357 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895622 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 358 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895634 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 359 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895640 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 360 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895646 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 361 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895652 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 362 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895658 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 363 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895946 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 364 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895952 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 365 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895958 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 366 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895964 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 367 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895970 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 368 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1895976 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 369 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896264 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 370 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896270 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 371 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896276 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 372 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896282 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 373 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896288 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 374 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896294 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 375 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896582 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 376 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896588 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 377 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896594 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 378 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896600 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 379 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896606 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 380 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896612 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 381 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896834 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 382 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896840 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 383 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896846 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 384 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896852 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 385 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896876 | `AIza...TJrQ` | Review and remediate per Cor.30 R3 |
| 386 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896882 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 387 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896888 | `AIza...J8zw` | Review and remediate per Cor.30 R3 |
| 388 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896894 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 389 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896900 | `AIza...xxxx` | Review and remediate per Cor.30 R3 |
| 390 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896906 | `AIza...ewQe` | Review and remediate per Cor.30 R3 |
| 391 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896912 | `AIza...UIjA` | Review and remediate per Cor.30 R3 |
| 392 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896918 | `AIza...UIjA` | Review and remediate per Cor.30 R3 |
| 393 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896924 | `AIza...UIjA` | Review and remediate per Cor.30 R3 |
| 394 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896930 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 395 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896936 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 396 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896942 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 397 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896954 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 398 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896960 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 399 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896966 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 400 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896972 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 401 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1896978 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 402 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1897266 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 403 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1897272 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 404 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1897278 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 405 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1897284 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 406 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1897290 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 407 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1897296 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 408 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1897584 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 409 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1897590 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 410 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1897596 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 411 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1897602 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 412 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1897608 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 413 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1897614 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 414 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1897902 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 415 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1897908 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 416 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1897914 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 417 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1897920 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 418 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1897926 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 419 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1897932 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 420 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898154 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 421 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898160 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 422 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898166 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 423 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898172 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 424 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898196 | `AIza...TJrQ` | Review and remediate per Cor.30 R3 |
| 425 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898202 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 426 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898208 | `AIza...J8zw` | Review and remediate per Cor.30 R3 |
| 427 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898214 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 428 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898220 | `AIza...xxxx` | Review and remediate per Cor.30 R3 |
| 429 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898226 | `AIza...ewQe` | Review and remediate per Cor.30 R3 |
| 430 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898232 | `AIza...UIjA` | Review and remediate per Cor.30 R3 |
| 431 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898238 | `AIza...UIjA` | Review and remediate per Cor.30 R3 |
| 432 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898244 | `AIza...UIjA` | Review and remediate per Cor.30 R3 |
| 433 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898250 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 434 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898256 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 435 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898262 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 436 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898274 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 437 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898280 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 438 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898286 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 439 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898292 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 440 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898298 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 441 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898586 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 442 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898592 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 443 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898598 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 444 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898604 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 445 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898610 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 446 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898616 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 447 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898904 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 448 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898910 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 449 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898916 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 450 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898922 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 451 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898928 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 452 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1898934 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 453 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899222 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 454 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899228 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 455 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899234 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 456 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899240 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 457 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899246 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 458 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899252 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 459 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899474 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 460 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899480 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 461 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899486 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 462 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899492 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 463 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899516 | `AIza...TJrQ` | Review and remediate per Cor.30 R3 |
| 464 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899522 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 465 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899528 | `AIza...J8zw` | Review and remediate per Cor.30 R3 |
| 466 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899534 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 467 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899540 | `AIza...xxxx` | Review and remediate per Cor.30 R3 |
| 468 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899546 | `AIza...ewQe` | Review and remediate per Cor.30 R3 |
| 469 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899552 | `AIza...UIjA` | Review and remediate per Cor.30 R3 |
| 470 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899558 | `AIza...UIjA` | Review and remediate per Cor.30 R3 |
| 471 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899564 | `AIza...UIjA` | Review and remediate per Cor.30 R3 |
| 472 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899570 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 473 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899576 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 474 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899582 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 475 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899594 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 476 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899600 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 477 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899606 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 478 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899612 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 479 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899618 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 480 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899906 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 481 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899912 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 482 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899918 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 483 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899924 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 484 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899930 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 485 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1899936 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 486 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1900224 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 487 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1900230 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 488 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1900236 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 489 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1900242 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 490 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1900248 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 491 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1900254 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 492 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1900542 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 493 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1900548 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 494 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1900554 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 495 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1900560 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 496 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1900566 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 497 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1900572 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 498 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1900794 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 499 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1900800 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 500 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1900806 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 501 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1900812 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 502 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1900836 | `AIza...TJrQ` | Review and remediate per Cor.30 R3 |
| 503 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1900842 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 504 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1900848 | `AIza...J8zw` | Review and remediate per Cor.30 R3 |
| 505 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1900854 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 506 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1900860 | `AIza...xxxx` | Review and remediate per Cor.30 R3 |
| 507 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1900866 | `AIza...ewQe` | Review and remediate per Cor.30 R3 |
| 508 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1900872 | `AIza...UIjA` | Review and remediate per Cor.30 R3 |
| 509 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1900878 | `AIza...UIjA` | Review and remediate per Cor.30 R3 |
| 510 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1900884 | `AIza...UIjA` | Review and remediate per Cor.30 R3 |
| 511 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1900890 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 512 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1900896 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 513 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1900902 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 514 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1907250 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 515 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1907256 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 516 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1907262 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 517 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1907268 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 518 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1907274 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 519 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1907280 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 520 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1907286 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 521 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1907574 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 522 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1907580 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 523 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1907586 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 524 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1907592 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 525 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1907598 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 526 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1907604 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 527 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1907892 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 528 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1907898 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 529 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1907904 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 530 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1907910 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 531 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1907916 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 532 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1907922 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 533 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1908210 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 534 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1908216 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 535 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1908222 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 536 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1908228 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 537 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1908234 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 538 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1908240 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 539 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1908462 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 540 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1908468 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 541 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1908756 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 542 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1908762 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 543 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1908768 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 544 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1908774 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 545 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1909062 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 546 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1909068 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 547 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1909074 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 548 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1909080 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 549 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1909086 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 550 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1909092 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 551 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1909098 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 552 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1909386 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 553 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1909392 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 554 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1909398 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 555 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1909404 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 556 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1909410 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 557 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1909416 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 558 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1909704 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 559 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1909710 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 560 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1909716 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 561 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1909722 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 562 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1909728 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 563 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1909734 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 564 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1910022 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 565 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1910028 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 566 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1910034 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 567 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1910040 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 568 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1910046 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 569 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1910052 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 570 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1910340 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 571 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1910346 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 572 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1910352 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 573 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1910358 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 574 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1910364 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 575 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1910370 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 576 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1910598 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 577 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1910604 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 578 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1910610 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 579 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1910616 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 580 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1910622 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 581 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1910628 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 582 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1910634 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 583 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1910640 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 584 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1910646 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 585 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1910934 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 586 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1910940 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 587 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1910946 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 588 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1910952 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 589 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1910958 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 590 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1910964 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 591 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1911252 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 592 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1911258 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 593 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1911264 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 594 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1911270 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 595 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1911276 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 596 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1911282 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 597 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1911570 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 598 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1911576 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 599 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1911582 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 600 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1911588 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 601 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1911594 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 602 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1911600 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 603 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1911822 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 604 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1911834 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 605 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1911840 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 606 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1911846 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 607 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1911852 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 608 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1911858 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 609 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1911864 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 610 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1911870 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 611 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1911876 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 612 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1911888 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 613 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1911894 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 614 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1911900 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 615 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1911906 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 616 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1911912 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 617 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1912200 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 618 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1912206 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 619 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1912212 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 620 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1912218 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 621 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1912224 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 622 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1912230 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 623 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1912518 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 624 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1912524 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 625 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1912530 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 626 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1912536 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 627 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1912542 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 628 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1912548 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 629 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1912836 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 630 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1912842 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 631 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1912848 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 632 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1912854 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 633 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1912860 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 634 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1912866 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 635 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1913088 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 636 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1913094 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 637 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1913100 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 638 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1913388 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 639 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1913394 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 640 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1913400 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 641 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1913406 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 642 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1913412 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 643 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1913418 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 644 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1913424 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 645 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1913712 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 646 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1913718 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 647 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1913724 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 648 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1913730 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 649 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1913736 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 650 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1913742 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 651 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1914030 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 652 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1914036 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 653 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1914042 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 654 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1914048 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 655 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1914054 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 656 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1914060 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 657 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1914348 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 658 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1914354 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 659 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1914360 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 660 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1914366 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 661 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1914372 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 662 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1914378 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 663 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1914666 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 664 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1914672 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 665 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1914678 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 666 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1914684 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 667 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1914690 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 668 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1914696 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 669 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1914924 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 670 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1914930 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 671 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1914936 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 672 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1914942 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 673 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1914948 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 674 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1914954 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 675 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1914960 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 676 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1914966 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 677 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1914972 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 678 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1915260 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 679 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1915266 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 680 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1915272 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 681 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1915278 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 682 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1915284 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 683 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1915290 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 684 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1915578 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 685 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1915584 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 686 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1915590 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 687 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1915596 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 688 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1915602 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 689 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1915608 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 690 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1915896 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 691 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1915902 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 692 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1915908 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 693 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1915914 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 694 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1915920 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 695 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1915926 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 696 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1916148 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 697 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1916160 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 698 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1916166 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 699 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1916172 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 700 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1916178 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 701 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1916184 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 702 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1916190 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 703 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1916196 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 704 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1916316 | `AIza...TJrQ` | Review and remediate per Cor.30 R3 |
| 705 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1916328 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 706 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1916346 | `AIza...J8zw` | Review and remediate per Cor.30 R3 |
| 707 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1916844 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 708 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1916880 | `AIza...xxxx` | Review and remediate per Cor.30 R3 |
| 709 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1917006 | `AIza...ewQe` | Review and remediate per Cor.30 R3 |
| 710 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1917012 | `AIza...UIjA` | Review and remediate per Cor.30 R3 |
| 711 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1917018 | `AIza...UIjA` | Review and remediate per Cor.30 R3 |
| 712 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1917024 | `AIza...UIjA` | Review and remediate per Cor.30 R3 |
| 713 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1917066 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 714 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1917072 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 715 | `google-api-key` | `docs/AUDIT_REPORT.json` | 1917078 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 716 | `google-api-key` | `tools/external_sdks/chrome-devtools-mcp/src/tools/performance.ts` | 229 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 717 | `google-api-key` | `apps/devrel-demos/data-analytics/data-dash/test.ipynb` | 1 | `AIza...fB5U` | Review and remediate per Cor.30 R3 |
| 718 | `google-api-key` | `apps/devrel-demos/data-analytics/next25-turbocharge-ecomm/demo6_publish_and_retrieve.ipynb` | 390 | `AIza...zyy7` | Review and remediate per Cor.30 R3 |
| 719 | `google-api-key` | `docs/ADAPTER_ONLY_HARDENING_REPORT.md` | 205 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 720 | `google-api-key` | `tools/antigravity-tools/launch.sh` | 88 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 721 | `google-api-key` | `.env` | 5 | `AIza...SOD4` | Review and remediate per Cor.30 R3 |
| 722 | `google-api-key` | `.env` | 5 | `AIza...SOD4` | Review and remediate per Cor.30 R3 |
| 723 | `google-api-key` | `biz_plan_raw.txt` | 5567 | `AIza...EEI8` | Review and remediate per Cor.30 R3 |
| 724 | `google-api-key` | `biz_plan_raw.txt` | 5567 | `AIza...P0hg` | Review and remediate per Cor.30 R3 |
| 725 | `google-api-key` | `biz_plan_raw.txt` | 5567 | `AIza...6J4o` | Review and remediate per Cor.30 R3 |
| 726 | `google-api-key` | `biz_plan_raw.txt` | 5567 | `AIza...70KY` | Review and remediate per Cor.30 R3 |
| 727 | `google-api-key` | `biz_plan_raw.txt` | 5567 | `AIza...kCVE` | Review and remediate per Cor.30 R3 |
| 728 | `google-api-key` | `biz_plan_raw.txt` | 5567 | `AIza...lO-k` | Review and remediate per Cor.30 R3 |
| 729 | `google-api-key` | `biz_plan_raw.txt` | 5567 | `AIza...SBDU` | Review and remediate per Cor.30 R3 |
| 730 | `google-api-key` | `biz_plan_raw.txt` | 5567 | `AIza...MRsE` | Review and remediate per Cor.30 R3 |
| 731 | `google-api-key` | `biz_plan_raw.txt` | 5567 | `AIza...7PmI` | Review and remediate per Cor.30 R3 |

## ⚠️ WARN — Manual Review Recommended

| # | Rule | File | Line | Reason |
|---|------|------|------|--------|
| 1 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/configs/secrets.example.yml` | 16 | Generic pattern match — manual review recommended |
| 2 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.example` | 13 | Generic pattern match — manual review recommended |
| 3 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.example` | 24 | Generic pattern match — manual review recommended |
| 4 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.example` | 26 | Generic pattern match — manual review recommended |
| 5 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 31 | Generic pattern match — manual review recommended |
| 6 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 32 | Generic pattern match — manual review recommended |
| 7 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 35 | Generic pattern match — manual review recommended |
| 8 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 38 | Generic pattern match — manual review recommended |
| 9 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 41 | Generic pattern match — manual review recommended |
| 10 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 47 | Generic pattern match — manual review recommended |
| 11 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.example` | 13 | Generic pattern match — manual review recommended |
| 12 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.example` | 24 | Generic pattern match — manual review recommended |
| 13 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.example` | 26 | Generic pattern match — manual review recommended |
| 14 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 31 | Generic pattern match — manual review recommended |
| 15 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 32 | Generic pattern match — manual review recommended |
| 16 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 35 | Generic pattern match — manual review recommended |
| 17 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 38 | Generic pattern match — manual review recommended |
| 18 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 41 | Generic pattern match — manual review recommended |
| 19 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 47 | Generic pattern match — manual review recommended |
| 20 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.example` | 13 | Generic pattern match — manual review recommended |
| 21 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.example` | 24 | Generic pattern match — manual review recommended |
| 22 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.example` | 26 | Generic pattern match — manual review recommended |
| 23 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 31 | Generic pattern match — manual review recommended |
| 24 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 32 | Generic pattern match — manual review recommended |
| 25 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 35 | Generic pattern match — manual review recommended |
| 26 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 38 | Generic pattern match — manual review recommended |
| 27 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 41 | Generic pattern match — manual review recommended |
| 28 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 47 | Generic pattern match — manual review recommended |
| 29 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/nightly_intel_pipeline/kubernetes/secret.yaml.example` | 15 | Generic pattern match — manual review recommended |
| 30 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/tests/test_config.py` | 18 | Test fixture — verify not using real credentials |
| 31 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/tests/test_config.py` | 108 | Test fixture — verify not using real credentials |
| 32 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/voice_consensus/k8s/05-secrets.yaml.template` | 22 | Generic pattern match — manual review recommended |
| 33 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/voice_consensus/k8s/05-secrets.yaml.template` | 25 | Generic pattern match — manual review recommended |
| 34 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/voice_consensus/k8s/05-secrets 2.yaml.template` | 22 | Generic pattern match — manual review recommended |
| 35 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/voice_consensus/k8s/05-secrets 2.yaml.template` | 25 | Generic pattern match — manual review recommended |
| 36 | `generic-api-key-inline` | `app/services/llm_orchestrator.py` | 23 | Generic pattern match — manual review recommended |
| 37 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/configs/secrets.example.yml` | 16 | Generic pattern match — manual review recommended |
| 38 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.example` | 13 | Generic pattern match — manual review recommended |
| 39 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.example` | 24 | Generic pattern match — manual review recommended |
| 40 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.example` | 26 | Generic pattern match — manual review recommended |
| 41 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 31 | Generic pattern match — manual review recommended |
| 42 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 32 | Generic pattern match — manual review recommended |
| 43 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 35 | Generic pattern match — manual review recommended |
| 44 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 38 | Generic pattern match — manual review recommended |
| 45 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 41 | Generic pattern match — manual review recommended |
| 46 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 47 | Generic pattern match — manual review recommended |
| 47 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 31 | Generic pattern match — manual review recommended |
| 48 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 32 | Generic pattern match — manual review recommended |
| 49 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 35 | Generic pattern match — manual review recommended |
| 50 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 38 | Generic pattern match — manual review recommended |
| 51 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 41 | Generic pattern match — manual review recommended |
| 52 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 47 | Generic pattern match — manual review recommended |
| 53 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.example` | 13 | Generic pattern match — manual review recommended |
| 54 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.example` | 24 | Generic pattern match — manual review recommended |
| 55 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.example` | 26 | Generic pattern match — manual review recommended |
| 56 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.example` | 13 | Generic pattern match — manual review recommended |
| 57 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.example` | 24 | Generic pattern match — manual review recommended |
| 58 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.example` | 26 | Generic pattern match — manual review recommended |
| 59 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 31 | Generic pattern match — manual review recommended |
| 60 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 32 | Generic pattern match — manual review recommended |
| 61 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 35 | Generic pattern match — manual review recommended |
| 62 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 38 | Generic pattern match — manual review recommended |
| 63 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 41 | Generic pattern match — manual review recommended |
| 64 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 47 | Generic pattern match — manual review recommended |
| 65 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/nightly_intel_pipeline/kubernetes/secret.yaml.example` | 15 | Generic pattern match — manual review recommended |
| 66 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/tests/test_config.py` | 18 | Test fixture — verify not using real credentials |
| 67 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/tests/test_config.py` | 108 | Test fixture — verify not using real credentials |
| 68 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/voice_consensus/k8s/05-secrets.yaml.template` | 22 | Generic pattern match — manual review recommended |
| 69 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/voice_consensus/k8s/05-secrets.yaml.template` | 25 | Generic pattern match — manual review recommended |
| 70 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/voice_consensus/k8s/05-secrets 2.yaml.template` | 22 | Generic pattern match — manual review recommended |
| 71 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/voice_consensus/k8s/05-secrets 2.yaml.template` | 25 | Generic pattern match — manual review recommended |
| 72 | `generic-api-key-inline` | `tests/test_config.py` | 19 | Test fixture — verify not using real credentials |
| 73 | `generic-api-key-inline` | `tests/test_config.py` | 118 | Test fixture — verify not using real credentials |
| 74 | `generic-api-key-inline` | `.tmp.driveupload/10805633` | 19 | Generic pattern match — manual review recommended |
| 75 | `generic-api-key-inline` | `.tmp.driveupload/10805633` | 118 | Generic pattern match — manual review recommended |
| 76 | `generic-api-key-inline` | `.tmp.driveupload/10809667` | 55 | Generic pattern match — manual review recommended |
| 77 | `generic-api-key-inline` | `.tmp.driveupload/10809667` | 57 | Generic pattern match — manual review recommended |
| 78 | `generic-api-key-inline` | `.tmp.driveupload/10810389` | 154 | Generic pattern match — manual review recommended |
| 79 | `generic-api-key-inline` | `.tmp.driveupload/10810389` | 157 | Generic pattern match — manual review recommended |
| 80 | `generic-api-key-inline` | `.tmp.driveupload/10811658` | 152 | Generic pattern match — manual review recommended |
| 81 | `generic-api-key-inline` | `.tmp.driveupload/10819911` | 62 | Generic pattern match — manual review recommended |
| 82 | `generic-api-key-inline` | `.tmp.driveupload/10819911` | 64 | Generic pattern match — manual review recommended |
| 83 | `generic-api-key-inline` | `.tmp.driveupload/10820007` | 72 | Generic pattern match — manual review recommended |
| 84 | `generic-api-key-inline` | `.tmp.driveupload/10820975` | 130 | Generic pattern match — manual review recommended |
| 85 | `generic-api-key-inline` | `.tmp.driveupload/10827360` | 22 | Generic pattern match — manual review recommended |
| 86 | `generic-api-key-inline` | `.tmp.driveupload/10809828` | 1132 | Generic pattern match — manual review recommended |
| 87 | `generic-api-key-inline` | `.tmp.driveupload/10809828` | 1438 | Generic pattern match — manual review recommended |
| 88 | `generic-api-key-inline` | `.tmp.driveupload/10809828` | 1988 | Generic pattern match — manual review recommended |
| 89 | `generic-api-key-inline` | `.tmp.driveupload/10814942` | 662 | Generic pattern match — manual review recommended |
| 90 | `generic-api-key-inline` | `.tmp.driveupload/10814942` | 1212 | Generic pattern match — manual review recommended |
| 91 | `generic-api-key-inline` | `.tmp.driveupload/10841345` | 1325 | Generic pattern match — manual review recommended |
| 92 | `generic-api-key-inline` | `.tmp.driveupload/11925881` | 20 | Generic pattern match — manual review recommended |
| 93 | `generic-api-key-inline` | `.tmp.driveupload/11928518` | 20 | Generic pattern match — manual review recommended |
| 94 | `generic-api-key-inline` | `core/sovereign_mlx/llama-cpp-turboquant/tools/server/tests/unit/test_security.py` | 7 | Test fixture — verify not using real credentials |
| 95 | `generic-api-key-inline` | `fastapi/docs_src/security/tutorial004_py310.py` | 12 | Generic pattern match — manual review recommended |
| 96 | `generic-api-key-inline` | `fastapi/docs_src/security/tutorial004_an_py310.py` | 13 | Generic pattern match — manual review recommended |
| 97 | `generic-api-key-inline` | `fastapi/docs_src/security/tutorial005_py310.py` | 16 | Generic pattern match — manual review recommended |
| 98 | `generic-api-key-inline` | `fastapi/docs_src/security/tutorial005_an_py310.py` | 17 | Generic pattern match — manual review recommended |
| 99 | `generic-api-key-inline` | `libs/autoresearch_sources/Kosmos/tests/requirements/core/test_req_logging.py` | 596 | Test fixture — verify not using real credentials |
| 100 | `generic-api-key-inline` | `fastapi/docs_src/security/tutorial004_an_py310.py` | 13 | Generic pattern match — manual review recommended |
| 101 | `generic-api-key-inline` | `fastapi/docs_src/security/tutorial005_an_py310.py` | 17 | Generic pattern match — manual review recommended |
| 102 | `generic-api-key-inline` | `fastapi/docs_src/security/tutorial004_py310.py` | 12 | Generic pattern match — manual review recommended |
| 103 | `generic-api-key-inline` | `fastapi/docs_src/security/tutorial005_py310.py` | 16 | Generic pattern match — manual review recommended |
| 104 | `generic-api-key-inline` | `libs/autoresearch_sources/Kosmos/kosmos-claude-scientific-skills/scientific-skills/perplexity-search/SKILL.md` | 43 | Documentation/example — likely placeholder |
| 105 | `generic-api-key-inline` | `libs/autoresearch_sources/Kosmos/kosmos-claude-scientific-skills/scientific-skills/perplexity-search/SKILL.md` | 265 | Documentation/example — likely placeholder |
| 106 | `generic-api-key-inline` | `libs/autoresearch_sources/Kosmos/kosmos-claude-scientific-skills/scientific-skills/perplexity-search/references/openrouter_setup.md` | 65 | Documentation/example — likely placeholder |
| 107 | `generic-api-key-inline` | `libs/autoresearch_sources/Kosmos/kosmos-claude-scientific-skills/scientific-skills/perplexity-search/references/openrouter_setup.md` | 71 | Documentation/example — likely placeholder |
| 108 | `generic-api-key-inline` | `libs/autoresearch_sources/Kosmos/kosmos-claude-scientific-skills/scientific-skills/perplexity-search/references/openrouter_setup.md` | 75 | Documentation/example — likely placeholder |
| 109 | `generic-api-key-inline` | `libs/autoresearch_sources/Kosmos/kosmos-claude-scientific-skills/scientific-skills/perplexity-search/references/openrouter_setup.md` | 81 | Documentation/example — likely placeholder |
| 110 | `generic-api-key-inline` | `libs/autoresearch_sources/Kosmos/kosmos-claude-scientific-skills/scientific-skills/perplexity-search/references/openrouter_setup.md` | 230 | Documentation/example — likely placeholder |
| 111 | `generic-api-key-inline` | `libs/autoresearch_sources/Kosmos/kosmos-claude-scientific-skills/scientific-skills/perplexity-search/references/openrouter_setup.md` | 306 | Documentation/example — likely placeholder |
| 112 | `generic-api-key-inline` | `libs/autoresearch_sources/Kosmos/kosmos-claude-scientific-skills/scientific-skills/perplexity-search/references/openrouter_setup.md` | 309 | Documentation/example — likely placeholder |
| 113 | `generic-api-key-inline` | `libs/autoresearch_sources/Kosmos/tests/requirements/core/test_req_logging.py` | 613 | Test fixture — verify not using real credentials |
| 114 | `generic-api-key-inline` | `libs/autoresearch_sources/Kosmos/tests/requirements/security/test_req_security_data.py` | 55 | Test fixture — verify not using real credentials |
| 115 | `generic-api-key-inline` | `libs/autoresearch_sources/Kosmos/tests/requirements/security/test_req_security_data.py` | 184 | Test fixture — verify not using real credentials |
| 116 | `generic-api-key-inline` | `libs/autoresearch_sources/Kosmos/tests/unit/core/test_async_llm.py` | 264 | Test fixture — verify not using real credentials |
| 117 | `generic-api-key-inline` | `app/services/llm_orchestrator.py` | 23 | Generic pattern match — manual review recommended |
| 118 | `generic-api-key-inline` | `erik-hancock-llm-memory/drive_knowledge/documents/Unlocking_the_Power_of_Auto_GPT_and_Its_Plugins___.txt` | 1606 | Generic pattern match — manual review recommended |
| 119 | `generic-api-key-inline` | `infrastructure/k8s/gemini-ingestion-cronjob.yaml` | 34 | Generic pattern match — manual review recommended |
| 120 | `generic-api-key-inline` | `infrastructure/k8s/gemini-ingestion-cronjob.yaml` | 35 | Generic pattern match — manual review recommended |
| 121 | `generic-api-key-inline` | `infrastructure/k8s/gemini-ingestion-cronjob.yaml` | 37 | Generic pattern match — manual review recommended |
| 122 | `generic-api-key-inline` | `k8s/cronjob_ingestion.yaml` | 56 | Generic pattern match — manual review recommended |
| 123 | `generic-api-key-inline` | `tests/test_config.py` | 19 | Test fixture — verify not using real credentials |
| 124 | `generic-api-key-inline` | `tests/test_config.py` | 118 | Test fixture — verify not using real credentials |
| 125 | `generic-api-key-inline` | `erik-hancock-llm-memory/drive_knowledge/documents/Nvidia_roll_up_pdf.txt` | 19272 | Generic pattern match — manual review recommended |
| 126 | `generic-api-key-inline` | `voice_consensus/PRODUCTION_DEPLOYMENT.md` | 154 | Documentation/example — likely placeholder |
| 127 | `generic-api-key-inline` | `voice_consensus/PRODUCTION_DEPLOYMENT.md` | 157 | Documentation/example — likely placeholder |
| 128 | `generic-api-key-inline` | `voice_consensus/k8s/05-secrets.yaml.template` | 22 | Generic pattern match — manual review recommended |
| 129 | `generic-api-key-inline` | `voice_consensus/k8s/05-secrets.yaml.template` | 25 | Generic pattern match — manual review recommended |
| 130 | `generic-api-key-inline` | `deployments/gemini-ingestion-layer/02-storage.yaml` | 21 | Generic pattern match — manual review recommended |
| 131 | `generic-api-key-inline` | `deployments/gemini-ingestion-layer/02-storage.yaml` | 22 | Generic pattern match — manual review recommended |
| 132 | `generic-api-key-inline` | `deployments/gemini-ingestion-layer/02-storage.yaml` | 24 | Generic pattern match — manual review recommended |
| 133 | `generic-api-key-inline` | `k8s/gemini_ingestion_cronjob.yaml` | 82 | Generic pattern match — manual review recommended |
| 134 | `generic-api-key-inline` | `k8s/cronjob.yaml` | 58 | Generic pattern match — manual review recommended |
| 135 | `generic-api-key-inline` | `k8s/cronjob.yaml` | 62 | Generic pattern match — manual review recommended |
| 136 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/QUICK_START.md` | 30 | Documentation/example — likely placeholder |
| 137 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/UNIFIED_INTEGRATION_SUMMARY.md` | 558 | Documentation/example — likely placeholder |
| 138 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/app/services/llm_orchestrator.py` | 26 | Generic pattern match — manual review recommended |
| 139 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/apps/deployment/kubernetes/secrets-template.yaml` | 7 | Generic pattern match — manual review recommended |
| 140 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/configs/secrets.example.yml` | 16 | Generic pattern match — manual review recommended |
| 141 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/configs/secrets.example.yml` | 45 | Generic pattern match — manual review recommended |
| 142 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/deployment/kubernetes/secrets-template.yaml` | 7 | Generic pattern match — manual review recommended |
| 143 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/deployments/gemini-ingestion-layer/02-storage.yaml` | 21 | Generic pattern match — manual review recommended |
| 144 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/deployments/gemini-ingestion-layer/02-storage.yaml` | 22 | Generic pattern match — manual review recommended |
| 145 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/deployments/gemini-ingestion-layer/02-storage.yaml` | 24 | Generic pattern match — manual review recommended |
| 146 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/examples/sdk_example.py` | 71 | Generic pattern match — manual review recommended |
| 147 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/examples/sdk_example.py` | 80 | Generic pattern match — manual review recommended |
| 148 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/cronjob_ingestion.yaml` | 56 | Generic pattern match — manual review recommended |
| 149 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.example` | 13 | Generic pattern match — manual review recommended |
| 150 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.example` | 24 | Generic pattern match — manual review recommended |
| 151 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.example` | 26 | Generic pattern match — manual review recommended |
| 152 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 31 | Generic pattern match — manual review recommended |
| 153 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 32 | Generic pattern match — manual review recommended |
| 154 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 35 | Generic pattern match — manual review recommended |
| 155 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 38 | Generic pattern match — manual review recommended |
| 156 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 41 | Generic pattern match — manual review recommended |
| 157 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 47 | Generic pattern match — manual review recommended |
| 158 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/deployment/kubernetes/secrets-template.yaml` | 7 | Generic pattern match — manual review recommended |
| 159 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/cronjob_ingestion.yaml` | 56 | Generic pattern match — manual review recommended |
| 160 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/gemini-ingestion-cronjob.yaml` | 34 | Generic pattern match — manual review recommended |
| 161 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/gemini-ingestion-cronjob.yaml` | 35 | Generic pattern match — manual review recommended |
| 162 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/gemini-ingestion-cronjob.yaml` | 37 | Generic pattern match — manual review recommended |
| 163 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.example` | 13 | Generic pattern match — manual review recommended |
| 164 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.example` | 24 | Generic pattern match — manual review recommended |
| 165 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.example` | 26 | Generic pattern match — manual review recommended |
| 166 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 31 | Generic pattern match — manual review recommended |
| 167 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 32 | Generic pattern match — manual review recommended |
| 168 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 35 | Generic pattern match — manual review recommended |
| 169 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 38 | Generic pattern match — manual review recommended |
| 170 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 41 | Generic pattern match — manual review recommended |
| 171 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 47 | Generic pattern match — manual review recommended |
| 172 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/judge-deployment.yaml` | 416 | Generic pattern match — manual review recommended |
| 173 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/judge-deployment.yaml` | 417 | Generic pattern match — manual review recommended |
| 174 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/judge-deployment.yaml` | 418 | Generic pattern match — manual review recommended |
| 175 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/judge-deployment.yaml` | 419 | Generic pattern match — manual review recommended |
| 176 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/judge-deployment.yaml` | 420 | Generic pattern match — manual review recommended |
| 177 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/cronjob_ingestion.yaml` | 56 | Generic pattern match — manual review recommended |
| 178 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/base/gemini-ingestion-layer.yaml` | 118 | Generic pattern match — manual review recommended |
| 179 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/base/gemini-ingestion-layer.yaml` | 122 | Generic pattern match — manual review recommended |
| 180 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/base/gemini-ingestion-layer.yaml` | 123 | Generic pattern match — manual review recommended |
| 181 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/gemini_ingestion_cronjob.yaml` | 82 | Generic pattern match — manual review recommended |
| 182 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.example` | 13 | Generic pattern match — manual review recommended |
| 183 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.example` | 24 | Generic pattern match — manual review recommended |
| 184 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.example` | 26 | Generic pattern match — manual review recommended |
| 185 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 31 | Generic pattern match — manual review recommended |
| 186 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 32 | Generic pattern match — manual review recommended |
| 187 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 35 | Generic pattern match — manual review recommended |
| 188 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 38 | Generic pattern match — manual review recommended |
| 189 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 41 | Generic pattern match — manual review recommended |
| 190 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 47 | Generic pattern match — manual review recommended |
| 191 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/nightly_intel_pipeline/kubernetes/secret.yaml.example` | 15 | Generic pattern match — manual review recommended |
| 192 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/pnkln/scout/importers/airtable_import.py` | 8 | Generic pattern match — manual review recommended |
| 193 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/pnkln/scout/importers/airtable_import.py` | 227 | Generic pattern match — manual review recommended |
| 194 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/pnkln/scout/importers/notion_import.py` | 8 | Generic pattern match — manual review recommended |
| 195 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/src/pnkln/intelligence_api.py` | 512 | Generic pattern match — manual review recommended |
| 196 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/src/pnkln/intelligence_api.py` | 522 | Generic pattern match — manual review recommended |
| 197 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/tests/test_config.py` | 19 | Test fixture — verify not using real credentials |
| 198 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/tests/test_config.py` | 108 | Test fixture — verify not using real credentials |
| 199 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/voice_consensus/PRODUCTION_DEPLOYMENT.md` | 199 | Documentation/example — likely placeholder |
| 200 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/voice_consensus/PRODUCTION_DEPLOYMENT.md` | 202 | Documentation/example — likely placeholder |
| 201 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/voice_consensus/k8s/05-secrets 2.yaml.template` | 22 | Generic pattern match — manual review recommended |
| 202 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/voice_consensus/k8s/05-secrets 2.yaml.template` | 25 | Generic pattern match — manual review recommended |
| 203 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/voice_consensus/k8s/05-secrets.yaml.template` | 22 | Generic pattern match — manual review recommended |
| 204 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/voice_consensus/k8s/05-secrets.yaml.template` | 25 | Generic pattern match — manual review recommended |
| 205 | `generic-api-key-inline` | `AUTOMATION_GUIDE.md` | 121 | Documentation/example — likely placeholder |
| 206 | `generic-api-key-inline` | `configs/secrets.example.yml` | 16 | Generic pattern match — manual review recommended |
| 207 | `generic-api-key-inline` | `configs/secrets.example.yml` | 45 | Generic pattern match — manual review recommended |
| 208 | `generic-api-key-inline` | `deployment/kubernetes/secrets-template.yaml` | 7 | Generic pattern match — manual review recommended |
| 209 | `generic-api-key-inline` | `drive_knowledge/documents/Unlocking_the_Power_of_Auto_GPT_and_Its_Plugins___.txt` | 1606 | Generic pattern match — manual review recommended |
| 210 | `generic-api-key-inline` | `Cor.Claude_Code_6/QUICKSTART.md` | 20 | Documentation/example — likely placeholder |
| 211 | `generic-api-key-inline` | `Cor.Claude_Code_6/QUICKSTART.md` | 69 | Documentation/example — likely placeholder |
| 212 | `generic-api-key-inline` | `Cor.Claude_Code_6/STRIPE_SETUP.md` | 26 | Documentation/example — likely placeholder |
| 213 | `generic-api-key-inline` | `Cor.Claude_Code_6/STRIPE_SETUP.md` | 226 | Documentation/example — likely placeholder |
| 214 | `generic-api-key-inline` | `k8s/secrets.yaml.example` | 13 | Generic pattern match — manual review recommended |
| 215 | `generic-api-key-inline` | `k8s/secrets.yaml.example` | 24 | Generic pattern match — manual review recommended |
| 216 | `generic-api-key-inline` | `k8s/secrets.yaml.example` | 26 | Generic pattern match — manual review recommended |
| 217 | `generic-api-key-inline` | `kubernetes/Claude_Code_6-api-deployment.yaml` | 23 | Generic pattern match — manual review recommended |
| 218 | `generic-api-key-inline` | `drive_knowledge/documents/Nvidia_roll_up_pdf.txt` | 19272 | Generic pattern match — manual review recommended |
| 219 | `generic-api-key-inline` | `nightly_intel_pipeline/kubernetes/secret.yaml.example` | 15 | Generic pattern match — manual review recommended |
| 220 | `generic-api-key-inline` | `tools/antigravity-tools/launch.sh` | 88 | Generic pattern match — manual review recommended |
| 221 | `generic-api-key-inline` | `tests/test_config.py` | 21 | Test fixture — verify not using real credentials |
| 222 | `generic-api-key-inline` | `tests/test_config.py` | 25 | Test fixture — verify not using real credentials |
| 223 | `generic-api-key-inline` | `tests/test_config.py` | 18 | Test fixture — verify not using real credentials |
| 224 | `generic-api-key-inline` | `erik-hancock-llm-memory/drive_knowledge 2/documents/Unlocking_the_Power_of_Auto_GPT_and_Its_Plugins___.txt` | 1606 | Generic pattern match — manual review recommended |
| 225 | `generic-api-key-inline` | `erik-hancock-llm-memory/drive_knowledge 2/documents/Nvidia_roll_up_pdf.txt` | 19272 | Generic pattern match — manual review recommended |
| 226 | `generic-api-key-inline` | `voice_consensus/k8s/05-secrets 2.yaml.template` | 22 | Generic pattern match — manual review recommended |
| 227 | `generic-api-key-inline` | `voice_consensus/k8s/05-secrets 2.yaml.template` | 25 | Generic pattern match — manual review recommended |
| 228 | `generic-api-key-inline` | `app/services/llm_orchestrator.py` | 23 | Generic pattern match — manual review recommended |
| 229 | `generic-api-key-inline` | `app/services/llm_orchestrator.py` | 23 | Generic pattern match — manual review recommended |
| 230 | `generic-api-key-inline` | `app/services/llm_orchestrator.py` | 23 | Generic pattern match — manual review recommended |
| 231 | `generic-api-key-inline` | `configs/secrets.example.yml` | 16 | Generic pattern match — manual review recommended |
| 232 | `generic-api-key-inline` | `configs/secrets.example.yml` | 45 | Generic pattern match — manual review recommended |
| 233 | `generic-api-key-inline` | `erik-hancock-llm-memory/drive_knowledge/documents/Unlocking_the_Power_of_Auto_GPT_and_Its_Plugins___.txt` | 1606 | Generic pattern match — manual review recommended |
| 234 | `generic-api-key-inline` | `erik-hancock-llm-memory/drive_knowledge/documents/Nvidia_roll_up_pdf.txt` | 19272 | Generic pattern match — manual review recommended |
| 235 | `generic-api-key-inline` | `configs/secrets.example.yml` | 16 | Generic pattern match — manual review recommended |
| 236 | `generic-api-key-inline` | `configs/secrets.example.yml` | 45 | Generic pattern match — manual review recommended |
| 237 | `generic-api-key-inline` | `erik-hancock-llm-memory/drive_knowledge/documents/Unlocking_the_Power_of_Auto_GPT_and_Its_Plugins___.txt` | 1606 | Generic pattern match — manual review recommended |
| 238 | `generic-api-key-inline` | `erik-hancock-llm-memory/drive_knowledge/documents/Nvidia_roll_up_pdf.txt` | 19272 | Generic pattern match — manual review recommended |
| 239 | `generic-api-key-inline` | `k8s/cronjob_ingestion.yaml` | 56 | Generic pattern match — manual review recommended |
| 240 | `generic-api-key-inline` | `k8s/cronjob_ingestion.yaml` | 56 | Generic pattern match — manual review recommended |
| 241 | `generic-api-key-inline` | `UNIFIED_INTEGRATION_SUMMARY.md` | 558 | Documentation/example — likely placeholder |
| 242 | `generic-api-key-inline` | `voice_consensus/k8s/05-secrets.yaml.template` | 22 | Generic pattern match — manual review recommended |
| 243 | `generic-api-key-inline` | `voice_consensus/k8s/05-secrets.yaml.template` | 25 | Generic pattern match — manual review recommended |
| 244 | `generic-api-key-inline` | `voice_consensus/k8s/05-secrets.yaml.template` | 22 | Generic pattern match — manual review recommended |
| 245 | `generic-api-key-inline` | `voice_consensus/k8s/05-secrets.yaml.template` | 25 | Generic pattern match — manual review recommended |
| 246 | `generic-api-key-inline` | `voice_consensus/PRODUCTION_DEPLOYMENT.md` | 154 | Documentation/example — likely placeholder |
| 247 | `generic-api-key-inline` | `voice_consensus/PRODUCTION_DEPLOYMENT.md` | 157 | Documentation/example — likely placeholder |
| 248 | `generic-api-key-inline` | `voice_consensus/PRODUCTION_DEPLOYMENT.md` | 154 | Documentation/example — likely placeholder |
| 249 | `generic-api-key-inline` | `voice_consensus/PRODUCTION_DEPLOYMENT.md` | 157 | Documentation/example — likely placeholder |
| 250 | `generic-api-key-inline` | `tests/conftest.py` | 61 | Test fixture — verify not using real credentials |
| 251 | `generic-api-key-inline` | `tests/test_config.py` | 18 | Test fixture — verify not using real credentials |
| 252 | `generic-api-key-inline` | `tests/test_config.py` | 116 | Test fixture — verify not using real credentials |
| 253 | `generic-api-key-inline` | `tests/conftest.py` | 61 | Test fixture — verify not using real credentials |
| 254 | `generic-api-key-inline` | `tests/test_config.py` | 18 | Test fixture — verify not using real credentials |
| 255 | `generic-api-key-inline` | `tests/test_config.py` | 116 | Test fixture — verify not using real credentials |
| 256 | `generic-api-key-inline` | `configs/secrets.example.yml` | 16 | Generic pattern match — manual review recommended |
| 257 | `generic-api-key-inline` | `configs/secrets.example.yml` | 45 | Generic pattern match — manual review recommended |
| 258 | `generic-api-key-inline` | `configs/secrets.example.yml` | 16 | Generic pattern match — manual review recommended |
| 259 | `generic-api-key-inline` | `configs/secrets.example.yml` | 45 | Generic pattern match — manual review recommended |
| 260 | `generic-api-key-inline` | `k8s/secrets.yaml.template` | 31 | Generic pattern match — manual review recommended |
| 261 | `generic-api-key-inline` | `k8s/secrets.yaml.template` | 32 | Generic pattern match — manual review recommended |
| 262 | `generic-api-key-inline` | `k8s/secrets.yaml.template` | 35 | Generic pattern match — manual review recommended |
| 263 | `generic-api-key-inline` | `k8s/secrets.yaml.template` | 38 | Generic pattern match — manual review recommended |
| 264 | `generic-api-key-inline` | `k8s/secrets.yaml.template` | 41 | Generic pattern match — manual review recommended |
| 265 | `generic-api-key-inline` | `k8s/secrets.yaml.template` | 47 | Generic pattern match — manual review recommended |
| 266 | `generic-api-key-inline` | `k8s/secrets.yaml.template` | 31 | Generic pattern match — manual review recommended |
| 267 | `generic-api-key-inline` | `k8s/secrets.yaml.template` | 32 | Generic pattern match — manual review recommended |
| 268 | `generic-api-key-inline` | `k8s/secrets.yaml.template` | 35 | Generic pattern match — manual review recommended |
| 269 | `generic-api-key-inline` | `k8s/secrets.yaml.template` | 38 | Generic pattern match — manual review recommended |
| 270 | `generic-api-key-inline` | `k8s/secrets.yaml.template` | 41 | Generic pattern match — manual review recommended |
| 271 | `generic-api-key-inline` | `k8s/secrets.yaml.template` | 47 | Generic pattern match — manual review recommended |
| 272 | `generic-api-key-inline` | `k8s/secrets.yaml.example` | 13 | Generic pattern match — manual review recommended |
| 273 | `generic-api-key-inline` | `k8s/secrets.yaml.example` | 24 | Generic pattern match — manual review recommended |
| 274 | `generic-api-key-inline` | `k8s/secrets.yaml.example` | 26 | Generic pattern match — manual review recommended |
| 275 | `generic-api-key-inline` | `k8s/secrets.yaml.example` | 13 | Generic pattern match — manual review recommended |
| 276 | `generic-api-key-inline` | `k8s/secrets.yaml.example` | 24 | Generic pattern match — manual review recommended |
| 277 | `generic-api-key-inline` | `k8s/secrets.yaml.example` | 26 | Generic pattern match — manual review recommended |
| 278 | `generic-api-key-inline` | `infrastructure/k8s/gemini-ingestion-cronjob.yaml` | 34 | Generic pattern match — manual review recommended |
| 279 | `generic-api-key-inline` | `infrastructure/k8s/gemini-ingestion-cronjob.yaml` | 35 | Generic pattern match — manual review recommended |
| 280 | `generic-api-key-inline` | `infrastructure/k8s/gemini-ingestion-cronjob.yaml` | 37 | Generic pattern match — manual review recommended |
| 281 | `generic-api-key-inline` | `infrastructure/k8s/gemini-ingestion-cronjob.yaml` | 34 | Generic pattern match — manual review recommended |
| 282 | `generic-api-key-inline` | `infrastructure/k8s/gemini-ingestion-cronjob.yaml` | 35 | Generic pattern match — manual review recommended |
| 283 | `generic-api-key-inline` | `infrastructure/k8s/gemini-ingestion-cronjob.yaml` | 37 | Generic pattern match — manual review recommended |
| 284 | `generic-api-key-inline` | `nightly_intel_pipeline/kubernetes/secret.yaml.example` | 15 | Generic pattern match — manual review recommended |
| 285 | `generic-api-key-inline` | `nightly_intel_pipeline/kubernetes/secret.yaml.example` | 15 | Generic pattern match — manual review recommended |
| 286 | `generic-api-key-inline` | `deployment/kubernetes/secrets-template.yaml` | 7 | Generic pattern match — manual review recommended |
| 287 | `generic-api-key-inline` | `deployment/kubernetes/secrets-template.yaml` | 7 | Generic pattern match — manual review recommended |

## ✅ IGNORE — Auto-classified (330 findings)

These were auto-classified as false positives and added to `.gitleaksignore`.

- **Third-party path: docs/CANONICALIZATION_REPORT**: 215 findings
- **Third-party path: docs/AUDIT_REPORT\.md**: 111 findings
- **Third-party path: \.agent/reports/**: 4 findings

---

## 5-Layer Defense Status

| Layer | Component | Status |
|-------|-----------|--------|
| 1 | Pre-commit hook (`.pre-commit-config.yaml`) | ✅ Active |
| 2 | Finish Changes pipeline (`finish_changes.py`) | ✅ Blocking |
| 3 | Omega Sync gate (`omega_sync.py`) | ✅ Blocking |
| 4 | CI/CD PR gate (`security-audit.yml`) | ✅ Active |
| 5 | On-demand audit (`/gitleaks-guardian`) | ✅ This scan |

