## Summary

## Goals / Non-Goals

## Architecture

## Interfaces & Contracts

## Invariants

## Risks & Mitigations

## Test Plan

## Rollout & Kill Switches

----------------------------- MODULE Proto -----------------------------
EXTENDS Naturals, Sequences
CONSTANTS Users
VARIABLES state
Init == state = [ users |-> {} , sessions |-> {} ]
CreateUser(u) == /\ u \notin DOMAIN state.users
                 /\ state' = [state EXCEPT !.users[u] = [active |-> TRUE]]
NoOrphanSessions == \A s \in DOMAIN state.sessions: state.sessions[s].user \in DOMAIN state.users
Next == \E u \in Users: CreateUser(u)
Spec == Init /\ [][Next]_state
THEOREM Safety == Spec => []NoOrphanSessions
=============================================================================
