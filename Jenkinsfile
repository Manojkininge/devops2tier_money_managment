pipeline {
    agent any

    environment {
        // CI MySQL container hostname on the Docker CI network
        DB_HOST = 'money-management-ci-mysql-1'

        // MySQL listens on port 3306 inside the Docker network
        DB_PORT = '3306'

        // Database created by the CI MySQL container
        DB_NAME = 'money_management'

        // Retrieve database username/password securely from Jenkins Credentials
        DB_CREDENTIALS = credentials('ci-mysql-credentials')
    }

    stages {

        // Create an isolated Python environment for this Jenkins build
        stage('Create Virtual Environment') {
            steps {
                sh 'python3 -m venv .venv'
            }
        }

        // Install application dependencies inside the virtual environment
        stage('Install Dependencies') {
            steps {
                sh '.venv/bin/pip install -r requirements.txt'
            }
        }

        // Run tests and generate the XML coverage report for SonarQube
        stage('Run Tests') {
            steps {
                withEnv([
                    "DB_USER=${DB_CREDENTIALS_USR}",
                    "DB_PASSWORD=${DB_CREDENTIALS_PSW}"
                ]) {
                    sh '''
                        .venv/bin/python -m pytest \
                            --cov=app \
                            --cov-report=term-missing \
                            --cov-report=xml
                    '''
                }
            }
        }

    }
}