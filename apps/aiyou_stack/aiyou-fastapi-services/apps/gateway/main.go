package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
)

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	workerURL := os.Getenv("WORKER_URL")
	if workerURL == "" {
		log.Println("WARNING: WORKER_URL not set. Chat proxy will fail.")
	}

	http.HandleFunc("/", healthHandler)
	http.HandleFunc("/chat", func(w http.ResponseWriter, r *http.Request) {
		proxyHandler(w, r, workerURL)
	})

	log.Printf("🦍 Autoresearch Gateway listening on port %s", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{
		"status":  "ok",
		"service": "gateway (go)",
		"speed":   "ultra-fast",
	})
}

func proxyHandler(w http.ResponseWriter, r *http.Request, target string) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Failed to read body", http.StatusInternalServerError)
		return
	}
	defer r.Body.Close()

	// Forward to Worker
    // Note: In Cloud Run, private services are secured. Ideally we use OIDC tokens.
    // For MVP/Speed, we assume public or simple forwarding first, then add Auth.
    // Actually, let's just forward.
	resp, err := http.Post(target+"/chat", "application/json", bytes.NewBuffer(body))
	if err != nil {
		log.Printf("Worker unreachable: %v", err)
		http.Error(w, fmt.Sprintf("Worker unreachable: %v", err), http.StatusBadGateway)
		return
	}
	defer resp.Body.Close()

	// Copy headers and body back
	for k, v := range resp.Header {
		w.Header()[k] = v
	}
	w.WriteHeader(resp.StatusCode)
	io.Copy(w, resp.Body)
}
