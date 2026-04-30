import inspect

from youtube_transcript_api import YouTubeTranscriptApi

print(f"Type: {type(YouTubeTranscriptApi)}")
print(f"Dir: {dir(YouTubeTranscriptApi)}")
try:
    print(f"File: {inspect.getfile(YouTubeTranscriptApi)}")
except Exception:
    print("File: unknown")

try:
    api = YouTubeTranscriptApi()
    transcript = api.fetch("S2evHtbl4F8")
    print(f"Call successful. Transcript length: {len(transcript)}")
    if transcript:
        first = transcript[0]
        print(f"First element type: {type(first)}")
        print(f"First element dir: {dir(first)}")
except Exception as e:
    print(f"Call failed: {e}")
