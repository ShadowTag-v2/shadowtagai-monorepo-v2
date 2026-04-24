use serde::{Deserialize, Serialize};
use tauri::{AppHandle, Emitter};

#[derive(Serialize, Deserialize, Clone)]
pub struct StreamPayload {
    log: Option<String>,
    node: Option<String>,
    status: Option<String>,
    result: Option<String>,
}

/// Polls GET /health up to 15× with 500ms gaps (7.5s total budget).
/// The 383MB PyInstaller binary takes 2-3s to decompress and start uvicorn.
/// Without this, the first invoke_agent POST fires before the engine is ready.
async fn wait_for_engine(client: &reqwest::Client) -> Result<(), String> {
    for _ in 0..15 {
        if client.get("http://127.0.0.1:8081/health").send().await.is_ok() {
            return Ok(());
        }
        tokio::time::sleep(std::time::Duration::from_millis(500)).await;
    }
    Err("Python engine failed to start within 7.5s".into())
}

#[tauri::command]
async fn invoke_agent(app: AppHandle, task: String, target_domain: Option<String>, use_ane: bool) -> Result<(), String> {
    let client = reqwest::Client::new();

    // 0. Wait for uvicorn to be ready before any POST (startup race guard)
    wait_for_engine(&client).await.map_err(|e| {
        let _ = app.emit("agent_stream", StreamPayload {
            log: Some(e.clone()),
            node: None,
            status: Some("error".into()),
            result: None,
        });
        e
    })?;

    // 1. Rust Firewall / "The Brakes"
    if let Some(ref domain) = target_domain {
        if domain.contains("internal-admin") || domain.contains("bank") || domain.contains("restricted.gov") {
            let msg = format!("BLOCKED BY RUST ENFORCER: Sub-agent requested high-risk domain scrape: {}", domain);
            app.emit("agent_stream", StreamPayload {
                log: Some(msg),
                node: None,
                status: Some("error".into()),
                result: None,
            }).unwrap();
            return Ok(());
        }
    }

    // 1.5 Client-Side ToolCall Intercept (Cor.Firebase Iron Straightjacket)
    // If the LLM generates a tool formulation for a material action, we verify it against Shield 1 BEFORE local execution
    if task.contains("execute_vanguard_purchase") || task.contains("trigger_swarm_refactor") {
        let function_name = if task.contains("execute_vanguard_purchase") { "execute_vanguard_purchase" } else { "trigger_swarm_refactor" };
        let intercept_payload = serde_json::json!({
            "function_name": function_name,
            "arguments": {
                "cost_usd": 150.0, // Mock parameter extracted from the LLM JSON
                "supplier_domain": target_domain.clone().unwrap_or_default(),
                "scope": task.clone()
            }
        });

        let intercept_res = client.post("http://127.0.0.1:8081/api/v1/intercept/tool-call")
            .json(&intercept_payload)
            .send()
            .await
            .map_err(|e| format!("Interceptor Reachability Error: {}", e))?;

        let json: serde_json::Value = intercept_res.json().await.map_err(|e| e.to_string())?;
        let status = json["status"].as_str().unwrap_or("RKILL");

        if status == "RKILL" || status == "REQUIRE_COA_CONFIRMATION" {
            let reason = json["reason"].as_str().unwrap_or("Unknown ATP 5-19 Violation");
            let msg = format!("[SHIELD 1 BLOCKED] ToolCall Intercepted. Status: {}. Reason: {}", status, reason);
            app.emit("agent_stream", StreamPayload {
                log: Some(msg),
                node: None,
                status: Some("blocked".into()),
                result: None,
            }).unwrap();
            return Ok(());
        }
    }

    // 2. Dispatch to Python Sidecar Streaming Engine
    let req_body = serde_json::json!({
        "task": task,
        "target_domain": target_domain,
        "use_ane": use_ane
    });

    let mut res = client.post("http://127.0.0.1:8081/api/agent/stream")
        .json(&req_body)
        .send()
        .await
        .map_err(|e| format!("Python Engine Communication Error: {}", e))?;

    // 3. Consume SSE Stream chunks and route directly to React
    let mut buffer = String::new();

    while let Some(chunk) = res.chunk().await.map_err(|e| e.to_string())? {
        let text = String::from_utf8_lossy(&chunk);
        buffer.push_str(&text);

        while let Some(pos) = buffer.find("\n\n") {
            let event = buffer[..pos].to_string();
            buffer = buffer[pos + 2..].to_string();

            if event.starts_with("data: ") {
                let data_str = &event[6..];
                if let Ok(payload) = serde_json::from_str::<StreamPayload>(data_str) {
                    let _ = app.emit("agent_stream", payload);
                }
            }
        }
    }

    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            #[cfg(desktop)]
            {
                use tauri_plugin_shell::ShellExt;
                let sidecar_command = app.shell().sidecar("engine").unwrap();
                let (_rx, _child) = sidecar_command.spawn().expect("Failed to spawn Python sidecar");
                println!("Agentic Engine Sidecar Boostrapped Successfully.");
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![invoke_agent])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
