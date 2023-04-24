# Time Series Comparison for Google's trace dataset (2019)

This repository contains a collection of tools that allows to collect, manipulate
and finally compare time series provided by Google's trace dataset (2019).

The repository is essentially a Python package that can be installed and used in
any Python scirpt. Once it is installed, it also offers a command line interface
(CLI) with limited capabilities (download and store Google's trace dataset mainly).

## Repository Structure

- `docs/`: instructions and examples on how to use the offered tools
- `gtd/`: source code
    - `cli/`: implementation of the CLI
    - `comparator/`: components and metrics for time series comparisons
    - `input/`: readers of different types of inputs (numeric data, images, etc.)
    - `internal/`: abstractions and components of the processing engine
    - `preprocessor/`: components for data preprocessing and feature engineering

## Installation

To install the Python package follow the [installation](docs/installation.md) instructions.

## Data Collection & Storage

**Option A**:

Follow the [collection](docs/data_collection.md) and [storage](docs/data_storage.md)
instructions to download and store Google's trace dataset.

**Option B**:

Use the sample dataset of the provided [demo](docs/demo/).

## Usage

### Read Input

### Preprocess Data

### Compare Time Series
