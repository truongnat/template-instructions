# Vendored Dependencies Migration Plan

## Overview

This document lists all vendored dependencies currently in `agentic_sdlc_old/lib/` that need to be migrated to `pyproject.toml` for proper dependency management.

## Vendored Packages

The following packages are currently vendored in the `lib/` directory and will be migrated to PyPI dependencies:

### Core Dependencies (Runtime)

| Package | Version | Purpose | Min Version | Max Version |
|---------|---------|---------|-------------|-------------|
| accelerate | 1.12.0 | Hugging Face acceleration library | >=1.12.0 | <2.0.0 |
| aiohttp | 3.13.3 | Async HTTP client/server | >=3.13.0 | <4.0.0 |
| aiosignal | 1.4.0 | Signal support for asyncio | >=1.4.0 | <2.0.0 |
| anyio | 4.12.1 | Async compatibility layer | >=4.12.0 | <5.0.0 |
| bleach | 6.3.0 | HTML sanitization | >=6.3.0 | <7.0.0 |
| certifi | 2026.1.4 | CA bundle | >=2026.1.0 | <2027.0.0 |
| cffi | 2.0.0 | C Foreign Function Interface | >=2.0.0 | <3.0.0 |
| charset_normalizer | 3.4.4 | Character encoding detection | >=3.4.0 | <4.0.0 |
| click | 8.3.1 | CLI framework | >=8.3.0 | <9.0.0 |
| colorama | 0.4.6 | Terminal colors | >=0.4.6 | <0.5.0 |
| defusedxml | 0.7.1 | XML security | >=0.7.1 | <0.8.0 |
| deprecated | 1.3.1 | Deprecation decorator | >=1.3.0 | <2.0.0 |
| dirtyjson | 1.0.8 | Lenient JSON parser | >=1.0.8 | <2.0.0 |
| distro | 1.9.0 | Linux distribution detection | >=1.9.0 | <2.0.0 |
| fastjsonschema | 2.21.2 | JSON schema validation | >=2.21.0 | <3.0.0 |
| filetype | 1.2.0 | File type detection | >=1.2.0 | <2.0.0 |
| frozenlist | 1.8.0 | Immutable list | >=1.8.0 | <2.0.0 |
| gitignore_parser | 0.1.13 | .gitignore parser | >=0.1.13 | <0.2.0 |
| greenlet | 3.3.1 | Lightweight concurrency | >=3.3.0 | <4.0.0 |
| griffe | 1.15.0 | Python API documentation | >=1.15.0 | <2.0.0 |
| h11 | 0.16.0 | HTTP/1.1 protocol | >=0.16.0 | <0.17.0 |
| httpx | 0.28.1 | HTTP client | >=0.28.0 | <0.29.0 |
| huggingface_hub | 0.36.0 | Hugging Face Hub client | >=0.36.0 | <0.37.0 |
| jinja2 | 3.1.6 | Template engine | >=3.1.0 | <4.0.0 |
| joblib | 1.5.3 | Parallel computing | >=1.5.0 | <2.0.0 |
| jsonschema | 4.26.0 | JSON schema validation | >=4.26.0 | <5.0.0 |
| jupyter_client | 8.8.0 | Jupyter client | >=8.8.0 | <9.0.0 |
| jupyter_core | 5.9.1 | Jupyter core | >=5.9.0 | <6.0.0 |
| leann_core | 0.3.6 | LEANN library | >=0.3.6 | <0.4.0 |
| llama_index_instrumentation | 0.4.2 | LlamaIndex instrumentation | >=0.4.0 | <0.5.0 |
| markupsafe | 3.0.3 | Safe string handling | >=3.0.0 | <4.0.0 |
| mistune | 3.2.0 | Markdown parser | >=3.2.0 | <4.0.0 |
| mlx | 0.30.4 | MLX framework | >=0.30.0 | <0.31.0 |
| mlx_lm | 0.29.1 | MLX language models | >=0.29.0 | <0.30.0 |
| mlx_metal | 0.30.4 | MLX Metal support | >=0.30.0 | <0.31.0 |
| mpmath | 1.3.0 | Arbitrary precision math | >=1.3.0 | <2.0.0 |
| msgpack | 1.1.2 | Message serialization | >=1.1.0 | <2.0.0 |
| multidict | 6.7.1 | Multi-value dictionary | >=6.7.0 | <7.0.0 |
| nbclient | 0.10.4 | Jupyter notebook client | >=0.10.0 | <0.11.0 |
| nbconvert | 7.17.0 | Notebook converter | >=7.17.0 | <8.0.0 |
| nbformat | 5.10.4 | Notebook format | >=5.10.0 | <6.0.0 |
| nest_asyncio | 1.6.0 | Nested asyncio support | >=1.6.0 | <2.0.0 |
| networkx | 3.6.1 | Network analysis | >=3.6.0 | <4.0.0 |
| nltk | 3.9.2 | Natural language toolkit | >=3.9.0 | <4.0.0 |
| numpy | 2.4.1 | Numerical computing | >=2.4.0 | <3.0.0 |
| openai | 2.16.0 | OpenAI API client | >=2.16.0 | <3.0.0 |
| pandas | 2.3.3 | Data analysis | >=2.3.0 | <3.0.0 |
| pandocfilters | 1.5.1 | Pandoc filters | >=1.5.0 | <2.0.0 |
| pdfminer_six | 20251230 | PDF text extraction | >=20251230 | <20260101 |
| pdfplumber | 0.11.9 | PDF extraction | >=0.11.0 | <0.12.0 |
| pillow | 12.1.0 | Image processing | >=12.1.0 | <13.0.0 |
| propcache | 0.4.1 | Property caching | >=0.4.0 | <0.5.0 |
| psutil | 7.2.2 | System utilities | >=7.2.0 | <8.0.0 |
| pycparser | 3.0 | C parser | >=3.0 | <4.0.0 |
| pygments | 2.19.2 | Syntax highlighting | >=2.19.0 | <3.0.0 |
| pymupdf | 1.26.7 | PDF library | >=1.26.0 | <2.0.0 |
| pypdfium2 | 5.3.0 | PDF library | >=5.3.0 | <6.0.0 |
| python_dateutil | 2.9.0 | Date utilities | >=2.9.0 | <3.0.0 |
| python_dotenv | 1.2.1 | .env file support | >=1.2.0 | <2.0.0 |
| pytz | 2025.2 | Timezone database | >=2025.2 | <2026.0 |
| pyyaml | 6.0.3 | YAML parser | >=6.0.0 | <7.0.0 |
| pyzmq | 27.1.0 | ZeroMQ bindings | >=27.1.0 | <28.0.0 |
| regex | 2026.1.15 | Regular expressions | >=2026.1.0 | <2027.0.0 |
| requests | 2.32.5 | HTTP library | >=2.32.0 | <3.0.0 |
| scipy | 1.17.0 | Scientific computing | >=1.17.0 | <2.0.0 |
| sentence_transformers | 5.2.2 | Sentence embeddings | >=5.2.0 | <6.0.0 |
| sentencepiece | 0.2.1 | Tokenization | >=0.2.0 | <0.3.0 |
| setuptools | 80.10.2 | Package tools | >=80.10.0 | <81.0.0 |
| six | 1.17.0 | Python 2/3 compatibility | >=1.17.0 | <2.0.0 |
| sniffio | 1.3.1 | Async library detection | >=1.3.0 | <2.0.0 |
| sqlalchemy | 2.0.46 | SQL toolkit | >=2.0.0 | <3.0.0 |
| striprtf | 0.0.26 | RTF text extraction | >=0.0.26 | <0.1.0 |
| sympy | 1.14.0 | Symbolic math | >=1.14.0 | <2.0.0 |
| tenacity | 9.1.2 | Retry library | >=9.1.0 | <10.0.0 |
| tiktoken | 0.12.0 | Token encoding | >=0.12.0 | <0.13.0 |
| torch | 2.10.0 | PyTorch | >=2.10.0 | <3.0.0 |
| tornado | 6.5.4 | Web framework | >=6.5.0 | <7.0.0 |
| tqdm | 4.67.1 | Progress bars | >=4.67.0 | <5.0.0 |
| transformers | 4.45.2 | Hugging Face transformers | >=4.45.0 | <5.0.0 |
| typing_inspect | 0.9.0 | Type inspection | >=0.9.0 | <0.10.0 |
| tzdata | 2025.3 | Timezone data | >=2025.3 | <2026.0 |
| urllib3 | 2.6.3 | HTTP client | >=2.6.0 | <3.0.0 |
| webencodings | 0.5.1 | Web encodings | >=0.5.0 | <0.6.0 |
| wrapt | 2.0.1 | Function wrapping | >=2.0.0 | <3.0.0 |
| yarl | 1.22.0 | URL handling | >=1.22.0 | <2.0.0 |

