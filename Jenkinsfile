
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
                                artifacts: 'reports/coverage.xml',
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
                    set -e

                    docker run -d \
                        --name "${APP_CONTAINER}" \
                        -p 18080:5000 \
                        "${APP_IMAGE}"

                    for i in $(seq 1 15); do
                        if curl -fsS http://localhost:18080/health; then
                            echo "Smoke test passed"
                            break
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
        }
    }

    post {
        always {
            script {
                /*
                 * Build status: 1 = SUCCESS, 0 = FAILURE
                 */
                def buildStatus =
                    currentBuild.currentResult == 'SUCCESS' ? 1 : 0

                def buildDurationSeconds =
                    currentBuild.duration / 1000.0

                def testsPassed = 0
                def testsFailed = 0
                def testCoveragePercent = 0.0

                /*
                 * Read test counts from the JUnit XML report.
                 */
                if (fileExists('reports/junit.xml')) {
                    def junitXml = readFile('reports/junit.xml')

                    def testsMatch =
                        junitXml =~ /tests="([0-9]+)"/

                    def failuresMatch =
                        junitXml =~ /failures="([0-9]+)"/

                    def errorsMatch =
                        junitXml =~ /errors="([0-9]+)"/

                    if (testsMatch.find()) {
                        def totalTests =
                            testsMatch.group(1).toInteger()

                        def failures = 0
                        def errors = 0

                        if (failuresMatch.find()) {
                            failures =
                                failuresMatch.group(1).toInteger()
                        }

                        if (errorsMatch.find()) {
                            errors =
                                errorsMatch.group(1).toInteger()
                        }

                        testsFailed = failures + errors
                        testsPassed = totalTests - testsFailed
                    }
                }

                /*
                 * Read overall line coverage from coverage.xml.
                 */
                if (fileExists('reports/coverage.xml')) {
                    def coverageXml =
                        readFile('reports/coverage.xml')

                    def coverageMatch =
                        coverageXml =~ /line-rate="([0-9.]+)"/

                    if (coverageMatch.find()) {
                        testCoveragePercent =
                            coverageMatch.group(1).toBigDecimal() * 100
                    }
                }

                echo "pipeline_build_status=${buildStatus}"
                echo "pipeline_build_duration_seconds=${buildDurationSeconds}"
                echo "pipeline_tests_passed=${testsPassed}"
                echo "pipeline_tests_failed=${testsFailed}"
                echo "pipeline_test_coverage_percent=${testCoveragePercent}"

                /*
                 * Publish metrics to Prometheus Pushgateway.
                 */
                sh """
                    cat <<'METRICS' | wget -q --post-file=- \
                        --header="Content-Type: text/plain" \
                        "${PUSHGATEWAY_URL}/metrics/job/interview_pipeline"

                    # TYPE pipeline_build_status gauge
                    pipeline_build_status ${buildStatus}

                    # TYPE pipeline_build_duration_seconds gauge
                    pipeline_build_duration_seconds ${buildDurationSeconds}

                    # TYPE pipeline_tests_passed gauge
                    pipeline_tests_passed ${testsPassed}

                    # TYPE pipeline_tests_failed gauge
                    pipeline_tests_failed ${testsFailed}

                    # TYPE pipeline_test_coverage_percent gauge
                    pipeline_test_coverage_percent ${testCoveragePercent}
                    METRICS
                """

                echo 'Metrics successfully pushed to Pushgateway.'
            }

            /*
             * Remove the smoke-test container.
             */
            sh '''
                docker rm -f "${APP_CONTAINER}" 2>/dev/null || true
            '''

            /*
             * Clean the Jenkins workspace.
             */
            deleteDir()
        }

        success {
            echo 'Pipeline completed successfully.'
        }

        failure {
            emailext(
                to: 'johnsondsouza2023@gmail.com',
                subject: "Jenkins FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
Jenkins build failed.

Job: ${env.JOB_NAME}
Build Number: #${env.BUILD_NUMBER}
Build Status: ${currentBuild.currentResult}

Build URL:
${env.BUILD_URL}

Console Output:
${env.BUILD_URL}console
"""
            )
        }

        cleanup {
            echo 'Pipeline cleanup completed.'
        }
    }
}
