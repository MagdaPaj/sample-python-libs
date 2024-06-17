# Python wheel generation

This repository shows pipelines that illustrate diverse methods and tools for packaging and distributing Python libraries.

All approaches initially generate a `.whl` (aka [wheel](https://packaging.python.org/en/latest/glossary/#term-Wheel)) file as outlined in the [Python Packaging User guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/#generating-distribution-archives). Subsequently, different methods are used to distribute it.


## Approach 1 - uploading the package to the Python Package Index (PyPI)

The [python-publish-to-pypi.yml](.github/workflows/python-publish-to-pypi.yml) pipeline leverages `twine` to upload the Python wheel to Test PyPI. You can find a detailed explanation about this setup [here](https://packaging.python.org/en/latest/tutorials/packaging-projects/#uploading-the-distribution-archives).

Pipeline is triggered manually.


## Approach 2 - creating a GitHub Release with a wheel using a third-party GitHub Action

The [create-release](.github/workflows/create-release.yml) pipeline is triggered whenever a new git tag is pushed. It creates a GitHub release named after the tag name, and upload the previously generated wheel as an additional asset file.

It's important to note that the wheel version and the GitHub release number can be different, as the wheel version is based on the version specified in the [pyproject.toml](pyproject.toml) file.

Release creation step utilizes a third-party GitHub Action, which is developed by an individual and not directly by GitHub. Previously, GitHub supported actions such as ([actions/create-release](https://github.com/actions/create-release) and [actions/upload-release-asset](https://github.com/actions/upload-release-asset)), but these are no longer maintained (refer to [this issue](https://github.com/actions/create-release/issues/119) for more information). The third-party action that was selected is [softprops/action-gh-release](https://github.com/softprops/action-gh-release). This action was chosen due to its ongoing maintenance, its recommendation on the repositories of `actions/create-release` and `actions/upload-release-asset`, and its widespread usage. Additionally, this single action provides the functionality to both create a release and upload assets.


## Approach 3 - creating a tag, a GitHub release with a wheel using `gh` CLI

The [create-tag-and-release.yaml](.github/workflows/create-tag-and-release.yml) is triggered whenever changes to the [pyproject.toml](pyproject.toml) file are merged into the `main` branch. It then extracts the version from the file, creates a git tag that matches the extracted version, creates a GitHub release named after the git tag, and upload the generated wheel as an additional asset file. This approach uses the GitHub API directly through the `gh` command-line tool.

Please note that the `gh` tool is pre-installed in the GitHub-hosted runners, but if you're using a self-hosted runner, you might need to install it yourself.


An alternative option is to use `curl` with the GitHub API. For example:

```yml
- name: Release
  run: |
    curl -L -X POST \
      -H "Accept: application/vnd.github+json" \
      -H "Authorization: Bearer $GH_TOKEN" \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      https://api.github.com/repos/MagdaPaj/sample-python-libs/releases \
      -d '{
      "tag_name":"v${{ env.VERSION }}",
      "name":"Release v${{ env.VERSION }}"
      }'
  env:
    GH_TOKEN: ${{ github.token }}
```

## Tokens

GitHub Actions provides a secret token, [GITHUB_TOKEN](https://docs.github.com/en/actions/security-guides/automatic-token-authentication), which can be used for authentication. However, by default, this token does not have sufficient permissions to push a git tag or create a release. To overcome this, you need to specify [permissions](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#permissions) with the `contents: write` scope in your pipeline file. This approach was used in the [create-tag-and-release.yml](.github/workflows/create-tag-and-release.yml)

Alternatively, you can create a Personal Access Token (PAT) with the `repo` scope and add it as a repository secret. This approach was used in the [create-release.yml](.github/workflows/create-release.yml) workflow. Remember to handle your PAT with care to ensure the security of your repository.

## Example installation/usage

* From Test PyPI

```pyspark
%pip install -i https://test.pypi.org/simple/ custom_python_libs==0.0.9
```

* From GitHub release

```pyspark
%pip install https://github.com/MagdaPaj/sample-python-libs/releases/download/v0.0.10/custom_python_libs-0.0.10-py3-none-any.whl
```

* If you are using Microsfoft Fabric, 
[create a Fabric environment](https://learn.microsoft.com/en-us/fabric/data-engineering/create-and-use-environment#create-an-environment) and upload the wheel as explained [here](https://learn.microsoft.com/en-us/fabric/data-engineering/environment-manage-library#custom-libraries). Then make sure to [attach the created environment](https://learn.microsoft.com/en-us/fabric/data-engineering/create-and-use-environment#attach-an-environment).