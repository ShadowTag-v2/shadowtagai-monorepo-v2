// Force Webpack to copy the WASM
import "tiktoken/tiktoken_bg.wasm";
import { encoding_for_model, get_encoding, init, Tiktoken } from "tiktoken/init";
import { load } from "tiktoken/load";

export { encoding_for_model, get_encoding, init, load, Tiktoken };
