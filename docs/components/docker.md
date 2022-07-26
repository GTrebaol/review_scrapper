# Docker component

The docker component provides docker images for the CI/CD of applications.

- [Use case](#use-case)
- [Global variables](#global-variables)
- [Jobs](#jobs)
  - [.gitrise](#.gitrise)
  - [.gitrise_download_artifacts](#.gitrise_download_artifacts)
  - [.sonar](#.sonar)

## Use case

```yml
include:
  - project: "opsdev/0e08/mobile-indus"
    file: "/gitlab-ci/components/technical/.docker.yml"

stages:
  - build
  - quality

build:
    stage: build
  extends:
    - .gitrise
  variables:
    BITRISE_USER_TOKEN: $BITRISE_USER_TOKEN
    BITRISE_APP_SLUG: $BITRISE_APP_SLUG
    CI_COMMIT_REF_NAME: $CI_COMMIT_REF_NAME
    BITRISE_WORKFLOW: build
    BITRISE_VARS: ENV:REC

quality:
    stage: quality
  extends:
    - .gitrise_download_artifacts
  variables:
    BITRISE_USER_TOKEN: $BITRISE_USER_TOKEN
    BITRISE_APP_SLUG: $BITRISE_APP_SLUG
    CI_COMMIT_REF_NAME: $CI_COMMIT_REF_NAME
    BITRISE_WORKFLOW: build
    BITRISE_VARS: ENV:REC
    BITRISE_ARTIFACTS_OUTPUT_DIR: sonar-reports
  artifacts:
    paths:
      - sonar-reports/

sonar:
    stage: quality
  extends:
    - .sonar
```

## Global variables

| Variables                    | Description                                                       |
| ---------------------------- | ----------------------------------------------------------------- |
| BITRISE_USER_TOKEN           | Bitrise personal access token to authenticate to the Bitrise API. |
| BITRISE_APP_SLUG             | Bitrise project identifier.                                       |
| CI_COMMIT_REF_NAME           | The branch or tag name for which project is built.                |
| BITRISE_WORKFLOW             | Workflow to execute on Bitrise.                                   |
| BITRISE_VARS                 | Environment variables to pass to the Bitrise build.               |
| BITRISE_ARTIFACTS_OUTPUT_DIR | Output folder that will contain the bitrise workflow's artifacts. |

## Jobs

### .gitrise

Use of the gitrise script to launch a build on a Bitrise project.

| Variables          | Description                                                       |
| ------------------ | ----------------------------------------------------------------- |
| BITRISE_USER_TOKEN | Bitrise personal access token to authenticate to the Bitrise API. |
| BITRISE_APP_SLUG   | Bitrise project identifier.                                       |
| CI_COMMIT_REF_NAME | The branch or tag name for which project is built.                |
| BITRISE_WORKFLOW   | Workflow to execute on Bitrise.                                   |
| BITRISE_VARS       | Environment variables to pass to the Bitrise build.               |

### .gitrise_download_artifacts

Use of the gitrise script to launch a build on a Bitrise project with artifacts recovery.

| Variables                    | Description                                                       |
| ---------------------------- | ----------------------------------------------------------------- |
| BITRISE_USER_TOKEN           | Bitrise personal access token to authenticate to the Bitrise API. |
| BITRISE_APP_SLUG             | Bitrise project identifier.                                       |
| CI_COMMIT_REF_NAME           | The branch or tag name for which project is built.                |
| BITRISE_WORKFLOW             | Workflow to execute on Bitrise.                                   |
| BITRISE_VARS                 | Environment variables to pass to the Bitrise build.               |
| BITRISE_ARTIFACTS_OUTPUT_DIR | Output folder that will contain the bitrise workflow's artifacts. |

### .sonar

Use of the sonar-source script to upload the source code and the different quality reports.
