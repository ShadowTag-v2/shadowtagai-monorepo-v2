# contracts

## Purpose
This directory is the canonical home for shared contracts used across services, libraries, and applications.

## What belongs here
Use contracts/ for:
* shared API schemas
* protobuf definitions
* shared DTO / interface declarations
* event schemas
* generated code configuration
* cross-language service contracts

## What does not belong here
Do not put:
* service-private models that are not shared
* duplicated local copies of shared schemas
* temporary migration copies
* archival or legacy definitions

## Rules
* Shared contracts must be declared once here and consumed from here.
* Services may not maintain independent duplicate versions of shared contracts.
* Breaking changes must be versioned or coordinated explicitly.
* Generated artifacts should be reproducible from source contracts.

## Suggested layout
contracts/
├── proto/
├── events/
├── http/
├── generated/
└── README.md

## Required metadata for each contract area
Document:
* owner
* consumers
* versioning policy
* generation method
* compatibility expectations

## Migration rule
If a shared contract exists in multiple service-local locations:
1. select the canonical definition
2. move it under contracts/
3. update consumers
4. delete or archive duplicate local copies after validation
