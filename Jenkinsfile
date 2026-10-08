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

                    curl --fail http://localhost:5000/health
                '''
            }
        }
    }

    post {
        always {
            sh '''
                docker rm -f interview-app-${BUILD_NUMBER} 2>/dev/null || true
            '''

            deleteDir()
        }
    }
}