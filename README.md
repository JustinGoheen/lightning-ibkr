# Python Package and Lightning Component Template

<!-- # Copyright Justin R. Goheen.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License. -->

This repo is opinionated boilerplate for creating a Python package or [Lightning AI](https://lightning.ai) Apps [component](https://lightning.ai/components).

To get started, copy the repo from the template then clone the repo to your local machine.

## Required Refactoring

### Step 1

In your code editor, search for `{ component_name }` and change to whatever you'd like to call your component e.g. lightning_component; please keep in mind this will be the name of the python package created with `pip install -e .`

> literally search for `{ component_name }`, not `component name`

The search for `{ component_name }` will return results in 5 files. One of those files is this README, the other four files must be changed, and are:

- .lightning
- pyproject.toml
- setup.cfg
- setup.py

### Step 2

The file `.lightning` will be the name of your component in your Lightning Account, should you chose to upload it to Lightning Platform. The name of the component in this file can (and likely should) be different than the component name you choose for the package; however, this is entirely your decision.

### Step 3

The final change to make is for the package directory located at `src/{ component_name }`. Change this to the name you've used for the package in step 1.

## Setup

> You must refactor first, even if you simply rename the component to `lightning_component`.

Then, in terminal do:

```sh
cd {{ path to clone }}
python3 -m venv .venv/
source .venv/bin/activate
pip install - ".[all]"
pre-commit install
```

This will install an opinionated framework:

Core

- Lightning 2.0
- PyTorch 2.0

Code Quality

- Ruff
- Black
- PyTest
- MyPy
- Bandit
- Coverage
- Pre-Commit
- iSort

Docs

- MkDocs Material
- my fork of keras-autodoc

Packaging

- setuptools
- build
- twine

## Documenting Your Component

This template uses mkdocs-material and keras-autodoc for sake of simplicity. A key aspect of keras-autodoc is that docstrings require markdown header tags in order for the tool to parse correctly. In other words, `- Args` becomes `# Arguments`. Aside from that, the body of the docstring remains the same, and the familiar mkdocs project tools and requirements remain in place.

See [material-for-mkdocs](https://squidfunk.github.io/mkdocs-material/) and [keras-autodoc-community](https://github.com/JustinGoheen/keras-autodoc-community) for examples of using either tool.

## Other Templates

If you already have lightning installed, a [minimal component template](https://lightning.ai/docs/app/stable/workflows/build_lightning_component/publish_a_component.html) without my dependency choices can be created from the command line with:

```sh
lightning init component { your-component-name }
```

My template uses Lightning's `.github/workflows/ci-testing.yml`.
