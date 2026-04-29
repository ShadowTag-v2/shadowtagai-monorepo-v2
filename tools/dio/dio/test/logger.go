// Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

package main

import (
	"fmt"
	"time"
)

// Logging defines the interface for diagnostic message output.
type Logging interface {
	Info(msg string)
	Error(err error, msg string)
}

// Logger implements the Logging interface.
type Logger struct {
	Prefix string
}

// Info logs an informational message.
func (l *Logger) Info(msg string) {
	fmt.Printf("[%s] INFO: %s %s\n", time.Now().Format(time.RFC3339), l.Prefix, msg)
}

// Error logs an error message.
func (l *Logger) Error(err error, msg string) {
	fmt.Printf("[%s] ERROR: %s %s: %v\n", time.Now().Format(time.RFC3339), l.Prefix, msg, err)
}
