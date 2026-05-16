# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import re

content = open("apps/shadowtag-web/app/pitch/page.tsx").read()

# Fix Line 12
content = content.replace(
  'min-h-screen flex flex-col justify-${align} px-8 md:px-24 border-b snap-start" style={{ borderBottomColor: "rgba(234,179,8,0.2)" }} relative overflow-hidden`}',
  'min-h-screen flex flex-col justify-${align} px-8 md:px-24 border-b snap-start relative overflow-hidden`} style={{ borderBottomColor: "rgba(234,179,8,0.15)" }}',
)

# Fix Line 47
content = content.replace(
  '<div className="fixed top-0 left-0 w-full z-50 p-6 flex justify-between items-center pointer-events-none border-b bg-[#02040A]/60 backdrop-blur-md">',
  '<div className="fixed top-0 left-0 w-full z-50 p-6 flex justify-between items-center pointer-events-none border-b bg-[#02040A]/60 backdrop-blur-md" style={{ borderBottomColor: "rgba(234,179,8,0.2)" }}>',
)

# Fix all other 'border-yellow-500/10' and 'border-yellow-500/20' border-b to inline style
content = re.sub(
  r'className="([^"]*)border-b border-yellow-500/20([^"]*)"',
  r'className="\1border-b\2" style={{ borderBottomColor: "rgba(234,179,8,0.2)" }}',
  content,
)
content = re.sub(
  r'className="([^"]*)border-b border-yellow-500/10([^"]*)"',
  r'className="\1border-b\2" style={{ borderBottomColor: "rgba(234,179,8,0.1)" }}',
  content,
)

open("apps/shadowtag-web/app/pitch/page.tsx", "w").write(content)
