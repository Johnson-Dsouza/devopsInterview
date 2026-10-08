# DevOps Exercise – Notes

## Overview

This exercise covers Jenkins CI pipeline setup and Grafana monitoring.

I completed the required tasks and verified the pipeline using both successful and failed builds.

---

## Task 1 – Jenkins Pipeline

I created a `Jenkinsfile` with the following stages:

* Checkout
* Lint using `flake8`
* Test using `pytest`
* Publish JUnit test results
* Build Docker image
* Smoke test
* Cleanup

### Broken Test Fix

One test was initially failing because it expected HTTP status `201`, while the `/add` endpoint correctly returned `200`.

I updated the test to expect `200`. After the fix, all **5 tests passed** and the Jenkins pipeline completed successfully.

The failed build (`#4.txt`) and successful build (`#8.txt`) logs are available in the `screenshots/logs` folder.

---

## Task 2 – Grafana Monitoring

I created a Grafana dashboard to monitor the Jenkins CI pipeline.

The dashboard provides a simple view of the build status and makes it easier to identify successful and failed builds.

Dashboard file:

`monitoring/grafana/dashboards/ci-pipeline.json`

I verified the dashboard with both successful and failed Jenkins builds.

### Screenshots and Logs

* [Successful Jenkins build](screenshots/Screenshot-green-build-jenkins.png)
* [Failed Jenkins build](screenshots/Screenshot-red-build-jenkins.png)
* [Successful build with Grafana dashboard](screenshots/Screenshot-green-build-grafana-dashboard.png)
* [Failed build with Grafana dashboard](screenshots/Screenshot-red-build-grafana-dashboard.png)
* Failed build logs: [#15.txt](screenshots/logs/%2315.txt)
* Successful build logs: [#16.txt](screenshots/logs/%2316.txt)

---

## Design Choices

I kept the implementation simple and focused on the requirements of the exercise.

The Jenkins pipeline is divided into separate stages so that failures can be easily identified.

Grafana was used to provide a simple visual view of the Jenkins pipeline status.

---

## Bonus Items

The README mentioned the following bonus improvements:

* Auto-provision the Grafana dashboard with `docker compose up`
* Add a Grafana alert when the last build fails
* Run Lint and Test stages in parallel

I did not implement these bonus items due to the available time. They could be added as future improvements.

---

## What I Would Add for Production

For a production setup, I would consider adding:

* Automatic Grafana dashboard provisioning
* Grafana alerts for failed builds
* Slack or email notifications
* Parallel execution of independent pipeline stages
* Test coverage and improved test reporting

---

## Deliverables

The completed deliverables are:

* `Jenkinsfile`
* Fix for the broken test
* `monitoring/grafana/dashboards/ci-pipeline.json`
* `NOTES.md`
* Screenshots of successful and failed Jenkins builds
* Grafana dashboard screenshots
* Jenkins build logs in `screenshots/logs`
