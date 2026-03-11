# VertexCoverKernelization

A benchmark of various kernelization methods for the parametrized vertex cover

## Project setup

1. **Clone the repository:**

    ```bash
    git clone https://github.com/uberdomi/VertexCoverKernelization.git
    cd VertexCoverKernelization
    ```

2. **Install `uv`** (if not already installed). [Learn about the uv package manager](https://docs.astral.sh/uv/guides/install-python/)

   - Unix systems:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   - Windows:

   ```ps
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

   - `pip`

   ```bash
   pip install uv
   ```

3. **Download** the packages:

    ```bash
    uv sync
    ```

    (Optionally) download all packages (including development and Jupyter Notebook libraries):

    ```bash
    uv sync --all-groups
    ```

    Or just selected package groups:

    ```bash
    uv sync --extra dev
    ```
