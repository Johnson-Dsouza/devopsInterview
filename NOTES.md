# DevOps Exercise – Notes

## Overview

This exercise covers Jenkins CI pipeline setup and Grafana monitoring.

I focused on completing the required tasks and verifying the pipeline with both successful and failed builds.

---

## Task 1 – Jenkins Pipeline

I created a `Jenkinsfile` for the CI pipeline.

The pipeline includes:

* Checkout source code
* Install dependencies
* Run lint
* Run tests
* Show the build result

### Broken Test Fix

There was a broken test in the application.

I checked the test failure, identified the issue in the application code, and made the required fix.

After the fix, I ran the Jenkins pipeline again and confirmed that the build was successful.

I also kept screenshots of one failed build and one successful build to show the pipeline behavior before and after the fix.

---

## Task 2 – Grafana Monitoring

I created a Grafana dashboard to monitor the Jenkins CI pipeline.

The dashboard shows the build information and helps identify successful and failed builds without checking Jenkins manually.

The dashboard file is:

`monitoring/grafana/dashboards/ci-pipeline.json`

I verified the dashboard using the Jenkins build results.

---

## Design Choices

I kept the implementation simple and focused on the requirements of the exercise.

The Jenkins pipeline is divided into separate stages so that it is easy to identify whether the issue is related to linting or testing.

Grafana was used to provide a simple visual view of the CI pipeline status.

---

## Bonus Items

The README mentioned the following bonus improvements:

* Auto-provision the Grafana dashboard with `docker compose up`
* Add a Grafana alert when the last build fails
* Run Lint and Test stages in parallel

I did not implement these bonus items due to the available time.

They would be good improvements for a production-ready setup.

---

## What I Would Add for Production

If I had more time, I would add:

* Automatic Grafana dashboard provisioning
* Grafana alerts for failed builds
* Notifications through Slack or email
* Parallel execution of independent pipeline stages
* Test coverage and better test reports
* Jenkins credential management for secrets

---

## Deliverables

The completed deliverables are:

* `Jenkinsfile`
* Fix for the broken test
* `monitoring/grafana/dashboards/ci-pipeline.json`
* `NOTES.md`
* Screenshots showing a failed and successful Jenkins build and the Grafana dashboard
