#!/usr/bin/env python3
"""Async parallel benchmark for gap fill - run 3 models on 21 docs simultaneously."""

import asyncio
import json
import os
import time
from pathlib import Path

# Load environment
from dotenv import load_dotenv

load_dotenv()

# Premium model configs
MODELS = {
    "anthropic": {
        "model": "claude-sonnet-4-5",
        "model_id": "claude-sonnet-4-5-20250929",
    },
    "openai": {
        "model": "gpt-5.1",
    },
    "gemini": {
        "model": "gemini-3-pro-preview",
    },
}

# Documents to process (skip arxiv papers - too slow)
FAST_DOCS = [
    "14_table_financial",
    "19_list_mixed_types",
    "21_column_two_column",
    "24_column_newsletter",
    "27_mixed_business_report",
    "32_mixed_comprehensive",
    "invoice_001",
    "invoice_015",
    "invoice_030",
    "invoice_050",
    "invoice_075",
    "resume_001",
    "resume_005",
    "resume_010",
    "resume_020",
    "resume_030",
]

# Arxiv papers (slow, handle separately)
ARXIV_DOCS = [
    "arxiv-2302.00722",
    "arxiv-2302.13971",
    "arxiv-2312.00752",
    "arxiv-2401.06244",
    "arxiv-2403.09313",
]


def find_pdf(doc_id: str, corpus_dir: Path) -> Path | None:
    """Find PDF file for document ID."""
    for pattern in [f"**/{doc_id}.pdf", f"**/{doc_id}/*.pdf"]:
        matches = list(corpus_dir.glob(pattern))
        if matches:
            return matches[0]
    return None


async def parse_anthropic(pdf_path: Path, output_dir: Path, model_id: str) -> dict:
    """Parse with Anthropic async."""
    import base64

    import anthropic

    client = anthropic.AsyncAnthropic()
    pdf_data = base64.standard_b64encode(pdf_path.read_bytes()).decode("utf-8")

    start = time.time()
    try:
        message = await asyncio.wait_for(
            client.messages.create(
                model=model_id,
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": pdf_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": "Convert this PDF to clean Markdown. Output only the Markdown content.",
                            },
                        ],
                    }
                ],
            ),
            timeout=120.0,
        )
        markdown = "".join(block.text for block in message.content if hasattr(block, "text"))
        elapsed = time.time() - start

        # Save output
        output_path = output_dir / f"{pdf_path.stem}.md"
        output_path.write_text(markdown, encoding="utf-8")

        return {
            "success": True,
            "parse_time_seconds": elapsed,
            "input_tokens": message.usage.input_tokens if message.usage else 0,
            "output_tokens": message.usage.output_tokens if message.usage else 0,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "parse_time_seconds": time.time() - start}


async def parse_openai(pdf_path: Path, output_dir: Path, model: str) -> dict:
    """Parse with OpenAI async."""
    from openai import AsyncOpenAI

    client = AsyncOpenAI()

    start = time.time()
    try:
        # Upload file
        with open(pdf_path, "rb") as f:
            file = await asyncio.wait_for(
                client.files.create(file=f, purpose="user_data"), timeout=30.0
            )

        # Parse
        response = await asyncio.wait_for(
            client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "file", "file": {"file_id": file.id}},
                            {
                                "type": "text",
                                "text": "Convert this PDF to clean Markdown. Output only the Markdown content.",
                            },
                        ],
                    }
                ],
            ),
            timeout=120.0,
        )

        markdown = response.choices[0].message.content or ""
        elapsed = time.time() - start

        # Cleanup
        try:
            await client.files.delete(file.id)
        except Exception:
            pass

        # Save output
        output_path = output_dir / f"{pdf_path.stem}.md"
        output_path.write_text(markdown, encoding="utf-8")

        return {
            "success": True,
            "parse_time_seconds": elapsed,
            "input_tokens": response.usage.prompt_tokens if response.usage else 0,
            "output_tokens": response.usage.completion_tokens if response.usage else 0,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "parse_time_seconds": time.time() - start}


