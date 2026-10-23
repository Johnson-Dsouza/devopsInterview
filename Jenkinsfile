
pipeline {
    agent any

    options {
        timeout(time: 10, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    triggers {
        pollSCM('H/2 * * * *')
    }

    environment {
        APP_IMAGE = "interview-app:${BUILD_NUMBER}"
        APP_CONTAINER = "interview-app-smoke-${BUILD_NUMBER}"
        PUSHGATEWAY_URL = "http://pushgateway:9091"
        METRICS_JOB = "interview_pipeline"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Parallel Quality Checks') {
            parallel {
                stage('Lint') {
                    steps {
                        sh '''
                            set -e
                            python3 -m flake8 app/
                        '''
                    }
                }

                stage('Test') {
                    steps {
                        sh '''
                            set -e

                            python3 -m pip install \
                                --break-system-packages \
                                -r app/requirements.txt

                            mkdir -p reports

                            python3 -m pytest \
                                --junitxml=reports/junit.xml \
                                --cov=app \
                                --cov-report=term-missing \
                                --cov-report=xml:reports/coverage.xml \
                                --cov-fail-under=90
                        '''
                    }

                    post {
                        always {
                            junit(
                                testResults: 'reports/junit.xml',
                                allowEmptyResults: true
                            )

                            archiveArtifacts(
                                artifacts: 'reports/**',
                                allowEmptyArchive: true
                            )
                        }
                    }
                }
            }
        }

        stage('Build') {
            steps {
                sh '''
                    set -e
                    docker build -t "${APP_IMAGE}" .
                '''
            }
        }

        stage('Smoke Test') {
            steps {
                sh '''
                    set -eu

                    docker rm -f "${APP_CONTAINER}" \
                        >/dev/null 2>&1 || true

                    # Publish container port 5000 on an available host port.
                    docker run -d -P \
                        --name "${APP_CONTAINER}" \
                        "${APP_IMAGE}"

                    HOST_PORT=$(docker port "${APP_CONTAINER}" 5000/tcp |
                        head -n 1 | awk -F: '{print $NF}')

                    if [ -z "$HOST_PORT" ]; then
                        echo "Could not determine the mapped host port"
                        docker logs "${APP_CONTAINER}" || true
                        exit 1
                    fi

                    echo "Testing application on port ${HOST_PORT}"

                    for i in $(seq 1 15); do
                        if curl -fsS \
                            "http://host.docker.internal:${HOST_PORT}/health"; then
                            echo "Smoke test passed"
                            exit 0
                        fi

                        if [ "$i" -eq 15 ]; then
                            echo "Smoke test failed"
                            docker logs "${APP_CONTAINER}" || true
                            exit 1
                        fi

                        sleep 2
                    done
                '''
            }

            post {
                always {
                    sh '''
                        docker rm -f "${APP_CONTAINER}" \
                            >/dev/null 2>&1 || true
                    '''
                }
            }
        }
    }

    post {
        always {
            script {
                def buildStatusValue =
                    currentBuild.currentResult == 'SUCCESS' ? 1 : 0

                def buildDurationSeconds =
                    currentBuild.duration / 1000.0

                def testsPassed = 0
                def testsFailed = 0
                def testCoverageFraction = '0.0'

                // Read JUnit test results.
                if (fileExists('reports/junit.xml')) {
                    def junitXml = readFile('reports/junit.xml')

                    def passedMatch =
                        junitXml =~ /<testsuite[^>]*\stests="(\d+)"/

                    def failuresMatch =
                        junitXml =~ /<testsuite[^>]*\sfailures="(\d+)"/

                    def errorsMatch =
                        junitXml =~ /<testsuite[^>]*\serrors="(\d+)"/

                    if (passedMatch.find()) {
                        testsPassed = passedMatch.group(1).toInteger()
                    }

                    if (failuresMatch.find()) {
                        testsFailed = failuresMatch.group(1).toInteger()
                    }

                    if (errorsMatch.find()) {
                        testsFailed += errorsMatch.group(1).toInteger()
                    }
                }

                // Read coverage fraction from coverage.xml.
                if (fileExists('reports/coverage.xml')) {
                    def coverageXml = readFile('reports/coverage.xml')

                    def coverageMatch =
                        coverageXml =~ /line-rate="([0-9.]+)"/

                    if (coverageMatch.find()) {
                        testCoverageFraction = coverageMatch.group(1)
                    }
                }

                // Use awk to avoid Groovy sandbox restrictions.
                def testCoveragePercent = sh(
                    script: """
                        awk 'BEGIN {
                            printf "%.2f", ${testCoverageFraction} * 100
                        }'
                    """,
                    returnStdout: true
                ).trim()

                echo "Build status: ${buildStatusValue}"
                echo "Build duration: ${buildDurationSeconds}"
                echo "Tests passed: ${testsPassed}"
                echo "Tests failed: ${testsFailed}"
                echo "Test coverage: ${testCoveragePercent}%"

                def metricsPayload = """
pipeline_build_status{job="${METRICS_JOB}"} ${buildStatusValue}
pipeline_build_duration_seconds{job="${METRICS_JOB}"} ${buildDurationSeconds}
pipeline_tests_passed{job="${METRICS_JOB}"} ${testsPassed}
pipeline_tests_failed{job="${METRICS_JOB}"} ${testsFailed}
pipeline_test_coverage_percent{job="${METRICS_JOB}"} ${testCoveragePercent}
""".trim() + "\n"

                writeFile(
                    file: 'reports/pipeline-metrics.txt',
                    text: metricsPayload
                )

                archiveArtifacts(
                    artifacts: 'reports/pipeline-metrics.txt',
                    allowEmptyArchive: true
                )

                // Push metrics without masking the original build result.
                withEnv(["METRICS_PAYLOAD=${metricsPayload}"]) {
                    sh '''
                        set +e

                        printf '%s' "$METRICS_PAYLOAD" |
                            curl --silent --show-error \
                                --fail \
                                --data-binary @- \
                                "${PUSHGATEWAY_URL}/metrics/job/${METRICS_JOB}"

                        RESULT=$?

                        if [ "$RESULT" -ne 0 ]; then
                            echo "WARNING: Could not push metrics to Pushgateway"
                        fi

                        exit 0
                    '''
                }
            }
        }

        success {
            echo 'Pipeline completed successfully.'
        }

        failure {
            echo 'Pipeline failed. Sending Jenkins email notification.'

            emailext(
                to: 'johnsondsouza2023@gmail.com',
                subject: "Jenkins FAILURE: ${JOB_NAME} #${BUILD_NUMBER}",
                body: """Hello,

The Jenkins pipeline has failed.

Job: ${JOB_NAME}
Build Number: #${BUILD_NUMBER}
Status: ${currentBuild.currentResult}
Build URL: ${BUILD_URL}

Please check the Jenkins console output to identify the failure.

Regards,
Jenkins
""",
                attachLog: false
            )
        }

        cleanup {
            echo 'Pipeline cleanup completed.'
        }
    }
}
