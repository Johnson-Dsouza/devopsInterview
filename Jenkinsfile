pipeline {
    agent any

    options {
        timeout(time: 10, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    triggers {
        pollSCM('H/2 * * * *')
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Lint') {
            steps {
                sh 'flake8 app/'
            }
        }

        stage('Test') {
            steps {
                sh 'mkdir -p reports'
                sh 'pip3 install --break-system-packages -r app/requirements.txt'
                sh 'pytest --junitxml=reports/junit.xml'
            }

            post {
                always {
                    junit testResults: 'reports/junit.xml',
                          allowEmptyResults: true
                }
            }
        }

        stage('Build') {
            steps {
                sh 'docker build -t interview-app:${BUILD_NUMBER} .'
            }
        }

        stage('Smoke test') {
            steps {
                sh '''
                    docker run -d \
                      --name interview-app-${BUILD_NUMBER} \
                      -p 5000:5000 \
                      interview-app:${BUILD_NUMBER}

                    sleep 5

                    curl --fail http://host.docker.internal:5000/health
                '''
            }
        }
    }

    post {
        always {
            script {
                /*
                 * Build status:
                 * 1 = SUCCESS
                 * 0 = FAILURE
                 */
                def buildStatus = currentBuild.currentResult == 'SUCCESS' ? 1 : 0

                /*
                 * Jenkins build duration in seconds
                 */
                def buildDuration = (currentBuild.duration ?: 0) / 1000

                /*
                 * Default test counts
                 */
                def testsPassed = 0
                def testsFailed = 0

                /*
                 * Read JUnit test results if the report exists.
                 */
                if (fileExists('reports/junit.xml')) {

                    def junitXml = readFile('reports/junit.xml')

                    def testsMatch = junitXml =~ /tests="([0-9]+)"/
                    def failuresMatch = junitXml =~ /failures="([0-9]+)"/
                    def errorsMatch = junitXml =~ /errors="([0-9]+)"/

                    def totalTests = testsMatch.find()
                            ? testsMatch.group(1).toInteger()
                            : 0

                    def failures = failuresMatch.find()
                            ? failuresMatch.group(1).toInteger()
                            : 0

                    def errors = errorsMatch.find()
                            ? errorsMatch.group(1).toInteger()
                            : 0

                    testsFailed = failures + errors
                    testsPassed = totalTests - testsFailed
                }

                /*
                 * Display metrics in Jenkins console.
                 */
                echo "========================================"
                echo "Pipeline Metrics"
                echo "========================================"
                echo "pipeline_build_status=${buildStatus}"
                echo "pipeline_build_duration_seconds=${buildDuration}"
                echo "pipeline_tests_passed=${testsPassed}"
                echo "pipeline_tests_failed=${testsFailed}"
                echo "========================================"

                /*
                 * Push metrics to Prometheus Pushgateway.
                 *
                 * Jenkins and Pushgateway are on the same
                 * Docker Compose network, so the hostname
                 * 'pushgateway' can be used.
                 */
                sh """
                    cat <<EOF | curl --fail --data-binary @- http://pushgateway:9091/metrics/job/interview_pipeline
# TYPE pipeline_build_status gauge
pipeline_build_status ${buildStatus}

# TYPE pipeline_build_duration_seconds gauge
pipeline_build_duration_seconds ${buildDuration}

# TYPE pipeline_tests_passed gauge
pipeline_tests_passed ${testsPassed}

# TYPE pipeline_tests_failed gauge
pipeline_tests_failed ${testsFailed}
EOF
                """

                echo "Metrics successfully pushed to Pushgateway."
            }

            /*
             * Remove the application container if it exists.
             */
            sh '''
                docker rm -f interview-app-${BUILD_NUMBER} 2>/dev/null || true
            '''

            /*
             * Clean Jenkins workspace after every build.
             */
            deleteDir()
        }
    }
}