async def parse_gemini(pdf_path: Path, output_dir: Path, model: str) -> dict:
    """Parse with Gemini async."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))

    start = time.time()
    try:
        pdf_data = pdf_path.read_bytes()
        pdf_part = types.Part.from_bytes(data=pdf_data, mime_type="application/pdf")

        # Gemini SDK doesn't have native async, run in executor
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None,
                lambda: client.models.generate_content(
                    model=model,
                    contents=[
                        pdf_part,
                        "Convert this PDF to clean Markdown. Output only the Markdown content.",
                    ],
                ),
            ),
            timeout=120.0,
        )

        markdown = response.text or ""
        elapsed = time.time() - start

        # Save output
        output_path = output_dir / f"{pdf_path.stem}.md"
        output_path.write_text(markdown, encoding="utf-8")

        input_tokens = 0
        output_tokens = 0
        if response.usage_metadata:
            input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
            output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) or 0

        return {
            "success": True,
            "parse_time_seconds": elapsed,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "parse_time_seconds": time.time() - start}


async def process_document(doc_id: str, pdf_path: Path, cache_dir: Path) -> list[dict]:
    """Process a single document with all 3 models in parallel."""
    results = []

    # Create output dirs
    anthropic_dir = cache_dir / "anthropic_claude_sonnet_4_5" / doc_id
    openai_dir = cache_dir / "openai_gpt_5_1" / doc_id
    gemini_dir = cache_dir / "gemini_gemini_3_pro_preview" / doc_id

    anthropic_dir.mkdir(parents=True, exist_ok=True)
    openai_dir.mkdir(parents=True, exist_ok=True)
    gemini_dir.mkdir(parents=True, exist_ok=True)

    # Run all 3 in parallel
    tasks = [
        parse_anthropic(pdf_path, anthropic_dir, MODELS["anthropic"]["model_id"]),
        parse_openai(pdf_path, openai_dir, MODELS["openai"]["model"]),
        parse_gemini(pdf_path, gemini_dir, MODELS["gemini"]["model"]),
    ]

    parser_names = [
        "anthropic_claude_sonnet_4_5",
        "openai_gpt_5_1",
        "gemini_gemini_3_pro_preview",
    ]

    responses = await asyncio.gather(*tasks, return_exceptions=True)

    for parser_name, response in zip(parser_names, responses, strict=False):
        if isinstance(response, Exception):
            result = {"success": False, "error": str(response), "parse_time_seconds": 0}
        else:
            result = response

        results.append(
            {
                "document_id": doc_id,
                "parser_name": parser_name,
                **result,
                "metrics": {},  # Will be computed later
            }
        )

        status = "✓" if result.get("success") else "✗"
        print(f"  {status} {parser_name}: {result.get('parse_time_seconds', 0):.1f}s")

    return results


async def main():
    """Run parallel benchmark."""
    corpus_dir = Path("corpus")
    cache_dir = Path(".cache/parsers")
    output_file = Path("results/gap_fill_async.json")

    all_results = []

    # Process fast docs first (non-arxiv)
    print(f"Processing {len(FAST_DOCS)} fast documents...")

    # Run 4 documents at a time (12 API calls in parallel)
    for i in range(0, len(FAST_DOCS), 4):
        batch = FAST_DOCS[i : i + 4]
        print(f"\nBatch {i // 4 + 1}: {batch}")

        tasks = []
        for doc_id in batch:
            pdf_path = find_pdf(doc_id, corpus_dir)
            if pdf_path:
                tasks.append(process_document(doc_id, pdf_path, cache_dir))
            else:
                print(f"  ⚠ PDF not found: {doc_id}")

        batch_results = await asyncio.gather(*tasks)
        for results in batch_results:
            all_results.extend(results)

        # Save checkpoint
        output_file.parent.mkdir(exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(
                {
                    "benchmark": "gap_fill_async",
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "results": all_results,
                },
                f,
                indent=2,
            )
        print(f"  Checkpoint: {len(all_results)} results saved")

    # Optionally process arxiv papers (slower)
    if os.getenv("INCLUDE_ARXIV", "").lower() == "true":
        print(f"\nProcessing {len(ARXIV_DOCS)} arxiv documents (slow)...")
        for doc_id in ARXIV_DOCS:
            pdf_path = find_pdf(doc_id, corpus_dir)
            if pdf_path:
                print(f"\n{doc_id}:")
                results = await process_document(doc_id, pdf_path, cache_dir)
                all_results.extend(results)

                # Save checkpoint
                with open(output_file, "w") as f:
                    json.dump(
                        {
                            "benchmark": "gap_fill_async",
                            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "results": all_results,
                        },
                        f,
                        indent=2,
                    )

    print(f"\n✓ Complete: {len(all_results)} results in {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
