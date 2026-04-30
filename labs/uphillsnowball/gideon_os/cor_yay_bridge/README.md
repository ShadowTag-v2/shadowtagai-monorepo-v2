# Cor.Yay Bridge

> Gideon OS Block — Inter-Process Communication Bridge

## Purpose

The Cor.Yay Bridge provides the communication fabric between Gideon OS blocks,
enabling secure, bidirectional message passing across language boundaries
(Python ↔ Go ↔ Rust ↔ C++ ↔ TypeScript).

## Architecture

```
┌─────────────────────┐     ┌──────────────────────┐
│  Python Agents      │◄───►│  Cor.Yay Bridge      │
│  (Kairos, Panopticon)│    │  (gRPC + Protobuf)   │
└─────────────────────┘     └──────┬───────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
              ┌──────────┐  ┌──────────┐  ┌──────────┐
              │ Go Block │  │ Rust Blk │  │ C++ Block│
              │ (Shield1)│  │ (Vault)  │  │ (Midas)  │
              └──────────┘  └──────────┘  └──────────┘
```

## Transport

- **Primary**: gRPC with Protobuf serialization
- **Fallback**: Unix domain sockets for local-only blocks
- **Security**: mTLS between all block pairs, certificate rotation via Vault Constitution

## Status

- **Phase**: Scaffold
- **Language**: Python (coordinator) + Protocol Buffers (IDL)
- **Dependencies**: `grpcio`, `protobuf`

## Integration Points

| Block | Direction | Protocol |
|-------|-----------|----------|
| Kairos Supervisor | Bidirectional | gRPC |
| Shield1 Ingress | Outbound | gRPC |
| Midas Monte Carlo | Outbound | gRPC |
| Panopticon | Inbound | gRPC |
| Vault Constitution | Config-only | File watch |

## Development

```bash
# Generate protobuf stubs
python -m grpc_tools.protoc -I=proto --python_out=. --grpc_python_out=. proto/*.proto

# Run bridge in development mode
python bridge.py --mode=dev --port=50051
```
