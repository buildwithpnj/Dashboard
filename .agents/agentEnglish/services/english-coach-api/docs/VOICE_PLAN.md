# Voice Interface Integration Plan - Warborn Agent Platform

This document describes the design of the spoken interface and the plan to transition from text stubs to active streaming in V2.

---

## 1. Current Chained Voice Architecture (V1.5)

To maintain simplicity and prevent dependency bloat, V1.5 implements a **chained voice processing pipeline** mounted at `POST /v1/coach/voice/respond`:

```
Audio Input (Base64) 
   |
   v
[TranscriptionService] (STT Stub) ---> Plain Text Query
                                             |
                                             v
                                     [Orchestrator Router]
                                             |
                                             v
                                     [Active Product Coach] ---> Coached Text Response
                                                                       |
                                                                       v
Audio Output (Base64) <--- [TTSService] (TTS Stub) <------------------/
```

- **Audio Ingestion**: Accepts standard base64 encoded audio strings representing spoken queries.
- **Audio Output**: Synthesizes responses into base64 encoded speech segments.

---

## 2. V2 Active Streaming Migration Plan

In V2, the current request-response block will be upgraded to support **bidirectional real-time audio streams** (such as WebSockets or WebRTC):

### WebSocket Streaming Lifecycle:
1. **Audio Streaming Loop**: The browser/client establishes a WebSocket connection to `WS /v1/coach/voice/stream`.
2. **Chunked STT (VAD)**: The client pipes microphone raw PCM audio chunks. A local Voice Activity Detector (VAD) identifies speech boundaries, feeding chunks directly to the Whisper streaming transcriber.
3. **LLM Chunk Piping**: Transcribed text tokens are sent to the LLM. The LLM streams completion tokens to the TTS engine.
4. **TTS Audio Synthesizer**: The TTS engine converts text tokens to audio bytes on-the-fly and streams them back to the client.

### Technology Stack:
- **Speech-to-Text**: OpenAI Whisper API (`v1/audio/transcriptions`) or faster local instances (e.g. `whisper.cpp`).
- **Text-to-Speech**: ElevenLabs WebSocket API or OpenAI TTS (`v1/audio/speech`).
- **Client Player**: Web Audio API AudioWorklet for low-latency playback of incoming raw PCM float buffers.
