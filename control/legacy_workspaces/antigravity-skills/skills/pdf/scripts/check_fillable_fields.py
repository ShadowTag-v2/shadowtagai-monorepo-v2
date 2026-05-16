# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import sys
from pypdf import PdfReader


reader = PdfReader(sys.argv[1])
if reader.get_fields():
  print("This PDF has fillable form fields")
else:
  print(
    "This PDF does not have fillable form fields; you will need to visually determine where to enter data"
  )
