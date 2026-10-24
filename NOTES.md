# DevOps Exercise – Notes

## Overview

This exercise covers setting up a Jenkins CI pipeline and monitoring it using Grafana.

I configured the pipeline, tested it with both successful and failed builds, and set up monitoring and email alerts.

## Task 1 – Jenkins Pipeline

I created a `Jenkinsfile` with the following stages:

- Checkout
- Lint using Flake8
- Test using Pytest
- Publish JUnit test results
- Build Docker image
- Smoke test
- Cleanup

### Broken Test Fix

One test was initially failing because it expected HTTP status `201`, while the `/add` endpoint correctly returned `200`.

I updated the test to expect `200`. After the fix, all 5 tests passed and the Jenkins pipeline completed successfully.

The failed build (`#4.txt`) and successful build (`#8.txt`) logs are available in the screenshots/logs folder.

## Task 2 – Grafana Monitoring

I integrated Jenkins with Pushgateway and Prometheus to collect pipeline metrics.

The metrics include:

- Build status
- Build duration
- Number of passed tests
- Number of failed tests

I created a Grafana dashboard named **CI pipeline health** to view the pipeline results and monitor build performance.

Dashboard file:

`monitoring/grafana/dashboards/ci-pipeline.json`

I checked the dashboard using Jenkins build results and verified that the pipeline metrics were available in Prometheus.

## Grafana Alerts and Email Notifications

I configured a Grafana alert named **Jenkins Build Failure** to detect failed builds.

I also configured Brevo SMTP for email notifications and tested the alerting setup. I received emails for both firing and resolved alert states.

If the pipeline metrics are missing, Grafana may report a no-data alert. This is different from an alert confirming an actual build failure.

## Screenshots and Logs

The following evidence is available in the project:

- Successful Jenkins build
- Failed Jenkins build
- Jenkins build logs (`#15.txt` and `#16.txt`)
- Grafana dashboard screenshots
- Evidence of alert email notifications

## Design Choices

I kept the implementation simple and divided the pipeline into separate stages so that failures are easier to identify.

Jenkins handles the build and testing process, Prometheus collects the metrics, and Grafana provides the dashboard and email alerts.

I also kept SMTP credentials in a local `.env` file excluded from Git tracking. The `.env.example` file contains placeholder values only.

## Deliverables

The completed project includes:

- `Jenkinsfile`
- Fix for the broken test
- `monitoring/grafana/dashboards/ci-pipeline.json`
- Prometheus configuration
- Docker and Docker Compose configuration
- `.env.example`
- `NOTES.md`
- Screenshots and logs of successful and failed builds
- Grafana dashboard and alert email evidence

## Summary

This exercise helped me set up a CI pipeline for a Flask application and connect it to a monitoring stack. I tested both successful and failed builds, verified the pipeline metrics, and configured Grafana email alerts to make build failures easier to identify.