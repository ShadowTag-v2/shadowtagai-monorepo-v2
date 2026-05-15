// src-tauri/src/main.rs
// ============================================================================
// Tauri Cockpit — Rust Local Enforcer & Hammock Watcher
// ============================================================================
// Block 12 of the Ex Toto Omni-Compile (Gideon OS Architecture)
// The Biometric Airlock. Watches Obsidian for the [x] EXIT 0 checkmark.
// Teleports ULTRAPLAN code to local machine.
// ============================================================================
#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use notify::{watcher, RecursiveMode, Watcher};
use std::fs;
use std::path::Path;
use std::sync::mpsc::channel;
use std::thread;
use std::time::Duration;
use tauri::Manager;

/// INVARIANT 4: THE HAMMOCK PROTOCOL
/// Watches Obsidian for the [x] EXIT 0: AUTHORIZE BATTLE checkbox.
fn watch_hammock_file(app_handle: tauri::AppHandle) {
    thread::spawn(move || {
        let (tx, rx) = channel();
        let mut _watcher = watcher(tx, Duration::from_secs(2)).unwrap();
        let hammock_path =
            Path::new("/Users/Shared/Obsidian_Vault/Inbox/pending_battle.md");

        _watcher
            .watch(
                hammock_path.parent().unwrap(),
                RecursiveMode::NonRecursive,
            )
            .unwrap();

        for res in rx {
            match res {
                Ok(_event) => {
                    let content =
                        fs::read_to_string(hammock_path).unwrap_or_default();
                    if content.contains("[x] EXIT 0: AUTHORIZE BATTLE") {
                        println!("⚔ [HAMMOCK PROTOCOL] Authorization Detected. Teleporting Artifacts.");
                        app_handle
                            .emit_all("hammock_authorized", ())
                            .unwrap();
                        fs::rename(
                            hammock_path,
                            hammock_path.with_extension("executed"),
                        )
                        .unwrap();
                    }
                }
                Err(e) => println!("watch error: {:?}", e),
            }
        }
    });
}

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            watch_hammock_file(app.handle());
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