## Custom Modifications

After reviewing the vendored packages, no custom modifications were detected. All packages appear to be standard distributions from PyPI.

## Migration Strategy

### Phase 1: Add to pyproject.toml
All packages listed above will be added to the `[project.dependencies]` section with appropriate version constraints.

### Phase 2: Test Installation
After adding dependencies to pyproject.toml:
1. Create a clean virtual environment
2. Install the SDK: `pip install -e .`
3. Verify all imports work without the lib/ directory
4. Test core functionality

### Phase 3: Remove lib/ Directory
Once verified that all dependencies are properly declared:
1. Delete the `agentic_sdlc_old/lib/` directory
2. Update .gitignore if needed
3. Verify no code references the lib/ directory

## Dependency Categories

### Core Runtime Dependencies (Always Installed)
- pydantic, python-dotenv, requests, PyYAML
- openai, anthropic, streamlit
- dspy-ai, docker, googlesearch-python
- autogen-agentchat, neo4j
- PyMuPDF, torch, transformers, sentencepiece, Pillow, unstructured

### Optional CLI Dependencies
- click, rich

### Optional Development Dependencies
- pytest, pytest-cov, pytest-asyncio, pytest-mock, pytest-benchmark
- hypothesis (for property-based testing)
- black, ruff, pylint, flake8, isort
- mypy, sphinx, mkdocs
- build, twine, wheel
- ipython, ipdb, pre-commit
- bandit, safety

## Notes

- All version constraints use semantic versioning (>=X.Y.Z, <X+1.0.0)
- Minimum versions are set to the vendored versions to ensure compatibility
- Maximum versions prevent major version upgrades that could introduce breaking changes
- Some packages (torch, transformers, numpy) are large and may require significant disk space
- The migration maintains backward compatibility with existing code
