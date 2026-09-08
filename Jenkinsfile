pipeline {
    agent any

    environment {
        DB_HOST = 'money-management-ci-mysql-1'
        DB_PORT = '3306'
        DB_NAME = 'money_management'

        DB_CREDENTIALS = credentials('ci-mysql-credentials')
    }

    stages {

        stage('Create Virtual Environment') {
            steps {
                sh 'python3 -m venv .venv'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '.venv/bin/pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                withEnv([
                    "DB_USER=${DB_CREDENTIALS_USR}",
                    "DB_PASSWORD=${DB_CREDENTIALS_PSW}"
                ]) {
                    sh '.venv/bin/python -m pytest -q'
                }
            }
        }

    }
}