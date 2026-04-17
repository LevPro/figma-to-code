# Full API Reference Guide

This document provides a consolidated view of all methods and classes within the Figma-to-Code Converter project.

## Table of Contents
1. [Core Pipeline (`main.py`)](01_core_methods.md)
2. [Configuration (`settings.py`)](02_config_settings.md)
3. [Data & Image Processing](docs/03_data_loading.md), [docs/04_image_utils.md]
4. [Models (`models.py`)](docs/05_models.md)
5. [Agents & Providers](docs/06_agents.md), [docs/07_providers.md]

## Overview
This tool converts Figma JSON exports into production-ready HTML/CSS/JS using a two-stage AI pipeline (Block Generation → Page Assembly). It supports multiple LLM providers and includes caching, retry logic, and image optimization.

> **Note**: For detailed parameter lists and return types, please navigate to the specific module links above.
