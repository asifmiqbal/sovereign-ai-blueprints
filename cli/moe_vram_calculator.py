#!/usr/bin/env python3
"""
Logic42 Sovereign MoE VRAM & Bare-Metal GPU Repatriation Calculator (2026)
Author: Asif Muhammad Iqbal (Founder & CEO at Logic42 — https://logic42.ai)
Interactive Web Workbench: https://logic42.ai/assessments/gpu-tco
"""

import argparse
import math

MODELS = {
    "deepseek-v4.1-flash": {
        "name": "DeepSeek-V4.1-Flash (955B Total / 16B Active + 196B Engram)",
        "weights_fp8_gb": 511.0,
        "kv_gb_per_32k_stream": 4.61,
        "cloud_blended_per_1m_tok": 6.33,
    },
    "kimi-k2.5": {
        "name": "Kimi K2.5 Native Multimodal (1.0T Total / 32B Active INT4)",
        "weights_fp8_gb": 595.0,
        "kv_gb_per_32k_stream": 5.12,
        "cloud_blended_per_1m_tok": 7.50,
    },
    "glm-5.3-flash": {
        "name": "GLM-5.3-Flash Agentic MoE (355B Total / 32B Active FP8)",
        "weights_fp8_gb": 355.0,
        "kv_gb_per_32k_stream": 3.84,
        "cloud_blended_per_1m_tok": 5.20,
    },
    "qwen-3.8-max": {
        "name": "Qwen 3.8-Max MoE (480B Total / 35B Active FP8)",
        "weights_fp8_gb": 480.0,
        "kv_gb_per_32k_stream": 4.20,
        "cloud_blended_per_1m_tok": 6.00,
    },
}

NODES = [
    ("8x NVIDIA HGX H200 (1,128 GB HBM3e)", 1128.0, 248000, 2650),
    ("8x NVIDIA HGX B200 (1,440 GB HBM3e)", 1440.0, 345000, 3200),
    ("8x NVIDIA HGX H100 (640 GB HBM3)", 640.0, 195000, 2400),
]

def calculate(model_key: str, streams: int, context_k: int, daily_million_tokens: float):
    m = MODELS[model_key]
    kv_pool_gb = streams * (context_k / 32.0) * m["kv_gb_per_32k_stream"]
    subtotal = m["weights_fp8_gb"] + kv_pool_gb
    total_vram_gb = round(subtotal * 1.15, 1)

    selected_node = NODES[0]
    nodes_needed = math.ceil(total_vram_gb / selected_node[1])
    capex = nodes_needed * selected_node[2]
    monthly_opex = nodes_needed * selected_node[3]
    bare_metal_24m = capex + (24 * monthly_opex)

    monthly_cloud = daily_million_tokens * 30.0 * m["cloud_blended_per_1m_tok"]
    cloud_24m = monthly_cloud * 24.0
    net_monthly_savings = monthly_cloud - monthly_opex
    payback_months = round(capex / net_monthly_savings, 1) if net_monthly_savings > 0 else 99.9

    print(f"=== Logic42 Sovereign MoE Sizing Report ===")
    print(f"Model:                  {m['name']}")
    print(f"Concurrency & Context:  {streams} streams @ {context_k}k tokens")
    print(f"Base Weights Residency: {m['weights_fp8_gb']} GB")
    print(f"Dynamic KV-Cache Pool:  {kv_pool_gb:.1f} GB")
    print(f"Total HBM3e Required:   {total_vram_gb} GB (incl. 15% CUDA/activation buffer)")
    print(f"Recommended Hardware:   {nodes_needed}x {selected_node[0]}")
    print(f"24-Month Cloud API TCO: ${cloud_24m:,.0f} (${monthly_cloud:,.0f}/mo)")
    print(f"24-Month Bare-Metal:    ${bare_metal_24m:,.0f} (${capex:,.0f} CAPEX + ${monthly_opex:,.0f}/mo colocation)")
    print(f"CAPEX Break-Even:       Month {payback_months}")
    print(f"Full Interactive X-Ray: https://logic42.ai/assessments/gpu-tco")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Logic42 2026 Frontier MoE VRAM & TCO Calculator")
    parser.add_argument("--model", default="deepseek-v4.1-flash", choices=list(MODELS.keys()))
    parser.add_argument("--streams", type=int, default=64)
    parser.add_argument("--context-k", type=int, default=32)
    parser.add_argument("--daily-m-tokens", type=float, default=150.0)
    args = parser.parse_args()
    calculate(args.model, args.streams, args.context_k, args.daily_m_tokens)
