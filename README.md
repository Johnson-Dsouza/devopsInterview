# DevOps exercise: Jenkins pipeline + Grafana

Time box: 90 minutes. You need Docker and Docker Compose.

## Start the stack

```bash
git init && git add . && git commit -m "starter"   # Jenkins checks out this local repo
docker compose up -d --build
```

| Service     | URL                    | Login       |
|-------------|------------------------|-------------|
| Jenkins     | http://localhost:8080  | none needed |
| Grafana     | http://localhost:3000  | admin/admin |
| Prometheus  | http://localhost:9090  | —           |
| Pushgateway | http://localhost:9091  | —           |

In Jenkins, create a **Pipeline** job, choose "Pipeline script from SCM",
set the Git repository URL to `/repo` and the branch to your current branch.
Commit your changes before each build; Jenkins only sees committed work.

The Jenkins image already has Python 3, the Docker CLI and the pipeline plugins.

## The app

A small Flask app in `app/` with `/health` and `/add?a=&b=`, listening on port 5000.

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r app/requirements.txt
flake8 app/ && pytest
```

## Task 1: Automate the pipeline in Jenkins

Write a declarative `Jenkinsfile` at the repo root. It must:

1. Trigger automatically on changes (SCM polling every 2 minutes is fine).
2. Run these stages in order: **Checkout**, **Lint** (`flake8 app/`),
   **Test** (`pytest --junitxml=reports/junit.xml`), **Build** a Docker image
   tagged `interview-app:${BUILD_NUMBER}`, and **Smoke test** (run the image,
   check `/health`, stop and remove the container).
3. Publish the JUnit report so results show on the build page, even when tests fail.
4. Skip Build and Smoke test if Lint or Test fails.
5. Time out the whole pipeline after 10 minutes.
6. Always clean up the workspace and any containers it started.

One test is broken. Use the Jenkins test report to find it, then fix it.

## Task 2: Show pipeline results in Grafana

At the end of every build, success or failure, push these metrics to the
Pushgateway at `http://pushgateway:9091` under job `interview_pipeline`:

| Metric                            | Meaning                                   |
|-----------------------------------|-------------------------------------------|
| `pipeline_build_status`           | 1 if the build succeeded, 0 if it failed  |
| `pipeline_build_duration_seconds` | Total build time                          |
| `pipeline_tests_passed`           | Passed tests from the JUnit report        |
| `pipeline_tests_failed`           | Failed tests from the JUnit report        |

Build a Grafana dashboard named **CI pipeline health** with three panels:
last build status, build duration over time, and passed/failed tests over time.
The Prometheus data source is already set up.

Export the dashboard JSON to `monitoring/grafana/dashboards/ci-pipeline.json`.

## Deliverables

- `Jenkinsfile`
- The fix for the broken test
- `monitoring/grafana/dashboards/ci-pipeline.json`
- Screenshots of one red and one green build, and the dashboard showing both
- `NOTES.md`: your design choices, what you'd add for production, anything you skipped

**Bonus:** auto-provision the dashboard so it appears on `docker compose up`,
add a Grafana alert when the last build fails, or run Lint and Test in parallel.
