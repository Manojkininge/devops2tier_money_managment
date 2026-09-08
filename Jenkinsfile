pipeline {
    agent any

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

    }
}